FROM python:3.9-slim

WORKDIR /app

COPY . /app/

# Print the current working directory
RUN pwd

# List the contents of the working directory
RUN ls -la

# Install dependencies
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Set environment variables
ENV MONGODB_CONNECTION_URI=${MONGODB_CONNECTION_URI}
ENV DB_NAME=${DB_NAME}
ENV COLLECTION_NAME=${COLLECTION_NAME}
ENV PORT=8001

# Print environment variables for debugging purposes
RUN echo "MongoDB URI: ${MONGODB_CONNECTION_URI}"
RUN echo "DB Name: ${DB_NAME}"
RUN echo "Collection Name: ${COLLECTION_NAME}"
RUN echo "Port: ${PORT}"

EXPOSE 8001

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001"]
