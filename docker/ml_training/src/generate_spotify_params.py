import argparse
from typing import List

import torch

from models.MapperMCMC import MapperMCMC
from utils import inference_utils

# Model is defined as a global variable to ensure that we only load it once in memory.
MODEL = None


# noinspection PyUnresolvedReferences
def enable_dropout_in_eval():

    # Init here because we change the global variable's attributes.
    global MODEL

    if MODEL is None:
        raise ValueError("Model is not initialized!")

    for m in MODEL.modules():
        if m.__class__.__name__.lower().startswith('dropout'):
            m.train()


# noinspection PyUnresolvedReferences,PyCallingNonCallable
def run_mcmc_inference(emb: torch.Tensor, num_passes: int = 50):

    """
    Generates the Spotify parameters by running inference through the MCMC model (with Dropout active).
    The model will run inference on `emb` for `num_passes` times and report the results. For each
    parameter, we have min_, max_, and target_.
    :param emb: Aggregated embedding vector.
    :param num_passes: Number of passes through the MCMC model (default: 100)
    :return: The required JSON response.
    """

    if MODEL is None:
        raise ValueError("Model is None!")

    MODEL.eval()
    enable_dropout_in_eval()

    prediction_tensor = list()

    for pass_ix in range(num_passes):
        prediction = MODEL(emb)
        prediction_tensor.append(prediction.detach())

    # Stack the predictions.
    stacked = torch.cat(prediction_tensor, dim=0)

    return_dict = dict()

    # Keep this order fixed!
    for attr_ix, attr in enumerate([
        'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness',
        'instrumentalness', 'liveness', 'valence', 'tempo', 'time_signature'
    ]):
        return_dict.update(
            {
                'min_' + attr: stacked[:, attr_ix].min().item(),
                'max_' + attr: stacked[:, attr_ix].max().item(),
                'target_' + attr: stacked[:, attr_ix].mean().item()
            }
        )

    return {'params': return_dict}


def load_model(model_dir: str):
    global MODEL

    if MODEL is not None:
        # Don't load model again.
        return

    try:
        MODEL = MapperMCMC()
        MODEL.load_state_dict(torch.load(model_dir, map_location='cpu'))
    except Exception as e:
        print("Error while loading model into global memory!")

    print("Model and weights loaded on CPU.")


def get_spotify_params(request: List[dict], n_inference_iters: int = 50):

    # Sample request:
    # sample = [
    #     {'query': 'blues00016', 'rating': '4'},
    #     {'query': 'rock00069', 'rating': 1.0},
    #     {'query': 'jazz00009', 'rating': 5},
    #     {'query': 'pop00001', 'rating': '3'},
    #     {'query': 'classical00091', 'rating': 4}
    # ]

    # Add a dummy batch dim.
    aggregate_embedding = inference_utils.compute_aggregate_embedding(request).unsqueeze(0)
    response = run_mcmc_inference(aggregate_embedding, num_passes=n_inference_iters)

    print("Generated response for request.")

    return response


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--model_weights', metavar='model-weights', type=str, default="./models/mcmc.pt", help="Path to model weights"
    )

    return parser.parse_args()


if __name__ == "__main__":

    args = parse_args()

    # Load the model into global memory.
    load_model(args.model_weights)

    # sample invocation from here. Actual endpoint will be invoked by Flask.
    # TODO: Comment this when the API endpoint is created.
    sample_request = [
        {'query': 'blues00016', 'rating': '4'},
        {'query': 'rock00069', 'rating': 1.0},
        {'query': 'jazz00009', 'rating': 5},
        {'query': 'pop00001', 'rating': '3'},
        {'query': 'classical00091', 'rating': 4}
    ]

    print(get_spotify_params(sample_request))
