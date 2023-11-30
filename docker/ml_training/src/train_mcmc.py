import os
import torch

from dotenv import load_dotenv
from pymongo import MongoClient

from utils.db_utils import download_embeddings
from utils.preprocessor import DatasetType
from utils.spotify_preprocessor import SpotifyPreprocessor
from utils import model_utils
from models.MapperMCMC import MapperMCMC

import torch.optim as optim
import torch.nn as nn
import numpy as np


def enable_dropout_in_eval(_model: nn.Module):
    for m in _model.modules():
        if m.__class__.__name__.lower().startswith('dropout'):
            m.train()


def train(_epoch, _model, dataloader, _device, _opt, _criterion):

    _model.train()

    print_steps = len(dataloader) // 5

    losses = []
    for ix, (x, y) in enumerate(dataloader):

        _opt.zero_grad()

        x = x.to(_device)
        y = y.to(_device)

        preds = _model(x)
        loss = _criterion(preds, y)
        losses.append(loss.item())

        if ix and ix % print_steps == 0:
            print(f"Epoch {_epoch}, batch_ix {ix} | Mean train loss: {np.nanmean(losses)}")

        loss.backward()
        _opt.step()

    return losses


def test(_epoch, _model, _loader, _device, _criterion, num_passes=5):
    model.eval()
    # Keep dropout active
    enable_dropout_in_eval(model)

    print_every = len(_loader) // 5
    if not print_every:
        print_every = 1

    losses = []

    # No gradient flow allowed.
    with torch.no_grad():
        for ix, (x, y) in enumerate(_loader):
            x = x.to(_device)
            y = y.to(_device)

            y_passes = list()

            for mc in range(num_passes):
                y_pred = _model(x)
                y_passes.append(y_pred)

            y_stacked = torch.stack(y_passes, dim=0)
            y_avg = y_stacked.mean(dim=0, keepdims=True)

            if y_avg.ndim == 3:
                y_avg = y_avg.squeeze(0)

            if y.ndim == 3:
                y = y.squeeze(0)

            loss = _criterion(y_avg, y)

            losses.append(loss.detach().cpu().item())

            if ix and ix % print_every == 0:
                print(f"Epoch {_epoch}, batch_ix {ix} | Mean test loss: {np.nanmean(losses)}")

    return losses


if __name__ == "__main__":

    # resolve device.
    device = torch.device('mps') if torch.backends.mps.is_available() else 'cpu'
    # device = 'cpu'

    load_dotenv()

    user = os.getenv('MOODSICK_USER')
    password = os.getenv('MOODSICK_PASS')
    uri = os.getenv('ATLAS_URI')

    if user is None or password is None or uri is None:
        raise EnvironmentError(
            "Username and/or password and/or URI not found in environment."
        )

    client = MongoClient(
        f'mongodb+srv://{user}:{password}@{uri}/?retryWrites=true&w=majority'
    )

    collection = client.embeddings_db.spec_embeddings

    # Get embeddings.
    embeddings = download_embeddings(collection)

    # Get preprocessor.
    preprocessor = SpotifyPreprocessor(embeddings, '../data')
    train_loader = preprocessor.get_dataloader(DatasetType.TRAIN, batch_size=128)
    test_loader = preprocessor.get_dataloader(DatasetType.TEST, batch_size=64)

    model = MapperMCMC()
    print("#Parameters: ", sum(p.numel() for p in model.parameters()))
    model_utils.weights_init(model)
    model.to(device)

    opt = optim.Adam(model.parameters(), lr=2e-3)
    criterion = nn.MSELoss()

    epochs = 250
    loss_dict = dict()
    for epoch in range(epochs):

        loss_dict[epoch] = {}

        tr_epoch_losses = train(epoch, model, train_loader, device, opt, criterion)
        loss_dict[epoch][DatasetType.TRAIN] = tr_epoch_losses

        print(50*'+')

        te_epoch_losses = test(epoch, model, test_loader, device, criterion, num_passes=10)
        loss_dict[epoch][DatasetType.TEST] = te_epoch_losses

        print(50 * '+')

        if epoch and epoch % 50 == 0:
            print("Bumping down LR by 5%")
            opt.param_groups[0]['lr'] *= 0.95

    # Plot losses.
    model_utils.plot_losses(loss_dict)

    model_utils.save_model(model, "./models/mcmc.pt")
