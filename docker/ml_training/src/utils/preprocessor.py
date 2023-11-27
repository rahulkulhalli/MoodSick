import torch

from PIL import Image
from enum import Enum
from pathlib import Path
from torch.utils.data import DataLoader, Dataset

import torchvision.transforms as tsfm
import numpy as np
import pandas as pd


class DatasetType(Enum):
    TRAIN = 0
    TEST = 1
    FULL = 2


class CustomDataset(Dataset):
    def __init__(self, genre_dict: dict, dset: DatasetType):

        self.g_dict = genre_dict
        self.dset = dset
        self.data = self._make_data()

        # Set-up transform functions.
        self.transforms = {
            DatasetType.TRAIN: tsfm.Compose(
                [
                    tsfm.PILToTensor(),
                    tsfm.RandomCrop(size=256),
                    tsfm.RandomRotation(degrees=(0, 180)),
                    tsfm.ConvertImageDtype(torch.float),
                ]
            ),
            DatasetType.TEST: tsfm.Compose(
                [
                    tsfm.PILToTensor(),
                    tsfm.CenterCrop(256),
                    tsfm.ConvertImageDtype(torch.float)
                ]
            ),
            DatasetType.FULL: tsfm.Compose(
                [
                    tsfm.PILToTensor(),
                    tsfm.CenterCrop(256),
                    tsfm.ConvertImageDtype(torch.float)
                ]
            )
        }

    def _make_data(self):
        data = list()
        for genre in self.g_dict.keys():
            data.extend(self.g_dict[genre][self.dset])

        data = [d for d in data if Path(d).exists()]
        return data

    def __len__(self):
        return len(self.data)

    def __getitem__(self, item):
        data = self.data[item]

        with Image.open(data, 'r') as image:
            image = image.convert('RGB')
            x = self.transforms[self.dset](image)

        return x, x


class Preprocessor:
    def __init__(self, data_path: str, train_size: float = 0.8):
        self.data_path = Path(data_path)
        self.train_size = train_size
        self.test_size = 1. - self.train_size

        # Read the CSV file.
        self.csv = pd.read_csv(self.data_path / 'features_30_sec.csv')

        # Add a column for the filepath.
        self.csv['im_path'] = self.csv.apply(
            lambda x: data_path + '/images_original/' + x.label + '/'
                      + x.filename.strip('wav').replace('.', '') + '.png',
            axis=1
        )

        self._genre_dict = self._make_ix_splits()

    def _make_ix_splits(self):
        genre_dict = dict()
        for genre in self.csv.label.unique():
            index = self.csv.loc[self.csv.label == genre, :].index
            # shuffle the indices.
            shuffled = np.random.permutation(index)
            split = int(len(shuffled) * self.train_size)

            train_files = self.csv.loc[shuffled[:split], 'im_path'].tolist()
            test_files = self.csv.loc[shuffled[split:], 'im_path'].tolist()
            all_files = self.csv.loc[shuffled, 'im_path'].tolist()

            genre_dict[genre] = {
                DatasetType.TRAIN: train_files,
                DatasetType.TEST: test_files,
                DatasetType.FULL: all_files
            }

        return genre_dict

    def get_genre_dict(self):
        return self._genre_dict

    def get_dataloader(self, dset: DatasetType, batch_size: int = 128, shuffle: bool = True):
        if self._genre_dict is None:
            raise NotImplementedError("Genre dict is not created.")

        dataset = CustomDataset(self._genre_dict, dset)

        return DataLoader(
            dataset,
            batch_size=batch_size,
            shuffle=shuffle
        )
