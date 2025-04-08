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

# Copy preprocessed_data.csv
COPY preprocessed_data.csv /app/

# Copy run.sh script
COPY run.sh /app/

# Copy requirements.txt
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --upgrade -r requirements.txt python-dotenv pymongo pandas joblib motor

# Make port 8001 available to the world outside this container
EXPOSE 8001

# Make the script executable inside the container
RUN chmod +x /app/run.sh

# Run the script when the container launches
CMD ["/app/run.sh"]
