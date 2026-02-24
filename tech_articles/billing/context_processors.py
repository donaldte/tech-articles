"""Context processors for billing-related data."""

from typing import Any

from django.utils import timezone

from tech_articles.billing.models import Purchase
from tech_articles.billing.models import Subscription
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

    if request.user.is_authenticated:
        # Get active subscription (include both succeeded and free_accepted statuses)
        # Case 1: Lifetime access (no period end)
        case_1 = Subscription.objects.filter(
            user=request.user,
            status__in=[PaymentStatus.SUCCEEDED, PaymentStatus.FREE_ACCEPTED],
            plan__price__gt=0,
            current_period_end__isnull=True,
        )

        # Case 2: Active subscription (period end in future)
        case_2 = Subscription.objects.filter(
            user=request.user,
            status__in=[PaymentStatus.SUCCEEDED, PaymentStatus.FREE_ACCEPTED],
            plan__price__gt=0,
            current_period_end__gt=timezone.now(),
        )

        # Combine both cases
        active_subscription: Any = (case_1 | case_2).first()

        if active_subscription:
            context["has_active_subscription"] = True
            context["active_subscription"] = active_subscription
            request.has_active_subscription = True
            request.active_subscription = active_subscription
        else:
            request.has_active_subscription = False
            request.active_subscription = None
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
    purchased_article_ids = set()

    if request.user.is_authenticated:
        # Get all successfully purchased article IDs for this user
        purchased_article_ids = set(
            Purchase.objects.filter(user=request.user, status=PaymentStatus.SUCCEEDED).values_list(
                "article_id", flat=True
            )
        )

    request.purchased_article_ids = purchased_article_ids

    return {
        "purchased_article_ids": purchased_article_ids,
    }
