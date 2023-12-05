from pydantic import BaseModel, EmailStr

class UserRegisterData(BaseModel):
    email: EmailStr
    password: str
    age: int
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

