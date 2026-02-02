"""
Billing views module - backward compatibility.
Import views from the new modular structure.
"""
from .views.plan_views import (
    PlanListView,
    PlanCreateView,
    PlanUpdateView,
    PlanDeleteView,
)
from .views.coupon_views import (
    CouponListView,
    CouponCreateView,
    CouponUpdateView,
    CouponDeleteView,
)

__all__ = [
    "PlanListView",
    "PlanCreateView",
    "PlanUpdateView",
    "PlanDeleteView",
    "CouponListView",
    "CouponCreateView",
    "CouponUpdateView",
    "CouponDeleteView",
]
