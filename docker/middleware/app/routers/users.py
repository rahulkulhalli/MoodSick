import os
from typing import List
from app.db_communcation.users import create_user, login_user, save_user_mood_maping, get_genres_from_mood, save_model_response_data, save_user_ratings

import pandas as pd
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
from app.db_communcation.users import (save_user_refresh_token, get_user_refresh_token,
                                       get_user_authorization_code, save_user_authorization_code,
                                       get_songs_for_user, get_user_data, get_user_flow_history)
from app.routers.spotify_communication import get_spotify_and_user_preferences
# import pymongo
import requests
import re
import json
from bson import json_util
from traceback import format_exc


pattern = re.compile(r'([a-z]+)\d+')
router = APIRouter()

# spotify_client_id = os.getenv("SPOTIFY_CLIENT_ID")
# spotify_client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

# @router.get("/all", tags=["users"])
# async def read_users():
#     return [{"username": "Test-1"}, {"username": "Test-2"}]

@router.post("/login", tags=["users"])
async def login(creds: UserData):
    result = await login_user(creds)
    # print(result)
    response = json.loads(json_util.dumps(result))
    return response

@router.post("/register", tags=["users"])
async def register(user_data: UserData):
    result = await create_user(user_data)
    return {"Status": result}

@router.post("/save-user-mood-genres", tags=["Users"])
async def save_user_mood_genres(user_moods: UserPreferences):
    result = await save_user_mood_maping(user_moods)
    return {"Status": result}


# {moods: "happy"}
@router.post("/get-songs", tags=["Users"])
async def get(response: Request):
    response = await response.json()
    mood = response.get("mood")
    user_id = response.get("user_id")
    request_data_dict = {
        "user_id": user_id,
        "mood": mood
    }
    response_data = await get_songs_for_user(request_data_dict)
    # print(list(response_data))
    response_data = [(f"http://10.9.0.6/static/{song.get('songs').get('filename')}") for song in response_data]
    # print(response_data)

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
    # print("input", input)
    inserted_mood_flow_id = await save_user_ratings(input)
    print("inserted_mood_flow_id", inserted_mood_flow_id)
    response = requests.post(url, data=json.dumps(input))
    response = response.json()
    user_id = request.get("user_id", "656f7c14d74f3263c8d44cd0")
    await save_model_response_data(response, user_id, mood, inserted_mood_flow_id)
    genres = await get_genres_from_mood(mood, user_id)
    response = response["message"]["params"]
    response["genre"] = ",".join([i for i in genres])
    response["user_id"] = user_id
    response["market"] = "US"
    response["sort_by_popularity"] = False
    # print(response, type(response))
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
    # print(user_authorization_code)
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
        # print(token_response.json())
        if user_refresh_token is None or token_response.status_code == 200:
            access_token = token_response.json().get("access_token")
            new_user_refresh_token = token_response.json().get("refresh_token")
            # print(f"Refresh token: {new_user_refresh_token}")
            await save_user_refresh_token(user_id, new_user_refresh_token)
            return access_token
        
        if user_refresh_token:
            # print("user_refresh_token", user_refresh_token)
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
    

@router.post("/user-auth-url")
async def create_auth_url(request: Request):
    request = await request.json()
    # print(request)
    base_url = "https://accounts.spotify.com/authorize"
    params = {
        "client_id": spotify_client_id,
        "response_type": "code",
        "redirect_uri": "http://localhost:3000/SpotifyCallback",
        "scope": "playlist-modify-public playlist-modify-private playlist-read-private playlist-read-collaborative user-read-private",
        "state": request.get("user_id")
    }
    get_token_url = f"{base_url}?{urllib.parse.urlencode(params)}"
    return {"url": get_token_url}

@router.post("/save-user-auth-code")
async def callback(request: Request):
    request = await request.json()
    user_id = request.get("user_id")
    code = request.get("code")
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


@router.post('/viz')
async def generate_viz(request: Request):
    """

    A  method to return visualization data to the front-end.
    The following data will be called from this method:
        - user login history
        - user mood mapping dictionary
        - user rated song history
        - model generated params for rated songs
        - spotify hits for rated songs
        - average params for user

    :param request: the incoming request JSON body.
    :return: A dictionary of graphing data, each key being the title of the graph.
    """

    # Global dictionary to hold visualizations.
    viz_dict = dict()

    try:
        # Get the JSON body.
        request = await request.json()

        # Retrieve the user_id.
        user_id = request.get('user_id')

        # Retrieve user data from the db.
        user_data = await get_user_data(user_id)
        flow_history = await get_user_flow_history(user_id)

        # Login history visualizations.
        if 'login_history' in user_data.keys():

            dow_mapping = {
                0: "Monday",
                1: "Tuesday",
                2: "Wednesday",
                3: "Thursday",
                4: "Friday",
                5: "Saturday",
                6: "Sunday"
            }

            login_times = user_data['login_history']

            if isinstance(login_times, list) and len(login_times) > 0:

                viz_dict['login_viz'] = dict()

                # Convert the list into a series and return the
                login_times = pd.DataFrame(
                    login_times, columns=['timestamp']
                ).sort_values(by=['timestamp'], ascending=True, inplace=False)

                # Extract the date.
                login_times['date'] = login_times.apply(lambda x: x.timestamp.date(), axis=1)
                # Extract the day of week and map it to a string name.
                login_times['dow'] = login_times.apply(lambda x: dow_mapping[x.date.weekday()], axis=1)
                # Get the hour of day.
                login_times['hod'] = login_times.apply(lambda x: x.timestamp.hour, axis=1)

                viz_dict['login_viz']['date_freq'] = login_times['date'].value_counts().to_dict()
                viz_dict['login_viz']['hour_of_day_freq'] = login_times['hod'].value_counts().to_dict()
                viz_dict['login_viz']['day_of_week_freq'] = login_times['dow'].value_counts().to_dict()

        # Mood mapping visualizations.
        if 'mood_preferences' in user_data.keys():
            viz_dict['mood_viz'] = dict()
            counter = dict()
            genres = [
                "rock", "hip-hop", "blues", "jazz",
                "classical", "metal", "reggae", "country", "pop",
                "disco"
            ]

            preferences = user_data['mood_preferences']

            for genre in genres:
                counter[genre] = 0
                for k in preferences.keys():
                    if genre in preferences[k]:
                        counter[genre] += 1

            viz_dict['mood_viz']['genre_frequency'] = counter

        if len(flow_history) > 0:

            agg_flow_dict = dict()
            agg_input_rating = dict()

            # First, collect.
            for flow_dict in flow_history:

                # User input aggregate.
                if 'user_input' in flow_dict.keys():
                    input_ratings = flow_dict['user_input']

                    # Iterate over the ratings.
                    for rating_dict in input_ratings:
                        if ('query' in rating_dict
                                and 'rating' in rating_dict
                                and str(rating_dict['rating']).isnumeric()
                        ):
                            _genre = re.search(pattern, rating_dict['query'])
                            if _genre and _genre.group(1) is not None:
                                genre = _genre.group(1)
                                rating = int(rating_dict['rating'])
                                if genre not in agg_input_rating.keys():
                                    agg_input_rating[genre] = (rating, 1)
                                else:
                                    agg_input_rating[genre] = (
                                        agg_input_rating[genre][0] + rating,
                                        agg_input_rating[genre][1] + 1
                                    )

                # Model output aggregate.
                if 'model_output' in flow_dict.keys() and 'mood' in flow_dict.keys():
                    mood = flow_dict['mood']
                    current_model_output = flow_dict['model_output']['message']['params']

                    if mood not in agg_flow_dict:
                        # We're not concerned with {min, max} now, only {target}.
                        # Slightly hacky, but create a dummy entry to keep count.
                        agg_flow_dict[mood] = {k: v for k, v in current_model_output.items() if 'target' in k}
                        agg_flow_dict[mood]['count'] = 1
                    else:
                        agg_flow_dict[mood]['count'] += 1
                        for k in agg_flow_dict[mood].keys():
                            if k != 'count':
                                agg_flow_dict[mood][k] += current_model_output[k]

            # Now, aggregate.
            for rating in agg_input_rating.keys():
                agg = agg_input_rating[rating][0] / agg_input_rating[rating][1]
                agg_input_rating[rating] = agg

            # Now, aggregate
            for mood_key in agg_flow_dict.keys():
                for param in agg_flow_dict[mood_key].keys():
                    if param != 'count':
                        agg_flow_dict[mood_key][param] = agg_flow_dict[mood_key][param]/agg_flow_dict[mood_key]['count']

            # remove the 'count' key.
            for mood in agg_flow_dict.keys():
                agg_flow_dict[mood].pop('count')

            viz_dict['model_param_history'] = agg_flow_dict
            viz_dict['aggregate_input_ratings'] = agg_input_rating

        if 'recommendations' in user_data.keys():
            viz_dict['spotify_param_history'] = user_data['recommendations']

        viz_dict['RESPONSE_STATUS'] = "SUCCESS"
        viz_dict['TRACE'] = None

    except:
        viz_dict['RESPONSE_STATUS'] = "ERROR"
        viz_dict['TRACE'] = format_exc()

    finally:
        return viz_dict
