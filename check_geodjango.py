#!/usr/bin/env python3
import os
import sys
import django
from django.contrib.gis.geos import Point
from geopy.geocoders import Nominatim

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'viciniti.settings')
django.setup()

# Import models
from main_app.models import User, Appointment, ServiceProvider
from main_app.utils.geo_utils import geocode_address, create_point_from_coords

def test_geocoding():
    """Test the geocoding functionality"""
    print("Testing geocoding functionality...")
    
    # Test address
    address = "1600 Amphitheatre Parkway, Mountain View, CA 94043, USA"
    print(f"Geocoding address: {address}")
    
    # Initialize the geolocator
    geolocator = Nominatim(user_agent="viciniti-test")
    location = geolocator.geocode(address)
    
    if location:
        print(f"Found coordinates: {location.latitude}, {location.longitude}")
        
        # Create a point
        point = Point(location.longitude, location.latitude, srid=4326)
        print(f"Created point: {point}")
        
        return True
    else:
        print("Geocoding failed.")
        return False

def test_database():
    """Test database connection and models"""
    print("\nTesting database connection...")
    
    # Check if we can query users
    user_count = User.objects.count()
    print(f"Found {user_count} users in the database")
    
    # Check if we can access the location field
    if user_count > 0:
        user = User.objects.first()
        print(f"First user: {user.username}")
        print(f"Location field: {user.location}")
    
    return True

def main():
    """Main test function"""
    print("GeoDjango test script")
    print("="*40)
    
    geocoding_ok = test_geocoding()
    db_ok = test_database()
    
    if geocoding_ok and db_ok:
        print("\nAll tests passed successfully!")
        return 0
    else:
        print("\nSome tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 