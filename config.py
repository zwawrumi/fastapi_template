import os

from dotenv import load_dotenv

load_dotenv()

DB_CLIENT = os.environ.get('DB_CLIENT')
DB_DRIVER = os.environ.get('DB_DRIVER')
DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASS = os.environ.get('DB_PASS')

SECRET_KEY = os.environ.get('SECRET_KEY')
SECRET_AUTH = os.environ.get('SECRET_AUTH')

PROJECT_ID = os.environ.get('PROJECT_ID')
PRIVATE_KEY = os.environ.get('PRIVATE_KEY')

EMAIL = os.environ.get('EMAIL')
GM_PASS = os.environ.get('GM_PASS')
SECRET_TOKEN = os.environ.get('SECRET_TOKEN')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get('ACCESS_TOKEN_EXPIRE_MINUTES'))
ALGORITHM = str(os.environ.get('ALGORITHM'))
