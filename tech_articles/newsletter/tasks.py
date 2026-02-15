"""
Newsletter tasks for sending emails asynchronously.
"""
import logging

from celery import shared_task
from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext as _

from tech_articles.utils.email import EmailUtil

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_newsletter_confirmation_email(self, subscriber_id: str, subscriber_email: str, language: str):
    """
    Send double opt-in confirmation email to new newsletter subscriber.

    Args:
        subscriber_id: UUID of the subscriber
        subscriber_email: Email address of the subscriber
        language: Preferred language code (e.g., 'en', 'fr')
    """
    try:
        from tech_articles.newsletter.models import NewsletterSubscriber
        from django.utils import translation
        from django.urls import translate_url

        subscriber = NewsletterSubscriber.objects.get(id=subscriber_id)

        # Build path using reverse (path without domain)
        path = reverse('newsletter:confirm-subscription', kwargs={'token': subscriber.unsub_token})

        # Ensure the path is translated/has language prefix using translate_url
        translated_path = translate_url(path, language)

        site_url = getattr(settings, 'SITE_URL', '') or ''
        confirmation_url = f"{site_url.rstrip('/')}{translated_path}"

        # Unsubscribe URL
        unsubscribe_path = reverse('newsletter:unsubscribe', kwargs={'token': subscriber.unsub_token})
        unsubscribe_translated = translate_url(unsubscribe_path, language)
        unsubscribe_url = f"{site_url.rstrip('/')}{unsubscribe_translated}"

        context = {
            'confirmation_url': confirmation_url,
            'unsubscribe_url': unsubscribe_url,
            'site_url': site_url,
            'subscriber_email': subscriber_email,
        }

        # Activate language for email rendering
        translation.activate(language)

        success = EmailUtil.send_email_with_template(
            template='tech-articles/emails/newsletter/confirmation.html',
            context=context,
            receivers=[subscriber_email],
            subject=str(_('Confirm your newsletter subscription')),
        )

        translation.deactivate()

        if success:
            logger.info(f'Confirmation email sent to {subscriber_email}')
        else:
            logger.error(f'Failed to send confirmation email to {subscriber_email}')
            raise Exception('Failed to send confirmation email')

        return True

    except Exception as exc:
        logger.exception(f'Error sending confirmation email to {subscriber_email}: {exc}')
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@shared_task(bind=True, max_retries=3)
def send_newsletter_welcome_email(self, subscriber_id: str, subscriber_email: str, language: str):
    """
    Send welcome email to confirmed newsletter subscriber.

    Args:
        subscriber_id: UUID of the subscriber
        subscriber_email: Email address of the subscriber
        language: Preferred language code (e.g., 'en', 'fr')
    """
    try:
        from tech_articles.newsletter.models import NewsletterSubscriber
        from django.utils import translation
        from django.urls import translate_url

        subscriber = NewsletterSubscriber.objects.get(id=subscriber_id)

        unsubscribe_path = reverse('newsletter:unsubscribe', kwargs={'token': subscriber.unsub_token})
        unsubscribe_translated = translate_url(unsubscribe_path, language)

        site_url = getattr(settings, 'SITE_URL', '') or ''
        unsubscribe_url = f"{site_url.rstrip('/')}{unsubscribe_translated}"

        context = {
            'site_url': site_url,
            'unsubscribe_url': unsubscribe_url,
            'subscriber_email': subscriber_email,
        }

        # Activate language for email rendering
        translation.activate(language)

        success = EmailUtil.send_email_with_template(
            template='tech-articles/emails/newsletter/welcome.html',
            context=context,
            receivers=[subscriber_email],
            subject=str(_('Welcome to Runbookly!')),
        )

        translation.deactivate()

        if success:
            logger.info(f'Welcome email sent to {subscriber_email}')
        else:
            logger.error(f'Failed to send welcome email to {subscriber_email}')
            raise Exception('Failed to send welcome email')

        return True

    except Exception as exc:
        logger.exception(f'Error sending welcome email to {subscriber_email}: {exc}')
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
