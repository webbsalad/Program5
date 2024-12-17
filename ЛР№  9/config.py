# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DATABASE_URL = os.getenv('DATABASE_URL')
    SECRET_KEY = os.getenv('SECRET_KEY')
    JWT_ALGORITHM = 'HS256'
    JWT_EXP_DELTA_MINUTES = 60
