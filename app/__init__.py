from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)

    with app.app_context():
        # Import models and create database tables
        from . import models
        db.create_all()

        # Import and register blueprints
        from .routes import app as main_blueprint
        app.register_blueprint(main_blueprint)

    return app
