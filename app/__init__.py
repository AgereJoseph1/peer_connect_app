from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # Import the Migrate class

db = SQLAlchemy()

# Initialize Migrate
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    migrate.init_app(app, db)  # Initialize Flask-Migrate with your app and db

    with app.app_context():
        # Import models and create database tables if necessary
        from . import models

        # Import and register blueprints
        from .routes import app as main_blueprint
        app.register_blueprint(main_blueprint)

    return app
