from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
app = Flask(__name__)

def create_app():
    # Assuming you have a 'Config' class in 'config.py' that holds configurations
    app.config.from_object('config.Config')

    db.init_app(app)

    # Register routes
    from . import routes
    # ...
    with app.app_context():
        from . import models
         
        print("Creating database tables...")
        db.create_all()
        print("Database tables created.")
# ...

    return app


