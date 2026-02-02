"""
Plan URL patterns for dashboard CRUD operations.
"""
from django.urls import path

from tech_articles.billing.views import (
    PlanListView,
    PlanCreateView,
    PlanUpdateView,
    PlanDeleteView,
    PlanHistoryView,
)

urlpatterns = [
    path("", PlanListView.as_view(), name="plans_list"),
    path("create/", PlanCreateView.as_view(), name="plans_create"),
    path("<uuid:pk>/edit/", PlanUpdateView.as_view(), name="plans_edit"),
    path("<uuid:pk>/delete/", PlanDeleteView.as_view(), name="plans_delete"),
    path("<uuid:pk>/history/", PlanHistoryView.as_view(), name="plans_history"),
]
