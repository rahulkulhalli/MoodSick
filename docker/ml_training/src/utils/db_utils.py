import os
from typing import List

import numpy as np
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.database import Collection


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
