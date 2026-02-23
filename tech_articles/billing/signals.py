"""
Billing signals: fired when subscription status changes.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver, Signal
from django.utils.translation import gettext_lazy as _

from tech_articles.billing.models import Subscription
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
