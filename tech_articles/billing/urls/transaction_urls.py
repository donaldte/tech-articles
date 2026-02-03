"""
Transaction URL patterns for dashboard.
"""
from django.urls import path

from tech_articles.billing.views import (
    TransactionListView,
)

urlpatterns = [
    path("transactions/", TransactionListView.as_view(), name="transactions_list"),
]
