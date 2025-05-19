from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Provider URLs
    path('provider/setup/', views.provider_setup, name='provider_setup'),
    path('provider/dashboard/', views.provider_dashboard, name='provider_dashboard'),
    path('provider/services/create/', views.ServiceCreateView.as_view(), name='service_create'),
    path('provider/profile/', views.ProviderProfileAPI.as_view(), name='provider_profile'),
    
    # Service URLs
    path('services/', views.ServiceListAPI.as_view(), name='service_list'),
    path('services/create/', views.ServiceCreateAPI.as_view(), name='service_create_api'),
    path('services/<int:service_id>/', views.ServiceDetailAPI.as_view(), name='service_detail'),
    path('services/provider/<int:provider_id>/', views.ProviderServiceListAPI.as_view(), name='provider_services'),
    path('services/categories/', views.ServiceCategoriesAPI.as_view(), name='service_categories'),
    
    # Appointment URLs
    path('appointments/', views.AppointmentListAPI.as_view(), name='appointment_list'),
    path('appointments/<int:appointment_id>/', views.AppointmentDetailAPI.as_view(), name='appointment_detail'),
    path('appointments/<int:appointment_id>/status/', views.AppointmentStatusAPI.as_view(), name='appointment_status'),
    path('appointments/provider/<int:provider_id>/', views.ProviderAppointmentListAPI.as_view(), name='provider_appointments'),
    path('appointments/consumer/<int:consumer_id>/', views.ConsumerAppointmentListAPI.as_view(), name='consumer_appointments'),
    
    # Provider Availability URLs
    path('providers/<int:provider_id>/availability/', views.ProviderAvailabilityAPI.as_view(), name='provider_availability'),
    path('services/<int:service_id>/availability/', views.ServiceAvailabilityAPI.as_view(), name='service_availability'),
] 