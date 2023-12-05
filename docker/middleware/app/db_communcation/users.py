from app.models.users import UserRegisterData
from . import db_name as collection
from bson import ObjectId


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