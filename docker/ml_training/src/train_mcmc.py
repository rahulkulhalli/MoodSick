import os

from dotenv import load_dotenv
from pymongo import MongoClient

from utils.db_utils import download_embeddings
from utils.preprocessor import DatasetType
from utils.spotify_preprocessor import SpotifyPreprocessor
from models.MapperMCMC import MapperMCMC

import torch.optim as optim
import torch.nn as nn


def train(_epoch, _model, dataloader, _device, _opt, _criterion):

    print_steps = len(dataloader) // 10

    for ix, (x, y) in enumerate(dataloader):

        _opt.zero_grad()

        x = x.to(_device)
        y = y.to(_device)

        preds = _model(x)
        loss = _criterion(preds, y)

        if ix and ix % print_steps == 0:
            print(f"Epoch {_epoch}, Iteration {ix} | Loss: {loss}")

        loss.backward()
        _opt.step()


if __name__ == "__main__":

    # resolve device.
    # device = torch.device('mps') if torch.backends.mps.is_available() else 'cpu'
    device = 'cpu'

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
    train_loader = preprocessor.get_dataloader(DatasetType.TRAIN, batch_size=8)
    test_loader = preprocessor.get_dataloader(DatasetType.TEST, batch_size=8)

    model = MapperMCMC()
    model.to(device)

    opt = optim.Adam(model.parameters(), lr=1e-3)
    criterion = nn.MSELoss()

    epochs = 50
    for epoch in range(epochs):
        train(epoch, model, train_loader, device, opt, criterion)

