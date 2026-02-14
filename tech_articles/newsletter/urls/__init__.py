"""
Newsletter URLs module.
Main URL configuration for newsletter management.
Accessible at /newsletter/ (after i18n prefix)
"""
from .subscriber_urls import urlpatterns as subscriber_urls
from .campaign_urls import urlpatterns as campaign_urls
from .subscription_urls import urlpatterns as subscription_urls

app_name = "newsletter"

urlpatterns = subscription_urls + subscriber_urls + campaign_urls
