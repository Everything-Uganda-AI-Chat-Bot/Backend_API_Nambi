import os
import google.generativeai as genai

MODEL_NAME = "models/gemini-1.5-flash"

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:Reigns@localhost:5432/nambi_db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
