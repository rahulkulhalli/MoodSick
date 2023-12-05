from typing import List
from fastapi import FastAPI
from .routers import users, spotify_communication, admin
from dotenv import load_dotenv
import pymongo


app = FastAPI()

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
