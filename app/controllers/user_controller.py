import requests
from flask import current_app as app
from app.models import User, db
from utils.func import resolve_location
from werkzeug.security import generate_password_hash
from flask import session
from werkzeug.exceptions import BadRequest, NotFound

class UserController:
    """
    Controller for user-related actions, including profile updates, user creation, 
    retrieval, updates, and authentication handling.
    """

    @staticmethod
    def update_user_profile(user_id, email=None, phone=None, location_name=None):
        """
        Updates the profile information of a specific user.

        Parameters:
        - user_id: The ID of the user to update.
        - email: New email address to update (optional).
        - phone: New phone number to update (optional).
        - location_name: New location name to resolve and update (optional).

        Returns:
        - The updated user object.

        Raises:
        - NotFound: The user does not exist.
        - BadRequest: The email or phone number provided is already in use.

        Note:
        - The location_name, if provided, is resolved to latitude and longitude 
          using an external service and the coordinates are stored.
        - The method commits the changes to the database.
        """
        user = User.query.get(user_id)
        if user is None:
            raise NotFound("User not found.")

        if email:
            if User.query.filter_by(email=email).first():
                raise BadRequest("Email already in use.")
            user.email = email

        if phone:
            if User.query.filter_by(phone=phone).first():
                raise BadRequest("Phone number already in use.")
            user.phone = phone

        if location_name:
            latitude, longitude = resolve_location(location_name)
            user.latitude = latitude
            user.longitude = longitude

        db.session.commit()
        return user

    @staticmethod
    def create_user(username, password):
        """
        Creates a new user with a username and password.

        Parameters:
        - username: The desired username for the new user.
        - password: The password for the new user.

        Returns:
        - The newly created user object.

        Raises:
        - BadRequest: The username is already taken.

        Note:
        - The password is hashed before being stored for security.
        """
        if User.query.filter_by(username=username).first() is not None:
            raise BadRequest("Username already taken.")

        user = User(username=username)
        user.set_password(password)  # Assuming set_password handles hashing
        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.id
        return user

    @staticmethod
    def get_user_by_id(user_id):
        """
        Retrieves a user by their ID.

        Parameters:
        - user_id: The ID of the user to retrieve.

        Returns:
        - The requested user object.

        Raises:
        - NotFound: The user does not exist.
        """
        user = User.query.get(user_id)
        if user is None:
            raise NotFound("User not found.")
        return user

    @staticmethod
    def update_user(user_id, username=None, password=None):
        """
        Updates a user's username and/or password.

        Parameters:
        - user_id: The ID of the user to update.
        - username: The new username (optional).
        - password: The new password (optional).

        Returns:
        - The updated user object.

        Raises:
        - NotFound: The user does not exist.
        - BadRequest: The new username is already taken.

        Note:
        - If a password is provided, it is hashed before storage.
        - Commits the changes to the database.
        """
        user = User.query.get(user_id)
        if user is None:
            raise NotFound("User not found.")

        if username:
            if User.query.filter_by(username=username).first():
                raise BadRequest("Username already taken.")
            user.username = username

        if password:
            user.password_hash = generate_password_hash(password)

        db.session.commit()
        return user

    @staticmethod
    def delete_user(user_id):
        """
        Deletes a user by their ID.

        Parameters:
        - user_id: The ID of the user to delete.

        Raises:
        - NotFound: The user does not exist.

        Note:
        - Commits the change to the database.
        """
        user = User.query.get(user_id)
        if user is None:
            raise NotFound("User not found.")

        db.session.delete(user)
        db.session.commit()

    @staticmethod
    def authenticate(username, password):
        """
        Authenticates a user and initiates a session.

        Parameters:
        - username: The username of the user.
        - password: The password of the user.

        Raises:
        - BadRequest: Invalid username or password.

        Note:
        - The user ID is stored in the session upon successful authentication.
        """
        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(password):
            raise BadRequest("Invalid username or password.")
        
        session['user_id'] = user.id

    @staticmethod
    def logout_user():
        """
        Logs out the current user.

        Note:
        - Removes the user ID from the session.
        """
        session.pop('user_id', None)
