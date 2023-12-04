import os
import requests
from fastapi import HTTPException, APIRouter, Request
from httpx import AsyncClient
from .import admin
import base64
from pydantic import BaseModel
from enum import Enum
import json
import urllib.parse


router = APIRouter()

spotify_user_id = os.getenv("SPOTIFY_USER_ID")
spotify_client_id = os.getenv("SPOTIFY_CLIENT_ID")
spotify_client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
moodsick_authorization_code = os.getenv("SPOTIFY_ACCESS_TOKEN")
user_redirect_uri = os.getenv("SPOTIFY_USER_REDIRECT_URI")
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


user_refreshToken = None
user_authorization_code = None
# This function is used to get the token from spotify
async def get_user_spotify_token():
    global user_authorization_code
    global user_refreshToken
    url = "https://accounts.spotify.com/api/token"
    
    token_headers = {
        "Authorization": f"Basic {base64.b64encode(f'{spotify_client_id}:{spotify_client_secret}'.encode()).decode()}"
    }

    token_data = {
        "grant_type": "authorization_code",
        "code": user_authorization_code,
        "redirect_uri": user_redirect_uri
    }

    async with AsyncClient() as client:
        token_response = await client.post(url, data=token_data, headers=token_headers)
        if user_refreshToken is None and token_response.status_code == 200:
            user_refreshToken = token_response.json().get("refresh_token")
        
        print("User Refresh:", user_refreshToken)

        if token_response.status_code != 200:
            token = await get_user_refresh_token(user_refreshToken)
            return token
        
        token = token_response.json().get("access_token")
        return token

async def get_user_refresh_token(refreshToken):
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


async def read_spotify_profile_user(user_token: str):
    url = 'https://api.spotify.com/v1/me'
    headers = {'Authorization': f"Bearer {user_token}"}

    async with AsyncClient() as client:
        response = await client.get(url, headers=headers)
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        return response.json().get("id"), response.json().get("display_name")

# This function is used to get the spotify recommendations based on the parameters passed by the model
@router.post("/spotify-recommendations")
async def get_spotify_recommendations(request: ModelParams):
    user_token = await get_user_spotify_token()
    moodsick_token = await admin.get_moodsick_spotify_token()
    url = 'https://api.spotify.com/v1/recommendations'
    headers = {
        'Authorization': f"Bearer {user_token}"  # Replace with your actual token
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

        # Check if the user has a playlist
        # If the user has a playlist, save the tracks to the playlist
        # If the user does not have a playlist, create a playlist and save the tracks to the playlist
        # user_playlist_uri = Get from the database
        # Create a playlist for the user
        #user_playlist_uri = await create_playlist(user_token=user_token)
        #user_playlist_uri = user_playlist_uri.split(":")[-1]
        user_playlist_uri = "2vsbJJ1WUEp0D9Nwa4wdzH"
        # Save the tracks to the user playlist
        await save_to_user_playlist(user_token, track_uris, user_playlist_uri)
        # Save the tracks to the moodsick playlist according to user's age
        user_age = 23
        await save_to_moodsick_playlist(user_age, moodsick_token, track_uris)
        # return response.json()
        return responseJson
    
async def save_to_user_playlist(user_token, track_uris, user_playlist_link):
    endpoint_url_user = f"https://api.spotify.com/v1/playlists/{user_playlist_link}/tracks"

    headers = {
        'Authorization': f"Bearer {user_token}",
        'Content-Type': 'application/json'
    }

    data = {
        "uris": track_uris,
        "position": 0
    }

    async with AsyncClient() as client:
        # response = await client.post(endpoint_url, headers=headers, json=data)
        response_personal = await client.post(endpoint_url_user, headers=headers, json=data)
        if response_personal.status_code != 201:
            raise HTTPException(status_code=response_personal.status_code, detail=response_personal.text)
        
        return response_personal.json()
    
async def save_to_moodsick_playlist(age, moodsick_token, track_uris):
    # Get playlist id based on age
    if age < 20:
        playlist_id = SpotifyPlaylist.AGE_10_20.value
    elif age < 30:
        playlist_id = SpotifyPlaylist.AGE_20_30.value
    elif age < 40:
        playlist_id = SpotifyPlaylist.AGE_30_40.value
    elif age < 50:
        playlist_id = SpotifyPlaylist.AGE_40_50.value
    else:
        playlist_id = SpotifyPlaylist.AGE_50_60.value
    
    endpoint_url_mooksick = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"

    headers = {
        'Authorization': f"Bearer {moodsick_token}",
        'Content-Type': 'application/json'
    }

    data = {
        "uris": track_uris
    }

    async with AsyncClient() as client:
        response_moodsick = await client.post(endpoint_url_mooksick, headers=headers, json=data)
        if response_moodsick.status_code != 201:
            raise HTTPException(status_code=response_moodsick.status_code, detail=response_moodsick.text)
        
        return response_moodsick.json()
    


@router.get("/create-playlist")
async def create_playlist(user_token: str):
    spotify_user_id, spotify_user_name = await read_spotify_profile_user(user_token)
    print(spotify_user_id, spotify_user_name)
    endpoint_url_user = f"https://api.spotify.com/v1/users/{spotify_user_id}/playlists"
    user_playlist_name = "MoodSick Playlist for " + spotify_user_name + "!"
    user_description = "Playlist generated by MoodSick"

    request_body = json.dumps({
        "name": user_playlist_name,
        "description": user_description,
        "public": False # let's keep it between us - for now
    })
    response = requests.post(url = endpoint_url_user, data = request_body, headers={"Content-Type":"application/json", "Authorization": f"Bearer {user_token}"})
    print(response.json())
    return response.json().get("uri")

@router.get("/user-auth-url")
def create_auth_url():
    base_url = "https://accounts.spotify.com/authorize"
    params = {
        "client_id": spotify_client_id,
        "response_type": "code",
        "redirect_uri": user_redirect_uri,
        "scope": "playlist-modify-public playlist-modify-private playlist-read-private playlist-read-collaborative user-read-private"
    }
    get_token_url = f"{base_url}?{urllib.parse.urlencode(params)}"
    return get_token_url

@router.get("/callback")
async def callback(request: Request):
    code = request.query_params.get('code')
    print(request.query_params)
    # Now you can use this code to get the access token
    global user_authorization_code
    user_authorization_code = code
    return {"message": "User Authorization Successful"}
    