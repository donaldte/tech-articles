"""
Management command to send a test newsletter email.

Usage:
    python manage.py send_test_newsletter <email> [--type daily|digest]

Examples:
    python manage.py send_test_newsletter admin@example.com
    python manage.py send_test_newsletter admin@example.com --type digest
"""
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Command(BaseCommand):
    help = _("Send a test newsletter to a given email address")

    def add_arguments(self, parser):
        parser.add_argument(
            "email",
            type=str,
            help=_("Email address to receive the test newsletter"),
        )
        parser.add_argument(
            "--type",
            dest="newsletter_type",
            default="daily",
            choices=["daily", "digest"],
            help=_("Newsletter type: 'daily' (single article) or 'digest' (top 3 articles). Default: daily"),
        )
        parser.add_argument(
            "--language",
            dest="language",
            default="en",
            help=_("Language code for the email (e.g. en, fr). Default: en"),
        )

    def handle(self, *args, **options):
        from django.conf import settings
        from django.db.models import Count
        from django.utils import translation as _translation

        from tech_articles.content.models import Article
        from tech_articles.newsletter.tasks import (
            _build_unsubscribe_url,
            _serialize_article_for_email,
        )
        from tech_articles.utils.email import EmailUtil
        from tech_articles.utils.enums import ArticleStatus

        email = options["email"]
        newsletter_type = options["newsletter_type"]
        language = options["language"]
        site_url = getattr(settings, "SITE_URL", "").rstrip("/")

        _translation.activate(language)

        # Build a fake subscriber object for URL generation
        class _FakeSubscriber:
            unsub_token = "test-token"

        fake_subscriber = _FakeSubscriber()
        unsubscribe_url = f"{site_url}/?unsubscribe=test"

        if newsletter_type == "daily":
            self._send_daily_test(email, language, site_url, unsubscribe_url)
        else:
            self._send_digest_test(email, language, site_url, unsubscribe_url)

        _translation.deactivate()

    def _send_daily_test(self, email: str, language: str, site_url: str, unsubscribe_url: str):
        """Send a test daily newsletter."""
        from django.conf import settings
        from django.utils.translation import gettext as _

        from tech_articles.content.models import Article
        from tech_articles.newsletter.tasks import _serialize_article_for_email
        from tech_articles.utils.email import EmailUtil
        from tech_articles.utils.enums import ArticleStatus

        article_qs = (
            Article.objects.filter(status=ArticleStatus.PUBLISHED)
            .prefetch_related("categories")
            .order_by("-published_at")
        )
        article = article_qs.first()

        if article is None:
            self.stderr.write(self.style.WARNING("No published articles found. Sending empty daily email."))
            article_data = {
                "title": "Sample Article Title",
                "url": site_url,
                "excerpt": "This is a sample excerpt for the test email.",
                "image_url": "",
                "category": "Technology",
                "reading_time": 5,
            }
        else:
            article_data = _serialize_article_for_email(article, language, "test_daily")

        context = {
            "article": article_data,
            "subscriber_email": email,
            "unsubscribe_url": unsubscribe_url,
            "site_url": site_url,
            "current_date": timezone.now(),
        }

        subject = str(_("[TEST] Article of the day: %(title)s") % {"title": article_data["title"]})
        success = EmailUtil.send_email_with_template(
            template="tech-articles/emails/newsletter/daily.html",
            context=context,
            receivers=[email],
            subject=subject,
        )

        if success:
            self.stdout.write(self.style.SUCCESS(f"✅ Test daily newsletter sent to {email}"))
        else:
            self.stderr.write(self.style.ERROR(f"❌ Failed to send test daily newsletter to {email}"))

    def _send_digest_test(self, email: str, language: str, site_url: str, unsubscribe_url: str):
        """Send a test digest newsletter."""
        from datetime import timedelta

        from django.conf import settings
        from django.db.models import Count
        from django.utils.translation import gettext as _

        from tech_articles.content.models import Article
        from tech_articles.newsletter.tasks import _serialize_article_for_email
        from tech_articles.utils.email import EmailUtil
        from tech_articles.utils.enums import ArticleStatus

        week_ago = timezone.now() - timedelta(days=7)
        articles_qs = (
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

        if not articles_qs:
            # Fall back to the 3 most recent published articles
            articles_qs = (
                Article.objects.filter(status=ArticleStatus.PUBLISHED)
                .prefetch_related("categories")
                .order_by("-published_at")[:3]
            )

        if not articles_qs:
            self.stderr.write(self.style.WARNING("No published articles found. Sending empty digest."))
            articles_data = []
        else:
            articles_data = [_serialize_article_for_email(a, language, "test_digest") for a in articles_qs]

        context = {
            "articles": articles_data,
            "subscriber_email": email,
            "unsubscribe_url": unsubscribe_url,
            "site_url": site_url,
            "current_date": timezone.now(),
        }

        subject = str(_("[TEST] Your weekly digest — top articles this week"))
        success = EmailUtil.send_email_with_template(
            template="tech-articles/emails/newsletter/digest.html",
            context=context,
            receivers=[email],
            subject=subject,
        )

        if success:
            self.stdout.write(self.style.SUCCESS(f"✅ Test digest newsletter sent to {email}"))
        else:
            self.stderr.write(self.style.ERROR(f"❌ Failed to send test digest newsletter to {email}"))
