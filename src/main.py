from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import numpy as np
from typing import Union
import os
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env
load_dotenv()

app = FastAPI()

# Define the request model
class PredictRequest(BaseModel):
    Pregnancies: int
    Glucose: int
    BloodPressure: int
    SkinThickness: int
    Insulin: int
    BMI: float
    DiabetesPedigreeFunction: float
    Age: int

# Load the diabetes model
try:
    current_dir = os.path.dirname(__file__)
    model_path = os.path.join(current_dir, 'models/model.pkl')
    diabetes_model = joblib.load(model_path)
    logger.info("Loaded diabetes model successfully.")
except FileNotFoundError:
    raise HTTPException(status_code=500, detail="Model file not found.")
except Exception as e:
    raise HTTPException(status_code=500, detail=f"Failed to load model: {e}")

# Load the scaler if it was saved separately
try:
    scaler_path = os.path.join(current_dir, 'models/scaler.pkl')
    scaler = joblib.load(scaler_path)
    logger.info("Loaded scaler successfully.")
except FileNotFoundError:
    raise HTTPException(status_code=500, detail="Scaler file not found.")
except Exception as e:
    raise HTTPException(status_code=500, detail=f"Failed to load scaler: {e}")

# Connect to MongoDB on startup
@app.on_event("startup")
def startup_db_client():
    try:
        logger.info("Connecting to MongoDB...")
        mongodb_uri = os.environ.get("MONGODB_CONNECTION_URI")
        db_name = os.environ.get("DB_NAME")
        collection_name = os.environ.get("COLLECTION_NAME")

        logger.info(f"MongoDB URI: {mongodb_uri}")
        logger.info(f"DB Name: {db_name}")
        logger.info(f"Collection Name: {collection_name}")

        app.mongodb_client = MongoClient(mongodb_uri)
        app.database = app.mongodb_client[db_name]
        app.collection = app.database[collection_name]
        logger.info("Connected to MongoDB successfully!")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise e

# Close MongoDB connection on shutdown
@app.on_event("shutdown")
def shutdown_db_client():
    try:
        app.mongodb_client.close()
        logger.info("Closed MongoDB connection.")
    except Exception as e:
        logger.error(f"Failed to close MongoDB connection: {e}")

@app.post('/diabetes_prediction')
def diabetes_prediction(request: PredictRequest):
    try:
        # Convert input data to a numpy array
        input_data = np.array([
            request.Pregnancies,
            request.Glucose,
            request.BloodPressure,
            request.SkinThickness,
            request.Insulin,
            request.BMI,
            request.DiabetesPedigreeFunction,
            request.Age
        ]).reshape(1, -1)

        # Standardize the input data using the saved scaler
        standardized_data = scaler.transform(input_data)

        # Make prediction using the loaded model
        prediction = diabetes_model.predict(standardized_data)

        # Interpret the prediction
        if prediction[0] == 0:
            return {'prediction': 'The person is not diabetic'}
        else:
            return {'prediction': 'The person is diabetic'}
    except Exception as e:
        logger.error(f"Failed to make prediction: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to make prediction: {e}")

@app.get("/")
def read_root():
    return {"Welcome to the Diabetes Prediction API"}

@app.get("/data")
def read_data():
    try:
        data = list(app.collection.find())
        # Convert ObjectId to string for JSON serialization
        for item in data:
            item['_id'] = str(item['_id'])
        return data
    except Exception as e:
        logger.error(f"Failed to retrieve data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve data: {e}")
