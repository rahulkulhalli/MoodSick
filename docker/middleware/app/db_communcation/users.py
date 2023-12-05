from app.models.users import UserRegisterData
from . import db_name as collection


async def create_user(user: UserRegisterData):
    _id = collection.users.insert_one(dict(user))
    # user = users_serializer(collection.find({"_id": _id.inserted_id}))
    return {"status": "Ok","data": user}
