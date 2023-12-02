import os
from typing import List
from fastapi import Depends, FastAPI, HTTPException
from httpx import AsyncClient
from .routers import users
import base64
from dotenv import load_dotenv
from pydantic import BaseModel
import requests


spotify_client_id = os.getenv("SPOTIFY_CLIENT_ID")
spotify_client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

class ModelParams(BaseModel):
    min_danceability: float
    max_danceability: float
    target_danceability: float
    min_energy: float
    max_energy: float
    target_energy: float
    min_key: float
    max_key: float
    target_key: float
    min_loudness: float
    max_loudness: float
    target_loudness: float
    min_mode: float
    max_mode: float
    target_mode: float
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
    min_tempo: float
    max_tempo: float
    target_tempo: float
    min_time_signature: float
    max_time_signature: float
    target_time_signature: float



app = FastAPI()

app.include_router(users.router,
                   prefix="/user")

async def get_spotify_token():
    url = "https://accounts.spotify.com/api/token"
    token_data = {
        "grant_type": "client_credentials"
    }
    token_headers = {
        "Authorization": f"Basic {base64.b64encode(f'{spotify_client_id}:{spotify_client_secret}'.encode()).decode()}"
    }
    async with AsyncClient() as client:
        token_response = await client.post(url, data=token_data, headers=token_headers)
        print(token_response)
        if token_response.status_code != 200:
            raise HTTPException(status_code=token_response.status_code, detail="Failed to obtain token")
        token = token_response.json().get("access_token")
        print(token_response.json())
        return token

@app.get("/")
async def root():
    return {"message": "Hello MoodSick!"}

@app.post("/spotify-recommendations")
async def get_spotify_recommendations(request: ModelParams):
    token = await get_spotify_token()
    url = 'https://api.spotify.com/v1/recommendations'
    headers = {
        'Authorization': f"Bearer {token}"  # Replace with your actual token
    }
    seed_genres = "pop,rock,blues"
    limit = 10
    # The foolowing params are cauing the api to fail: mode, key, time_signature
    params = {
        'seed_genres': seed_genres,
        'limit': limit,
        'min_danceability': request.min_danceability * 0.9,
        'max_danceability': request.max_danceability * 1.1,
        'target_danceability': request.target_danceability,
        'min_energy': request.min_energy * 0.9,
        'max_energy': request.max_energy * 1.1,
        'target_energy': request.target_energy,
        'min_loudness': request.min_loudness * 0.9,
        'max_loudness': request.max_loudness  * 1.1,
        'target_loudness': request.target_loudness,
        'min_speechiness': request.min_speechiness * 0.9,
        'max_speechiness': request.max_speechiness * 1.1,
        'target_speechiness': request.target_speechiness,
        # 'min_acousticness': request.min_acousticness * 0.9,
        # 'max_acousticness': request.max_acousticness * 1.1,
        'target_acousticness': request.target_acousticness,
        # 'min_instrumentalness': request.min_instrumentalness * 0.9,
        # 'max_instrumentalness': request.max_instrumentalness * 1.1,
        'target_instrumentalness': request.target_instrumentalness,
        # 'min_liveness': request.min_liveness * 0.9,
        # 'max_liveness': request.max_liveness  * 1.1,
        'target_liveness': request.target_liveness,
        # 'min_valence': request.min_valence * 0.9,
        # 'max_valence': request.max_valence * 1.1,
        'target_valence': request.target_valence,
        # 'min_tempo': request.min_tempo * 0.9,
        # 'max_tempo': request.max_tempo * 1.1,
        'target_tempo': request.target_tempo,
    }
    print(params)

    async with AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        return response.json()

    # response = requests.get(url, headers=headers, params=params)

    # if response.status_code == 200:
    #     return response.json()  # This will print the response in JSON format
    # else:
    #     print(f"Failed to fetch data: {response.status_code}")