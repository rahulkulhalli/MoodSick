# Base image for ml_model for moodSick application
# Link to Docker HubL https://hub.docker.com/repository/docker/moodsick/ml_model/
FROM moodsick/ml_model:latest

# Set the working directory as the fastapi app runs from here
WORKDIR /ml_model/src

COPY main.py .

# The below command will run the app from main.py inside the docker container with reload functionality
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]
