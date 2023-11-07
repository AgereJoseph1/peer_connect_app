import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # SQLite database file will be located at the project's root directory
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'peer_connect.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'your-secret-key'  # Used to add additional security for Flask sessions
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    BANNER_UPLOAD_FOLDER = os.path.join(basedir, 'banner_uploads')
BASE_URL = 'http://localhost:5000'  # Base URL for the application