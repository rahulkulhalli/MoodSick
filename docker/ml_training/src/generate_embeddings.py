import argparse

from pathlib import Path

import torch
import torch.nn.functional as F

from models.static_autoencoder import ConvolutionalAutoencoder
from utils import model_utils
from tqdm import tqdm
from utils.preprocessor import DatasetType
from utils.preprocessor import Preprocessor


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'weights', type=str, help="Path to the model weights"
    )
    parser.add_argument(
        '--generate-preview', action='store_true', help="Generate a batch preview"
    )
    # TODO: Add mongo API key here.

    return parser.parse_args()


def get_embeddings(autoencoder, dataloader):
    # Set model to eval mode.
    autoencoder.eval()

    embeddings = list()

    with torch.no_grad():
        for ix, (x, y) in tqdm(enumerate(dataloader)):
            # (B, 2, 2, 1024)
            z, _ = autoencoder(x)

            # (B, 1, 1, 1024)
            z = F.adaptive_avg_pool2d(z, output_size=(1, 1))

            # (B, 1024)
            z = z.detach().view(-1, 1024).numpy()

            for row_ix in range(z.shape[0]):
                embeddings.append(z[row_ix, :])

    return embeddings


if __name__ == "__main__":
    args = parse_args()

    model_path = Path(args.weights)
    if not model_path.exists():
        raise FileNotFoundError("Model weights file not found!")

    # Load the model weights.
    model = ConvolutionalAutoencoder()
    model.load_state_dict(torch.load(model_path, map_location='cpu'))

    print("Loaded model and weights on CPU.")

    preprocessor = Preprocessor(data_path='../data/gztan')
    loader = preprocessor.get_dataloader(DatasetType.FULL, batch_size=64, shuffle=False)

    if args.generate_preview:
        sample, _ = next(iter(loader))
        model_utils.generate_previews(model, sample, 'cpu')

    vectors = get_embeddings(model, loader)

    print(len(vectors), vectors[0].shape)