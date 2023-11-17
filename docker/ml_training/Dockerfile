# Use the official PyTorch base image
FROM pytorch/pytorch:latest

WORKDIR /app

RUN apt-get update && apt-get install
# Copy the requirements.txt file to the container
COPY requirements.txt .

# Install the dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the content of the local src directory to the working directory
COPY ./src .

# Specify the command to run on container start
CMD ["python", "train.py"]
