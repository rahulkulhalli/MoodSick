# Use Ubuntu 20.04 LTS as the base image
FROM ubuntu:20.04

ARG WORKDIR=/ml_model

COPY . $WORKDIR

# Avoid prompts from apt
ENV DEBIAN_FRONTEND=noninteractive

# Update and install dependencies
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-dev \
    build-essential \
    nano \
    vim 

# Upgrade pip
RUN pip3 install --upgrade pip

# Install requirements for ml_training
RUN pip3 install --no-cache-dir -r ml_model/requirements.txt
