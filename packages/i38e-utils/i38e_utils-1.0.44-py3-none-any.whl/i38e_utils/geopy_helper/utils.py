from .geolocation_service import GeolocationService, GeocoderTimedOut, GeocoderServiceError

# Initialize the geolocator once
geolocator = None


def get_geolocator():
    global geolocator
    if geolocator is None:
        geolocator = GeolocationService(debug=True)
    return geolocator

def get_address_by_coordinates(latitude, longitude, exactly_one=True):
    geolocator = get_geolocator()
    try:
        location = geolocator.reverse((latitude, longitude), exactly_one=exactly_one)
        if not location:
            return "No address found for this location."
        address = location.address
        return address
    except GeocoderTimedOut:
        return "GeocoderTimedOut: Failed to reach the server."


def get_coordinates_for_address(address):
    """
    Geocode an address using a custom Nominatim server.

    :param address: The address to geocode.
    :return: A dictionary with the location's latitude, longitude, and full address, or a message if an error occurs.
    """
    geolocator = get_geolocator()
    try:
        location = geolocator.geocode(address)

        # Check if location was found
        if location:
            return {
                "Address": location.address,
                "Latitude": location.latitude,
                "Longitude": location.longitude
            }
        else:
            return "Location not found."

    except GeocoderTimedOut:
        return "GeocoderTimedOut: Request timed out."
    except GeocoderServiceError as e:
        return f"GeocoderServiceError: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"
