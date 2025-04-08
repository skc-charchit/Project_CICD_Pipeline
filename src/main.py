from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import numpy as np
from typing import Union
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env

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
    diabetes_model = joblib.load(open(model_path, 'rb'))
except FileNotFoundError:
    raise HTTPException(status_code=500, detail="Model file not found.")
except Exception as e:
    raise HTTPException(status_code=500, detail=f"Failed to load model: {e}")

# Load the scaler if it was saved separately
try:
    scaler_path = os.path.join(current_dir, 'models/scaler.pkl')
    scaler = joblib.load(open(scaler_path, 'rb'))
except FileNotFoundError:
    raise HTTPException(status_code=500, detail="Scaler file not found.")
except Exception as e:
    raise HTTPException(status_code=500, detail=f"Failed to load scaler: {e}")

# Connect to MongoDB on startup
@app.on_event("startup")
def startup_db_client():
    app.mongodb_client = MongoClient(os.getenv("MONGODB_CONNECTION_URI"), server_api='1')
    app.database = app.mongodb_client[os.getenv("DB_NAME")]
    app.collection = app.database[os.getenv("COLLECTION_NAME")]
    print("Connected to the MongoDB database!")

# Close MongoDB connection on shutdown
@app.on_event("shutdown")
def shutdown_db_client():
    app.mongodb_client.close()

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
        raise HTTPException(status_code=500, detail=f"Failed to make prediction: {e}")

@app.get("/")
def read_root():
    return {"Welcome to the diabetes prediction API"}

@app.get("/data")
async def read_data():
    data = app.collection.find()
    return list(data)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
