from fastapi import Depends, FastAPI
from .routers import users

app = FastAPI()

app.include_router(users.router,
                   prefix="/user")


@app.get("/")
async def root():
    return {"message": "Hello MoodSick!"}
