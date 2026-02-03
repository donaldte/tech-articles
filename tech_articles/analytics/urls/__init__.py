"""
Analytics URL patterns for dashboard.
"""
from django.urls import path

from tech_articles.analytics.views import (
    AnalyticsOverviewView,
    EventsListView,
)

app_name = "analytics"

urlpatterns = [
    path("", AnalyticsOverviewView.as_view(), name="analytics_overview"),
    path("events/", EventsListView.as_view(), name="analytics_events"),
]
