from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from app.models.spotify_communication import SongFeature

class UserData(BaseModel):
    email: EmailStr
    password: str
    age: Optional[int] 
    name: Optional[str]
    login_history: Optional[list[str]]
    authorization_code: str = None
    refresh_token: str = None
    user_playlist_uri: str = None
    user_audio_preferance: dict = None

class MoodMapping(BaseModel):
    Very_Happy: List[str] = Field(..., alias='Very Happy')
    Happy: List[str] = []
    Neutral: List[str] = []
    Sad: List[str] = []
    Very_Sad: List[str] = Field(..., alias='Very Sad')

class UserPreferences(BaseModel):
    email: EmailStr
    mapping: MoodMapping
    class Config:
        allow_population_by_field_name = True


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

