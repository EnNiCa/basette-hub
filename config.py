import os
from dotenv import load_dotenv

load_dotenv() # busca el archivo .env y carga sus variables

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    
    DB_CONFIG ={
        'host': os.environ.get('DB_HOST'),
        'user': os.environ.get('DB_USER'),
        'password':os.environ.get('DB_PASSWORD'),
        'database':os.environ.get('DB_NAME')
    }