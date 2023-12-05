from typing import List
from fastapi import FastAPI
from .routers import users, spotify_communication, admin
from dotenv import load_dotenv
import pymongo


app = FastAPI()

spotify_user_id = None
spotify_client_id = None
spotify_client_secret = None

app.include_router(users.router,
                   prefix="/user")

app.include_router(spotify_communication.router,
                   prefix="/spotify")

app.include_router(admin.router,
                   prefix="/admin")

db_client = pymongo.MongoClient("mongodb://localhost:27017/")
db_name = db_client["moodsick_db"]

@app.get("/")
async def root():
    return {"message": "Hello MoodSick!"}

@app.on_event("startup")
async def startup_event():
    global spotify_user_id, spotify_client_id, spotify_client_secret
    spotify_user_id = os.getenv("SPOTIFY_USER_ID")
    spotify_client_id = os.getenv("SPOTIFY_CLIENT_ID")
    spotify_client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")