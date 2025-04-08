# Use an official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.9-slim

# Set work directory
WORKDIR /app

# Copy project files
COPY src /app/src

# Copy model and scaler files
COPY src/models /app/src/models

# Copy mongodb.py script
COPY mongodb.py /app/

# Copy requirements.txt
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --upgrade -r requirements.txt python-dotenv pymongo pandas

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run the script when the container launches
CMD ["sh", "-c", "python mongodb.py && uvicorn src.main:app --host 0.0.0.0 --port 8000"]
