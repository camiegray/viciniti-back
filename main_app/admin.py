from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, ServiceProvider, Service, Appointment

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'user_type', 'is_staff')
    list_filter = ('user_type', 'is_staff', 'is_superuser')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('user_type', 'phone_number', 'address')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('user_type', 'phone_number', 'address')}),
    )

class ServiceProviderAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'user', 'created_at', 'updated_at')
    search_fields = ('business_name', 'business_description')

class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'provider', 'duration', 'price', 'is_active')
    list_filter = ('is_active', 'provider')
    search_fields = ('name', 'description')

class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('service', 'consumer', 'start_time', 'end_time', 'status')
    list_filter = ('status', 'start_time')
    search_fields = ('service__name', 'consumer__username')

admin.site.register(User, CustomUserAdmin)
admin.site.register(ServiceProvider, ServiceProviderAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(Appointment, AppointmentAdmin)
