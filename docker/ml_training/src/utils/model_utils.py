import torch
import torchvision.transforms.functional as F
from torchvision.utils import make_grid
from pathlib import Path
import numpy as np
import torch.nn as nn
import matplotlib.pyplot as plt
from .preprocessor import DatasetType


def show(imgs):
    if not isinstance(imgs, list):
        imgs = [imgs]
    fig, axs = plt.subplots(ncols=len(imgs), squeeze=False)
    for i, img in enumerate(imgs):
        img = img.detach()
        img = F.to_pil_image(img)
        axs[0, i].imshow(np.asarray(img))
        axs[0, i].set(xticklabels=[], yticklabels=[], xticks=[], yticks=[])
    plt.show()


def generate_previews(model, test_input, device):
    # Pass through the model.

    _input = test_input.to(device)

    _, predicted = model(_input)

    grid = make_grid(predicted, nrow=8, normalize=False)
    show(grid)


def weights_init(m):
    if isinstance(m, (nn.Conv1d, nn.Conv2d, nn.ConvTranspose2d, nn.Linear)):
        nn.init.xavier_uniform_(m.weight.data)
        if m.bias is not None:
            nn.init.zeros_(m.bias.data)


def plot_losses(losses: dict):
    # Let's sort the keys first.
    sorted_keys = sorted(list(losses.keys()))

    train_losses, test_losses = list(), list()

    # Now, iterate over the sorted keys.
    for epoch_ix in sorted_keys:
        train_losses.extend(losses[epoch_ix][DatasetType.TRAIN])
        test_losses.extend(losses[epoch_ix][DatasetType.TEST])

    fig, ax = plt.subplots(nrows=1, ncols=2)
    ax[0].plot(train_losses, 'b-')
    ax[0].set_title('Train MSE loss')
    ax[1].plot(test_losses, 'r-')
    ax[1].set_title('Test MSE loss')
    plt.tight_layout()
    plt.show()


def save_model(model: nn.Module, dir: str):
    torch.save(model.state_dict(), dir)
    print(f"Model successfully saved at {dir}.")


def load_model(model: nn.Module, weights: Path):
    assert weights.exists()

    # Load the model weights on the cpu.
    return model.load_state_dict(torch.load(weights, map_location='cpu'))
