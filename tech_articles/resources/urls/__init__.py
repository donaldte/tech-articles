"""
Resources URLs module.
Main URL configuration for resources management.
Accessible at /resources/ (after i18n prefix)
"""
from .resource_urls import urlpatterns as resource_urls

app_name = "resources"

urlpatterns = resource_urls
