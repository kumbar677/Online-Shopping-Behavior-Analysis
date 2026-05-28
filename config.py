import os
from dotenv import load_dotenv

load_dotenv(override=True)

class Config:
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
    MONGO_DB = os.environ.get('MONGO_DB', 'shopping_analysis')
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-secret-key-123')
