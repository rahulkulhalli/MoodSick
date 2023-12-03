import os

import requests
from fastapi import HTTPException, APIRouter, Request
from httpx import AsyncClient
import base64
from pydantic import BaseModel
from enum import Enum
import json
import urllib.parse


router = APIRouter()

# spotify_user_id = os.getenv("SPOTIFY_USER_ID")
spotify_client_id = os.getenv("SPOTIFY_CLIENT_ID")
spotify_client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
# authorization_code = os.getenv("SPOTIFY_ACCESS_TOKEN")
redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI")
scopes = os.getenv("SPOTIFY_SCOPES")


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


refreshToken = None
authorization_code = None
# This function is used to get the token from spotify
async def get_spotify_token():
    global authorization_code
    global refreshToken
    url = "https://accounts.spotify.com/api/token"
    
    token_headers = {
        "Authorization": f"Basic {base64.b64encode(f'{spotify_client_id}:{spotify_client_secret}'.encode()).decode()}"
    }

    token_data = {
        "grant_type": "authorization_code",
        "code": authorization_code,
        "redirect_uri": redirect_uri
    }

    async with AsyncClient() as client:
        token_response = await client.post(url, data=token_data, headers=token_headers)
        if refreshToken is None and token_response.status_code == 200:
            refreshToken = token_response.json().get("refresh_token")
        
        print(refreshToken)

        if token_response.status_code != 200:
            token = await get_refresh_token(refreshToken)
            return token
        
        token = token_response.json().get("access_token")
        return token

async def get_refresh_token(refreshToken):
    url = "https://accounts.spotify.com/api/token"
    token_data = {
        "grant_type": "refresh_token",
        "refresh_token": refreshToken
    }
    token_headers = {
        "Authorization": f"Basic {base64.b64encode(f'{spotify_client_id}:{spotify_client_secret}'.encode()).decode()}"
    }
    async with AsyncClient() as client:
        token_response = await client.post(url, data=token_data, headers=token_headers)
        if token_response.status_code != 200:
            raise HTTPException(status_code=token_response.status_code, detail="Failed to refresh token")
        new_access_token = token_response.json().get("access_token")
        return new_access_token
    
@router.get("/read-spotify-profile")
async def read_spotify_profile():
    token = await get_spotify_token()
    url = 'https://api.spotify.com/v1/me'
    headers = {'Authorization': f"Bearer {token}"}

    async with AsyncClient() as client:
        response = await client.get(url, headers=headers)
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        return response.json().get("id")

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
        track_uris = []
        for each in range(len (responseJson["tracks"])):
            del responseJson["tracks"][each]["available_markets"]
            del responseJson["tracks"][each]["album"]
            track_uris.append(responseJson["tracks"][each]["uri"])        

        # print(track_uris)
        personal_playlist_uri = await create_playlist(user_age=19, token=token)
        #keep the last part from the uri
        personal_playlist_link = personal_playlist_uri.split(":")[-1]
        await save_to_playlist(token, track_uris, personal_playlist_link)
        return responseJson
    
async def save_to_playlist(token, track_uris, personal_playlist_link):
    # Get current user age from database
    # age = 19

    # # Get playlist id based on age
    # if age < 20:
    #     playlist_id = SpotifyPlaylist.AGE_10_20.value
    # elif age < 30:
    #     playlist_id = SpotifyPlaylist.AGE_20_30.value
    # elif age < 40:
    #     playlist_id = SpotifyPlaylist.AGE_30_40.value
    # elif age < 50:
    #     playlist_id = SpotifyPlaylist.AGE_40_50.value
    # else:
    #     playlist_id = SpotifyPlaylist.AGE_50_60.value
    
    # endpoint_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    endpoint_url_personal = f"https://api.spotify.com/v1/playlists/{personal_playlist_link}/tracks"

    headers = {
        'Authorization': f"Bearer {token}",
        'Content-Type': 'application/json'
    }

    data = {
        "uris": track_uris
    }

    async with AsyncClient() as client:
        # response = await client.post(endpoint_url, headers=headers, json=data)
        response_personal = await client.post(endpoint_url_personal, headers=headers, json=data)
        if response_personal.status_code != 201:
            raise HTTPException(status_code=response_personal.status_code, detail=response_personal.text)
        
        return response_personal.json()

@router.get("/create-playlist")
async def create_playlist(user_age: int, token: str):
    user_id = await read_spotify_profile()
    print(user_id)
    endpoint_url = f"https://api.spotify.com/v1/users/{user_id}/playlists"
    if user_age < 20:
        name = "MoodSick Playlist for Age Group 10-20"
        description = "Playlist for Age Group 10-20 generated by MoodSick"
    elif user_age < 30:
        name = "MoodSick Playlist for Age Group 20-30"
        description = "Playlist for Age Group 20-30 generated by MoodSick"
    elif user_age < 40:
        name = "MoodSick Playlist for Age Group 30-40"
        description = "Playlist for Age Group 30-40 generated by MoodSick"
    elif user_age < 50:
        name = "MoodSick Playlist for Age Group 40-50"
        description = "Playlist for Age Group 40-50 generated by MoodSick"
    else:
        name = "MoodSick Playlist for Age Group 50-60"
        description = "Playlist for Age Group 50-60 generated by MoodSick"
    
    request_body = json.dumps({
        "name": name,
        "description": description,
        "public": False # let's keep it between us - for now
    })
    response = requests.post(url = endpoint_url, data = request_body, headers={"Content-Type":"application/json", "Authorization": f"Bearer {token}"})
    print(response.json().get("uri"))
    return response.json().get("uri")

@router.get("/auth-url")
def create_auth_url():
    base_url = "https://accounts.spotify.com/authorize"
    params = {
        "client_id": spotify_client_id,
        "response_type": "code",
        "redirect_uri": 'http://localhost:8080/spotify/callback',
        "scope": "playlist-modify-public playlist-modify-private playlist-read-private playlist-read-collaborative user-read-private"
    }
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    return url

    
@router.get("/callback")
async def callback(request: Request):
    code = request.query_params.get('code')
    print(request.query_params)
    # Now you can use this code to get the access token
    global authorization_code
    authorization_code = code
    return {"message": "success"}
    