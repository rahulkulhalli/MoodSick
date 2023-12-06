from pydantic import BaseModel, EmailStr
from app.models.spotify_communication import SongFeature

class UserRegisterData(BaseModel):
    email: EmailStr
    password: str
    age: int
    authorization_code: str = None
    refresh_token: str = None
    user_playlist_uri: str = None
    user_audio_preferance: dict = None

class UserPlaylistData(BaseModel):
    uri : str
    name : str
    total_songs : str
    track_uri : list

class UserAudioPreferance(BaseModel):
    avg_acousticness: float
    avg_danceability: float
    avg_energy: float
    avg_instrumentalness: float
    avg_key: int
    avg_liveness: float
    avg_loudness:  float
    avg_mode: int
    avg_speechiness: float
    avg_tempo: float
    avg_time_signature: int
    avg_valence: float

class UserAudioPreferanceData(BaseModel):
    user_id: str
    songs_data: list[SongFeature]

