# Import necessary modules and classes
from app.models import Group, GroupMember, InviteToken, User
from werkzeug.exceptions import BadRequest, NotFound
from app import db
from werkzeug.utils import secure_filename
import os
from flask import current_app as app
from utils.func import allowed_file
from flask_mail import Message
from app import mail

# Define a GroupController class to handle group-related actions
class GroupController:

    # Static method to create a new group
    @staticmethod
    def create_group(name, user_id, description, banner=None):
        # Check if the user exists in the database
        user = User.query.get(user_id)
        if user is None:
            raise NotFound("User not found.")

        # Create a new Group instance with the provided name and description
        group = Group(name=name, description=description)

        # If a banner image is provided and it's a valid file type
        if banner and allowed_file(banner.filename):
            # Secure the filename and create a path where the banner will be saved
            filename = secure_filename(banner.filename)
            # Use the BANNER_UPLOAD_FOLDER defined in the app's configuration
            banner_path = os.path.join(app.config['BANNER_UPLOAD_FOLDER'], filename)
            # Ensure the BANNER_UPLOAD_FOLDER exists
            if not os.path.exists(app.config['BANNER_UPLOAD_FOLDER']):
                os.makedirs(app.config['BANNER_UPLOAD_FOLDER'])
            # Save the banner to the specified path
            banner.save(banner_path)
            # Assign the saved banner's path to the group's banner_image attribute
            group.banner_image = banner_path
        elif banner:
            raise BadRequest("File type not allowed.")
        # If no banner is provided, leave the group.banner_image as None
        # This could also be set to an empty string if that works better with your application logic
        # group.banner_image = None

        # Add the new group to the database session and commit to save changes
        db.session.add(group)
        db.session.commit()

        # Automatically add the creator (user) as a member of the group
        member = GroupMember(user_id=user_id, group_id=group.id)
        db.session.add(member)
        db.session.commit()

        # Return the newly created group object
        return group

    # ... rest of the methods from your GroupController class ...

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
    
    @staticmethod
    def get_group_members(group_id):
        # Retrieve the group from the database
        group = Group.query.get(group_id)
        if group is None:
            raise NotFound("Group not found.")
        
        # Query the GroupMember model for all members of the group
        group_members = GroupMember.query.filter_by(group_id=group_id).all()
        if not group_members:
            raise NotFound("No members found for the group.")
        
        # Extract user information from the group members
        members_info = [{'user_id': member.user_id, 'username': member.user.username, 'email': member.user.email} for member in group_members]
        
        # Return the list of members' information
        return members_info

    # Static method to get all members of a group
    @staticmethod
    def get_user_groups(user_id):
        # Check if the user exists in the database
        user = User.query.get(user_id)
        if user is None:
            raise NotFound("User not found.")

        # Get all the groups where the user is a member
        user_groups = Group.query.join(GroupMember).filter(GroupMember.user_id == user_id).all()

        return user_groups

    # Static method to get all members of a group
    @staticmethod
    def get_group_details(group_id):
        """
        Retrieves the details of a specific group from the database.

        Parameters:
        - group_id: The ID of the group to retrieve.

        Returns:
        - The group object with the specified ID.

        Raises:
        - NotFound: The group does not exist.
        """
        group = Group.query.get(group_id)
        if group is None:
            raise NotFound("Group not found.")

        return group


    # Static method to get all members location
    @staticmethod
    def get_group_member_locations(group_id):
        """
        Retrieves the locations (latitude and longitude) of all members of a group.

        Parameters:
        - group_id: The ID of the group.

        Returns:
        - A list of tuples, each containing the latitude and longitude of group members.

        Raises:
        - NotFound: If the group does not exist.
        """
        group = Group.query.get(group_id)
        if not group:
            raise NotFound("Group not found.")

        member_locations = []
        for group_member in group.members:
            user = group_member.user
            if user.latitude is not None and user.longitude is not None:
                member_locations.append({
                    'latitude': user.latitude,
                    'longitude': user.longitude
                })

        if not member_locations:
            raise NotFound("No member locations available for this group.")

        return member_locations
    

    @staticmethod
    def get_group_member_preferences(group_id):
        """
        Retrieves distinct lists of all preferences (ambiances, cuisines, dietary restrictions, 
        and budget preferences) of all members of a group.

        Parameters:
        - group_id: The ID of the group.

        Returns:
        - A dictionary containing lists of distinct preferences for all group members.

        Raises:
        - NotFound: If the group does not exist or has no members.
        """
        group = Group.query.get(group_id)
        if not group:
            raise NotFound("Group not found.")

        # Initialize sets to store unique preferences
        all_ambiances = set()
        all_cuisines = set()
        all_dietary_restrictions = set()
        all_budget_preferences = set()

        for group_member in group.members:
            user = group_member.user
            all_ambiances.update(ambiance.name for ambiance in user.ambiances)
            all_cuisines.update(cuisine.name for cuisine in user.cuisines)
            all_dietary_restrictions.update(dietary.name for dietary in user.dietary_restrictions)
            all_budget_preferences.update(budget.name for budget in user.budget_preferences)

        # Convert sets to lists to return them
        return {
            'ambiances': list(all_ambiances),
            'cuisines': list(all_cuisines),
            'dietary_restrictions': list(all_dietary_restrictions),
            'budget_preferences': list(all_budget_preferences)
        }


    @staticmethod
    def send_meeting_email(group_id, meeting_details):
        """
        Sends an email notification to all members of the group about a scheduled meeting.

        Parameters:
        - group_id: The ID of the group.
        - meeting_details: A dictionary with details of the meeting like subject, time, date, location.

        Raises:
        - NotFound: If the group does not exist.
        """
        group = Group.query.get(group_id)
        if not group:
            raise NotFound("Group not found.")

        members = GroupMember.query.filter_by(group_id=group_id).all()
        if not members:
            raise NotFound("No members found for the group.")

        subject = f"Peer Connect - Let's Meet Up!"
        body = f"""
        Hello Team,

        A member has requested a meeetup. The perfect spot has been found! 
        Here are the details:
        Activity: {meeting_details['activity']}
        Time: {meeting_details['time']}
        Date: {meeting_details['date']}
        Location: {meeting_details['location']}

        Please mark this in your calendars.

        Warm Regards,
        ----------------------------------------
        Peer Connect Team
        """
        
        with app.app_context():
            for member in members:
                user = User.query.get(member.user_id)
                if user and user.email:
                    msg = Message(subject,
                                  recipients=[user.email],
                                  body=body)
                    mail.send(msg)
                    
        return "Meeting notification sent to all group members."


    
    

