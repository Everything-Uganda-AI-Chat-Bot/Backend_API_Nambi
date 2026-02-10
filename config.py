import os

# MODEL_NAME = "gemini-2.0-flash"

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:Reigns@localhost:5432/nambi_db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
