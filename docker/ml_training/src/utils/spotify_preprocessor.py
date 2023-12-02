import json
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd
import torch
from sklearn.model_selection import train_test_split
from torch.utils.data import Dataset, DataLoader

from .db_utils import DbEntry
from .preprocessor import DatasetType


class SpotifyDataset(Dataset):
    def __init__(self, dset: DatasetType, inputs: List[DbEntry], outputs: pd.DataFrame):
        self.dset = dset
        self.inputs = inputs
        self.outputs = outputs

    def __len__(self):
        return len(self.inputs)

    def __getitem__(self, item):
        _input = self.inputs[item]

        # Sample a random output.
        genre_outputs = self.outputs.loc[
            self.outputs.mapped_genre == _input.genre,
            [
                'danceability','energy','key','loudness','mode','speechiness','acousticness',
                'instrumentalness','liveness','valence','tempo','time_signature'
            ]
        ].sample(1)

        # track_id = genre_outputs.track_id
        # genre_outputs.drop(columns=['track_id'], inplace=True)

        x = torch.tensor(_input.embedding.flatten(), dtype=torch.float)
        y = torch.tensor(genre_outputs.values.flatten(), dtype=torch.float)

        return x, y


class SpotifyPreprocessor:
    def __init__(self, embeddings: List[DbEntry], data_path: str, train_ratio: float = 0.8):
        self._embeddings = embeddings

        self._spotify_data_path = Path(data_path) / 'spotify_data.csv'
        self._genre_mapper_path = Path(data_path) / 'genre_mapping.json'
        assert self._spotify_data_path.exists() and self._genre_mapper_path.exists()

        self.train_ratio = train_ratio

        self.spotify_df = pd.read_csv(self._spotify_data_path)
        with open(self._genre_mapper_path, 'r') as f:
            self._genre_mapper = json.loads(f.read())['genre_mapping']

        # Create a new column with the mapped genre.
        self.spotify_df['mapped_genre'] = self.spotify_df.apply(
            lambda x: self._genre_mapper[x.track_genre], axis=1
        )

        # Make splits.
        self.input_splits = self._make_input_splits()
        self.output_splits = self._make_output_splits()

    def get_genre_mapping(self):
        return self._genre_mapper

    def _make_input_splits(self):
        train, test = list(), list()

        genre_dict = dict()
        for entry in self._embeddings:
            if entry.genre not in genre_dict:
                genre_dict[entry.genre] = list()

            genre_dict[entry.genre].append(entry)

        for genre in genre_dict.keys():
            values = genre_dict[genre]

            # Shuffle in-place.
            np.random.shuffle(values)

            split_ix = int(self.train_ratio * len(values))
            train.extend(values[:split_ix])
            test.extend(values[split_ix:])

        return {DatasetType.TRAIN: train, DatasetType.TEST: test}

    def _make_output_splits(self):
        x_tr, x_te = train_test_split(
            self.spotify_df, train_size=self.train_ratio,
            shuffle=True, stratify=self.spotify_df.mapped_genre
        )

        return {DatasetType.TRAIN: x_tr, DatasetType.TEST: x_te}

    def get_dataloader(self, dset: DatasetType, batch_size: int = 64, shuffle: bool = True):
        dataset = SpotifyDataset(dset, self.input_splits[dset], self.output_splits[dset])

        return DataLoader(
            dataset, batch_size=batch_size, shuffle=shuffle
        )