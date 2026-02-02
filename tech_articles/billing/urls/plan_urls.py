"""
Plan URL patterns for dashboard CRUD operations.
"""
from django.urls import path

from tech_articles.billing.views import (
    PlanListView,
    PlanCreateView,
    PlanUpdateView,
    PlanDeleteView,
)

urlpatterns = [
    path("", PlanListView.as_view(), name="plans_list"),
    path("create/", PlanCreateView.as_view(), name="plans_create"),
    path("<uuid:pk>/edit/", PlanUpdateView.as_view(), name="plans_update"),
    path("<uuid:pk>/delete/", PlanDeleteView.as_view(), name="plans_delete"),
]
