import streamlit as st
from pymongo import MongoClient
import json
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import os
from dotenv import load_dotenv

load_dotenv()

mongodb_uri = os.getenv("MONGODB_CONNECTION_URI")
db_name = os.getenv("DB_NAME")
collection_name = os.getenv("COLLECTION_NAME")

client = MongoClient(mongodb_uri)
db = client[db_name]
collection = db[collection_name]

# Use the correct import and initialize ChatOpenAI
llm = ChatOpenAI(model="gpt-4", temperature=0)

st.title("Talk to MongoDB - Diabetes Dataset")
user_question = st.text_area("Enter your question here:")

prompt_template_text = """
You are an AI assistant that converts natural language questions into MongoDB aggregation pipeline queries.
Only return the JSON array representing the aggregation pipeline, nothing else.

MongoDB fields:
- Pregnancies, Glucose, BloodPressure, SkinThickness, Insulin, BMI, DiabetesPedigreeFunction, Age, Outcome

Sample:
Question: Find all patients with glucose > 150
Output:
[
  {"$match": {"Glucose": {"$gt": 150}}}
]

Question: {question}
Output:
"""

query_with_prompt = PromptTemplate(
    template=prompt_template_text,
    input_variables=["question"]
)

llmchain = LLMChain(llm=llm, prompt=query_with_prompt, verbose=True)

if user_question:
    if st.button("Submit"):
        with st.spinner("Generating MongoDB query..."):
            try:
                response = llmchain.invoke({"question": user_question})
                query_text = response["text"].strip()
                st.text_area("Raw LLM output:", query_text, height=150)

                # Attempt to parse JSON
                mongo_query = json.loads(query_text)

                st.subheader("Generated MongoDB Aggregation Pipeline Query")
                st.json(mongo_query)

                results = collection.aggregate(mongo_query)

                st.subheader("Query Results")
                count = 0
                for result in results:
                    st.write(result)
                    count += 1
                    if count >= 20:
                        st.info("Showing first 20 results only.")
                        break

                if count == 0:
                    st.info("No results found for the query.")

            except json.JSONDecodeError as e:
                st.error(f"Failed to parse JSON from LLM output: {e}")
            except Exception as e:
                st.error(f"Error during prediction or query execution: {e}")
