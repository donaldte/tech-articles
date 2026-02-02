"""
Billing URLs module.
Main URL configuration for billing management (plans, coupons).
Accessible at /billing/ (after i18n prefix)
"""
from django.urls import path, include

from tech_articles.billing.views import (
    PlanListView,
    PlanCreateView,
    PlanUpdateView,
    PlanDeleteView,
    CouponListView,
    CouponCreateView,
    CouponUpdateView,
    CouponDeleteView,
)

app_name = "billing"

urlpatterns = [
    # =====================
    # PLANS CRUD
    # =====================
    path("plans/", PlanListView.as_view(), name="plans_list"),
    path("plans/create/", PlanCreateView.as_view(), name="plans_create"),
    path("plans/<uuid:pk>/edit/", PlanUpdateView.as_view(), name="plans_update"),
    path("plans/<uuid:pk>/delete/", PlanDeleteView.as_view(), name="plans_delete"),

    # =====================
    # COUPONS CRUD
    # =====================
    path("coupons/", CouponListView.as_view(), name="coupons_list"),
    path("coupons/create/", CouponCreateView.as_view(), name="coupons_create"),
    path("coupons/<uuid:pk>/edit/", CouponUpdateView.as_view(), name="coupons_update"),
    path("coupons/<uuid:pk>/delete/", CouponDeleteView.as_view(), name="coupons_delete"),
]
