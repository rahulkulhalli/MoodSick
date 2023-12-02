from typing import List, Union
from generate_spotify_params import get_spotify_params, load_model
from fastapi import Depends, FastAPI
from pydantic import BaseModel

app = FastAPI()


class SpotifyParams(BaseModel):
    query: str
    rating: str

@app.get("/")
async def root():
    return {"message": "Hello MoodSicks- ML Container!"}

@app.post("/get-recommendation-params")
async def spotify(request: List[SpotifyParams]):
    input = []
    for each in request:
        input.append({
            'query': each.query,
            'rating': each.rating
        })
    res= get_spotify_params(input)
    return {"message": res}

