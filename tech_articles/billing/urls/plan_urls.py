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
    path("plans/", PlanListView.as_view(), name="plans_list"),
    path("plans/create/", PlanCreateView.as_view(), name="plans_create"),
    path("plans/<uuid:pk>/edit/", PlanUpdateView.as_view(), name="plans_update"),
    path("plans/<uuid:pk>/delete/", PlanDeleteView.as_view(), name="plans_delete"),
    path("plans/<uuid:pk>/history/", PlanHistoryView.as_view(), name="plans_history"),
]
