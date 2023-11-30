import torch
import torch.nn as nn
from models.MapperMCMC import MapperMCMC
from utils import db_utils
# from torchsummary import summary
from pprint import pprint


def enable_dropout_in_eval(_model: nn.Module):
    for m in _model.modules():
        if m.__class__.__name__.lower().startswith('dropout'):
            m.train()


def run_mcmc_inference(_model: nn.Module, emb: torch.Tensor, num_passes: int = 50):

    """
    output:
    ['danceability','energy','key','loudness','mode','speechiness','acousticness',
    'instrumentalness','liveness','valence','tempo','time_signature']

    :param _model:
    :param emb:
    :param num_passes:
    :return:
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

    # print(summary(model, (1024,)))

    print("Model and weights loaded on CPU")

    sample = [
        {'filename': '../data/gztan/images_original/blues/blues00016.png', 'rating': 4},
        {'filename': '../data/gztan/images_original/rock/rock00069.png', 'rating': 1},
        {'filename': '../data/gztan/images_original/jazz/jazz00009.png', 'rating': 5},
        {'filename': '../data/gztan/images_original/pop/pop00001.png', 'rating': 3},
        {'filename': '../data/gztan/images_original/classical/classical00091.png', 'rating': 4}
    ]

    # Add a dummy batch dim.
    aggregate_embedding = db_utils.compute_aggregate_embedding(sample).unsqueeze(0)
    response = run_mcmc_inference(model, aggregate_embedding)

    pprint(response)

