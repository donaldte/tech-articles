"""
Billing URLs module.
Main URL configuration for billing management (plans, coupons, subscriptions, transactions).
Accessible at /billing/ (after i18n prefix)
"""
from .coupon_urls import urlpatterns as coupon_urls
from .plan_urls import urlpatterns as plan_urls
from .subscription_urls import urlpatterns as subscription_urls
from .transaction_urls import urlpatterns as transaction_urls

app_name = "billing"

urlpatterns = plan_urls + coupon_urls + subscription_urls + transaction_urls
