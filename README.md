# MoodSick
A repository housing our implementation for the CIS 600 (Social Media and Data Mining) project

## Data procurement
To get started with MoodSick, you will first need to download two datasets from Kaggle, specifically, from [here](https://www.kaggle.com/datasets/andradaolteanu/gtzan-dataset-music-genre-classification?rvi=1) and [here](https://www.kaggle.com/datasets/mrmorj/dataset-of-songs-in-spotify).
Once you download these datasets, extract the files and arrange them in the `data/` directory  in the following way:

```
MoodSick
    | - data
        | - spotify
            | - genres_v2.csv
            | - playlists.csv
        | - gztan
            | - genres_original
            | - images_original
            | - features_3_sec.csv
            | - features_30_sec.csv
```

## Environment set-up
Now that your data is set-up, we recommend installing Anaconda and creating a virtual environment for separating the project
dependencies from the existing Python packages. First, please install your version of Anaconda from [here](https://www.anaconda.com/download). Once conda is installed,
set-up the environment and the dependencies using the `setup_env.sh` script located in the `scripts/conda/` directory.

First, navigate to `scripts/conda/ directory and run the following commands:
```language=bash
chmod +x setup_env.sh
./setup_env.sh
```
This script will create an environment called `smdm`, install all the project dependencies, and add the new environment to ipykernel.

## Exploration
If you'd like to do some data exploration, open the notebook located at the following location:
`data_exploration/initial_exploration.ipynb`

## Acknowledgements
We'd like to thank the authors of the [GZTAN](https://www.kaggle.com/andradaolteanu) and the [Spotify](https://www.kaggle.com/mrmorj) datasets.