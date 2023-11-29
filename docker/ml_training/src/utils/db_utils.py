import numpy as np
from pymongo.database import Database


class DbEntry:
    """
    A DB entity class.
    """

    def __init__(self, result: dict):
        self._id = result.get('_id')
        self.embedding = np.array(result.get('embedding'))

        metadata = result.get('metadata')
        self.genre = metadata.get('genre')
        self.im_path = metadata.get('metadata')

    def __repr__(self):
        return f"DBEntry[_id={self._id}, genre={self.genre}, path={self.im_path}]"


def download_embeddings(collection: Database):
    # Get all the results.
    raw_results = collection.find({})
    print("Embeddings downloaded.")
    results = list()

    for result in raw_results:
        entry = DbEntry(result)
        results.append(entry)

    return results
