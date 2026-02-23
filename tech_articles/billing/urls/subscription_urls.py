"""
Subscription URL patterns: admin views + user-facing subscription management.
"""
from django.urls import path

from tech_articles.billing.views import (
    SubscriptionListView,
    SubscriptionDetailView,
    PlanListPublicView,
    PlanSubscribeView,
    PlanSubscribeConfirmView,
    SubscriptionCancelView,
    SubscriptionChangePlanView,
)

urlpatterns = [
    # Admin
    path("subscriptions/", SubscriptionListView.as_view(), name="subscriptions_list"),
    path("subscriptions/<uuid:pk>/", SubscriptionDetailView.as_view(), name="subscriptions_detail"),

    # User-facing
    path("plans/", PlanListPublicView.as_view(), name="plans_public"),
    path("plans/<slug:slug>/subscribe/", PlanSubscribeView.as_view(), name="subscribe"),
    path("plans/<slug:slug>/subscribe/confirm/", PlanSubscribeConfirmView.as_view(), name="subscribe_confirm"),
    path("subscriptions/<uuid:pk>/cancel/", SubscriptionCancelView.as_view(), name="subscription_cancel"),
    path("subscriptions/change-plan/", SubscriptionChangePlanView.as_view(), name="subscription_change_plan"),
]
