from typing import List
from fastapi import FastAPI
from .routers import users, spotify_communication, admin
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

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


spotify_user_id = None
spotify_client_id = None
spotify_client_secret = None

app.include_router(users.router,
                   prefix="/user")

app.include_router(spotify_communication.router,
                   prefix="/spotify")

app.include_router(admin.router,
                   prefix="/admin")

@app.get("/")
async def root():
    return {"message": "Hello MoodSick!"}

# @app.on_event("startup")
# async def startup_event():
#     global spotify_user_id, spotify_client_id, spotify_client_secret
#     spotify_user_id = os.getenv("SPOTIFY_USER_ID")
#     spotify_client_id = os.getenv("SPOTIFY_CLIENT_ID")
#     spotify_client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")