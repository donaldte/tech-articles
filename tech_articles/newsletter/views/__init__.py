"""
Newsletter views module.
"""
from .subscriber_views import (
    SubscriberListView,
    SubscriberCreateView,
    SubscriberUpdateView,
    SubscriberDeleteView,
)
from .campaign_views import (
    CampaignListView,
    CampaignCreateView,
    CampaignUpdateView,
    CampaignDeleteView,
)

__all__ = [
    "SubscriberListView",
    "SubscriberCreateView",
    "SubscriberUpdateView",
    "SubscriberDeleteView",
    "CampaignListView",
    "CampaignCreateView",
    "CampaignUpdateView",
    "CampaignDeleteView",
]
