"""
Billing URLs module.
Main URL configuration for billing management (plans, coupons, subscriptions, transactions, webhooks).
Accessible at /billing/ (after i18n prefix)
"""
from .coupon_urls import urlpatterns as coupon_urls
from .plan_urls import urlpatterns as plan_urls
from .purchase_urls import urlpatterns as purchase_urls
from .subscription_urls import urlpatterns as subscription_urls
from .transaction_urls import urlpatterns as transaction_urls
from .webhook_urls import urlpatterns as webhook_urls
from .appointment_payment_urls import urlpatterns as appointment_payment_urls

app_name = "billing"

urlpatterns = (
    plan_urls
    + coupon_urls
    + subscription_urls
    + transaction_urls
    + purchase_urls
    + webhook_urls
    + appointment_payment_urls
)
