# Import necessary modules and classes
from models import Group, GroupMember, InviteToken, User
from werkzeug.exceptions import BadRequest, NotFound
from app import db
from werkzeug.utils import secure_filename
import os
from utils.func import allowed_file

# Define a GroupController class to handle group-related actions
class GroupController:

    # Static method to create a new group
    @staticmethod
    def create_group(name, user_id, distribution, banner=None):
        # Check if the user exists in the database
        user = User.query.get(user_id)
        if user is None:
            raise NotFound("User not found.")

        # Create a new Group instance with the provided name and distribution
        group = Group(name=name, distribution=distribution)

        # If a banner image is provided and it's a valid file type
        if banner and allowed_file(banner.filename):
            # Secure the filename and create a path where the banner will be saved
            filename = secure_filename(banner.filename)
            banner_path = os.path.join('path/to/banner_images', filename)
            # Save the banner to the specified path
            banner.save(banner_path)
            # Assign the saved banner's path to the group's banner_image attribute
            group.banner_image = banner_path
        else:
            # If no banner is provided or the file is not allowed, use a default image
            group.banner_image = 'default_banner.png'

        # Add the new group to the database session and commit to save changes
        db.session.add(group)
        db.session.commit()

        # Automatically add the creator (user) as a member of the group
        member = GroupMember(user_id=user_id, group_id=group.id)
        db.session.add(member)
        db.session.commit()

        # Return the newly created group object
        return group

    # Static method to generate an invitation link for a group
    @staticmethod
    def generate_invite_link(group_id):
        # Retrieve the group from the database
        group = Group.query.get(group_id)
        if group is None:
            raise NotFound("Group not found.")

        # Create a new InviteToken instance for the group
        invite_token = InviteToken(group_id=group_id)
        # Add the invite token to the database session and commit to save
        db.session.add(invite_token)
        db.session.commit()
        # Return the token
        return invite_token.token

    # Static method for a user to join a group using an invitation link
    @staticmethod
    def join_group_via_invite(token, user_id):
        # Find the invite token in the database
        invite_token = InviteToken.query.filter_by(token=token).first()
        # If the token is invalid or expired, raise an exception
        if not invite_token or not invite_token.is_valid():
            raise BadRequest("Invalid or expired invite token.")

        # Check if the user is already a member of the group
        if GroupMember.query.filter_by(group_id=invite_token.group_id, user_id=user_id).first():
            raise BadRequest("User already a member of the group.")

        # If not, create a new GroupMember instance for the user to join the group
        new_member = GroupMember(group_id=invite_token.group_id, user_id=user_id)
        # Add the new member to the database session and commit to save
        db.session.add(new_member)
        db.session.commit()
        # Return the new member object
        return new_member