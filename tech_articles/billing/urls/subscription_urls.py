"""
Subscription URL patterns for dashboard.
"""
from django.urls import path

from tech_articles.billing.views import (
    SubscriptionListView,
    SubscriptionDetailView,
)

urlpatterns = [
    path("subscriptions/", SubscriptionListView.as_view(), name="subscriptions_list"),
    path("subscriptions/<uuid:pk>/", SubscriptionDetailView.as_view(), name="subscriptions_detail"),
]
