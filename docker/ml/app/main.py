from typing import List
from fastapi import Depends, FastAPI
from pydantic import BaseModel

app = FastAPI()

class SpotifyParams(BaseModel):
    query: str
    rating: str

@app.get("/get_spotify_params")
async def get_params_for_api_call(params : List[SpotifyParams]):
    return params
