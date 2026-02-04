"""
Tests for newsletter app.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from tech_articles.newsletter.models import NewsletterSubscriber, SubscriberTag
from tech_articles.newsletter.forms import NewsletterSubscribeForm
from tech_articles.utils.enums import LanguageChoices, SubscriberStatus

User = get_user_model()


class NewsletterSubscriberModelTests(TestCase):
    """Tests for NewsletterSubscriber model."""

    def test_create_subscriber(self):
        """Test creating a newsletter subscriber."""
        subscriber = NewsletterSubscriber.objects.create(
            email="test@example.com",
            language=LanguageChoices.EN,
        )
        
        self.assertEqual(subscriber.email, "test@example.com")
        self.assertEqual(subscriber.language, LanguageChoices.EN)
        self.assertFalse(subscriber.is_confirmed)
        self.assertFalse(subscriber.is_active)
        self.assertIsNotNone(subscriber.unsub_token)
        self.assertIsNotNone(subscriber.confirm_token)

    def test_confirm_subscriber(self):
        """Test confirming a subscriber."""
        subscriber = NewsletterSubscriber.objects.create(
            email="test@example.com",
            language=LanguageChoices.EN,
        )
        
        subscriber.confirm()
        
        self.assertTrue(subscriber.is_confirmed)
        self.assertIsNotNone(subscriber.confirmed_at)
        self.assertEqual(subscriber.status, SubscriberStatus.ACTIVE)

    def test_unsubscribe_subscriber(self):
        """Test unsubscribing a subscriber."""
        subscriber = NewsletterSubscriber.objects.create(
            email="test@example.com",
            language=LanguageChoices.EN,
            is_confirmed=True,
            is_active=True,
        )
        
        subscriber.unsubscribe()
        
        self.assertFalse(subscriber.is_active)
        self.assertEqual(subscriber.status, SubscriberStatus.UNSUBSCRIBED)


class NewsletterSubscribeFormTests(TestCase):
    """Tests for newsletter subscription form."""

    def test_valid_form(self):
        """Test form with valid data."""
        form_data = {
            "email": "test@example.com",
            "language": LanguageChoices.EN,
            "consent": True,
        }
        form = NewsletterSubscribeForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_duplicate_email(self):
        """Test form rejects duplicate email."""
        NewsletterSubscriber.objects.create(
            email="test@example.com",
            language=LanguageChoices.EN,
        )
        
        form_data = {
            "email": "test@example.com",
            "language": LanguageChoices.EN,
            "consent": True,
        }
        form = NewsletterSubscribeForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_missing_consent(self):
        """Test form requires consent."""
        form_data = {
            "email": "test@example.com",
            "language": LanguageChoices.EN,
            "consent": False,
        }
        form = NewsletterSubscribeForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("consent", form.errors)


class NewsletterSubscribeViewTests(TestCase):
    """Tests for newsletter subscription view."""

    def setUp(self):
        self.client = Client()

    def test_subscribe_view_get(self):
        """Test GET request to subscribe view."""
        url = reverse("newsletter:subscribe")
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Subscribe")

    def test_subscribe_view_post_valid(self):
        """Test POST request with valid data."""
        url = reverse("newsletter:subscribe")
        data = {
            "email": "test@example.com",
            "language": LanguageChoices.EN,
            "consent": True,
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 302)
        self.assertTrue(NewsletterSubscriber.objects.filter(email="test@example.com").exists())

    def test_subscribe_view_post_invalid(self):
        """Test POST request with invalid data."""
        url = reverse("newsletter:subscribe")
        data = {
            "email": "invalid-email",
            "language": LanguageChoices.EN,
            "consent": True,
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 200)
        self.assertFalse(NewsletterSubscriber.objects.filter(email="invalid-email").exists())


class NewsletterConfirmViewTests(TestCase):
    """Tests for newsletter confirmation view."""

    def setUp(self):
        self.client = Client()
        self.subscriber = NewsletterSubscriber.objects.create(
            email="test@example.com",
            language=LanguageChoices.EN,
        )

    def test_confirm_with_valid_token(self):
        """Test confirmation with valid token."""
        url = reverse("newsletter:confirm", args=[self.subscriber.confirm_token])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        self.subscriber.refresh_from_db()
        self.assertTrue(self.subscriber.is_confirmed)

    def test_confirm_with_invalid_token(self):
        """Test confirmation with invalid token."""
        url = reverse("newsletter:confirm", args=["invalid-token"])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 302)


class NewsletterUnsubscribeViewTests(TestCase):
    """Tests for newsletter unsubscribe view."""

    def setUp(self):
        self.client = Client()
        self.subscriber = NewsletterSubscriber.objects.create(
            email="test@example.com",
            language=LanguageChoices.EN,
            is_confirmed=True,
            is_active=True,
        )

    def test_unsubscribe_get(self):
        """Test GET request to unsubscribe view."""
        url = reverse("newsletter:unsubscribe", args=[self.subscriber.unsub_token])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.subscriber.email)

    def test_unsubscribe_post(self):
        """Test POST request to unsubscribe."""
        url = reverse("newsletter:unsubscribe", args=[self.subscriber.unsub_token])
        data = {"confirm": True}
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 302)
        
        self.subscriber.refresh_from_db()
        self.assertFalse(self.subscriber.is_active)
        self.assertEqual(self.subscriber.status, SubscriberStatus.UNSUBSCRIBED)

    def test_unsubscribe_invalid_token(self):
        """Test unsubscribe with invalid token."""
        url = reverse("newsletter:unsubscribe", args=["invalid-token"])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 404)


class SubscriberTagModelTests(TestCase):
    """Tests for SubscriberTag model."""

    def test_create_tag(self):
        """Test creating a subscriber tag."""
        tag = SubscriberTag.objects.create(
            name="VIP",
            description="VIP subscribers",
            color="#FF0000",
        )
        
        self.assertEqual(tag.name, "VIP")
        self.assertEqual(tag.description, "VIP subscribers")
        self.assertEqual(tag.color, "#FF0000")

