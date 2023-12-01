import argparse

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

from models.MapperMCMC import MapperMCMC
from utils import model_utils, db_utils
from utils.preprocessor import DatasetType
from utils.spotify_preprocessor import SpotifyPreprocessor


def enable_dropout_in_eval(_model: nn.Module):
    for m in _model.modules():
        if m.__class__.__name__.lower().startswith('dropout'):
            m.train()


def train(_epoch, _model, dataloader, _device, _opt, _criterion):

    _model.train()

    print_steps = len(dataloader) // 5
    if not print_steps:
        print_steps = 1

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


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'name', type=str, help="Model name", metavar="NAME"
    )
    parser.add_argument(
        '--batch-size', type=int, default=128, help="Batch size to use for train and test loaders"
    )
    parser.add_argument(
        '--n-epochs', type=int, default=250, help="Number of epochs to train for"
    )
    parser.add_argument(
        '--init-lr', type=float, default=1e-3, help="Initial learning rate"
    )
    parser.add_argument(
        '--n-inference-passes', type=int, default=10, help="Number of inference passes"
    )

    return parser.parse_args()


if __name__ == "__main__":

    args = parse_args()

    # resolve device.
    device = torch.device('mps') if torch.backends.mps.is_available() else 'cpu'
    # device = 'cpu'

    collection = db_utils.get_collection_instance('embeddings_db', 'spec_embeddings')

    # Get embeddings.
    embeddings = db_utils.download_embeddings(collection)

    # Get preprocessor.
    preprocessor = SpotifyPreprocessor(embeddings, '../data')
    train_loader = preprocessor.get_dataloader(DatasetType.TRAIN, batch_size=args.batch_size)
    test_loader = preprocessor.get_dataloader(DatasetType.TEST, batch_size=args.batch_size)

    model = MapperMCMC()
    print("#Parameters: ", sum(p.numel() for p in model.parameters()))
    model_utils.weights_init(model)
    model.to(device)

    opt = optim.Adam(model.parameters(), lr=args.init_lr)
    criterion = nn.MSELoss()

    loss_dict = dict()
    for epoch in range(args.n_epochs):

        loss_dict[epoch] = {}

        tr_epoch_losses = train(epoch, model, train_loader, device, opt, criterion)
        loss_dict[epoch][DatasetType.TRAIN] = tr_epoch_losses

        print(50*'+')

        te_epoch_losses = test(epoch, model, test_loader, device, criterion, num_passes=args.n_inference_passes)
        loss_dict[epoch][DatasetType.TEST] = te_epoch_losses

        print(50 * '+')

        if epoch and epoch % 50 == 0 and epoch < 300:
            print("Bumping down LR by 15%")
            opt.param_groups[0]['lr'] *= 0.85
            print("New LR: ", opt.param_groups[0]['lr'])

    # Plot losses.
    model_utils.plot_losses(loss_dict)

    model_utils.save_model(model, f"./models/{args.name}.pt")
