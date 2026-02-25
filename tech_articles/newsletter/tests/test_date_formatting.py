"""
Tests for newsletter email date formatting with language support.
"""
from datetime import datetime, timedelta

import pytz
from django.test import TestCase
from django.utils import timezone, translation
from django.template import Template, Context

from tech_articles.newsletter.models import NewsletterSubscriber
from tech_articles.newsletter.tasks import (
    send_daily_newsletter,
    send_digest_newsletter,
)
from tech_articles.content.models import Article, Category
from tech_articles.utils.enums import ArticleStatus


class NewsletterDateFormatTest(TestCase):
    """Test date formatting in newsletter emails for different languages."""

    def setUp(self):
        """Set up test data."""
        self.tz = pytz.timezone('America/Toronto')
        self.now = timezone.now()

        # Create test subscribers with different languages
        self.subscriber_en = NewsletterSubscriber.objects.create(
            email='test_en@example.com',
            language='en',
            is_active=True,
            is_confirmed=True,
        )
        self.subscriber_fr = NewsletterSubscriber.objects.create(
            email='test_fr@example.com',
            language='fr',
            is_active=True,
            is_confirmed=True,
        )
        self.subscriber_es = NewsletterSubscriber.objects.create(
            email='test_es@example.com',
            language='es',
            is_active=True,
            is_confirmed=True,
        )

        # Create a test article
        self.category = Category.objects.create(
            name='Technology',
            slug='technology',
        )
        self.article = Article.objects.create(
            title='Test Article',
            slug='test-article',
            status=ArticleStatus.PUBLISHED,
            published_at=self.now - timedelta(days=1),
            language='en',
            access_type='free',
        )
        self.article.categories.add(self.category)

    def test_format_date_for_locale_english(self):
        """Test date formatting for English."""
        translation.activate('en')
        template = Template("{% load newsletter_filters %}{{ date|format_date_for_locale:'en' }}")
        context = Context({'date': datetime(2024, 2, 15, tzinfo=self.tz)})
        result = template.render(context)

        # English format: "Thursday, February 15, 2024"
        self.assertIn('February', result)
        self.assertIn('15', result)
        self.assertIn('2024', result)
        translation.deactivate()

    def test_format_date_for_locale_french(self):
        """Test date formatting for French."""
        translation.activate('fr')
        template = Template("{% load newsletter_filters %}{{ date|format_date_for_locale:'fr' }}")
        context = Context({'date': datetime(2024, 2, 15, tzinfo=self.tz)})
        result = template.render(context)

        # French format should contain month in French
        self.assertIn('15', result)
        self.assertIn('2024', result)
        translation.deactivate()

    def test_format_date_for_locale_spanish(self):
        """Test date formatting for Spanish."""
        translation.activate('es')
        template = Template("{% load newsletter_filters %}{{ date|format_date_for_locale:'es' }}")
        context = Context({'date': datetime(2024, 2, 15, tzinfo=self.tz)})
        result = template.render(context)

        # Spanish format should contain "de" separators
        self.assertIn('15', result)
        self.assertIn('2024', result)
        translation.deactivate()

    def test_format_date_without_language_code(self):
        """Test date formatting without explicit language code uses current language."""
        translation.activate('en')
        template = Template("{% load newsletter_filters %}{{ date|format_date_for_locale }}")
        context = Context({'date': datetime(2024, 2, 15, tzinfo=self.tz)})
        result = template.render(context)

        # Should use English format by default
        self.assertIn('February', result)
        self.assertIn('2024', result)
        translation.deactivate()

    def test_format_date_empty_input(self):
        """Test format_date_for_locale with None input."""
        template = Template("{% load newsletter_filters %}{{ date|format_date_for_locale:'en' }}")
        context = Context({'date': None})
        result = template.render(context)

        # Should return empty string for None input
        self.assertEqual(result.strip(), '')

