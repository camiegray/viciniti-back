from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.contrib.gis.db import models as gis_models
import uuid

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('provider', 'Service Provider'),
        ('consumer', 'Service Consumer'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    street_address = models.CharField(max_length=100, blank=True)
    apartment = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=50, blank=True)
    state = models.CharField(max_length=20, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    location = gis_models.PointField(null=True, blank=True, geography=True)

    def save(self, *args, **kwargs):
        """Override the save method to automatically geocode the address when necessary"""
        # Check if we need to geocode (if address fields are set but no location)
        address_fields_set = self.street_address and self.city and self.state
        
        # Only attempt geocoding if we have all required address fields and either:
        # 1. No location exists, or
        # 2. One of the address fields has changed
        if address_fields_set and (
            not self.location or 
            self._has_address_changed()
        ):
            try:
                print(f"DEBUG USER MODEL: Auto-geocoding address for user {self.username}")
                from .utils.geo_utils import get_location_from_address
                
                address_components = {
                    'address_line1': self.street_address,
                    'city': self.city,
                    'state': self.state,
                    'zip_code': self.zip_code,
                    'country': 'USA'
                }
                
                # Get location point from address
                location = get_location_from_address(address_components)
                
                if location:
                    print(f"DEBUG USER MODEL: Successfully geocoded to {location.y}, {location.x}")
                    self.location = location
                    self.latitude = location.y
                    self.longitude = location.x
                else:
                    print(f"DEBUG USER MODEL: Failed to geocode address in model save")
            except Exception as e:
                print(f"DEBUG USER MODEL: Error geocoding user address: {str(e)}")
        
        # Call the superclass save method
        super().save(*args, **kwargs)
    
    def _has_address_changed(self):
        """Check if any address fields have changed since the last save"""
        if not self.pk:  # New instance
            return True
            
        try:
            old_instance = User.objects.get(pk=self.pk)
            return (
                old_instance.street_address != self.street_address or
                old_instance.city != self.city or
                old_instance.state != self.state or
                old_instance.zip_code != self.zip_code
            )
        except User.DoesNotExist:
            return True

class ServiceProvider(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='provider_profile')
    business_name = models.CharField(max_length=100)
    business_description = models.TextField()
    business_hours = models.JSONField(default=dict)  # Store business hours as JSON
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    business_location = gis_models.PointField(null=True, blank=True, geography=True)
    
    # Address fields
    address_line1 = models.CharField(max_length=255, default='')
    address_line2 = models.CharField(max_length=255, default='')
    city = models.CharField(max_length=100, default='')
    state = models.CharField(max_length=100, default='')
    postal_code = models.CharField(max_length=20, default='')
    country = models.CharField(max_length=100, default='United States')
    service_radius = models.FloatField(default=10.0)  # Default radius in miles
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.business_name

    def save(self, *args, **kwargs):
        """Override save to sync user location with business location"""
        # First check if we need to sync with user's location
        if not self.business_location and self.user.location:
            print(f"DEBUG PROVIDER MODEL: Syncing business location with user location for {self.business_name}")
            self.business_location = self.user.location
            self.latitude = self.user.location.y
            self.longitude = self.user.location.x
        
        # If we have our own address but no location, try to geocode it
        address_fields_set = self.address_line1 and self.city and self.state
        if address_fields_set and not self.business_location:
            try:
                print(f"DEBUG PROVIDER MODEL: Geocoding business address for {self.business_name}")
                from .utils.geo_utils import get_location_from_address
                
                address_components = {
                    'address_line1': self.address_line1,
                    'city': self.city,
                    'state': self.state,
                    'zip_code': self.postal_code,
                    'country': self.country
                }
                
                # Get location point from address
                location = get_location_from_address(address_components)
                
                if location:
                    print(f"DEBUG PROVIDER MODEL: Successfully geocoded to {location.y}, {location.x}")
                    self.business_location = location
                    self.latitude = location.y
                    self.longitude = location.x
                else:
                    print(f"DEBUG PROVIDER MODEL: Failed to geocode business address")
            except Exception as e:
                print(f"DEBUG PROVIDER MODEL: Error geocoding business address: {str(e)}")
        
        # Call the superclass save method
        super().save(*args, **kwargs)

SERVICE_CATEGORIES = (
    ('beauty_hair', 'Beauty - Hair'),
    ('beauty_nails', 'Beauty - Nails'),
    ('beauty_makeup', 'Beauty - Makeup'),
    ('beauty_skin', 'Beauty - Skin'),
    ('cleaning_tidy', 'Cleaning - Tidy Up'),
    ('cleaning_deep', 'Cleaning - Deep Clean'),
    ('pet_care_walk', 'Pet Care - Dog Walk'),
    ('pet_care_sit', 'Pet Care - Petsit'),
    ('car_care_wash', 'Car Care - Wash/Wax'),
    ('car_care_detail', 'Car Care - Detail'),
    ('errands', 'Errands'),
    ('handyman', 'Handyman'),
)

class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name='services')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.IntegerField(help_text='Duration in minutes')
    category = models.CharField(max_length=20, choices=SERVICE_CATEGORIES, default='beauty')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Appointment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    )
    
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='appointments')
    consumer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    
    # Address fields that already exist in the database
    address_line1 = models.CharField(max_length=100, blank=True, null=True)
    address_line2 = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=20, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    zip_code = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True, default='United States')
    
    # Add geospatial location field
    location = gis_models.PointField(null=True, blank=True, geography=True)
    
    # Other fields that exist in the database
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    final_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_reason = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.service.name} - {self.consumer.username} - {self.start_time}"

    def save(self, *args, **kwargs):
        if not self.end_time:
            self.end_time = self.start_time + timezone.timedelta(minutes=self.service.duration)
        super().save(*args, **kwargs)

class ProviderAvailability(models.Model):
    provider = models.ForeignKey('ServiceProvider', on_delete=models.CASCADE, related_name='availabilities')
    day_of_week = models.CharField(max_length=10)  # e.g., "2023-06-15" for a specific date
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('provider', 'day_of_week', 'start_time')

    def __str__(self):
        return f"{self.provider.business_name} - {self.day_of_week} - {self.start_time.strftime('%H:%M')} to {self.end_time.strftime('%H:%M')}"

class ProximityDiscountConfig(models.Model):
    """
    Configuration for proximity-based discounts for a specific provider.
    
    Defines discount percentages based on distance tiers and number of appointments.
    
    Discounts are only applied when:
    1. An appointment slot is temporally adjacent (immediately before or after) to existing appointments
    2. Those existing appointments are geographically close to the consumer's location
    
    This encourages consumers to book multiple appointments in the same area during a single trip,
    reducing travel time and expenses for service providers.
    """
    provider = models.OneToOneField(ServiceProvider, on_delete=models.CASCADE, related_name='discount_config')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Tier distance thresholds in yards
    tier1_distance = models.IntegerField(default=200)  # 0-200 yards
    tier2_min_distance = models.IntegerField(default=200)  # 200 yards
    tier2_max_distance = models.IntegerField(default=600)  # 600 yards
    tier3_min_distance = models.IntegerField(default=600)  # 600 yards
    tier3_max_distance = models.IntegerField(default=1760)  # 1 mile (1760 yards)
    tier4_min_distance = models.IntegerField(default=1760)  # 1 mile
    tier4_max_distance = models.IntegerField(default=5280)  # 3 miles (5280 yards)
    
    # Discount percentages for each tier and appointment count combination
    # Tier 1 discounts (0-200 yards)
    tier1_1appt_discount = models.IntegerField(default=15)  # 15% discount
    tier1_2appt_discount = models.IntegerField(default=20)  # 20% discount
    tier1_3appt_discount = models.IntegerField(default=25)  # 25% discount
    tier1_4appt_discount = models.IntegerField(default=30)  # 30% discount
    tier1_5appt_discount = models.IntegerField(default=35)  # 35% discount
    
    # Tier 2 discounts (200-600 yards)
    tier2_1appt_discount = models.IntegerField(default=12)  # 12% discount
    tier2_2appt_discount = models.IntegerField(default=15)  # 15% discount
    tier2_3appt_discount = models.IntegerField(default=18)  # 18% discount
    tier2_4appt_discount = models.IntegerField(default=21)  # 21% discount
    tier2_5appt_discount = models.IntegerField(default=24)  # 24% discount
    
    # Tier 3 discounts (600 yards - 1 mile)
    tier3_1appt_discount = models.IntegerField(default=10)  # 10% discount
    tier3_2appt_discount = models.IntegerField(default=11)  # 11% discount
    tier3_3appt_discount = models.IntegerField(default=12)  # 12% discount
    tier3_4appt_discount = models.IntegerField(default=13)  # 13% discount
    tier3_5appt_discount = models.IntegerField(default=14)  # 14% discount
    
    # Tier 4 discounts (1 mile - 3 miles)
    tier4_1appt_discount = models.IntegerField(default=5)   # 5% discount
    tier4_2appt_discount = models.IntegerField(default=6)   # 6% discount
    tier4_3appt_discount = models.IntegerField(default=7)   # 7% discount
    tier4_4appt_discount = models.IntegerField(default=8)   # 8% discount
    tier4_5appt_discount = models.IntegerField(default=9)   # 9% discount
    
    def get_discount_for_distance_and_count(self, distance_yards, appointment_count):
        """
        Calculate the discount percentage based on distance and number of appointments.
        
        Args:
            distance_yards: Distance in yards from existing appointment
            appointment_count: Number of additional appointments in proximity (1-5)
            
        Returns:
            Discount percentage as an integer (0-100)
        """
        # Cap the appointment count at 5
        if appointment_count > 5:
            appointment_count = 5
        elif appointment_count < 1:
            appointment_count = 1
        
        # Determine which tier the distance falls into
        if distance_yards <= self.tier1_distance:
            tier = 1
        elif self.tier2_min_distance <= distance_yards <= self.tier2_max_distance:
            tier = 2
        elif self.tier3_min_distance <= distance_yards <= self.tier3_max_distance:
            tier = 3
        elif self.tier4_min_distance <= distance_yards <= self.tier4_max_distance:
            tier = 4
        else:
            # Beyond maximum distance, no discount
            return 0
        
        # Get the appropriate discount based on tier and appointment count
        field_name = f"tier{tier}_{appointment_count}appt_discount"
        discount = getattr(self, field_name, 0)
        
        return discount
