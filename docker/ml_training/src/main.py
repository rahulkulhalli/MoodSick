from typing import List

from fastapi import FastAPI
from pydantic import BaseModel

from generate_spotify_params import get_spotify_params, load_model

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

@app.on_event("startup")
async def startup_event():
    load_model("./models/mcmc.pt")
