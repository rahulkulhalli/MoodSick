import argparse

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import torch.optim as optim

import model_config
from models.autoencoder import MultiModalEncoder
from utils.preprocessor import DatasetType
from utils.dataset import AutoencoderDataset
from utils.preprocessor import Preprocessor


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'data_path', type=str, help="Input CSV path for training"
    )
    parser.add_argument(
        '--epochs', required=False, default=10, type=int, help="Number of epochs to train model for"
    )
    parser.add_argument(
        '--model-dir', required=False, default='models/', type=str, help="Directory to store model"
    )
    parser.add_argument(
        '--batch-size', required=False, default=16, type=int, help="Batch size"
    )

    return parser.parse_args()


def train(model, optim, dataloader, loss_fn, **kwargs):

    model.train()
    optim.zero_grad()

    log_every = kwargs['log_every']

    losses = []
    for ix, (X, Y) in enumerate(dataloader):
        X = X.to(device)
        Y = Y.to(device)

        z, y_pred = model(X)
        loss = loss_fn(y_pred, Y)

        losses.append(loss.item())

        if ix and ix % log_every == 0:
            print(f"Loss: {np.nanmean(losses)}")

        loss.backward()
        optim.step()

    return losses


def evaluate(model, dataloader, loss_fn, **kwargs):
    model.eval()
    log_every = kwargs['log_every']

    losses = []
    with torch.no_grad():
        for ix, (X, Y) in enumerate(dataloader):
            X = X.to(device)
            Y = Y.to(device)

            z, y_pred = model(X)
            loss = loss_fn(y_pred, Y)

            losses.append(loss.item())

            if ix and ix % log_every == 0:
                print(f"Loss: {np.nanmean(losses)}")

    return losses


if __name__ == "__main__":
    args = parse_arguments()
    device = torch.device('mps') if torch.backends.mps.is_available() else 'cpu'
    print(f"Device set to: {device}")

    preprocessor = Preprocessor(args.data_path, save_crops=True)
    print(f"Finished Cropping and computing statistics.")

    # Define the datasets and dataloaders.
    train_dset = AutoencoderDataset(DatasetType.TRAIN, preprocessor.cropped_dir, preprocessor)
    train_loader = DataLoader(train_dset, batch_size=args.batch_size, shuffle=True)

    test_dset = AutoencoderDataset(DatasetType.TEST, preprocessor.cropped_dir, preprocessor)
    test_loader = DataLoader(test_dset, batch_size=args.batch_size, shuffle=False)

    config = model_config.get_config()

    model = MultiModalEncoder(im_size=1, config=config)
    model = model.to(device)
    print("Model loaded.")

    optimizer = optim.Adam(model.parameters(), lr=1e-4)
    loss_fn = nn.MSELoss()

    print(50*'-')

    total_losses = dict()
    for epoch in range(1, args.epochs + 1):
        tr_losses = train(model, optimizer, train_loader, loss_fn, log_every=100)
        print(f"Mean train loss for epoch {epoch}: {np.nanmean(tr_losses)}")

        te_losses = evaluate(model, test_loader, loss_fn, log_every=100)
        print(f"Mean test loss for epoch {epoch}: {np.nanmean(te_losses)}")

        total_losses[epoch] = {DatasetType.TRAIN: tr_losses, DatasetType.TEST: te_losses}
