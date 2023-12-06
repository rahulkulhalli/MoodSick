import os
from app.db_communcation.users import create_user, login_user, save_user_mood_maping
from app.models.users import UserData, UserPreferences
from fastapi import HTTPException, APIRouter, Request
from fastapi.responses import FileResponse
from httpx import AsyncClient
import base64
from pydantic import BaseModel
import urllib.parse
import pymongo
from app import spotify_user_id, spotify_client_id, spotify_client_secret
from app.db_communcation.users import save_user_refresh_token, get_user_refresh_token, get_user_authorization_code, save_user_authorization_code
# import pymongo

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

@router.post("/get-songs", tags=["Users"])
async def get():
    some_file_path1 = "/code/app/static_songs/blues.00004.wav"
    some_file_path2 = "/code/app/static_songs/blues.00004.wav"
    some_file_path3 = "/code/app/static_songs/blues.00004.wav"
    some_file_path4 = "/code/app/static_songs/blues.00004.wav"
    some_file_path5 = "/code/app/static_songs/blues.00004.wav"
    response_data = [
        FileResponse(some_file_path1),
        FileResponse(some_file_path2),
        FileResponse(some_file_path3),
        FileResponse(some_file_path4),
        FileResponse(some_file_path5),
    ]

    return  response_data



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
