import os
import requests
from fastapi import HTTPException, APIRouter, Request
from httpx import AsyncClient
from .import users, admin
import base64
from pydantic import BaseModel
from enum import Enum
import numpy as np
from app.models.spotify_communication import SpotifyPlaylist, SpotifyRecommendationInput, SongFeature
from app.models.users import UserPlaylistData, UserAudioPreferance
from app.db_communcation.spotify_communications import save_track_audio_preferances, get_track_audio_preferances
from app.db_communcation.users import get_user_playlist_uri, get_user_age, save_user_playlist_uri, save_user_audio_preferance, get_user_tracks, save_user_recommendations_based_on_mood 
import json
from asyncio import gather
from app.routers import base_categories
import traceback

router = APIRouter()


async def read_spotify_profile_user(user_token):
    url = 'https://api.spotify.com/v1/me'
    headers = {'Authorization': f"Bearer {user_token}"}

    async with AsyncClient() as client:
        response = await client.get(url, headers=headers)
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        return response.json().get("id"), response.json().get("display_name")

async def create_user_playlist(user_id):
    user_token = await users.get_user_spotify_token(user_id)
    # Get the user id and name
    spotify_user_id, spotify_user_name = await read_spotify_profile_user(user_token)
    # print(spotify_user_id, spotify_user_name)
    endpoint_url_user = f"https://api.spotify.com/v1/users/{spotify_user_id}/playlists"
    user_playlist_name = "MoodSick Playlist for " + spotify_user_name + "!"
    user_description = "Playlist generated by MoodSick"

    request_body = json.dumps({
        "name": user_playlist_name,
        "description": user_description,
        "public": False # let's keep it between us - for now
    })
    # Get the user playlist uri after creating the playlist
    response = requests.post(url = endpoint_url_user, data = request_body, headers={"Content-Type":"application/json", "Authorization": f"Bearer {user_token}"})
    # print(response.json())
    # Save the user playlist uri to the mongodb database
    await save_user_playlist_uri(user_id, response.json().get("uri"))
    
    return response.json().get("uri")

async def get_spotify_and_user_preferences(user_mood,request: SpotifyRecommendationInput):
    user_id = request.user_id
    user_age = await get_user_age(user_id)
    moodsick_playlist_uri = None
    if user_age < 20:
        moodsick_playlist_uri = SpotifyPlaylist.AGE_10_20.value
    elif user_age < 30:
        moodsick_playlist_uri = SpotifyPlaylist.AGE_20_30.value
    elif user_age < 40:
        moodsick_playlist_uri = SpotifyPlaylist.AGE_30_40.value
    elif user_age < 50:
        moodsick_playlist_uri = SpotifyPlaylist.AGE_40_50.value
    else:
        moodsick_playlist_uri = SpotifyPlaylist.AGE_50_60.value
    

    user_playlist_data = await get_user_tracks(user_id)
    # print(user_playlist_data)
    if len(user_playlist_data) == 0:
         await get_user_audio_preferance(user_id)

    recommendations_task = get_spotify_recommendations(user_mood, request)
    user_preference_task = get_songs_based_on_audio_preferance(user_id, request)
    
    results = await gather(recommendations_task, user_preference_task)
    return {
        "recommendations": results[0],
        "data_mined_songs": set(results[1]),
        "moodsick_playlist_uri": "spotify:playlist:" + moodsick_playlist_uri
    }

# @router.post("/spotify-recommendations")
# async def test_get_spotify_recommendations(request: SpotifyRecommendationInput):
#     user_mood = "Happy"
#     return await get_spotify_and_user_preferences(user_mood, request)


# This function is used to get the spotify recommendations based on the parameters passed by the model
async def get_spotify_recommendations(user_mood, request: SpotifyRecommendationInput):
    user_id = request.user_id
    user_token = await users.get_user_spotify_token(user_id)
    # moodsick_token = await admin.get_moodsick_spotify_token()
    url = 'https://api.spotify.com/v1/recommendations'
    headers = {
        'Authorization': f"Bearer {user_token}"  # Replace with your actual token
    }
    seed_genres = request.genre
    genres = seed_genres.split(",")
    # print(seed_genres)
    sampled_genres = ",".join([np.random.choice(base_categories[genre]) for genre in genres])
    # print(f"Original genres: {seed_genres}, sampled genres: {sampled_genres}")
    limit = 100
    sort_by_popularity = request.sort_by_popularity
    # The following params are cauing the api to fail: mode, key, time_signature
    params_target = {
        'market': request.market,
        'seed_genres': sampled_genres,
        'limit': limit,
        'target_danceability': request.target_danceability,
        'target_energy': request.target_energy,
        'target_loudness': request.target_loudness,
        'target_speechiness': request.target_speechiness,
        'target_acousticness': request.target_acousticness,
        'target_instrumentalness': request.target_instrumentalness,
        'target_liveness': request.target_liveness,
        'target_valence': request.target_valence,
        'target_tempo': request.target_tempo,
    }

    async with AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params_target)
        # print(response.json())
        # if(len(response.json().get("tracks")) == 0 or response.status_code != 200):
        #     response = await client.get(url, headers=headers, params=params_target)
        #     if(len(response.json().get("tracks")) == 0):
        #         raise HTTPException(status_code=500, detail="No tracks found")
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        responseJson = response.json()

        # Dict to save the track uri and popularity
        track_uris = {}
        for each in range(len (responseJson["tracks"])):
            #del responseJson["tracks"][each]["available_markets"]
            # del responseJson["tracks"][each]["album"]
            track_uris[responseJson["tracks"][each]["uri"]] = responseJson["tracks"][each]["popularity"]
            # track_uris.append(responseJson["tracks"][each]["uri"])
        
        # track_features = await get_track_features(user_token, track_uris)
        # print(track_features)
        # return track_features
        # Sort the tracks based on popularity
        sorted_uris = sorted(track_uris, key=track_uris.get, reverse=True)
        # Get top 5 tracks
        popular_songs = sorted_uris[:5]
        
        # Choose 5 random tracks
        track_uris = np.random.choice(list(track_uris.keys()), 5, replace=False).tolist()

        analysis_tracks = popular_songs + track_uris
        analysis_tracks = [uri.split(":")[-1] for uri in analysis_tracks]
        analysis = await analyze_tracks(user_id, user_mood, analysis_tracks)
        # print(f"analysis::::::::::::::::::::::::::{analysis}")
        # Check if the user has a playlist
        # If the user has a playlist, save the tracks to the playlist
        # If the user does not have a playlist, create a playlist and save the tracks to the playlist
        user_playlist_uri = await get_user_playlist_uri(user_id)
        if user_playlist_uri is None or len(user_playlist_uri) == 0:
            user_playlist_uri = await create_user_playlist(user_id)

        user_playlist_uri = user_playlist_uri.split(":")[-1]
        # user_playlist_uri = "2vsbJJ1WUEp0D9Nwa4wdzH"
        # Save the tracks to the user playlist
        await save_to_user_playlist(user_id, track_uris, user_playlist_uri)
        # Save the tracks to the moodsick playlist according to user's age
        user_age = await get_user_age(user_id)
        # await save_to_moodsick_playlist(user_age, moodsick_token, track_uris)

        return {
            "recommended_songs": track_uris,
            "popular_tracks": popular_songs
        }

async def analyze_tracks(user_id, user_mood, track_uris):
    # print(f"TRACKKK URIIIIIIII::::::::::::::::::::::::::::{len(track_uris)}")
    user_token = await users.get_user_spotify_token(user_id)
    endpoint = "https://api.spotify.com/v1/audio-features"
    headers = {
        'Authorization': f"Bearer {user_token}"
    }
    data = {
        "ids": ",".join(track_uris)
    }
    async with AsyncClient() as client:
        response = await client.get(endpoint, headers=headers, params=data)
        # print(f"Response of Get Audio Features: {response.json()}")
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        
        responseJson = response.json()
        audio_feature_dict = []
        for each in range(len(responseJson["audio_features"])):
            if responseJson["audio_features"][each] is not None:
                # we will save the uri of the track and the audio features of the track to the database
                audio_feature_dict.append(SongFeature(uri=responseJson["audio_features"][each]["uri"], acousticness=responseJson["audio_features"][each]["acousticness"], danceability=responseJson["audio_features"][each]["danceability"], duration_ms=responseJson["audio_features"][each]["duration_ms"], energy=responseJson["audio_features"][each]["energy"], instrumentalness=responseJson["audio_features"][each]["instrumentalness"], key=responseJson["audio_features"][each]["key"], liveness=responseJson["audio_features"][each]["liveness"], loudness=responseJson["audio_features"][each]["loudness"], mode=responseJson["audio_features"][each]["mode"], speechiness=responseJson["audio_features"][each]["speechiness"], tempo=responseJson["audio_features"][each]["tempo"], time_signature=responseJson["audio_features"][each]["time_signature"], valence=responseJson["audio_features"][each]["valence"]))
        
        song_params = {}
        for each in audio_feature_dict:
            # print(items.acousticness)
            song_params["mood_avg_acousticness"] = song_params.get("acousticness", 0) + each.acousticness
            song_params["mood_avg_danceability"] = song_params.get("danceability", 0) + each.danceability
            song_params["mood_avg_energy"] = song_params.get("energy", 0) + each.energy
            song_params["mood_avg_instrumentalness"] = song_params.get("instrumentalness", 0) + each.instrumentalness
            song_params["mood_avg_key"] = song_params.get("key", 0) + each.key
            song_params["mood_avg_liveness"] = song_params.get("liveness", 0) + each.liveness
            song_params["mood_avg_loudness"] = song_params.get("loudness", 0) + each.loudness
            song_params["mood_avg_mode"] = song_params.get("mode", 0) + each.mode
            song_params["mood_avg_speechiness"] = song_params.get("speechiness", 0) + each.speechiness
            song_params["mood_avg_tempo"] = song_params.get("tempo", 0) + each.tempo
            song_params["mood_avg_time_signature"] = song_params.get("time_signature", 0) + each.time_signature
            song_params["mood_avg_valence"] = song_params.get("valence", 0) + each.valence

        # print(song_params)
        # # Get the average of all the audio features
        song_params = {k: v / len(audio_feature_dict) for k, v in song_params.items()}
        #Save the audio features to the database
        # song_params = UserAudioPreferance(**song_params)
        
        await save_user_recommendations_based_on_mood(user_id, user_mood, song_params)

        return "Success"


async def save_to_user_playlist(user_id, track_uris, user_playlist_link):
    user_token = await users.get_user_spotify_token(user_id)
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
        "uris": track_uris,
        "position": 0
    }

    async with AsyncClient() as client:
        response_moodsick = await client.post(endpoint_url_mooksick, headers=headers, json=data)
        if response_moodsick.status_code != 201:
            raise HTTPException(status_code=response_moodsick.status_code, detail=response_moodsick.text)
        
        return response_moodsick.json()

# async def get_track_features(user_token, track_uris):
#     # Split each uri like this user_playlist_uri.split(":")[-1]
#     api_track_uri = ",".join([uri.split(":")[-1] for uri in track_uris])
#     enpoint_url = "https://api.spotify.com/v1/tracks"
#     headers = {
#         'Authorization': f"Bearer {user_token}"
#     }
#     data = {
#         "ids" : api_track_uri
#     }
#     async with AsyncClient() as client:
#         track_features = []
#         response = await client.get(enpoint_url, headers=headers, params=data)
#         print("Inside Get Track Features")
#         if response.status_code != 200:
#             raise HTTPException(status_code=response.status_code, detail=response.text)
        
#         responseJson = response.json()
#         for each in range(len(responseJson["tracks"])):
#         #     print(responseJson["tracks"][each]["artists"][0]["genres"])
#             track_features.append(SongFeature(uri=responseJson["tracks"][each]["uri"], genre=responseJson["tracks"][each]["artists"][0]["genres"], popularity=responseJson["tracks"][each]["popularity"]))
                
#         return responseJson

async def get_playlist_songs(user_token, playlist_uri):
    endpoint = f"https://api.spotify.com/v1/playlists/{playlist_uri}/tracks"
    headers = {
        'Authorization': f"Bearer {user_token}"
    }
    data = {
        "limit": 50,
        "offset": 0
    }
    async with AsyncClient() as client:
        response = await client.get(endpoint, headers=headers, params=data)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        
        responseJson = response.json()
        track_uri = []
        for each in range(len(responseJson["items"])):
            track_uri.append(responseJson["items"][each]["track"]["id"])

        return track_uri

# We will user the user's tracks to get the data. We will get the audio features of the tracks and then use the average of the audio features to get the user's audio features
async def get_audio_features(user_id, track_uris):
    # print(user_id)
    # print(track_uris)
    user_token = await users.get_user_spotify_token(user_id)
    endpoint = "https://api.spotify.com/v1/audio-features"
    headers = {
        'Authorization': f"Bearer {user_token}"
    }
    data = {
        "ids": ",".join(track_uris)
    }
    async with AsyncClient() as client:
        response = await client.get(endpoint, headers=headers, params=data)
        # print(f"Response of Get Audio Features: {response.json()}")
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        
        responseJson = response.json()
        audio_feature_dict = []
        for each in range(len(responseJson["audio_features"])):
            if responseJson["audio_features"][each] is not None:
                # we will save the uri of the track and the audio features of the track to the database
                audio_feature_dict.append(SongFeature(uri=responseJson["audio_features"][each]["uri"], acousticness=responseJson["audio_features"][each]["acousticness"], danceability=responseJson["audio_features"][each]["danceability"], duration_ms=responseJson["audio_features"][each]["duration_ms"], energy=responseJson["audio_features"][each]["energy"], instrumentalness=responseJson["audio_features"][each]["instrumentalness"], key=responseJson["audio_features"][each]["key"], liveness=responseJson["audio_features"][each]["liveness"], loudness=responseJson["audio_features"][each]["loudness"], mode=responseJson["audio_features"][each]["mode"], speechiness=responseJson["audio_features"][each]["speechiness"], tempo=responseJson["audio_features"][each]["tempo"], time_signature=responseJson["audio_features"][each]["time_signature"], valence=responseJson["audio_features"][each]["valence"]))

        return audio_feature_dict

# @router.post("/test_save_feature")
async def get_user_audio_preferance(user_id):
    # print("Inside get_user_audio_preferance")
    # print(user_id)
    # Using user token. So we don't have to worry about api rate limit
    user_token = await users.get_user_spotify_token(user_id)
    enpoint_url = "https://api.spotify.com/v1/me/playlists"
    headers = {
        'Authorization': f"Bearer {user_token}"
    }
    data = {
        "limit": 50, #Spotify allows upto 50 playlists.
        "offset": 0
    }
    async with AsyncClient() as client:
        response = await client.get(enpoint_url, headers=headers, params=data)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        
        responseJson = response.json()
        # print(responseJson)
        # Get the playlist uri of the user
        playlist_uri = []
        for each in range(len(responseJson["items"])):
            playlist_uri.append(responseJson["items"][each]["id"])
        # print(playlist_uri)
        # Get the tracks of the playlist and save it to UserPlaylistData
        playlist_track_dict = []
        for each in range(len(playlist_uri)):
            playlist_track_dict.append(UserPlaylistData(uri=playlist_uri[each], name=responseJson["items"][each]["name"], total_songs=responseJson["items"][each]["tracks"]["total"], track_uri=await get_playlist_songs(user_token, playlist_uri[each])))
        # print(playlist_track_dict)
        # feature_dict will save {k,v} where k = playlist_uri and v = audio features of the track
        feature_dict = {}
        for each in range(len(playlist_track_dict)):
            feature_dict[playlist_track_dict[each].uri] = await get_audio_features(user_id, playlist_track_dict[each].track_uri)
        # print(feature_dict)
        await save_track_audio_preferances(user_id, list(feature_dict.values()))

        
        # song_params will save {k,v} where k = audio feature and v = average of the audio feature
        song_params = {}
        for k,v in feature_dict.items():
            for each in v:
                song_params["avg_acousticness"] = song_params.get("acousticness", 0) + each.acousticness
                song_params["avg_danceability"] = song_params.get("danceability", 0) + each.danceability
                song_params["avg_energy"] = song_params.get("energy", 0) + each.energy
                song_params["avg_instrumentalness"] = song_params.get("instrumentalness", 0) + each.instrumentalness
                song_params["avg_key"] = song_params.get("key", 0) + each.key
                song_params["avg_liveness"] = song_params.get("liveness", 0) + each.liveness
                song_params["avg_loudness"] = song_params.get("loudness", 0) + each.loudness
                song_params["avg_mode"] = song_params.get("mode", 0) + each.mode
                song_params["avg_speechiness"] = song_params.get("speechiness", 0) + each.speechiness
                song_params["avg_tempo"] = song_params.get("tempo", 0) + each.tempo
                song_params["avg_time_signature"] = song_params.get("time_signature", 0) + each.time_signature
                song_params["avg_valence"] = song_params.get("valence", 0) + each.valence

        # Get the average of all the audio features
        song_params = {k: v / len(feature_dict) for k, v in song_params.items()}
        #Save the audio features to the database
        song_params = UserAudioPreferance(**song_params)

        await save_user_audio_preferance(user_id, song_params)
        
        return "Success"


async def get_songs_based_on_audio_preferance(user_id, request: SpotifyRecommendationInput):

    # user_token = await users.get_user_spotify_token()
    user_track_audio_features = await get_track_audio_preferances(user_id)
    track_uris = []
    count = 0
    min_multiplier = 1.0
    max_multiplier = 1.0
    increment = 0.05
    found = False
    #
    # Get the track uris based on the audio features The dict is in the format  [{'uri':
    # 'spotify:track:1qIAqSCPcRkkNU8dj5pIOC', 'acousticness': 0.00548, 'danceability': 0.459, 'duration_ms':
    # 231013.0, 'energy': 0.629, 'instrumentalness': 0.0, 'key': 10, 'liveness': 0.35, 'loudness': -5.492, 'mode': 1,
    # 'speechiness': 0.0277, 'tempo': 84.935, 'time_signature': 4, 'valence': 0.562},
    # {'uri': 'spotify:track:5ve0BYRZZ2aoHFqZMxqYgt', 'acousticness': 0.0083, 'danceability': 0.607, 'duration_ms':
    # 232467.0, 'energy': 0.619, 'instrumentalness': 0.0, 'key': 1, 'liveness': 0.366, 'loudness': -5.761, 'mode': 0,
    # 'speechiness': 0.038, 'tempo': 79.998, 'time_signature': 4, 'valence': 0.5}]
    
    while not found and min_multiplier >= 0.1 and max_multiplier <= 1.9:
        # print(min_multiplier, max_multiplier)
        for track_info in user_track_audio_features: 
            if all(
                key in track_info
                for key in ["danceability", "energy", "loudness", "uri", "acousticness",
                            "instrumentalness", "liveness", "speechiness", "tempo", "valence"]

            ):
                hits = 0
                hits_dict = []
                if min_multiplier * request.min_danceability <= track_info["danceability"] <= request.max_danceability * max_multiplier:
                    hits += 1
                    hits_dict.append("danceability")
                if min_multiplier * request.min_energy <= track_info["energy"] <= request.max_energy * max_multiplier:
                    hits += 1
                    hits_dict.append("energy")
                if min_multiplier * request.min_loudness <= track_info["loudness"] <= request.max_loudness * max_multiplier:
                    hits += 1
                    hits_dict.append("loudness")
                if min_multiplier * request.min_speechiness <= track_info["speechiness"] <= request.max_speechiness * max_multiplier:
                    hits += 1
                    hits_dict.append("speechiness")
                if min_multiplier * request.min_acousticness <= track_info["acousticness"] <= request.max_acousticness * max_multiplier:
                    hits += 1
                    hits_dict.append("acousticness")
                if min_multiplier * request.min_instrumentalness <= track_info["instrumentalness"] <= request.max_instrumentalness * max_multiplier:
                    hits += 1
                    hits_dict.append("instrumentalness")
                if min_multiplier * request.min_liveness <= track_info["liveness"] <= request.max_liveness * max_multiplier:
                    hits += 1
                    hits_dict.append("liveness")
                if min_multiplier * request.min_valence <= track_info["valence"] <= request.max_valence * max_multiplier:
                    hits += 1
                    hits_dict.append("valence")
                if min_multiplier * request.min_tempo <= track_info["tempo"] <= request.max_tempo * max_multiplier:
                    hits += 1
                    hits_dict.append("tempo")
                print(f"Hits:::::::::::::::::::::::::::::::::::{hits}")
                len_dict = len(hits_dict)
                if hits >= 6 and len_dict >= 6:
                    track_uris.append(track_info["uri"])
                    count += 1
                    if count >= 5:
                        found = True
                        break

            if not found:
                min_multiplier -= increment
                max_multiplier += increment

    return track_uris
