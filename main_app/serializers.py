from rest_framework import serializers
from .models import Service, Appointment

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'name', 'description', 'price', 'duration', 'category', 'provider', 'is_active', 'created_at', 'updated_at']

class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['id', 'service', 'consumer', 'start_time', 'end_time', 'status', 'notes', 'created_at', 'updated_at'] 