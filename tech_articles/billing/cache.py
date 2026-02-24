"""
Billing cache management for subscriptions and purchases.

Provides cached access to user subscriptions and purchased articles
with automatic cache invalidation.
"""

from django.core.cache import cache
from django.utils import timezone

from tech_articles.billing.models import Purchase, Subscription
from tech_articles.utils.enums import PaymentStatus


# Cache keys
SUBSCRIPTION_CACHE_KEY_PREFIX = "user_subscription_{user_id}"
PURCHASED_ARTICLES_CACHE_KEY_PREFIX = "user_purchased_articles_{user_id}"
CACHE_TIMEOUT = 3600  # 1 hour


class BillingCache:
    """Centralized cache management for billing data."""

    @staticmethod
    def get_active_subscription(user):
        """
        Get user's active subscription from cache, or query from DB if not cached.

        Args:
            user: Django User instance

        Returns:
            Subscription instance or None
        """
        if not user or not user.is_authenticated:
            return None

        cache_key = SUBSCRIPTION_CACHE_KEY_PREFIX.format(user_id=user.id)
        cached = cache.get(cache_key)

        # Return cached value (even if None)
        if cached is not None:
            return cached if cached != "NONE" else None

        # Query from database
        from django.db.models import Q

        subscription = (
            Subscription.objects.filter(
                user=user,
                status__in=[PaymentStatus.SUCCEEDED, PaymentStatus.FREE_ACCEPTED],
                plan__price__gt=0,
            )
            .filter(
                Q(current_period_end__isnull=True)
                | Q(current_period_end__gt=timezone.now())
            )
            .first()
        )

        # Store in cache (use "NONE" string for null values to distinguish from cache miss)
        cache_value = subscription if subscription else "NONE"
        cache.set(cache_key, cache_value, CACHE_TIMEOUT)

        return subscription

    @staticmethod
    def get_purchased_article_ids(user):
        """
        Get user's purchased article IDs from cache, or query from DB if not cached.

        Args:
            user: Django User instance

        Returns:
            Set of article IDs (UUIDs as strings)
        """
        if not user or not user.is_authenticated:
            return set()

        cache_key = PURCHASED_ARTICLES_CACHE_KEY_PREFIX.format(user_id=user.id)
        cached = cache.get(cache_key)

        # Return cached value if found
        if cached is not None:
            return cached

        # Query from database
        purchased_ids = set(
            Purchase.objects.filter(
                user=user, status=PaymentStatus.SUCCEEDED
            ).values_list("article_id", flat=True)
        )

        # Store in cache
        cache.set(cache_key, purchased_ids, CACHE_TIMEOUT)

        return purchased_ids

    @staticmethod
    def clear_subscription_cache(user):
        """
        Clear subscription cache for a specific user.

        Args:
            user: Django User instance
        """
        cache_key = SUBSCRIPTION_CACHE_KEY_PREFIX.format(user_id=user.id)
        cache.delete(cache_key)

    @staticmethod
    def clear_purchased_articles_cache(user):
        """
        Clear purchased articles cache for a specific user.

        Args:
            user: Django User instance
        """
        cache_key = PURCHASED_ARTICLES_CACHE_KEY_PREFIX.format(user_id=user.id)
        cache.delete(cache_key)

    @staticmethod
    def clear_all_caches(user):
        """
        Clear all billing caches for a specific user.

        Args:
            user: Django User instance
        """
        BillingCache.clear_subscription_cache(user)
        BillingCache.clear_purchased_articles_cache(user)


