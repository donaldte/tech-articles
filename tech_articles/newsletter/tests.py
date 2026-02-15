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

