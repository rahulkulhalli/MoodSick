import os
from fastapi import HTTPException, APIRouter, Request
from httpx import AsyncClient
import base64
from pydantic import BaseModel
import urllib.parse
from app import spotify_user_id, spotify_client_id, spotify_client_secret
from app.db_communcation.admin import save_admin_refresh_token, get_admin_refresh_token, get_admin_authorization_code, save_admin_authorization_code

router = APIRouter()

async def get_moodsick_spotify_token():
    admin_id = "656ede6aa993f0273facf85d"
    admin_authorization_code = await get_admin_authorization_code(admin_id)
    admin_refresh_token = await get_admin_refresh_token(admin_id)
    if admin_authorization_code is None:
        raise HTTPException(status_code=401, detail="Moodsick not authorized")
    
    url = "https://accounts.spotify.com/api/token"
    
    token_headers = {
        "Authorization": f"Basic {base64.b64encode(f'{spotify_client_id}:{spotify_client_secret}'.encode()).decode()}"
    }

    token_data = {
        "grant_type": "authorization_code",
        "code": admin_authorization_code,
        "redirect_uri": "http://localhost:8080/admin/callback"
    }

    async with AsyncClient() as client:
        token_response = await client.post(url, data=token_data, headers=token_headers)
        if admin_refresh_token is None or token_response.status_code == 200:
            access_token = token_response.json().get("access_token")
            new_user_refresh_token = token_response.json().get("refresh_token")
            print(f"Refresh token: {new_user_refresh_token}")
            await save_admin_refresh_token(admin_id, new_user_refresh_token)
            return access_token

        if admin_refresh_token:
            new_access_token = await get_moodsick_refresh_token(admin_refresh_token)
            return new_access_token

        raise HTTPException(status_code=400, detail="Authorization required")

async def get_moodsick_refresh_token(refreshToken):
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
    

@router.get("/admin-auth-url")
def create_auth_url():
    base_url = "https://accounts.spotify.com/authorize"
    params = {
        "client_id": spotify_client_id,
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
    admin_id = "656ede6aa993f0273facf85d"
    await save_admin_authorization_code(admin_id, code)
    # Now you can use this code to get the access token
    return {"message": "Moodsick Authorization Successfull"}