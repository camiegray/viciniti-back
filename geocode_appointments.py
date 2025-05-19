#!/usr/bin/env python3
import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'viciniti.settings')
django.setup()

from main_app.models import Appointment
from main_app.utils.geo_utils import get_location_from_address

def geocode_all_appointments():
    """Geocode all appointments with address data but no location"""
    print("Starting geocoding for all appointments...")
    
    # Get all appointments with address data but no location
    appointments = Appointment.objects.filter(
        location__isnull=True,
        address_line1__isnull=False,
        city__isnull=False,
        state__isnull=False
    ).exclude(
        address_line1='',
        city='',
        state=''
    )
    
    print(f"Found {appointments.count()} appointments with address data but no geocoded location")
    
    geocoded_count = 0
    error_count = 0
    
    for appointment in appointments:
        print(f"Geocoding appointment {appointment.id}")
        
        try:
            address_components = {
                'address_line1': appointment.address_line1,
                'city': appointment.city,
                'state': appointment.state,
                'zip_code': appointment.zip_code,
                'country': appointment.country or 'USA'
            }
            
            # Get location point from address
            location = get_location_from_address(address_components)
            
            if location:
                print(f"  Success: Geocoded to {location.y}, {location.x}")
                appointment.location = location
                appointment.latitude = location.y
                appointment.longitude = location.x
                appointment.save()
                geocoded_count += 1
            else:
                print(f"  Failed: Could not geocode address")
                error_count += 1
        except Exception as e:
            print(f"  Error: {str(e)}")
            error_count += 1
    
    print(f"\nGeocoding complete:")
    print(f"  {geocoded_count} appointments successfully geocoded")
    print(f"  {error_count} errors encountered")

if __name__ == "__main__":
    geocode_all_appointments() 