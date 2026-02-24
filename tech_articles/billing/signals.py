"""
Billing signals: fired when subscription status changes.
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver, Signal
from django.utils.translation import gettext_lazy as _

from tech_articles.billing.models import Subscription, Purchase
from tech_articles.utils.enums import PaymentStatus

# Custom signals
subscription_activated = Signal()   # args: subscription
subscription_cancelled = Signal()   # args: subscription


@receiver(post_save, sender=Subscription)
def handle_subscription_status_change(sender, instance: Subscription, created: bool, **kwargs):
    """Fire domain signals when a subscription becomes active or cancelled."""
    if not created:
        update_fields = kwargs.get("update_fields")
        if update_fields and "status" in update_fields:
            if instance.status == PaymentStatus.SUCCEEDED:
                subscription_activated.send(sender=Subscription, subscription=instance)
            elif instance.status == PaymentStatus.CANCELLED:
                subscription_cancelled.send(sender=Subscription, subscription=instance)


# ============================================================================
# Cache invalidation signals
# ============================================================================


@receiver(post_save, sender=Subscription)
def invalidate_subscription_cache_on_save(sender, instance, **kwargs):
    """Clear subscription cache when a subscription is saved."""
    from tech_articles.billing.cache import BillingCache
    BillingCache.clear_subscription_cache(instance.user)


@receiver(post_delete, sender=Subscription)
def invalidate_subscription_cache_on_delete(sender, instance, **kwargs):
    """Clear subscription cache when a subscription is deleted."""
    from tech_articles.billing.cache import BillingCache
    BillingCache.clear_subscription_cache(instance.user)


@receiver(post_save, sender=Purchase)
def invalidate_purchase_cache_on_save(sender, instance, **kwargs):
    """Clear purchased articles cache when a purchase is saved."""
    from tech_articles.billing.cache import BillingCache
    BillingCache.clear_purchased_articles_cache(instance.user)


@receiver(post_delete, sender=Purchase)
def invalidate_purchase_cache_on_delete(sender, instance, **kwargs):
    """Clear purchased articles cache when a purchase is deleted."""
    from tech_articles.billing.cache import BillingCache
    BillingCache.clear_purchased_articles_cache(instance.user)

