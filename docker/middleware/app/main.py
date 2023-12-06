import os
from typing import List
from fastapi import FastAPI
from .routers import users, spotify_communication, admin
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()
origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

folder = os.path.dirname(__file__)
app.mount("/static", StaticFiles(directory="/code/app/static"), name="static")



app.include_router(users.router,
                   prefix="/user")

app.include_router(spotify_communication.router,
                   prefix="/spotify")

app.include_router(admin.router,
                   prefix="/admin")

@app.get("/")
async def root():
    return {"message": "Hello MoodSick!"}