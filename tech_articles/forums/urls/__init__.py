"""
Analytics URL patterns for dashboard.
"""
from django.urls import path

from tech_articles.analytics.views import (
    AnalyticsOverviewView,
    EventsListView,
    EventDetailAPIView,
)

app_name = "forums"

urlpatterns = [
]
