from app.models.users import UserAudioPreferance
from bson import ObjectId
import random
from app.models.users import UserData, UserPreferences
from . import db_name as collection
from passlib.context import CryptContext
import traceback
from datetime import datetime
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_user(user: UserData):

    try:
        is_exist = collection.users.find_one({"email": str(user.email)})
        if is_exist is not None:
            return "Already Exists"
        hashed_password = pwd_context.hash(user.password)
        user.password = hashed_password
        user.login_history = list()
        collection.users.insert_one(dict(user))
        return True
    except Exception as e:
        print("Error while create_user", e)
        return False


async def login_user(user: UserData):
    try:
        user_data = collection.users.find_one(
            {"email": user.email}, {})
        res = pwd_context.verify(user.password, user_data["password"])
        if user_data and res:
            del user_data["password"]
            user_id = str(user_data["_id"])
            user_data["user_id"] = user_id
            # print(type(user_data["_id"]))
            # user_data["user_id"] = str(user_data["_id"])
            insert_login_record(user.email)
            return {"message": "Login Successful", "user_data": user_data}
        else:
            return {"message": "Invalid Credentials"}
    except Exception as e:
        # print(traceback.format_exc())
        print("Error while create_user", e)
        return False


def insert_login_record(email):
    try:
        collection.users.update_one({"email": email}, {
            "$push": {
                "login_history":    datetime.now()
            }
        })
    except Exception as e:
        print("Error in  insert_login_record", e)
        print(traceback.format_exc())


"""
Assume user has completed mapping.
Assumption: We limit mood:genre mappings to a max of 5.
On n=1+ flow,
    1. get all songs from db for given genres.
    2. sort al filtered songs (in ascending order) by the count of number of times they have been shown(k)
    3. 
    - Assume user has the following mapping:
    {"very happy": ["rock"]}
    Then, we will select 5 songs from rock such that they have the lowest count of k
    - Assume user has the foll. mapping:
    {"very happy": ["rock", "classical"]}
    Show 2 from each
    - if 3, then 6
    - if 4, then 4
    - if 5, then 5
"""


async def get_songs_for_user(request_data_dict: dict):
    print(request_data_dict)
    mood = request_data_dict.get("mood")
    user_id = request_data_dict.get("user_id")
    try:
        user_mood_genres = await get_user_mood_genres(user_id, mood)
        print("user_mood_genres", user_mood_genres)
        mood_genre = []
        # print(user_mood_genres)
        for genre in user_mood_genres:
            # print(genre)
            if genre == "hip-hop":
                mood_genre.append("hiphop")
            else:
                mood_genre.append(genre)
        user_mood_genres = mood_genre
        length = len(user_mood_genres)
        print(length)
        if length == 1:
            #['rock'] then select 5 songs from rock according to the least number of times played
            songs = collection.songs.aggregate([
                {"$match": {"genre": {"$in": user_mood_genres}}},
                {"$sort": {"number_of_times_played": 1}},
                {"$group": {"_id": "$genre", "songs": {"$push": "$$ROOT"}}},
                {"$project": {"songs": {"$slice": ["$songs", 5]}}}, 
                {"$unwind": "$songs"},
                {"$limit": 5} 
            ])
            songs = list(songs)
            for song in songs:
                song_id = song.get("songs").get("_id")
                collection.songs.update_one(
                    {"_id": song_id}, {"$inc": {"number_of_times_played": 1}})
            print(songs)
            return list(songs)
        elif length == 2:
            # ['rock', "jazz"] then select 2 songs from each genre according to the least number of times played
            songs = collection.songs.aggregate([
                {"$match": {"genre": {"$in": user_mood_genres}}},
                {"$sort": {"number_of_times_played": 1}},
                {"$group": {"_id": "$genre", "songs": {"$push": "$$ROOT"}}},
                {"$project": {"songs": {"$slice": ["$songs", 2]}}}, 
                {"$unwind": "$songs"},
                {"$limit": 4} 
            ])
            songs = list(songs)
            print(songs)
            for song in songs:
                song_id = song.get("songs").get("_id")
                collection.songs.update_one(
                    {"_id": song_id}, {"$inc": {"number_of_times_played": 1}})
            return songs
        elif length == 3:
            songs = collection.songs.aggregate([
                {"$match": {"genre": {"$in": user_mood_genres}}},
                {"$sort": {"number_of_times_played": 1}},
                {"$group": {"_id": "$genre", "songs": {"$push": "$$ROOT"}}},
                {"$project": {"songs": {"$slice": ["$songs", 2]}}},
                {"$unwind": "$songs"},
                {"$limit": 6}
            ])
            songs = list(songs)
            print(songs)
            for song in songs:
                song_id = song.get("songs").get("_id")
                collection.songs.update_one({"_id": song_id}, {"$inc": {"number_of_times_played": 1}})
            return songs
        elif length == 4:
            songs = collection.songs.aggregate([
                {"$match": {"genre": {"$in": user_mood_genres}}},
                {"$sort": {"number_of_times_played": 1}},
                {"$group": {"_id": "$genre", "songs": {"$push": "$$ROOT"}}},
                {"$project": {"songs": {"$slice": ["$songs", 1]}}},
                {"$unwind": "$songs"},
                {"$limit": 4}
            ])
            songs = list(songs)
            for song in songs:
                song_id = song.get("songs").get("_id")
                collection.songs.update_one(
                    {"_id": song_id}, {"$inc": {"number_of_times_played": 1}})
            return songs
        elif length == 5:
            songs = collection.songs.aggregate([
                {"$match": {"genre": {"$in": user_mood_genres}}},
                {"$sort": {"number_of_times_played": 1}},
                {"$group": {"_id": "$genre", "songs": {"$push": "$$ROOT"}}},
                {"$project": {"songs": {"$slice": ["$songs", 1]}}},
                {"$unwind": "$songs"},
                {"$limit": 5}
            ])
            songs = list(songs)
            for song in songs:
                song_id = song.get("songs").get("_id")
                collection.songs.update_one(
                    {"_id": song_id}, {"$inc": {"number_of_times_played": 1}})
            return songs

    except Exception as e:
        print("Error in  get_songs_for_user", e)
        print(traceback.format_exc())
        return []


async def save_model_response_data(response, user_id, mood, inserted_mood_flow_id):
    update = collection.flow_history.update_one({"_id": ObjectId(inserted_mood_flow_id)}, {
        "$set": {
            "user_id": user_id,
            "model_output": response,
            "mood": mood
        }
    })


async def save_user_ratings(input):
    _insert = collection.flow_history.insert_one({"user_input": input})
    inserted_id = _insert.inserted_id
    return inserted_id
#      "mood_preferences": {
#     "Very Happy": [
#       "rock"
#     ],
#     "Happy": [],
#     "Neutral": [],
#     "Sad": [
#       "hip-hop",
#       "blues",
#       "rock"
#     ],
#     "Very Sad": [
#       "classical",
#       "metal",
#       "reggae"
#     ]
#   }


async def get_user_mood_genres(user_id, mood):
    try:
        print(mood)
        user_data = collection.users.find_one({"_id": ObjectId(user_id)})
        if user_data is not None:
            mood_preferences = user_data.get("mood_preferences")
            return mood_preferences.get(mood)
    except Exception as e:
        print("Error in  get_user_mood_genres", e)
        print(traceback.format_exc())
        return []


async def save_user_mood_maping(data: UserPreferences):
    try:
        r_data = transform_preferences_data(data)
        # for k, v in r_data["mapping"].items():
        #     r_data["mapping"][k] = set(v)
        collection.users.update_one({"email": r_data["email"]}, {
            "$set": {
                "mood_preferences": r_data["mapping"]
            }
        })
        return True
    except Exception as e:
        print("Error in  save_user_mood_maping", e)
        print(traceback.format_exc())
        return False


def transform_preferences_data(preferences: UserPreferences):
    data = preferences.dict(by_alias=True)
    data['mapping'] = {k.replace('_', ' '): v for k,
                       v in data['mapping'].items()}
    for k,v in data['mapping'].items():
        data['mapping'][k] = list(set(v))
    return data


async def save_user_authorization_code(user_id, authorization_code):
    print(user_id)
    print(authorization_code)
    collection.users.update_one({"_id": ObjectId(user_id)}, {
                                "$set": {"authorization_code": authorization_code}})
    return {"status": "Ok"}


async def save_user_refresh_token(user_id, refresh_token):
    collection.users.update_one({"_id": ObjectId(user_id)}, {
                                "$set": {"refresh_token": refresh_token}})
    return {"status": "Ok"}


async def get_user_authorization_code(user_id):
    user = collection.users.find_one({"_id": ObjectId(user_id)})
    return user.get("authorization_code")


async def get_user_refresh_token(user_id):
    # print(user_id)
    user = collection.users.find_one({"_id": ObjectId(user_id)})
    return user.get("refresh_token")


async def get_user_age(user_id):
    user_age = collection.users.find_one({"_id": ObjectId(user_id)})
    return user_age.get("age")


async def save_user_playlist_uri(user_id, user_playlist_uri):
    # print("Saved User Playlist")
    collection.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"user_playlist_uri": user_playlist_uri}})
    return {"status": "Ok"}


async def get_user_playlist_uri(user_id):
    user = collection.users.find_one({"_id": ObjectId(user_id)})
    return user.get("user_playlist_uri")


async def save_user_audio_preferance(user_id, user_audio_preferance: UserAudioPreferance):
    user_audio_preferance = dict(user_audio_preferance)
    collection.users.update_one({"_id": ObjectId(user_id)}, {
                                "$set": {"user_audio_preferance": user_audio_preferance}})
    return {"status": "Ok"}


async def get_user_tracks(user_id):
    track = collection.track_features.find_one({"user_id": user_id})
    if track:
        return track.get("songs_data")
    return []


async def get_genres_from_mood(mood, user_id):
    mood_data = collection.users.find_one(
        {"_id": ObjectId(user_id)}, {"mood_preferences": 1})
    genres = mood_data.get("mood_preferences")[mood]
    return genres


def edit_songs_data():
    # Get all the songs from the database
    songs = list(collection.songs.find())
    # Update the songs data and create a fields number of songs played
    for song in songs:
        song_id = song.get("_id")
        song["number_of_times_played"] = random.randint(1, 10)
        collection.songs.update_one({"_id": ObjectId(song_id)}, {"$set": song})

    return {"status": "Ok"}


async def get_user_data(user_id):
    user = collection.users.find_one({"_id": ObjectId(user_id)})
    return user


async def save_user_recommendations_based_on_mood(user_id, user_mood, recommendations):
    # print(recommendations)
    current_mood_recommendations = collection.users.find_one({"_id": ObjectId(user_id)}, {f"recommendations"})
    
    if current_mood_recommendations is None or current_mood_recommendations.get("recommendations", {}).get(user_mood) is None:
        collection.users.update_one({"_id": ObjectId(user_id)}, {"$set": {f"recommendations.{user_mood}": recommendations}})
    else:
        previous_average = current_mood_recommendations.get("recommendations").get(user_mood)
        new_average_params = {}
        for key, value in recommendations.items():
            new_average_params[key] = (previous_average.get(key,0) + value) / 2
        collection.users.update_one({"_id": ObjectId(user_id)}, {"$set": {f"recommendations.{user_mood}": new_average_params}})

    return {"status": "Ok"}


async def get_user_flow_history(user_id: str):
    # Returns a cursor. Convert to list before returning
    flow_history = collection.flow_history.find({"user_id": user_id})
    return list(flow_history)
