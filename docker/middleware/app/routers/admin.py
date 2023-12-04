import os
from fastapi import HTTPException, APIRouter, Request
from httpx import AsyncClient
import base64
from pydantic import BaseModel
import urllib.parse

router = APIRouter()

moodsick_id = os.getenv("SPOTIFY_USER_ID")
moodsick_client_id = os.getenv("SPOTIFY_CLIENT_ID")
moodsick_client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
admin_redirect_uri = os.getenv("SPOTIFY_ADMIN_REDIRECT_URI")
scopes = os.getenv("SPOTIFY_SCOPES")

moodsick_refreshToken = None
moodsick_authorization_code = None
async def get_moodsick_spotify_token():
    global moodsick_authorization_code
    global moodsick_refreshToken
    url = "https://accounts.spotify.com/api/token"
    
    token_headers = {
        "Authorization": f"Basic {base64.b64encode(f'{moodsick_client_id}:{moodsick_client_secret}'.encode()).decode()}"
    }

    token_data = {
        "grant_type": "authorization_code",
        "code": moodsick_authorization_code,
        "redirect_uri": "http://localhost:8080/admin/callback"
    }

    async with AsyncClient() as client:
        token_response = await client.post(url, data=token_data, headers=token_headers)
        if moodsick_refreshToken is None and token_response.status_code == 200:
            moodsick_refreshToken = token_response.json().get("refresh_token")
        
        print("Response:", token_response.json())
        print("Admin Token:", moodsick_authorization_code)
        print("Admin Refresh:",moodsick_refreshToken)

        if token_response.status_code != 200:
            token = await get_moodsick_refresh_token(moodsick_refreshToken)
            return token
        
        token = token_response.json().get("access_token")
        return token

async def get_moodsick_refresh_token(refreshToken):
    url = "https://accounts.spotify.com/api/token"
    token_data = {
        "grant_type": "refresh_token",
        "refresh_token": refreshToken
    }
    token_headers = {
        "Authorization": f"Basic {base64.b64encode(f'{moodsick_client_id}:{moodsick_client_secret}'.encode()).decode()}"
    }
    async with AsyncClient() as client:
        token_response = await client.post(url, data=token_data, headers=token_headers)
        if token_response.status_code != 200:
            raise HTTPException(status_code=token_response.status_code, detail="Failed to refresh token")
        new_access_token = token_response.json().get("access_token")
        return new_access_token
    

@router.get("/admin-auth-url")
def create_auth_url():
    base_url = "https://accounts.spotify.com/authorize"
    params = {
        "client_id": moodsick_client_id,
        "response_type": "code",
        "redirect_uri": 'http://localhost:8080/admin/callback',
        "scope": "playlist-modify-public playlist-modify-private playlist-read-private playlist-read-collaborative user-read-private"
    }
    get_token_url = f"{base_url}?{urllib.parse.urlencode(params)}"
    return get_token_url

@router.get("/callback")
async def callback(request: Request):
    code = request.query_params.get('code')
    print(request.query_params)
    global moodsick_authorization_code
    moodsick_authorization_code = code
    # Now you can use this code to get the access token
    return {"message": "Moodsick Authorization Successfull"}