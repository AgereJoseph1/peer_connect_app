from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Assuming you have a 'Config' class in 'config.py' that holds configurations
    app.config.from_object('config.Config')

    db.init_app(app)

    # ...
    with app.app_context():
        from . import models
        print("Creating database tables...")
        db.create_all()
        print("Database tables created.")
# ...

    return app
