from pathlib import Path

import pandas as pd
import torch
import torchvision.transforms as transforms
from PIL import Image
from torch.utils.data import Dataset

from .preprocessor import DatasetType, Preprocessor


class AutoencoderDataset(Dataset):
    def __init__(self, dset: DatasetType, dir: Path, preprocessor: Preprocessor, tsfm: bool = False):
        self.dset = dset
        self.dir = dir
        self.tsfm = tsfm
        self.preprocessor = preprocessor
        self.transforms = self._setup_transforms()
        self.test_tsfm = transforms.Compose([
            # transforms.Grayscale(num_output_channels=1),
            transforms.PILToTensor(),
            transforms.CenterCrop(256),
            transforms.ConvertImageDtype(torch.float)
        ])
        self.data = self._load()

    def _load(self):
        rows = []
        for genre in self.preprocessor.get_genre_dict().keys():
            subdir = self.dir / genre / 'train' if self.dset == DatasetType.TRAIN else self.dir / genre / 'test'
            pngs = list(subdir.glob('*.png'))
            for png_file in pngs:
                rows.append((genre, png_file))

        return pd.DataFrame(rows, columns=['genre', 'filename'])

    def _setup_transforms(self):
        transforms_dict = dict()
        for genre, tsfm in self.preprocessor.genre_statistics.items():
            transforms_dict[genre] = transforms.Compose([
                # transforms.Grayscale(num_output_channels=1),
                transforms.PILToTensor(),
                # transforms.CenterCrop(256),
                transforms.RandomCrop(size=256),
                transforms.RandomRotation(degrees=(0, 180)),
                transforms.ConvertImageDtype(torch.float),
                # transforms.Normalize(mean=tsfm['mean'], std=tsfm['std'])
            ])
        return transforms_dict

    def __len__(self):
        return len(self.data)

    def __getitem__(self, i):
        im_name = self.data.loc[i, 'filename']
        genre = self.data.loc[i, 'genre']

        with Image.open(im_name, 'r') as im:
            if self.tsfm:
                im = self.transforms[genre](im)
            else:
                im = self.test_tsfm(im)

        # X and Y are the same.
        return im, im
