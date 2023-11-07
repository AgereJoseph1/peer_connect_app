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
    def create_event(group_id, activity_type, start_time, end_time, location_name=None, location_address=None):
        """Creates a new event and adds it to the database."""
        # Check if the group exists in the database
        group = Group.query.get(group_id)
        if group is None:
            raise NotFound("Group not found.")

        # Parse and validate start_time and end_time
        start_time = EventController.parse_date(start_time)
        end_time = EventController.parse_date(end_time)

        # Create a new Event instance with the provided details
        event = Event(
            group_id=group_id,
            activity_type=activity_type,
            start_time=start_time,
            end_time=end_time,
            location_name=location_name,
            location_address=location_address
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

    @staticmethod
    def check_event_overlap(group_id, start_time, end_time):
        """Checks for overlapping events within the same group and time range."""
        # Parse and validate start_time and end_time
        start_time = EventController.parse_date(start_time)
        end_time = EventController.parse_date(end_time)

        # Find overlapping events
        overlapping_events = Event.query.filter(
            Event.group_id == group_id,
            Event.end_time > start_time,
            Event.start_time < end_time
        ).all()

        return bool(overlapping_events)
