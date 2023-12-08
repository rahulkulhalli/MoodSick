from . import db_name as collection
from bson import ObjectId
import random


async def save_admin_authorization_code(user_id, authorization_code):
    # print(user_id)
    # print(authorization_code)
    collection.admin.update_one({"_id": ObjectId(user_id)}, {"$set": {"authorization_code": authorization_code}})
    return {"status": "Ok"}

async def save_admin_refresh_token(user_id, refresh_token):
    collection.admin.update_one({"_id": ObjectId(user_id)}, {"$set": {"refresh_token": refresh_token}})
    return {"status": "Ok"}

async def get_admin_authorization_code(user_id):
    # print(user_id)
    admin = collection.admin.find_one({"_id": ObjectId(user_id)})
    return admin.get("authorization_code")

async def get_admin_refresh_token(user_id):
    # print(user_id)
    admin = collection.admin.find_one({"_id": ObjectId(user_id)})
    return admin.get("refresh_token")
