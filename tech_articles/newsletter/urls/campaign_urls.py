"""
Newsletter campaign URL patterns for dashboard CRUD operations.
"""
from django.urls import path

from tech_articles.newsletter.views import (
    CampaignListView,
    CampaignCreateView,
    CampaignUpdateView,
    CampaignDeleteView,
)

urlpatterns = [
    path("campaigns/", CampaignListView.as_view(), name="campaigns_list"),
    path("campaigns/create/", CampaignCreateView.as_view(), name="campaigns_create"),
    path("campaigns/<uuid:pk>/edit/", CampaignUpdateView.as_view(), name="campaigns_update"),
    path("campaigns/<uuid:pk>/delete/", CampaignDeleteView.as_view(), name="campaigns_delete"),
]
