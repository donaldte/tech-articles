"""
Webhook URL patterns for Stripe and PayPal.
These endpoints must be accessible without authentication (CSRF-exempt).
Register them in your Stripe and PayPal dashboards.
"""
from django.urls import path

from tech_articles.billing.views import (
    StripeWebhookView,
    PayPalWebhookView,
)

urlpatterns = [
    path("webhooks/stripe/", StripeWebhookView.as_view(), name="stripe_webhook"),
    path("webhooks/paypal/", PayPalWebhookView.as_view(), name="paypal_webhook"),
]
