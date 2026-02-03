"""
Newsletter URLs module.
Main URL configuration for newsletter management.
Accessible at /newsletter/ (after i18n prefix)
"""
from .subscriber_urls import urlpatterns as subscriber_urls
from .campaign_urls import urlpatterns as campaign_urls

app_name = "newsletter"

urlpatterns = subscriber_urls + campaign_urls
