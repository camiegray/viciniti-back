from django.urls import path, re_path
from . import views
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

# Apply AllowAny permission to specific views - the decorator approach might be causing issues
# Let's use the direct approach by setting permission_classes in the view itself

urlpatterns = [
    # Authentication endpoints (no authentication required)
    path('auth/register/', views.RegisterAPI.as_view(), name='api_register'),
    path('auth/login/', views.LoginAPI.as_view(), name='api_login'),
    path('auth/profile/', views.UserProfileAPI.as_view(), name='api_user_profile'),
    path('auth/password/', views.PasswordChangeAPI.as_view(), name='api_password_change'),
    
    # Provider endpoints
    path('provider/setup/', views.ProviderSetupAPI.as_view(), name='api_provider_setup'),
    path('provider/profile/', views.ProviderProfileAPI.as_view(), name='api_provider_profile'),
    path('providers/<int:provider_id>/availability/', views.ProviderAvailabilityAPI.as_view(), name='api_provider_availability'),
    path('provider/discount-config/', views.ProximityDiscountConfigAPI.as_view(), name='api_provider_discount_config'),
    
    # Service endpoints
    path('services/', views.ServiceListAPI.as_view(), name='api_service_list'),
    path('services/<int:service_id>/', views.ServiceDetailAPI.as_view(), name='api_service_detail'),
    path('services/categories/', views.ServiceCategoriesAPI.as_view(), name='api_service_categories'),
    path('services/create/', views.ServiceCreateAPI.as_view(), name='api_service_create'),
    path('services/provider/<int:provider_id>/', views.ProviderServiceListAPI.as_view(), name='api_provider_services'),
    path('services/<int:service_id>/availability/', views.ServiceAvailabilityAPI.as_view(), name='api_service_availability'),
    path('services/<int:service_id>/availability-with-discount/', views.ServiceAvailabilityWithDiscountAPI.as_view(), name='api_service_availability_with_discount'),
    
    # Appointment endpoints - Updated to support UUID format
    path('appointments/', views.AppointmentListAPI.as_view(), name='api_appointment_list'),
    # Use UUID pattern for appointment endpoints
    path('appointments/<uuid:appointment_id>/', views.AppointmentDetailAPI.as_view(), name='api_appointment_detail'),
    path('appointments/<uuid:appointment_id>/status/', views.AppointmentStatusAPI.as_view(), name='api_appointment_status'),
    path('appointments/provider/<int:provider_id>/', views.ProviderAppointmentListAPI.as_view(), name='api_provider_appointments'),
    path('appointments/consumer/<int:consumer_id>/', views.ConsumerAppointmentListAPI.as_view(), name='api_consumer_appointments'),
] 