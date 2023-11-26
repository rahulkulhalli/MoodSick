from enum import Enum
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image


class DatasetType(Enum):
    TRAIN = 0
    TEST = 1


class Preprocessor:
    def __init__(self, csv_path: str, train_size: float = 0.8, save_crops: bool = False):
        self.csv_path = Path(csv_path)
        self.train_size = train_size
        self.test_size = 1. - self.train_size
        self.cropped_dir = self.csv_path.parent / 'cropped'
        if not self.cropped_dir.exists():
            self.cropped_dir.mkdir(exist_ok=False)
            print("Created cropped dir.")

        self.csv = pd.read_csv(csv_path)

        # Add a column for the filepath.
        self.csv['im_path'] = self.csv.apply(lambda x: x.filename.strip('wav').replace('.', '') + '.png', axis=1)

        self.genre_ix = self._make_ix_splits()
        self.genre_statistics = self.preprocess_image_and_compute_stats(save_crops)

    def _make_ix_splits(self):
        genre_dict = dict()
        for genre in self.csv.label.unique():
            index = self.csv.loc[self.csv.label == genre, :].index
            # shuffle the indices.
            shuffled = np.random.permutation(index)
            split = int(len(shuffled) * self.train_size)
            genre_dict[genre] = {DatasetType.TRAIN: shuffled[:split], DatasetType.TEST: shuffled[split:]}
        return genre_dict

    def preprocess_image_and_compute_stats(self, save_crops=False):

        def _save_images(genre, im_paths, path_to_save):
            for im_path in im_paths:
                joined_path = self.csv_path.parent / 'images_original' / genre / im_path
                if not joined_path.exists():
                    continue

                with Image.open(joined_path, 'r') as image:
                    # Convert from CMYK to RGB.
                    im = image.convert('RGB')
                    # Crop the image.
                    # (224, 352)
                    # im = im.crop(box=(44, 29, 396, 253))
                    im_name = 'cropped_' + im_path
                    im.save(path_to_save / im_name)

        def _compute_stats(im_path):
            images = list(im_path.glob('*.png'))
            means = []
            stds = []
            for image in images:
                with Image.open(image, 'r') as im:
                    # Convert the cropped images to ndarrays
                    arr = np.asarray(im)
                    # Compute channel-wise means
                    means.append(np.mean(arr, axis=(0, 1), keepdims=True))

                    # Compute the channel-wise
                    stds.append(np.std(arr, axis=(0, 1), keepdims=True))

            return (
                np.mean(np.concatenate(means, axis=0), axis=0).flatten(),
                np.mean(np.concatenate(stds, axis=0), axis=0).flatten()
            )

        genre_stats = dict()

        for genre, genre_dict in self.genre_ix.items():
            train_df = self.csv.loc[genre_dict[DatasetType.TRAIN]]
            test_df = self.csv.loc[genre_dict[DatasetType.TEST]]

            print(f"genre: {genre}, train: {train_df.shape}, test: {test_df.shape}")

            genre_dir = self.cropped_dir / genre
            if not genre_dir.exists():
                genre_dir.mkdir(exist_ok=False)

            train_dir = genre_dir / 'train'
            if not train_dir.exists():
                train_dir.mkdir(exist_ok=False)

            test_dir = genre_dir / 'test'
            if not test_dir.exists():
                test_dir.mkdir(exist_ok=False)

            if save_crops:
                _save_images(genre, train_df.im_path, train_dir)
                _save_images(genre, test_df.im_path, test_dir)

            genre_mean, genre_std = _compute_stats(train_dir)
            genre_stats[genre] = {'mean': genre_mean, 'std': genre_std}

        return genre_stats
