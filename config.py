import os

basedir = os.path.abspath(os.path.dirname(__file__))

API_KEY = 'AIzaSyAJ7BoV6AdTat8DK14e2nFCAqOHTl1asqM'

BASE_URL = 'http://localhost:5000'  # Base URL for the application

class Config:
    # SQLite database file will be located at the project's root directory
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'peer_connect.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'your-secret-key'  # Used to add additional security for Flask sessions

   


    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    BANNER_UPLOAD_FOLDER = os.path.join(basedir, 'banner_uploads')
    API_KEY = 'AIzaSyAJ7BoV6AdTat8DK14e2nFCAqOHTl1asqM'

    
    MAIL_SERVER = 'smtp.gmail.com'  # Replace with your mail server
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'princemi1976@uds.edu.gh'  # Replace with your email
    MAIL_PASSWORD = '19010225'  # Replace with your password
    MAIL_DEFAULT_SENDER = 'princemi1976@uds.edu.gh'  # Replace with your email

