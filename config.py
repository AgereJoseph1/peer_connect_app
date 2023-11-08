import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # SQLite database file will be located at the project's root directory
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'peer_connect.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'your-secret-key'  # Used to add additional security for Flask sessions

BASE_URL = 'http://localhost:5000'  # Base URL for the application

API_KEY = 'AIzaSyAJ7BoV6AdTat8DK14e2nFCAqOHTl1asqM'
UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
BANNER_UPLOAD_FOLDER = os.path.join(basedir, 'banner_uploads')
