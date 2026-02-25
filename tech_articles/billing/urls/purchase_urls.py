"""
Article purchase URL patterns.
Separate from subscription URLs to keep flows independent.
"""
from django.urls import path

from tech_articles.billing.views import (
    ArticlePurchaseCheckoutView,
    PurchaseStripeSuccessView,
    PurchasePayPalReturnView,
    PurchaseCancelView,
)

urlpatterns = [
    # Checkout page: article summary + payment method selector
    path(
        "articles/<slug:slug>/purchase/",
        ArticlePurchaseCheckoutView.as_view(),
        name="article_purchase_checkout",
    ),
    # Payment return/result URLs
    path(
        "purchases/stripe/success/",
        PurchaseStripeSuccessView.as_view(),
        name="purchase_stripe_success",
    ),
    path(
        "purchases/paypal/return/",
        PurchasePayPalReturnView.as_view(),
        name="purchase_paypal_return",
    ),
    path(
        "purchases/<uuid:pk>/cancel/",
        PurchaseCancelView.as_view(),
        name="purchase_cancel",
    ),
]
