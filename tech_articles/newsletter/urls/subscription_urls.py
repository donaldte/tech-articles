"""
Newsletter public subscription URL patterns.
"""
from django.urls import path

from tech_articles.newsletter.views import (
    subscribe_newsletter,
    unsubscribe_newsletter,
)

urlpatterns = [
    path("subscribe/", subscribe_newsletter, name="subscribe"),
    path("unsubscribe/<str:token>/", unsubscribe_newsletter, name="unsubscribe"),
]
