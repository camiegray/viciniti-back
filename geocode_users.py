#!/usr/bin/env python3
import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'viciniti.settings')
django.setup()

from main_app.models import User
from main_app.utils.geo_utils import get_location_from_address

def geocode_all_users():
    """Geocode all users with address data"""
    print("Starting geocoding for all users...")
    
    # Get all users with address data but no location
    users = User.objects.filter(
        location__isnull=True,
        street_address__isnull=False,
        city__isnull=False,
        state__isnull=False
    ).exclude(
        street_address='',
        city='',
        state=''
    )
    
    print(f"Found {users.count()} users with address data but no geocoded location")
    
    geocoded_count = 0
    error_count = 0
    
    for user in users:
        print(f"Geocoding user {user.id}: {user.username}")
        
        try:
            address_components = {
                'address_line1': user.street_address,
                'city': user.city,
                'state': user.state,
                'zip_code': user.zip_code,
                'country': 'USA'
            }
            
            # Get location point from address
            location = get_location_from_address(address_components)
            
            if location:
                print(f"  Success: Geocoded to {location.y}, {location.x}")
                user.location = location
                user.latitude = location.y
                user.longitude = location.x
                user.save()
                geocoded_count += 1
            else:
                print(f"  Failed: Could not geocode address")
                error_count += 1
        except Exception as e:
            print(f"  Error: {str(e)}")
            error_count += 1
    
    print(f"\nGeocoding complete:")
    print(f"  {geocoded_count} users successfully geocoded")
    print(f"  {error_count} errors encountered")

if __name__ == "__main__":
    geocode_all_users() 