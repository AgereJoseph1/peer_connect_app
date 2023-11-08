from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()  # Create the Mail instance

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)  # Initialize Flask-Mail with your app

    with app.app_context():
        # Import models and create database tables if necessary
        from . import models

        # Import and register blueprints
        from .routes import app as main_blueprint
        app.register_blueprint(main_blueprint)

    return app