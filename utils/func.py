import math
import requests
from flask import current_app as app
import googlemaps
from googlemaps.exceptions import ApiError



def allowed_file(filename):
    # Ensure that the file has a valid extension
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}


def parse_lat_long(lat_long_str):
    """
    Splits a string containing latitude and longitude separated by a comma.

    Parameters:
    - lat_long_str: A string with the format "latitude,longitude".

    Returns:
    - A tuple containing (latitude, longitude) as floats.

    Raises:
    - ValueError: If the input string is not properly formatted or values cannot be converted to floats.
    """
    try:
        lat_str, long_str = lat_long_str.split(',')
        latitude = float(lat_str.strip())
        longitude = float(long_str.strip())
        return latitude, longitude
    except ValueError as e:
        raise ValueError("Invalid input for latitude and longitude. Please use the format 'lat, long'") from e


