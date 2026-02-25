"""
Billing views module.
Exports all views from feature-specific modules.
"""
from .plan_views import (
    PlanListView,
    PlanCreateView,
    PlanUpdateView,
    PlanDeleteView,
    PlanHistoryView,
)
from .coupon_views import (
    CouponListView,
    CouponCreateView,
    CouponUpdateView,
    CouponDeleteView,
)
from .subscription_views import (
    SubscriptionListView,
    SubscriptionDetailView,
    PlanListPublicView,
    PlanSubscribeView,
    PlanSubscribeConfirmView,
    SubscriptionCancelView,
    SubscriptionChangePlanView,
    StripeSuccessView,
    PayPalReturnView,
)
from .transaction_views import (
    TransactionListView,
)
from .purchase_views import (
    ArticlePurchaseCheckoutView,
    PurchaseStripeSuccessView,
    PurchasePayPalReturnView,
    PurchaseCancelView,
)
from .appointment_payment_views import (
    AppointmentPaymentCreateView,
    AppointmentPaymentSummaryView,
    AppointmentPaymentSuccessView,
    AppointmentPaymentPayPalReturnView,
)
from .webhook_views import (
    StripeWebhookView,
    PayPalWebhookView,
)

__all__ = [
    # Plans (admin)
    "PlanListView",
    "PlanCreateView",
    "PlanUpdateView",
    "PlanDeleteView",
    "PlanHistoryView",
    # Coupons (admin)
    "CouponListView",
    "CouponCreateView",
    "CouponUpdateView",
    "CouponDeleteView",
    # Subscriptions (admin)
    "SubscriptionListView",
    "SubscriptionDetailView",
    # Subscriptions (user-facing)
    "PlanListPublicView",
    "PlanSubscribeView",
    "PlanSubscribeConfirmView",
    "SubscriptionCancelView",
    "SubscriptionChangePlanView",
    "StripeSuccessView",
    "PayPalReturnView",
    # Transactions
    "TransactionListView",
    # Article purchases (user-facing)
    "ArticlePurchaseCheckoutView",
    "PurchaseStripeSuccessView",
    "PurchasePayPalReturnView",
    "PurchaseCancelView",
    # Appointment payments (user-facing)
    "AppointmentPaymentCreateView",
    "AppointmentPaymentSummaryView",
    "AppointmentPaymentSuccessView",
    "AppointmentPaymentPayPalReturnView",
    # Webhooks
    "StripeWebhookView",
    "PayPalWebhookView",
]
