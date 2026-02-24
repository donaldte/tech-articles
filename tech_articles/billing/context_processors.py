"""Context processors for billing-related data."""

from typing import Any

from tech_articles.billing.cache import BillingCache
from tech_articles.billing.models import Purchase
from tech_articles.utils.enums import PaymentStatus


def user_subscription(request):
    """
    Add user subscription status to template context.

    Provides:
        - has_active_subscription: Boolean indicating if user has active subscription
        - active_subscription: The active subscription object (or None)

    Also sets attributes on request object for use in views:
        - request.has_active_subscription
        - request.active_subscription
    """
    context = {
        "has_active_subscription": False,
        "active_subscription": None,
    }

    # Get subscription from cache
    active_subscription: Any = BillingCache.get_active_subscription(request.user)

    if active_subscription:
        context["has_active_subscription"] = True
        context["active_subscription"] = active_subscription
        request.has_active_subscription = True
        request.active_subscription = active_subscription
    else:
        request.has_active_subscription = False
        request.active_subscription = None

    return context


def user_purchased_articles(request):
    """
    Add user's purchased article IDs to template context.

    Provides:
        - purchased_article_ids: Set of article IDs that the user has purchased

    Also sets attribute on request object:
        - request.purchased_article_ids
    """
    # Get purchased articles from cache
    purchased_article_ids = BillingCache.get_purchased_article_ids(request.user)
    request.purchased_article_ids = purchased_article_ids

    return {
        "purchased_article_ids": purchased_article_ids,
    }
