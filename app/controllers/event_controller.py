# Import necessary modules and classes
from app.models import Event, Group
from werkzeug.exceptions import NotFound
from app import db
from datetime import datetime

# Define an EventController class to handle event-related actions
class EventController:

    @staticmethod
    def parse_date(date_string):
        """Helper method to parse date strings into datetime objects. Includes basic validation."""
        try:
            return datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            raise ValueError("Date format must be YYYY-MM-DD HH:MM:SS")

    @staticmethod
    def create_event(group_id, activity_type,date,duration):
        """Creates a new event and adds it to the database."""
        # Check if the group exists in the database
        group = Group.query.get(group_id)
        if group is None:
            raise NotFound("Group not found.")

        # Parse and validate start_time and end_time
        time = EventController.parse_date(date)
        print('Time' + time)
        print('Date' + date)

        # Create a new Event instance with the provided details
        event = Event(
            group_id=group_id,
            activity_type=activity_type,
            date=date ,
            duration=duration
            
        )

        # Add the new event to the database session and commit to save changes
        db.session.add(event)
        db.session.commit()

        return event

    @staticmethod
    def update_event(event_id, **kwargs):
        """Updates an existing event with the given keyword arguments."""
        # Retrieve the event from the database
        event = Event.query.get(event_id)
        if event is None:
            raise NotFound("Event not found.")

        # Update event attributes with provided keyword arguments
        for key, value in kwargs.items():
            if hasattr(event, key):
                # Special handling for date fields
                if key in ['start_time', 'end_time']:
                    value = EventController.parse_date(value)
                setattr(event, key, value)

        # Commit the changes to the database
        db.session.commit()

        return event

    @staticmethod
    def delete_event(event_id):
        """Deletes an event from the database."""
        # Find the event in the database
        event = Event.query.get(event_id)
        if event is None:
            raise NotFound("Event not found.")

        # Delete the event from the database
        db.session.delete(event)
        db.session.commit()

    @staticmethod
    def get_events_by_group(group_id):
        """Retrieves all events for a specific group."""
        # Check if the group exists
        group = Group.query.get(group_id)
        if group is None:
            raise NotFound("Group not found.")

        return Event.query.filter_by(group_id=group_id).all()

    @staticmethod
    def get_event(event_id):
        """Retrieves a single event by its ID."""
        event = Event.query.get(event_id)
        if event is None:
            raise NotFound("Event not found.")
        return event

   
