FROM python:3.9-slim

WORKDIR /app

COPY . /app/

# Install dependencies
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy .env file into the container
COPY .env .

# Set environment variables from .env file
RUN pip install python-dotenv
RUN python -c "import os, dotenv; dotenv.load_dotenv(); \
                print('MongoDB URI: ' + str(os.environ.get('MONGODB_CONNECTION_URI'))) ; \
                print('DB Name: ' + str(os.environ.get('DB_NAME'))) ; \
                print('Collection Name: ' + str(os.environ.get('COLLECTION_NAME')))"

ENV PORT=8001

EXPOSE 8001

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001"]
