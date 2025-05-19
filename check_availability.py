#!/usr/bin/env python3
import os
import sys
import django
from datetime import timedelta

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'viciniti.settings')
django.setup()

from django.utils import timezone
from main_app.models import Service, ProviderAvailability, Appointment

def check_service_availability(service_id):
    """Check availability records and simulate API response for a specific service"""
    try:
        # Get service
        service = Service.objects.get(id=service_id)
        provider = service.provider
        print(f"Service: {service.name}, Provider: {provider.business_name}")
        
        # Get availability records
        availabilities = ProviderAvailability.objects.filter(provider=provider)
        print(f"Provider has {availabilities.count()} availability records:")
        
        for avail in availabilities:
            print(f"  Day: '{avail.day_of_week}' (type: {type(avail.day_of_week)})")
            print(f"  Time: {avail.start_time} to {avail.end_time}")
            date_str = avail.start_time.strftime("%Y-%m-%d")
            print(f"  Date string: '{date_str}'")
            print()
        
        print(f"\n=== Let's revert availability data to full dates for provider {provider.id} ===")
        for avail in availabilities:
            old_day = avail.day_of_week
            # Convert back to full date
            new_day = avail.start_time.strftime("%Y-%m-%d")
            print(f"Changing day from '{old_day}' to '{new_day}'")
            avail.day_of_week = new_day
            avail.save()
        
        # Verify the fix
        print("\nAfter revert:")
        for avail in ProviderAvailability.objects.filter(provider=provider):
            print(f"  Day: '{avail.day_of_week}' - Time: {avail.start_time} to {avail.end_time}")
        
        # Get existing appointments
        existing_appointments = Appointment.objects.filter(
            service__provider=provider,
            status__in=['pending', 'confirmed']
        )
        print(f"\nProvider has {existing_appointments.count()} active appointments:")
        
        for appt in existing_appointments:
            appt_date = appt.start_time.strftime("%Y-%m-%d")
            print(f"  {appt.id}: {appt.start_time} to {appt.end_time} (date: {appt_date})")
        
        # Simulate API response
        print("\nSimulating availability calculations for the next 14 days:")
        
        # Calculate dates for the next 14 days
        today = timezone.now().date()
        days_to_check = 14
        
        for i in range(days_to_check):
            date = today + timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            
            # Check if this date has availability records
            available = any(avail.day_of_week == date_str for avail in ProviderAvailability.objects.filter(provider=provider))
            print(f"  {date_str}: {'Has availability records' if available else 'No availability records'}")
            
    except Service.DoesNotExist:
        print(f"Service with ID {service_id} not found")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        service_id = int(sys.argv[1])
    else:
        service_id = 2  # Default to service ID 2
        
    check_service_availability(service_id) 