"""
Newsletter public subscription URL patterns.
"""
from django.urls import path

from tech_articles.newsletter.views import (
    subscribe_newsletter,
    unsubscribe_newsletter,
    confirm_subscription,
)

urlpatterns = [
    path("subscribe/", subscribe_newsletter, name="subscribe"),
    path("unsubscribe/<str:token>/", unsubscribe_newsletter, name="unsubscribe"),
    path("confirm/<str:token>/", confirm_subscription, name="confirm-subscription"),
]
