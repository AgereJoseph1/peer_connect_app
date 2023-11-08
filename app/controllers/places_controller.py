activity_type_mapping = {
    'social': ['restaurant', 'cafe', 'bar'],
    'out_adv': ['park', 'campground', 'zoo'],
    'cul_edu': ['museum', 'art_gallery', 'library'],
    'ent_lei': ['movie_theater', 'amusement_park', 'bowling_alley'],
    'cor_pro': ['conference_center', 'coworking_space'],
}

# Get the nearby places for a given activity type
def get_nearby_places(central_location, activity_type_mapping, activity_type, gmaps):
    activity_types = activity_type_mapping.get(activity_type.lower(), ['restaurant'])  # Default to 'restaurant'
    all_places = []
    for place_type in activity_types:
        # API call for each place type
        places_result = gmaps.places_nearby(location=central_location, radius=5000, type=place_type)
        all_places.extend(places_result.get('results', []))
        # Check and handle pagination if necessary (not shown here)
    
    # Remove duplicate places by place_id
    unique_places = {place['place_id']: place for place in all_places}.values()
    return list(unique_places)[:10] # Return only the first 10 places

def filter_places(all_places, preferences):
    # Mappings for preferences to Google Places types
    preference_mapping = {
        'quiet': 'library',
        'lively': 'night_club',
        'cozy': 'cafe',
    }

    # Flatten the list of all preference-related types
    preferred_types = set()
    for category, prefs in preferences.items():
        for pref in prefs:
            google_type = preference_mapping.get(pref.lower())
            if google_type:
                preferred_types.add(google_type)

    # Filter places that match the preferred types
    filtered_places_list = [
        place for place in all_places
        if any(ptype in place.get('types', []) for ptype in preferred_types)
    ]

    # Return the filtered list of places
    return filtered_places_list
