"""
Newsletter views module.
"""
from .subscriber_views import (
    SubscriberListView,
    SubscriberCreateView,
    SubscriberUpdateView,
    SubscriberDeleteView,
    SubscriberExportCSVView,
    SubscriberImportCSVView,
)
from .campaign_views import (
    CampaignListView,
    CampaignCreateView,
    CampaignUpdateView,
    CampaignDeleteView,
)
from .subscription_views import (
    subscribe_newsletter,
    unsubscribe_newsletter,
)

__all__ = [
    "SubscriberListView",
    "SubscriberCreateView",
    "SubscriberUpdateView",
    "SubscriberDeleteView",
    "SubscriberExportCSVView",
    "SubscriberImportCSVView",
    "CampaignListView",
    "CampaignCreateView",
    "CampaignUpdateView",
    "CampaignDeleteView",
    "subscribe_newsletter",
    "unsubscribe_newsletter",
]
