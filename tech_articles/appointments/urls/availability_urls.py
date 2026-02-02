"""
Availability URLs for appointments management.
"""
from django.urls import path

from tech_articles.appointments.views import (
    AvailabilitySettingsView,
    SaveConfigurationView,
    AvailabilityRuleAPIView,
    ExceptionDateAPIView,
)

urlpatterns = [
    # =====================
    # AVAILABILITY SETTINGS
    # =====================
    path('availability/', AvailabilitySettingsView.as_view(), name='availability_settings'),
    
    # =====================
    # API ENDPOINTS
    # =====================
    path('api/config/', SaveConfigurationView.as_view(), name='save_config'),
    path('api/rules/', AvailabilityRuleAPIView.as_view(), name='availability_rules'),
    path('api/exceptions/', ExceptionDateAPIView.as_view(), name='exception_dates'),
]
