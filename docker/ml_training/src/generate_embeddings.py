import argparse
import os

from pathlib import Path

import numpy as np
import pymongo
from uuid import uuid4
from dotenv import load_dotenv

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
    parser.add_argument(
        '--upload', action='store_true', help="Upload the generated embeddings to Atlas"
    )
    parser.add_argument(
        '--batch_size', required=False, type=int, default=64, help="Batch size of dataloader"
    )
    parser.add_argument(
        '--simulate', action='store_true', help="Simulate a vector search"
    )

    return parser.parse_args()


def get_embeddings(autoencoder, dataloader):
    # Set model to eval mode.
    autoencoder.eval()

    embeddings = list()

    with torch.no_grad():
        for ix, (x, y, metadata) in tqdm(enumerate(dataloader), total=len(dataloader)):

            # (B, 2, 2, 1024)
            z, _ = autoencoder(x)

            # (B, 1, 1, 1024)
            z = F.adaptive_avg_pool2d(z, output_size=(1, 1))

            # (B, 1024)
            z = z.detach().view(-1, 1024).numpy()

            for row_ix in range(z.shape[0]):
                # Unfortunately, bson encoding seems to be unable to encode numpy vectors.
                # So, we will convert them to regular arrays.
                embeddings.append(
                    {
                        '_id': str(uuid4()),
                        'embedding': z[row_ix, :].tolist(),
                        'metadata': {
                            'im_path': metadata['im_path'][row_ix],
                            'genre': metadata['label'][row_ix]
                        }
                    }
                )

    return embeddings


if __name__ == "__main__":
    args = parse_args()

    # Load env variables.
    load_dotenv()

    user = os.getenv('MOODSICK_USER')
    password = os.getenv('MOODSICK_PASS')
    uri = os.getenv('ATLAS_URI')

    if user is None or password is None or uri is None:
        raise EnvironmentError(
            "Username and/or password and/or URI not found in environment."
        )

    model_path = Path(args.weights)
    if not model_path.exists():
        raise FileNotFoundError("Model weights file not found!")

    preprocessor = Preprocessor(data_path='../data/gztan')
    loader = preprocessor.get_dataloader(DatasetType.FULL, batch_size=args.batch_size, shuffle=False)

    # Load the model weights.
    model = ConvolutionalAutoencoder()
    model.load_state_dict(torch.load(model_path, map_location='cpu'))

    print("Loaded model and weights on CPU.")

    if args.generate_preview:
        sample, _, _ = next(iter(loader))
        model_utils.generate_previews(model, sample, 'cpu')

    print("Generating embeddings...")

    embeddings = get_embeddings(model, loader)
    print(f"Generated {len(embeddings)} embeddings, each of size: {len(embeddings[0]['embedding'])}")

    client = pymongo.MongoClient(
        f'mongodb+srv://{user}:{password}@{uri}/?retryWrites=true&w=majority'
    )

    print(f"Connected to Atlas.")

    db = client.embeddings_db
    collection = db.spec_embeddings

    if args.upload:

        print("Uploading embeddings to Atlas...")

        for embedding_doc in tqdm(embeddings):
            collection.insert_one(embedding_doc)

        print("Finished uploading embeddings to Atlas.")

    if args.simulate:
        # Number of choices.
        n = 5

        # Sample n random weights.
        random_weights = F.softmax(
            torch.FloatTensor(1, 5).normal_(0., 1.), dim=1
        ).numpy().flatten().tolist()

        sample_ix = np.random.choice(len(embeddings), n, replace=False)

        agg = list()
        for weight, ix in zip(random_weights, sample_ix):
            print(f"Song metadata: {embeddings[ix]['metadata']}, weight: {weight}")
            vec = (weight * np.array(embeddings[ix]['embedding'])).reshape((1, 1024))
            agg.append(vec)

        # Already weighted, now sum.
        agg = np.concatenate(agg, axis=0).sum(axis=0, keepdims=False).tolist()

        results = collection.aggregate([
            {"$vectorSearch": {
                "queryVector": agg,
                "path": "embedding",
                # All elements are candidates.
                "numCandidates": 999,
                # Return a max of 10 results.
                "limit": 10,
                "index": "EmbeddingSearch"
            }}
        ])

        if results is None:
            print("No results found!")

        print(10*'~')

        for ix, doc in enumerate(results):
            print(f"Result {ix}: Song metadata -> {doc['metadata']}")
