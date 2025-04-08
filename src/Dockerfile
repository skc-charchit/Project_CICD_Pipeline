# This Dockerfile is used to build a Docker image for the Python application.
# It uses the official Python 3.10 slim image as the base image.
FROM python:3.10-slim

# Set the working directory in the container to /app
COPY . /app

# Set the working directory in the container to /app
WORKDIR /app

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Command to run the application
CMD ["uvicorn", "main:app" , "--host", "0.0.0.0", "--port", "80"]