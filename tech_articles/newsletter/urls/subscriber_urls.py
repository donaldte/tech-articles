"""
Newsletter subscriber URL patterns for dashboard CRUD operations.
"""
from django.urls import path

from tech_articles.newsletter.views import (
    SubscriberListView,
    SubscriberCreateView,
    SubscriberUpdateView,
    SubscriberDeleteView,
)

urlpatterns = [
    path("subscribers/", SubscriberListView.as_view(), name="subscribers_list"),
    path("subscribers/create/", SubscriberCreateView.as_view(), name="subscribers_create"),
    path("subscribers/<uuid:pk>/edit/", SubscriberUpdateView.as_view(), name="subscribers_update"),
    path("subscribers/<uuid:pk>/delete/", SubscriberDeleteView.as_view(), name="subscribers_delete"),
]
