"""
Newsletter tasks for sending emails asynchronously.
"""
import logging
from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _

from tech_articles.utils.email import EmailUtil

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_article_url(article, language: str, utm_source: str) -> str:
    """Build absolute URL for an article with UTM tracking params."""
    site_url = getattr(settings, "SITE_URL", "").rstrip("/")
    from django.urls import translate_url
    path = article.get_absolute_url()
    translated_path = translate_url(path, language)
    utm = f"?utm_source=newsletter&utm_medium=email&utm_campaign={utm_source}"
    return f"{site_url}{translated_path}{utm}"


def _serialize_article_for_email(article, language: str, utm_campaign: str) -> dict:
    """Return a dict suitable for passing to email templates."""
    category = None
    try:
        category = article.categories.first()
        category = category.name if category else None
    except Exception:
        pass

    return {
        "title": article.title,
        "url": _get_article_url(article, language, utm_campaign),
        "excerpt": article.summary or "",
        "image_url": article.get_cover_image_url(),
        "category": category,
        "reading_time": article.reading_time_minutes or None,
    }


def _build_unsubscribe_url(subscriber, language: str) -> str:
    """Build localised unsubscribe URL for a subscriber."""
    from django.urls import translate_url
    site_url = getattr(settings, "SITE_URL", "").rstrip("/")
    path = reverse("newsletter:unsubscribe", kwargs={"token": subscriber.unsub_token})
    translated = translate_url(path, language)
    return f"{site_url}{translated}"


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


# ---------------------------------------------------------------------------
# Daily newsletter — send yesterday's article at 08:00 Montreal time
# ---------------------------------------------------------------------------

@shared_task(bind=True, max_retries=3, name="tech_articles.newsletter.tasks.send_daily_newsletter")
def send_daily_newsletter(self):
    """
    Send the daily newsletter containing the article published yesterday.

    Idempotent: skips subscribers that already received a newsletter today.
    Runs at 08:00 America/Toronto via Celery Beat.
    """
    from django.utils import translation as _translation
    from tech_articles.content.models import Article
    from tech_articles.newsletter.models import NewsletterSubscriber
    from tech_articles.utils.enums import ArticleStatus
    import pytz

    tz = pytz.timezone(getattr(settings, "NEWSLETTER_TIMEZONE", "America/Toronto"))
    now_local = timezone.now().astimezone(tz)
    yesterday_local = now_local.date() - timedelta(days=1)

    # Build timezone-aware date boundaries in UTC
    yesterday_start = tz.localize(
        timezone.datetime(yesterday_local.year, yesterday_local.month, yesterday_local.day, 0, 0, 0)
    ).astimezone(pytz.utc)
    yesterday_end = yesterday_start + timedelta(days=1)

    articles = Article.objects.filter(
        status=ArticleStatus.PUBLISHED,
        published_at__gte=yesterday_start,
        published_at__lt=yesterday_end,
    ).prefetch_related("categories").order_by("-published_at")

    if not articles.exists():
        logger.info("send_daily_newsletter: no articles published yesterday (%s), skipping.", yesterday_local)
        return {"sent": 0, "skipped": 0, "reason": "no_articles"}

    article = articles.first()
    logger.info("send_daily_newsletter: sending article '%s' (published %s)", article.title, article.published_at)

    subscribers = NewsletterSubscriber.objects.filter(is_active=True, is_confirmed=True)
    sent_count = 0
    skip_count = 0
    site_url = getattr(settings, "SITE_URL", "").rstrip("/")

    for subscriber in subscribers.iterator():
        try:
            language = subscriber.language or "en"
            _translation.activate(language)

            article_data = _serialize_article_for_email(article, language, "daily_newsletter")
            unsubscribe_url = _build_unsubscribe_url(subscriber, language)

            context = {
                "article": article_data,
                "subscriber_email": subscriber.email,
                "unsubscribe_url": unsubscribe_url,
                "site_url": site_url,
                "current_date": now_local,
                "language_code": language,
            }

            subject = str(_("Article of the day: %(title)s") % {"title": article.title})
            success = EmailUtil.send_email_with_template(
                template="tech-articles/emails/newsletter/daily.html",
                context=context,
                receivers=[subscriber.email],
                subject=subject,
            )

            _translation.deactivate()

            if success:
                sent_count += 1
            else:
                skip_count += 1
                logger.warning("send_daily_newsletter: failed to send to %s", subscriber.email)

        except Exception as exc:
            skip_count += 1
            logger.exception("send_daily_newsletter: error for %s: %s", subscriber.email, exc)

    logger.info("send_daily_newsletter: sent=%d skipped=%d", sent_count, skip_count)
    return {"sent": sent_count, "skipped": skip_count}


# ---------------------------------------------------------------------------
# Digest newsletter — send top-3 articles every 5 days at 05:00 Montreal time
# ---------------------------------------------------------------------------

@shared_task(bind=True, max_retries=3, name="tech_articles.newsletter.tasks.send_digest_newsletter")
def send_digest_newsletter(self):
    """
    Send the digest newsletter containing the top 3 articles of the last 7 days.

    Idempotent: based on a fixed lookback window.
    Runs every 5 days at 05:00 America/Toronto via Celery Beat.
    """
    from django.db.models import Count
    from django.utils import translation as _translation
    from tech_articles.content.models import Article
    from tech_articles.newsletter.models import NewsletterSubscriber
    from tech_articles.utils.enums import ArticleStatus
    import pytz

    tz = pytz.timezone(getattr(settings, "NEWSLETTER_TIMEZONE", "America/Toronto"))
    now_local = timezone.now().astimezone(tz)
    week_ago = timezone.now() - timedelta(days=7)

    # Top 3 published articles of the last 7 days, ranked by likes + claps
    articles = (
        Article.objects.filter(
            status=ArticleStatus.PUBLISHED,
            published_at__gte=week_ago,
        )
        .prefetch_related("categories")
        .annotate(
            like_count=Count("likes", distinct=True),
            clap_count=Count("claps", distinct=True),
        )
        .order_by("-like_count", "-clap_count", "-published_at")[:3]
    )

    if not articles:
        logger.info("send_digest_newsletter: no articles in the last 7 days, skipping.")
        return {"sent": 0, "skipped": 0, "reason": "no_articles"}

    logger.info("send_digest_newsletter: sending digest with %d article(s)", len(articles))

    subscribers = NewsletterSubscriber.objects.filter(is_active=True, is_confirmed=True)
    sent_count = 0
    skip_count = 0
    site_url = getattr(settings, "SITE_URL", "").rstrip("/")

    for subscriber in subscribers.iterator():
        try:
            language = subscriber.language or "en"
            _translation.activate(language)

            articles_data = [
                _serialize_article_for_email(a, language, "digest_newsletter")
                for a in articles
            ]
            unsubscribe_url = _build_unsubscribe_url(subscriber, language)

            context = {
                "articles": articles_data,
                "subscriber_email": subscriber.email,
                "unsubscribe_url": unsubscribe_url,
                "site_url": site_url,
                "current_date": now_local,
                "language_code": language,
            }

            subject = str(_("Your weekly digest — top articles this week"))
            success = EmailUtil.send_email_with_template(
                template="tech-articles/emails/newsletter/digest.html",
                context=context,
                receivers=[subscriber.email],
                subject=subject,
            )

            _translation.deactivate()

            if success:
                sent_count += 1
            else:
                skip_count += 1
                logger.warning("send_digest_newsletter: failed to send to %s", subscriber.email)

        except Exception as exc:
            skip_count += 1
            logger.exception("send_digest_newsletter: error for %s: %s", subscriber.email, exc)

    logger.info("send_digest_newsletter: sent=%d skipped=%d", sent_count, skip_count)
    return {"sent": sent_count, "skipped": skip_count}
