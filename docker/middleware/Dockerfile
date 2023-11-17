# Use Ubuntu 20.04 LTS as the base image
FROM ubuntu:20.04

# Update the package lists and install necessary dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    nginx

# Copy the requirements.txt file to the container
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the Nginx configuration file
COPY config/nginx.conf /etc/nginx/nginx.conf

# Copy everything to the working directory
COPY . .

# Expose port 80 for Nginx
EXPOSE 8000

# Start Nginx and run the Flask application
CMD service nginx start && python3 /app/app.py
