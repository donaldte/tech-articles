"""Context processors for billing-related data."""

from typing import Any

from django.utils import timezone

from tech_articles.billing.models import Purchase
from tech_articles.billing.models import Subscription


def user_subscription(request):
    """
    Add user subscription status to template context.

    Provides:
        - has_active_subscription: Boolean indicating if user has active subscription
        - active_subscription: The active subscription object (or None)
    """
    context = {
        "has_active_subscription": False,
        "active_subscription": None,
    }

    if request.user.is_authenticated:
        # Get active subscription
        active_subscription: Any = (
            Subscription.objects.filter(
                user=request.user,
                status="succeeded",
            ).filter(current_period_end__isnull=True)
            | Subscription.objects.filter(
                user=request.user,
                status="succeeded",
                current_period_end__gt=timezone.now(),
            )
        ).first()

        if active_subscription:
            context["has_active_subscription"] = True
            context["active_subscription"] = active_subscription

    return context


def user_purchased_articles(request):
    """
    Add user's purchased article IDs to template context.

    Provides:
        - purchased_article_ids: Set of article IDs that the user has purchased
    """
    purchased_article_ids = set()

    if request.user.is_authenticated:
        # Get all successfully purchased article IDs for this user
        purchased_article_ids = set(
            Purchase.objects.filter(user=request.user, status="succeeded").values_list(
                "article_id", flat=True
            )
        )

    return {
        "purchased_article_ids": purchased_article_ids,
    }
