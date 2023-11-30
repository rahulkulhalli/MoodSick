import numpy as np
from pymongo import MongoClient
from pymongo.database import Collection
import torch
import os
from dotenv import load_dotenv
from typing import List


def get_collection_instance(db_name: str, collection_name: str) -> Collection:
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

    return client.get_database(db_name).get_collection(collection_name)


class DbEntry:
    """
    A DB entity class.
    """

    def __init__(self, result: dict):
        self._id = result.get('_id')
        self.embedding = np.array(result.get('embedding'))

        metadata = result.get('metadata')
        self.genre = metadata.get('genre')
        self.im_path = metadata.get('im_path')

    def __repr__(self):
        return f"DBEntry[_id={self._id}, genre={self.genre}, path={self.im_path}]"


def download_embeddings(collection: Collection) -> List[DbEntry]:
    # Get all the results.
    raw_results = collection.find({})
    print("Embeddings downloaded.")
    results = list()

    for result in raw_results:
        entry = DbEntry(result)
        results.append(entry)

    return results


def compute_aggregate_embedding(request: List[dict]):
    """
    Compute the aggregate embeddings from the given input and return the Spotify parameters.
    :param request: Assuming a list[dict]. for e.g.:
    ```
    request = [
        {'filename': 'a.wav', 'rating': 3},
        {'filename': 'b.wav', 'rating': 1},
        {'filename': 'c.wav', 'rating': 4}
    ]
    ```
    :return: The Spoitfy parameters..

    TODO: Port this to a separate utils file.
    """

    assert all(
        ['filename' in req and 'rating' in req for req in request]
    )

    assert all(
        [isinstance(req['rating'], (int, float) or req['rating'].isnumeric()) for req in request]
    )

    filenames = [req['filename'] for req in request]
    ratings = torch.tensor(
        [req['rating'] for req in request]
    ).unsqueeze(-1).float()

    # Normalize the ratings to weights.
    weights = ratings/ratings.sum()

    # get the embeddings.
    collection = get_collection_instance(
        db_name='embeddings_db',
        collection_name='spec_embeddings'
    )

    embeddings = download_embeddings(collection)

    # Search through the embeddings for the given filenames.
    filtered_embeddings = list(
        filter(lambda x: x.im_path in filenames, embeddings)
    )

    if not filtered_embeddings or len(filtered_embeddings) == 0:
        raise ValueError("No results found!")

    stacked_tensor = list()
    for embedding in filtered_embeddings:
        stacked_tensor.append(torch.from_numpy(embedding.embedding).float())

    # Stack the tensors and compute the mean across dim=0
    stacked_tensor = torch.stack(stacked_tensor, dim=0) * weights

    # Simply sum over the tensor now.
    return stacked_tensor.sum(dim=0)
