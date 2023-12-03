from typing import List
from fastapi import FastAPI
from .routers import users, spotify_communication
from dotenv import load_dotenv


app = FastAPI()

app.include_router(users.router,
                   prefix="/user")

app.include_router(spotify_communication.router,
                   prefix="/spotify")

@app.get("/")
async def root():
    return {"message": "Hello MoodSick!"}
