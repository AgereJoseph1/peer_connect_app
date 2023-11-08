# Import necessary modules and classes
from app.models import Event, Group
from werkzeug.exceptions import NotFound
from app import db
from datetime import datetime

# Define an EventController class to handle event-related actions
class EventController:

    @staticmethod
    def parse_time(time_str):
        try:
            # Split the time string into hour and minute
            hour, minute = time_str.split(':')

            # Extract the meridiem (AM or PM) from the end of the string
            meridiem = time_str[-2:]

            # Create a datetime object with the specified format and return it
            dt_obj = datetime.strptime(f"{hour}:{minute}", "%H:%M")
            return dt_obj.time()
        except ValueError:
            raise ValueError(f"Invalid time string: {time_str}")

    def parse_date(date_str):
        """Converts a date string to a datetime.date object."""
        return datetime.strptime(date_str, '%Y-%m-%d').date()

    @staticmethod
    def create_event(activity_type,group_id,duration,date,time):
        """Creates a new event and adds it to the database."""
        # Check if the group exists in the database
        group = Group.query.get(group_id)
        if group is None:
            raise NotFound("Group not found.")

        # Parse the date string to a date object
        date = EventController.parse_date(date)
        time =EventController.parse_time(time)

        # Create a new Event instance with the provided details
        event = Event(
            activity_type=activity_type,
            group_id=group_id,
            duration=duration,
            date=date,
            time=time

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

   
