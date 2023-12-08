import pymongo
# from passlib.context import CryptContext


db_client = pymongo.MongoClient("mongodb://10.9.0.9:27017/")
db_name = db_client["moodsick_db"]



# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
