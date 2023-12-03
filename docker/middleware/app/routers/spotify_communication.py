import os
from fastapi import HTTPException, APIRouter
from httpx import AsyncClient
import base64
from pydantic import BaseModel

router = APIRouter()


spotify_client_id = os.getenv("SPOTIFY_CLIENT_ID")
spotify_client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

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

# This function is used to get the token from spotify
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

# This function is used to get the spotify recommendations based on the parameters passed by the model
@router.post("/spotify-recommendations")
async def get_spotify_recommendations(request: ModelParams):
    token = await get_spotify_token()
    url = 'https://api.spotify.com/v1/recommendations'
    headers = {
        'Authorization': f"Bearer {token}"  # Replace with your actual token
    }
    seed_genres = "pop,rock,blues,jazz,classical"
    limit = 5
    # The foolowing params are cauing the api to fail: mode, key, time_signature
    params = {
        'seed_genres': seed_genres,
        'limit': limit,
        # 'min_danceability': request.min_danceability,
        # 'max_danceability': request.max_danceability,
        'target_danceability': request.target_danceability,
        # 'min_energy': request.min_energy,
        # 'max_energy': request.max_energy,
        'target_energy': request.target_energy,
        # 'min_loudness': request.min_loudness,
        # 'max_loudness': request.max_loudness,
        'target_loudness': request.target_loudness,
        # 'min_speechiness': request.min_speechiness,
        # 'max_speechiness': request.max_speechiness,
        'target_speechiness': request.target_speechiness,
        # 'min_acousticness': request.min_acousticness,
        # 'max_acousticness': request.max_acousticness,
        'target_acousticness': request.target_acousticness,
        # 'min_instrumentalness': request.min_instrumentalness,
        # 'max_instrumentalness': request.max_instrumentalness,
        'target_instrumentalness': request.target_instrumentalness,
        # 'min_liveness': request.min_liveness,
        # 'max_liveness': request.max_liveness,
        'target_liveness': request.target_liveness,
        # 'min_valence': request.min_valence,
        # 'max_valence': request.max_valence,
        'target_valence': request.target_valence,
        # 'min_tempo': request.min_tempo,
        # 'max_tempo': request.max_tempo,
        'target_tempo': request.target_tempo,
    }
    print(params)

    async with AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        responseJson = response.json()
        for each in range(len (responseJson["tracks"])):
            del responseJson["tracks"][each]["available_markets"]
            del responseJson["tracks"][each]["album"]
        
        
        return responseJson