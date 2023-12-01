import re
from typing import List

import torch

from .db_utils import download_embeddings, get_collection_instance


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
    :return: The aggregate embedding vector.
    """

    pattern = re.compile(r'\b(blues|classical|country|disco|hiphop|jazz|metal|pop|reggae|rock)\d{5}\b')

    assert all(
        [
            'query' in req and 'rating' in req
            for req in request
        ]
    )

    assert all(
        [
            isinstance(req['rating'], (int, float)) or req['rating'].isnumeric()
            for req in request
        ]
    )

    queries = [req['query'] for req in request]

    ratings = torch.tensor(
        # Cast all ratings to integers.
        [int(req['rating']) for req in request]
    ).unsqueeze(-1).float()

    # Normalize the ratings to weights.
    weights = ratings/ratings.sum()

    # get the embeddings.
    collection = get_collection_instance(
        db_name='embeddings_db',
        collection_name='spec_embeddings'
    )

    embeddings = download_embeddings(collection)

    filtered_embeddings = list()

    # O(n^2) is BAD. Optimize this somehow.
    for query_name in queries:
        for embedding in embeddings:
            path = embedding.im_path
            matcher = re.search(pattern, path)
            if matcher is None:
                continue
            if matcher[0] == query_name:
                filtered_embeddings.append(embedding)
                break

    if len(filtered_embeddings) == 0:
        raise ValueError("No results found!")

    stacked_tensor = list()
    for embedding in filtered_embeddings:
        stacked_tensor.append(torch.from_numpy(embedding.embedding).float())

    # Stack the tensors and compute the mean across dim=0
    stacked_tensor = torch.stack(stacked_tensor, dim=0) * weights

    # Simply sum over the tensor now.
    return stacked_tensor.sum(dim=0)
