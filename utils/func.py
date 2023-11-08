import math
import requests
from flask import current_app as app
import googlemaps
from googlemaps.exceptions import ApiError

def find_geographical_center(locations):
    """
    Calculate the geographical center (centroid) for a set of geolocations.

    :param locations: List of tuples containing latitude and longitude
    :return: Tuple containing the latitude and longitude of the center
    """
    if not locations:
        raise ValueError("No locations provided")

    x_total, y_total, z_total = 0, 0, 0
    
    for lat, lon in locations:
        lat_rad = math.radians(lat)
        lon_rad = math.radians(lon)
        
        x_total += math.cos(lat_rad) * math.cos(lon_rad)
        y_total += math.cos(lat_rad) * math.sin(lon_rad)
        z_total += math.sin(lat_rad)

    num_locations = len(locations)
    x_avg, y_avg, z_avg = x_total / num_locations, y_total / num_locations, z_total / num_locations

    central_lon = math.atan2(y_avg, x_avg)
    hyp = math.sqrt(x_avg ** 2 + y_avg ** 2)
    central_lat = math.atan2(z_avg, hyp)

    return math.degrees(central_lat), math.degrees(central_lon)



def find_meeting_place_with_photo(api_key, location, place_type="restaurant"):
    """
    Find a meeting place of a specified type near a given geographical center and retrieve a photo.

    :param api_key: Google Maps API key
    :param location: Tuple containing the latitude and longitude of the center
    :param place_type: Type of place to search for
    :return: Dictionary containing name, location, and photo URL of the top place, or None if no place found
    """
    try:
        gmaps = googlemaps.Client(key=api_key)
        places_result = gmaps.places_nearby(location=location, type=place_type, rank_by='distance')

        if places_result['results']:
            top_place = places_result['results'][0]
            place_info = {
                'name': top_place['name'],
                'location': top_place['geometry']['location'],
            }
            
            # Check if the place has a photo available
            if 'photos' in top_place:
                photo_reference = top_place['photos'][0]['photo_reference']
                photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photo_reference={photo_reference}&key={api_key}"
                place_info['photo_url'] = photo_url
            
            return place_info
        else:
            return None
    except ApiError as e:
        print(f"Error when calling Google Places API: {e}")
        return None

def allowed_file(filename):
    # Ensure that the file has a valid extension
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}


