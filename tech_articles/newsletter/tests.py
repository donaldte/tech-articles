"""
Tests for newsletter subscription functionality.
"""
from unittest.mock import patch
from django.test import TestCase, Client
from django.urls import reverse
from tech_articles.newsletter.models import NewsletterSubscriber


class NewsletterSubscriptionFlowTestCase(TestCase):
    """Test newsletter subscription flow."""

    def setUp(self):
        """Set up test client and data."""
        self.client = Client()
        self.subscribe_url = reverse('newsletter:subscribe')
        self.test_email = 'test@example.com'

    @patch('tech_articles.newsletter.views.subscription_views.send_newsletter_confirmation_email.delay')
    def test_new_subscription_sends_confirmation_email(self, mock_send_email):
        """Test that a new subscription sends a confirmation email."""
        response = self.client.post(self.subscribe_url, {
            'email': self.test_email,
            'language': 'fr',
        })

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertIn('Thank you for subscribing', response.json()['message'])

        # Verify subscriber was created
        subscriber = NewsletterSubscriber.objects.get(email=self.test_email)
        self.assertTrue(subscriber.is_active)
        self.assertFalse(subscriber.is_confirmed)

        # Verify confirmation email was queued
        mock_send_email.assert_called_once()

    @patch('tech_articles.newsletter.views.subscription_views.send_newsletter_confirmation_email.delay')
    def test_unconfirmed_subscriber_resubscription_sends_new_confirmation(self, mock_send_email):
        """Test that resubscribing with an unconfirmed email sends a new confirmation."""
        # Create an unconfirmed subscriber
        subscriber = NewsletterSubscriber.objects.create(
            email=self.test_email,
            language='fr',
            is_active=True,
            is_confirmed=False,
        )

        # Try to subscribe again
        response = self.client.post(self.subscribe_url, {
            'email': self.test_email,
            'language': 'fr',
        })

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertIn('Thank you for subscribing', response.json()['message'])

        # Verify subscriber is still unconfirmed
        subscriber.refresh_from_db()
        self.assertTrue(subscriber.is_active)
        self.assertFalse(subscriber.is_confirmed)

        # Verify confirmation email was queued
        mock_send_email.assert_called_once()

    @patch('tech_articles.newsletter.views.subscription_views.send_newsletter_confirmation_email.delay')
    def test_confirmed_active_subscriber_cannot_resubscribe(self, mock_send_email):
        """Test that a confirmed and active subscriber cannot resubscribe."""
        # Create a confirmed and active subscriber
        subscriber = NewsletterSubscriber.objects.create(
            email=self.test_email,
            language='fr',
            is_active=True,
            is_confirmed=True,
        )

        # Try to subscribe again
        response = self.client.post(self.subscribe_url, {
            'email': self.test_email,
            'language': 'fr',
        })

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()['success'])
        self.assertIn('email', response.json()['errors'])
        self.assertIn('already subscribed', response.json()['errors']['email'][0])

        # Verify no confirmation email was sent
        mock_send_email.assert_not_called()

    @patch('tech_articles.newsletter.views.subscription_views.send_newsletter_confirmation_email.delay')
    def test_inactive_subscriber_can_resubscribe(self, mock_send_email):
        """Test that an inactive subscriber can resubscribe."""
        # Create an inactive subscriber (previously unsubscribed)
        subscriber = NewsletterSubscriber.objects.create(
            email=self.test_email,
            language='fr',
            is_active=False,
            is_confirmed=True,
        )

        # Try to subscribe again
        response = self.client.post(self.subscribe_url, {
            'email': self.test_email,
            'language': 'fr',
        })

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])

        # Verify subscriber is now active but needs to confirm again
        subscriber.refresh_from_db()
        self.assertTrue(subscriber.is_active)
        self.assertFalse(subscriber.is_confirmed)

        # Verify confirmation email was queued
        mock_send_email.assert_called_once()


# ---------------------------------------------------------------------------
# Newsletter task tests
# ---------------------------------------------------------------------------
from unittest.mock import patch, MagicMock
from django.utils import timezone


class SendDailyNewsletterTaskTestCase(TestCase):
    """Tests for send_daily_newsletter Celery task."""

    def _make_subscriber(self, email="subscriber@example.com"):
        return NewsletterSubscriber.objects.create(
            email=email,
            language="en",
            is_active=True,
            is_confirmed=True,
        )

    def _make_article(self, days_ago=1, title="Test Article"):
        from tech_articles.content.models import Article
        from tech_articles.utils.enums import ArticleStatus, LanguageChoices
        published = timezone.now() - timezone.timedelta(days=days_ago)
        return Article.objects.create(
            title=title,
            language=LanguageChoices.EN,
            status=ArticleStatus.PUBLISHED,
            published_at=published,
        )

    @patch("tech_articles.newsletter.tasks.EmailUtil.send_email_with_template", return_value=True)
    def test_daily_sends_to_confirmed_subscribers(self, mock_send):
        """Task sends one email per confirmed active subscriber."""
        self._make_subscriber("a@example.com")
        self._make_subscriber("b@example.com")
        self._make_article(days_ago=1)

        from tech_articles.newsletter.tasks import send_daily_newsletter
        result = send_daily_newsletter()

        self.assertEqual(result["sent"], 2)
        self.assertEqual(result["skipped"], 0)
        self.assertEqual(mock_send.call_count, 2)

    @patch("tech_articles.newsletter.tasks.EmailUtil.send_email_with_template", return_value=True)
    def test_daily_skips_when_no_articles(self, mock_send):
        """Task returns early when no article was published yesterday."""
        self._make_subscriber()
        # No article created

        from tech_articles.newsletter.tasks import send_daily_newsletter
        result = send_daily_newsletter()

        self.assertEqual(result["sent"], 0)
        self.assertEqual(result.get("reason"), "no_articles")
        mock_send.assert_not_called()

    @patch("tech_articles.newsletter.tasks.EmailUtil.send_email_with_template", return_value=True)
    def test_daily_skips_inactive_subscribers(self, mock_send):
        """Task does not send to inactive or unconfirmed subscribers."""
        NewsletterSubscriber.objects.create(email="inactive@example.com", is_active=False, is_confirmed=True)
        NewsletterSubscriber.objects.create(email="unconfirmed@example.com", is_active=True, is_confirmed=False)
        self._make_article(days_ago=1)

        from tech_articles.newsletter.tasks import send_daily_newsletter
        result = send_daily_newsletter()

        self.assertEqual(result["sent"], 0)
        mock_send.assert_not_called()


class SendDigestNewsletterTaskTestCase(TestCase):
    """Tests for send_digest_newsletter Celery task."""

    def _make_subscriber(self, email="sub@example.com"):
        return NewsletterSubscriber.objects.create(
            email=email,
            language="en",
            is_active=True,
            is_confirmed=True,
        )

    def _make_article(self, days_ago=3, title="Test"):
        from tech_articles.content.models import Article
        from tech_articles.utils.enums import ArticleStatus, LanguageChoices
        published = timezone.now() - timezone.timedelta(days=days_ago)
        return Article.objects.create(
            title=title,
            language=LanguageChoices.EN,
            status=ArticleStatus.PUBLISHED,
            published_at=published,
        )

    @patch("tech_articles.newsletter.tasks.EmailUtil.send_email_with_template", return_value=True)
    def test_digest_sends_top_articles(self, mock_send):
        """Digest task sends at most 3 articles."""
        self._make_subscriber()
        for i in range(4):
            self._make_article(days_ago=i + 1, title=f"Article {i}")

        from tech_articles.newsletter.tasks import send_digest_newsletter
        result = send_digest_newsletter()

        self.assertEqual(result["sent"], 1)
        # Verify the template used
        call_kwargs = mock_send.call_args[1]
        self.assertEqual(call_kwargs.get("template"), "tech-articles/emails/newsletter/digest.html")
        # Articles list passed to context should be <= 3
        context = call_kwargs.get("context", {})
        self.assertLessEqual(len(context.get("articles", [])), 3)

    @patch("tech_articles.newsletter.tasks.EmailUtil.send_email_with_template", return_value=True)
    def test_digest_skips_when_no_articles(self, mock_send):
        """Digest task returns early when no articles exist in the last 7 days."""
        self._make_subscriber()

        from tech_articles.newsletter.tasks import send_digest_newsletter
        result = send_digest_newsletter()

        self.assertEqual(result["sent"], 0)
        self.assertEqual(result.get("reason"), "no_articles")
        mock_send.assert_not_called()
