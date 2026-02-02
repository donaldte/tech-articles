"""
Coupon URL patterns for dashboard CRUD operations.
"""
from django.urls import path

from tech_articles.billing.views import (
    CouponListView,
    CouponCreateView,
    CouponUpdateView,
    CouponDeleteView,
)

urlpatterns = [
    path("", CouponListView.as_view(), name="coupons_list"),
    path("create/", CouponCreateView.as_view(), name="coupons_create"),
    path("<uuid:pk>/edit/", CouponUpdateView.as_view(), name="coupons_update"),
    path("<uuid:pk>/delete/", CouponDeleteView.as_view(), name="coupons_delete"),
]
