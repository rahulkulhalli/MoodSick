from pathlib import Path
import pandas as pd
import torch
import torchvision.transforms as transforms
from PIL import Image
from torch.utils.data import Dataset
from .preprocessor import DatasetType, Preprocessor


class AutoencoderDataset(Dataset):
    def __init__(self, dset: DatasetType, dir: Path, preprocessor: Preprocessor):
        self.dset = dset
        self.dir = dir
        self.preprocessor = preprocessor
        self.transforms = self._setup_transforms()
        self.data = self._load()

    def _load(self):
        rows = []
        for genre in self.preprocessor.genre_statistics.keys():
            subdir = self.dir / genre / 'train' if self.dset == DatasetType.TRAIN else self.dir / genre / 'test'
            pngs = list(subdir.glob('*.png'))
            for png_file in pngs:
                rows.append((genre, png_file))

        return pd.DataFrame(rows, columns=['genre', 'filename'])

    def _setup_transforms(self):
        transforms_dict = dict()
        for genre, tsfm in self.preprocessor.genre_statistics.items():
            transforms_dict[genre] = transforms.Compose([
                transforms.PILToTensor(),
                transforms.ConvertImageDtype(torch.float),
                transforms.Normalize(mean=tsfm['mean'], std=tsfm['std'])
            ])
        return transforms_dict

    def __len__(self):
        return len(self.data)

    def __getitem__(self, i):
        im_name = self.data.loc[i, 'filename']
        genre = self.data.loc[i, 'genre']

        with Image.open(im_name, 'r') as im:
            im = self.transforms[genre](im)

        # X and Y are the same.
        return im, im