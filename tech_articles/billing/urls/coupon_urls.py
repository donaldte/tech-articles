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
    path("coupons/", CouponListView.as_view(), name="coupons_list"),
    path("coupons/create/", CouponCreateView.as_view(), name="coupons_create"),
    path("coupons/<uuid:pk>/edit/", CouponUpdateView.as_view(), name="coupons_update"),
    path("coupons/<uuid:pk>/delete/", CouponDeleteView.as_view(), name="coupons_delete"),
]
