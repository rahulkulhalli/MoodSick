from app.models.users import UserData, UserPreferences
from . import db_name as collection
from passlib.context import CryptContext
import traceback
from datetime import datetime
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
from bson import ObjectId
from app.models.users import UserAudioPreferance 



async def create_user(user: UserData):

    try:
        is_exist = collection.users.find_one({"email": str(user.email)})
        if is_exist is not None:
            return "Already Exists"
        hashed_password = pwd_context.hash(user.password)
        user.password = hashed_password
        user.login_history = []
        collection.users.insert_one(dict(user))
        return True
    except Exception as e:
        print("Error while create_user", e)
        return False


async def login_user(user: UserData):
    try:
        user_data = collection.users.find_one(
            {"email": user.email}, {"_id": 0})
        res = pwd_context.verify(user.password, user_data["password"])
        if user_data and res:
            del user_data["password"]
            insert_login_record(user.email)
            return {"message": "Login Successful", "user_data": user_data}
        else:
            return {"message": "Invalid Credentials"}
    except Exception as e:
        print(traceback.format_exc())
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


async def save_user_mood_maping(data: UserPreferences):
    try:
        r_data = transform_preferences_data(data)
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
    return data


async def create_user(user: UserRegisterData):
    _id = collection.users.insert_one(dict(user))
    # user = users_serializer(collection.find({"_id": _id.inserted_id}))
    return {"status": "Ok","data": user}

async def save_user_authorization_code(user_id, authorization_code):
    print(user_id)
    print(authorization_code)
    collection.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"authorization_code": authorization_code}})
    return {"status": "Ok"}

async def save_user_refresh_token(user_id, refresh_token):
    collection.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"refresh_token": refresh_token}})
    return {"status": "Ok"}

async def get_user_authorization_code(user_id):
    user = collection.users.find_one({"_id": ObjectId(user_id)})
    return user.get("authorization_code")

async def get_user_refresh_token(user_id):
    print(user_id)
    user = collection.users.find_one({"_id": ObjectId(user_id)})
    return user.get("refresh_token")

async def get_user_age(user_id):
    user_age = collection.users.find_one({"_id": ObjectId(user_id)})
    return user_age.get("age")

async def save_user_playlist_uri(user_id, user_playlist_uri):
    print("Saved User Playlist")
    collection.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"user_playlist_uri": user_playlist_uri}})
    return {"status": "Ok"}

async def get_user_playlist_uri(user_id):
    user = collection.users.find_one({"_id": ObjectId(user_id)})
    return user.get("user_playlist_uri")

async def save_user_audio_preferance(user_id, user_audio_preferance: UserAudioPreferance):
    user_audio_preferance = dict(user_audio_preferance)
    collection.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"user_audio_preferance": user_audio_preferance}})
    return {"status": "Ok"}

async def get_user_tracks(user_id):
    track = collection.track_features.find_one({"user_id": user_id})
    if track:
        return track.get("songs_data")
    return []
