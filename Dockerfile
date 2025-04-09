# Use an official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.9-slim

# Set work directory
WORKDIR /app

# Copy project files
COPY src /app/src
COPY src/models /app/src/models
COPY .env /app/
# Copy mongodb.py script
COPY mongodb.py /app/

# Copy preprocessed_data.csv
COPY preprocessed_data.csv /app/

# Copy requirements.txt
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Set environment variable for port
ENV PORT=8001

# Make port 8001 available to the world outside this container
EXPOSE 8001

# Run the application directly using Uvicorn
CMD ["sh", "-c", "uvicorn src.main:app --host 0.0.0.0 --port $PORT"]

# Use the following command to build the Docker image
# docker build -t myapp:latest .
