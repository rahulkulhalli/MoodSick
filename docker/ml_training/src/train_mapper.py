import os
import pyro
import pyro.distributions as dist
import torch
from pyro.infer import SVI, Trace_ELBO
from pyro.infer.autoguide import AutoDiagonalNormal
from pyro.optim import Adam

from dotenv import load_dotenv
from pymongo import MongoClient
from utils.db_utils import download_embeddings
from utils.preprocessor import DatasetType
from utils.spotify_preprocessor import SpotifyPreprocessor
from models.mapper_network import MappingNetwork


def train(_epoch, _model, _guide, _svi, dataloader, _device):

    print_steps = len(dataloader) // 10

    for ix, (x, y) in enumerate(dataloader):
        x = x.to(_device)
        y = y.to(_device)

        pyro.clear_param_store()

        loss = _svi.step(x, y)

        if ix and ix % print_steps == 0:
            print(f"Epoch {_epoch}, Iteration {ix} | Loss: {loss}")


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

    # for _, (x, y) in enumerate(train_loader):
    #     print(x.size(), y.size())

    model = MappingNetwork(device=device)
    guide = AutoDiagonalNormal(model)

    model = model.to(device)
    guide = guide.to(device)

    print("Model and guide initialized.")

    svi = SVI(model, guide, Adam({"lr": 0.01}), loss=Trace_ELBO())

    print("SVI initialized")

    epochs = 20
    for epoch in range(epochs):
        train(epoch, model, guide, svi, train_loader, device)

