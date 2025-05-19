from geopy.geocoders import Nominatim
from django.contrib.gis.geos import Point
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def geocode_address(address_line1, city, state, zip_code, country="USA"):
    """
    Geocode an address to latitude and longitude using Nominatim.
    Returns a tuple of (latitude, longitude) or None if geocoding fails.
    """
    if not (address_line1 and city and state):
        logger.warning("Incomplete address provided for geocoding")
        return None
    
    # Format the complete address
    full_address = f"{address_line1}, {city}, {state} {zip_code}, {country}"
    logger.info(f"Geocoding address: {full_address}")
    print(f"DEBUG GEO_UTILS: Attempting to geocode: {full_address}")
    
    # Maximum retries for geocoding
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # Initialize the geolocator with user agent
            geolocator = Nominatim(user_agent="viciniti-address-geocoder")
            
            # Get location information
            location = geolocator.geocode(full_address, timeout=10)
            
            if location:
                logger.info(f"Geocoded address to: {location.latitude}, {location.longitude}")
                print(f"DEBUG GEO_UTILS: Successfully geocoded to: {location.latitude}, {location.longitude}")
                return (location.latitude, location.longitude)
            else:
                # Try alternative formatting if the initial geocoding fails
                if retry_count == 0:
                    # Try without zip code
                    full_address = f"{address_line1}, {city}, {state}, {country}"
                    logger.warning(f"Failed to geocode with zip code. Trying without: {full_address}")
                    print(f"DEBUG GEO_UTILS: Retrying without zip code: {full_address}")
                elif retry_count == 1:
                    # Try with just city and state (for major landmarks)
                    full_address = f"{address_line1}, {city}, {state}"
                    logger.warning(f"Failed again. Trying simplified address: {full_address}")
                    print(f"DEBUG GEO_UTILS: Retrying with simplified address: {full_address}")
                
                retry_count += 1
                
                if retry_count >= max_retries:
                    logger.warning(f"Failed to geocode address after {max_retries} attempts: {full_address}")
                    print(f"DEBUG GEO_UTILS: Failed to geocode after {max_retries} attempts")
                    return None
        except Exception as e:
            logger.error(f"Error geocoding address: {str(e)}")
            print(f"DEBUG GEO_UTILS: Error during geocoding: {str(e)}")
            retry_count += 1
            
            if retry_count >= max_retries:
                return None
    
    return None

def create_point_from_coords(latitude, longitude):
    """
    Create a GEOS Point object from latitude and longitude coordinates.
    """
    if latitude is None or longitude is None:
        return None
    
    try:
        # SRID 4326 refers to WGS84, the standard GPS coordinate system
        return Point(longitude, latitude, srid=4326)
    except Exception as e:
        logger.error(f"Error creating point: {str(e)}")
        return None

def get_location_from_address(address_components):
    """
    Helper function to create a Point object from address components.
    
    Args:
        address_components: dict containing address_line1, city, state, zip_code, etc.
    
    Returns:
        A Point object or None if geocoding fails
    """
    # Extract address components
    address_line1 = address_components.get('address_line1', '')
    city = address_components.get('city', '')
    state = address_components.get('state', '')
    zip_code = address_components.get('zip_code', '')
    country = address_components.get('country', 'USA')
    
    # Try to geocode the address
    coords = geocode_address(address_line1, city, state, zip_code, country)
    
    if coords:
        return create_point_from_coords(*coords)
    
    return None

def distance_between_points(point1, point2):
    """
    Calculate the distance between two points in meters.
    """
    if not point1 or not point2:
        return None
    
    try:
        # Make sure both points have the same SRID
        if point1.srid != point2.srid:
            point2.transform(point1.srid)
        
        # Calculate the distance in meters
        return point1.distance(point2) * 100000  # Approximate conversion to meters
    except Exception as e:
        logger.error(f"Error calculating distance: {str(e)}")
        return None 