from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import numpy as np
import os
from pymongo import MongoClient

# Create logger
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Define MongoDB connection
mongodb_uri = os.environ.get("MONGODB_CONNECTION_URI")
db_name = os.environ.get("DB_NAME")
collection_name = os.environ.get("COLLECTION_NAME")

# Load model and scaler from files
try:
    model_path = os.path.join(os.path.dirname(__file__), "models/model.pkl")
    scaler_path = os.path.join(os.path.dirname(__file__), "models/scaler.pkl")

    logger.info(f"Loading model from: {model_path}")
    diabetes_model = joblib.load(model_path)
    logger.info(f"Loading scaler from: {scaler_path}")
    scaler = joblib.load(scaler_path)
    logger.info("Model and scaler loaded successfully.")

except Exception as e:
    logger.error(f"Error loading model or scaler: {e}")
    raise HTTPException(status_code=500, detail="Failed to load model or scaler.")

# Initialize FastAPI app
app = FastAPI()

# MongoDB Connection
try:
    client = MongoClient(mongodb_uri)
    db = client[db_name]
    collection = db[collection_name]
    logger.info("Connected to MongoDB")

except Exception as e:
    logger.error(f"MongoDB connection error: {e}")
    raise HTTPException(status_code=500, detail="Failed to connect to MongoDB.")

# Define request model
class PredictRequest(BaseModel):
    Pregnancies: int
    Glucose: int
    BloodPressure: int
    SkinThickness: int
    Insulin: int
    BMI: float
    DiabetesPedigreeFunction: float
    Age: int

# Define API endpoints
@app.get("/")
async def read_root():
    return {"message": "Welcome to the Diabetes Prediction API"}

@app.post("/diabetes_prediction")
async def diabetes_prediction(request: PredictRequest):
    try:
        input_data = np.array([request.Pregnancies, request.Glucose, request.BloodPressure,
                                request.SkinThickness, request.Insulin, request.BMI,
                                request.DiabetesPedigreeFunction, request.Age]).reshape(1, -1)

        standardized_data = scaler.transform(input_data)
        prediction = diabetes_model.predict(standardized_data)

        if prediction[0] == 0:
            result = "The person is not diabetic."
        else:
            result = "The person is diabetic."

        return {"prediction": result}

    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail="Prediction failed.")

