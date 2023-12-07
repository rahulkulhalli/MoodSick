import os
from typing import List
from app.db_communcation.users import create_user, login_user, save_user_mood_maping, get_genres_from_mood
from app.models.users import UserData, UserPreferences, SpotifyParams
from app.models.spotify_communication import SpotifyRecommendationInput
from fastapi import HTTPException, APIRouter, Request
from fastapi.responses import FileResponse
from httpx import AsyncClient
import base64
from pydantic import BaseModel
import urllib.parse
import pymongo
from app import spotify_user_id, spotify_client_id, spotify_client_secret
from app.db_communcation.users import save_user_refresh_token, get_user_refresh_token, get_user_authorization_code, save_user_authorization_code, get_songs_for_user, get_user_data
from app.routers.spotify_communication import get_spotify_and_user_preferences
# import pymongo
import requests
import json

router = APIRouter()

# spotify_client_id = os.getenv("SPOTIFY_CLIENT_ID")
# spotify_client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

# @router.get("/all", tags=["users"])
# async def read_users():
#     return [{"username": "Test-1"}, {"username": "Test-2"}]

@router.post("/login", tags=["users"])
async def login(creds: UserData):
    result = await login_user(creds)
    return result

@router.post("/register", tags=["users"])
async def register(user_data: UserData):
    result = await create_user(user_data)
    return {"Status": result}

@router.post("/save-user-mood-genres", tags=["Users"])
async def save_user_mood_genres(user_moods: UserPreferences):
    result = await save_user_mood_maping(user_moods)
    return {"Status": result}


# {moods: "happy"}
@router.get("/get-songs", tags=["Users"])
async def get(response: Request):
    response = await response.json()
    mood = response.get("mood")
    user_id = response.get("user_id")
    request_data_dict = {
        "user_id": user_id,
        "mood": mood
    }
    response_data = await get_songs_for_user(request_data_dict)
    print(list(response_data))
    response_data = [(f"http://10.9.0.6/static/{song.get('songs').get('filename')}") for song in response_data]
    print(response_data)

    return response_data


@router.post("/get-recommendations-for-user", tags=["Users"])
async def get_recommendations_for_user(request: Request):
    request = await request.json()
    ratings = request.get("ratings")
    mood = request.get("mood")
    input = []
    for each in ratings:
        input.append({
            'query': each["query"],
            'rating': each["rating"]
        })
    url = "http://10.9.0.8/get-recommendation-params"
    print("input", input)
    response = requests.post(url, data=json.dumps(input))
    response = response.json()
    user_id = request.get("user_id", "656f7c14d74f3263c8d44cd0")
    genres = await get_genres_from_mood(mood, user_id)
    response = response["message"]["params"]
    response["genre"] = ",".join([i for i in genres])
    response["user_id"] = user_id
    response["market"] = "US"
    response["sort_by_popularity"] = False
    print(response, type(response))
    model_params = SpotifyRecommendationInput.parse_obj(response)
    data = await get_spotify_and_user_preferences(model_params)
    return {"data": data}

# This API is to get and generate data for user dashboard
@router.post("/user-dashboard")
async def get_user_dashboard(request: Request):
    request = await request.json()
    # Get user ID from request
    user_id = request.get("user_id")
    # Write code in db_communication to dump of Spotify recommendations
    # model_recommendations_for_user = await get_model_reccomendations_for_user(user_id)

    # Get user data from database
    user_data = await get_user_data(user_id)
    # Convert userData into UserData object
    user_data = UserData.parse_obj(user_data)
    user_data = user_data.dict()

    # Write code in db_communication/users.py to get dump of ratings that the user has given
    # user_rating_dumps = await get_user_rating_dumps(user_id)

    # Write code in db_communication/users.py to get dump of model-generated params for the user
    # dump_model_params = await get_dump_model_params(user_id)

    return {"user_data": user_data}


# This function is used to get the token from spotify
async def get_user_spotify_token(user_id):
    user_authorization_code = await get_user_authorization_code(user_id)
    print(user_authorization_code)
    user_refresh_token = await get_user_refresh_token(user_id)
    # if user_authorization_code is None:
    #     raise HTTPException(status_code=401, detail="User not authorized")
    
    url = "https://accounts.spotify.com/api/token"

    token_headers = {
        "Authorization": f"Basic {base64.b64encode(f'{spotify_client_id}:{spotify_client_secret}'.encode()).decode()}"
    }

    token_data = {
        "grant_type": "authorization_code",
        "code": user_authorization_code,
        "redirect_uri": "http://localhost:8080/user/callback"
    }

    async with AsyncClient() as client:
        token_response = await client.post(url, data=token_data, headers=token_headers)
        print(token_response.json())
        if user_refresh_token is None or token_response.status_code == 200:
            access_token = token_response.json().get("access_token")
            new_user_refresh_token = token_response.json().get("refresh_token")
            print(f"Refresh token: {new_user_refresh_token}")
            await save_user_refresh_token(user_id, new_user_refresh_token)
            return access_token
        
        if user_refresh_token:
            new_access_token = await get_refresh_token(user_refresh_token)
            return new_access_token

        raise HTTPException(status_code=400, detail="Authorization required")
    

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
    

@router.get("/user-auth-url")
async def create_auth_url(request: Request):
    request = await request.json()
    print(request)
    base_url = "https://accounts.spotify.com/authorize"
    params = {
        "client_id": spotify_client_id,
        "response_type": "code",
        "redirect_uri": "http://localhost:8080/user/callback",
        "scope": "playlist-modify-public playlist-modify-private playlist-read-private playlist-read-collaborative user-read-private",
        "state": request.get("user_id")
    }
    get_token_url = f"{base_url}?{urllib.parse.urlencode(params)}"
    return get_token_url

@router.get("/callback")
async def callback(request: Request):
    code = request.query_params.get('code')
    print(request.query_params)
    user_id = request.query_params.get('state')
    # Now you can use this code to get the access token
    await save_user_authorization_code(user_id, code)
    return {"message": "User Authorization Successful"}

# async def save_user_playlist(user_id, user_playlist_uri):
#     collection = db_name["your_collection_name"]

#     # Save the user playlist URI to the database where user_id is the key
#     document = {"user_id": user_id, "user_playlist_uri": user_playlist_uri}
#     collection.update_one({"user_id": user_id}, {"$set": document}, upsert=True)


# async def get_user_playlist(user_id):
#     collection = db_name["your_collection_name"]
#     document = collection.find_one({"user_id": user_id})
#     return document["user_playlist_uri"]
