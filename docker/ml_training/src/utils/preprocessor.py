from enum import Enum
from pathlib import Path

import pandas as pd
import torch
import torchvision.transforms as tsfm
from PIL import Image
from torch.utils.data import DataLoader, Dataset


class DatasetType(Enum):
    TRAIN = 0
    TEST = 1
    FULL = 2


class CustomDataset(Dataset):
    def __init__(self, splits_df: dict, dset: DatasetType):

        self.splits = splits_df
        self.dset = dset

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

    def __len__(self):
        return len(self.splits[self.dset])

    def __getitem__(self, item):
        metadata = self.splits[self.dset].loc[item, :].to_dict()

        with Image.open(metadata['im_path'], 'r') as image:
            image = image.convert('RGB')
            x = self.transforms[self.dset](image)

        return x, x, metadata


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

        self._splits_df = self._make_ix_splits()

    def _make_ix_splits(self):
        genre_dict = dict()
        data = self.csv[['im_path', 'label']].copy()
        for genre in self.csv.label.unique():

            indices = data.loc[data.label == genre, :].index.tolist()
            split = int(len(indices) * self.train_size)

            train_files = data.loc[indices[:split], :]
            train_files = train_files.loc[
                train_files.apply(lambda x: Path(x.im_path).exists(), axis=1), :
            ].reset_index(drop=True, inplace=False)

            test_files = data.loc[indices[split:], :]
            test_files = test_files.loc[
                          test_files.apply(lambda x: Path(x.im_path).exists(), axis=1), :
            ].reset_index(drop=True, inplace=False)

            all_files = data.loc[indices, :]
            all_files = all_files.loc[
                         all_files.apply(lambda x: Path(x.im_path).exists(), axis=1), :
            ].reset_index(drop=True, inplace=False)

            genre_dict[genre] = {
                DatasetType.TRAIN: train_files,
                DatasetType.TEST: test_files,
                DatasetType.FULL: all_files
            }

        train_df = pd.concat(
            [genre_dict[g][DatasetType.TRAIN] for g in genre_dict.keys()],
            axis=0
        ).reset_index(drop=True, inplace=False)

        test_df = pd.concat(
            [genre_dict[g][DatasetType.TEST] for g in genre_dict.keys()],
            axis=0
        ).reset_index(drop=True, inplace=False)

        full_df = pd.concat(
            [genre_dict[g][DatasetType.FULL] for g in genre_dict.keys()],
            axis=0
        ).reset_index(drop=True, inplace=False)

        return {DatasetType.TRAIN: train_df, DatasetType.TEST: test_df, DatasetType.FULL: full_df}

    def get_splits(self):
        return self._splits_df

    def get_dataloader(self, dset: DatasetType, batch_size: int = 128, shuffle: bool = True):
        if self._splits_df is None:
            raise NotImplementedError("Genre dict is not created.")

        dataset = CustomDataset(self._splits_df, dset)

        return DataLoader(
            dataset,
            batch_size=batch_size,
            shuffle=shuffle
        )
