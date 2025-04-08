from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import pandas as pd
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Print environment variable to verify it's loaded correctly
print("MONGODB_CONNECTION_URI:", os.getenv("MONGODB_CONNECTION_URI"))

# Connect to MongoDB using the connection string from .env
uri = os.getenv("MONGODB_CONNECTION_URI")
server_api = ServerApi('1')
client = MongoClient(uri, server_api=server_api)

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# Load data from CSV
df = pd.read_csv("preprocessed_data.csv")
print(df.head())
print(df["Outcome"].value_counts())

# Convert DataFrame to a list of dictionaries
list_of_dict = df.to_dict(orient="records")

# Access the database and collection
db = client[os.getenv("DB_NAME")]
print(db.list_collection_names())

# Create a collection if it doesn't exist
collection_name = os.getenv("COLLECTION_NAME")
if collection_name not in db.list_collection_names():
    collection = db.create_collection(collection_name)
else:
    collection = db[collection_name]

# Insert data into the collection
collection.insert_many(list_of_dict)

# Close the client when done
client.close()
