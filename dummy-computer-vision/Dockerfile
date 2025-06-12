####################################
# Dockerfile for dummy-computer-vision microservice
####################################

# FROM = Create a new build stage from a base image
# EXPOSE = Describe which ports your application is listening on
# ENTRYPOINT = Specify default executable (run a command)

# Use a minimal Python image
FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0

# Install required libraries
RUN pip install pika

# Add all the local files in src in src remote directory
COPY src/ src
COPY build_temp/dummy_dvde_api.py src/

# Change working directory
WORKDIR /src

# Copy the Python script and any other necessary files
COPY . .

# Set environment variables for broker credentials (replace with actual values)
ENV BROKER_CREDS_USER="admin"
ENV BROKER_CREDS_PASSWORD="admin"

# Expose the port for communication with the message broker
EXPOSE 5672

# Run the Python script
CMD ["python3", "sender.py"]