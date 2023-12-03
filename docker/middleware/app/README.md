# Middleware Docs
- We have python based FastAPI setup here to serve the backend server to cater to the UI Services and User Interactions.
- This will also be the connection point to the database which would store all the user related data.
- The requirements.txt file contains the python dependencies which are required for this container.
- The /app directory contains the source code and server configuration for the FastAPI backend which runs on the uvicorn ASGI server.
- The entrypoint of this FastAPI project is the /app/main.py file which creates the FastAPI instance. 
- All user related endpoints would be put up in the /app/routers/users.py file.