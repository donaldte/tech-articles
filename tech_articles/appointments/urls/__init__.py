"""
Appointments URLs module.
Main URL configuration for appointments management.
Accessible at /appointments/ (after i18n prefix)
"""
from .appointment_type_urls import urlpatterns as appointment_type_urls
from .availability_urls import urlpatterns as availability_urls
from .appointment_urls import urlpatterns as appointment_urls
from .home_urls import urlpatterns as home_urls

app_name = "appointments"

urlpatterns = home_urls + appointment_type_urls + availability_urls + appointment_urls
