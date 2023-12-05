# Use the Python base image
FROM python:3.9

# Set the working directory inside the container to /code
WORKDIR /code

# Copy the requirements.txt file 
COPY ./requirements.txt /code/requirements.txt

# Install the pip dependencies
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the contents of the ./app directory
COPY ./app /code/app

# Run the server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]
