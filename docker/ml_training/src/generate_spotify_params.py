from pprint import pprint

import torch
import torch.nn as nn

from models.MapperMCMC import MapperMCMC
from utils import inference_utils


def enable_dropout_in_eval(_model: nn.Module):
    for m in _model.modules():
        if m.__class__.__name__.lower().startswith('dropout'):
            m.train()


def run_mcmc_inference(_model: nn.Module, emb: torch.Tensor, num_passes: int = 50):

    """
    Generates the Spotify parameters by running inference through the MCMC model (with Dropout active).
    The model will run inference on `emb` for `num_passes` times and report the results. For each
    parameter, we have min_, max_, and target_.
    :param _model: MCMC model.
    :param emb: Aggregated embedding vector.
    :param num_passes: Number of passes through the MCMC model (default: 100)
    :return: The required JSON response.
    """

    _model.eval()
    enable_dropout_in_eval(_model)

    # emb = emb.double()

    prediction_tensor = list()

    for pass_ix in range(num_passes):
        prediction = _model(emb)
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


if __name__ == "__main__":

    weights_dir = './models/mcmc.pt'
    model = MapperMCMC()
    model.load_state_dict(torch.load(weights_dir, map_location='cpu'))

    print("Model and weights loaded on CPU")

    sample = [
        {'query': 'blues00016', 'rating': '4'},
        {'query': 'rock00069', 'rating': 1.0},
        {'query': 'jazz00009', 'rating': 5},
        {'query': 'pop00001', 'rating': '3'},
        {'query': 'classical00091', 'rating': 4}
    ]

    # Add a dummy batch dim.
    aggregate_embedding = inference_utils.compute_aggregate_embedding(sample).unsqueeze(0)
    response = run_mcmc_inference(model, aggregate_embedding)

    pprint(response)

