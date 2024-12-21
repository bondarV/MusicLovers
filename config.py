import os
import urllib
from dotenv import load_dotenv

base_dir = os.path.abspath(os.path.dirname(__file__))

load_dotenv(os.path.join(base_dir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess-what'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(base_dir, 'app.db')