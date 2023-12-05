from pydantic import BaseModel
from enum import Enum

class SpotifyPlaylist(Enum):
    AGE_10_20 = "2fVLPnOhxdWUJgIQNL3bTw"
    AGE_20_30 = "3cdJfW7OhCw6vl8CUP0Dsj"
    AGE_30_40 = "3VufVRa2CfR04x50ePLFER"
    AGE_40_50 = "2lyDBxRyHXRH5t5gHdTXXj"
    AGE_50_60 = "2Px1aIIcmJhWdYsiQhZePz"

class ModelParams(BaseModel):
    min_danceability: float
    max_danceability: float
    target_danceability: float
    min_energy: float
    max_energy: float
    target_energy: float
    min_key: int
    max_key: int
    target_key: int
    min_loudness: float
    max_loudness: float
    target_loudness: float
    min_mode: int
    max_mode: int
    target_mode: int
    min_speechiness: float
    max_speechiness: float
    target_speechiness: float
    min_acousticness: float
    max_acousticness: float
    target_acousticness: float
    min_instrumentalness: float
    max_instrumentalness: float
    target_instrumentalness: float
    min_liveness: float
    max_liveness: float
    target_liveness: float
    min_valence: float
    max_valence: float
    target_valence: float
    min_tempo: int
    max_tempo: int
    target_tempo: int
    min_time_signature: int
    max_time_signature: int
    target_time_signature: int
    genre: str
    sort_by_popularity: bool

class SongFeature(BaseModel):
    uri: str
    acousticness: float
    danceability: float
    duration_ms: float
    energy: float
    instrumentalness: float
    key: int
    liveness: float
    loudness:  float
    mode: int
    speechiness: float
    tempo: float
    time_signature: int
    valence: float