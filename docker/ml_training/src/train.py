import argparse
import shutil

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import torch.optim as optim
from torch.optim.lr_scheduler import MultiStepLR
from time import perf_counter

import model_config
# from models.autoencoder import MultiModalEncoder
from models.static_autoencoder import ConvolutionalAutoencoder
from utils.preprocessor import DatasetType
from utils.dataset import AutoencoderDataset
from utils.preprocessor import Preprocessor
from utils import model_utils


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


def train(model, optim, dataloader, loss_fn):

    model.train()
    optim.zero_grad()

    iters = len(dataloader)
    log_every = iters//10

    losses = []
    for ix, (X, Y) in enumerate(dataloader):
        X = X.to(device)
        Y = Y.to(device)

        z, y_pred = model(X)
        loss = loss_fn(y_pred, Y)

        losses.append(loss.item())

        if log_every == 0 or (ix and ix % log_every == 0):
            print(f"\t--> Loss: {np.nanmean(losses)}")

        loss.backward()
        optim.step()

    return losses


def evaluate(model, dataloader, loss_fn, **kwargs):
    model.eval()
    log_every = len(dataloader)//5

    losses = []
    with torch.no_grad():
        for ix, (X, Y) in enumerate(dataloader):
            X = X.to(device)
            Y = Y.to(device)

            z, y_pred = model(X)
            loss = loss_fn(y_pred, Y)

            losses.append(loss.item())

            if log_every == 0 or (ix and ix % log_every == 0):
                print(f"\t--> Loss: {np.nanmean(losses)}")

    return losses


if __name__ == "__main__":

    args = parse_arguments()
    device = torch.device('mps') if torch.backends.mps.is_available() else 'cpu'
    print(f"Device set to: {device}")

    preprocessor = Preprocessor(args.data_path, train_size=0.8, save_crops=True)
    print(f"Finished Cropping and computing statistics.")

    # Define the datasets and dataloaders.
    train_dset = AutoencoderDataset(DatasetType.TRAIN, preprocessor.cropped_dir, preprocessor, tsfm=True)
    train_loader = DataLoader(train_dset, batch_size=args.batch_size, shuffle=True)

    # Don't transform test data.
    test_dset = AutoencoderDataset(DatasetType.TEST, preprocessor.cropped_dir, preprocessor, tsfm=False)
    test_loader = DataLoader(test_dset, batch_size=args.batch_size, shuffle=False)

    config = model_config.get_config()

    # model = MultiModalEncoder(config=config)
    # Instantiate the model
    model = ConvolutionalAutoencoder()

    model.apply(model_utils.weights_init)

    model = model.to(device)
    num_params = sum(p.numel() for p in model.parameters())
    print(f"Model loaded. Number of trainable parameters: {num_params}")

    # sample, _ = next(iter(train_loader))
    # sample = sample.to(device)
    # z, out = model(sample)
    # step_every = 25

    init_lr = 1e-3
    optimizer = optim.Adam(model.parameters(), lr=init_lr)
    scheduler = MultiStepLR(
        optimizer,
        milestones=[20*i for i in range(1, 12)],
        gamma=0.9
    )

    loss_fn = nn.MSELoss()

    print("Initial LR: ", init_lr)
    print(50*'-')

    try:

        total_losses = dict()
        start = perf_counter()
        for epoch in range(1, args.epochs + 1):
            tr_losses = train(model, optimizer, train_loader, loss_fn)
            print(f"[Epoch {epoch}/{args.epochs}] Mean train loss: {np.nanmean(tr_losses)}")

            print(50 * '-')

            te_losses = evaluate(model, test_loader, loss_fn, log_every=100)
            print(f"[Epoch {epoch}/{args.epochs}] Mean test loss: {np.nanmean(te_losses)}")

            print(50 * '-')

            total_losses[epoch] = {DatasetType.TRAIN: tr_losses, DatasetType.TEST: te_losses}
            scheduler.step()
            print("Learning rate: ", optimizer.param_groups[0]['lr'])
            print(50 * '+')

        sample, _ = next(iter(test_loader))
        model_utils.generate_previews(model, sample, device)
        model_utils.plot_losses(total_losses)
        print(f"Training took {(perf_counter() - start)/60} minutes.")
        model_utils.save_model(model, dir='./models/unet_1.pt')

    except KeyboardInterrupt:
        # show a sample.
        sample, _ = next(iter(test_loader))
        model_utils.generate_previews(model, sample, device)

    finally:
        # # Delete the temporary cropped dir.
        shutil.rmtree('../data/gztan/cropped', ignore_errors=False)