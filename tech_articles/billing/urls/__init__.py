"""
Billing URLs module.
Main URL configuration for billing management (plans, coupons).
Accessible at /billing/ (after i18n prefix)
"""
from .coupon_urls import urlpatterns as coupon_urls
from .plan_urls import urlpatterns as plan_urls

app_name = "billing"

urlpatterns = plan_urls + coupon_urls
