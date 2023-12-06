from app.models.users import UserRegisterData
from . import db_name as collection
from bson import ObjectId
from app.models.users import UserAudioPreferance 


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