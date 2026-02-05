"""
Tests for Article Status API Views.
"""
import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from tech_articles.content.models import Article
from tech_articles.utils.enums import ArticleStatus, LanguageChoices

User = get_user_model()


class ArticleStatusAPITestCase(TestCase):
    """Test cases for article status transition API views."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()

        # Create admin user
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            is_staff=True,
            is_superuser=True
        )

        # Create regular user
        self.regular_user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='userpass123'
        )

        # Create test articles in different statuses
        self.draft_article = Article.objects.create(
            title='Draft Article',
            slug='draft-article',
            language=LanguageChoices.EN,
            status=ArticleStatus.DRAFT,
            author=self.admin
        )

        self.published_article = Article.objects.create(
            title='Published Article',
            slug='published-article',
            language=LanguageChoices.EN,
            status=ArticleStatus.PUBLISHED,
            author=self.admin
        )

        self.archived_article = Article.objects.create(
            title='Archived Article',
            slug='archived-article',
            language=LanguageChoices.EN,
            status=ArticleStatus.ARCHIVED,
            author=self.admin
        )

    def test_publish_draft_article_success(self):
        """Test publishing a draft article succeeds."""
        self.client.login(username='admin', password='adminpass123')
        url = reverse('content:articles_api_publish', kwargs={'pk': self.draft_article.pk})
        
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['article']['status'], ArticleStatus.PUBLISHED)
        
        # Verify database was updated
        self.draft_article.refresh_from_db()
        self.assertEqual(self.draft_article.status, ArticleStatus.PUBLISHED)

    def test_publish_already_published_article_fails(self):
        """Test publishing an already published article fails."""
        self.client.login(username='admin', password='adminpass123')
        url = reverse('content:articles_api_publish', kwargs={'pk': self.published_article.pk})
        
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertFalse(data['success'])

    def test_archive_published_article_success(self):
        """Test archiving a published article succeeds."""
        self.client.login(username='admin', password='adminpass123')
        url = reverse('content:articles_api_archive', kwargs={'pk': self.published_article.pk})
        
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['article']['status'], ArticleStatus.ARCHIVED)
        
        # Verify database was updated
        self.published_article.refresh_from_db()
        self.assertEqual(self.published_article.status, ArticleStatus.ARCHIVED)

    def test_archive_draft_article_fails(self):
        """Test archiving a draft article fails."""
        self.client.login(username='admin', password='adminpass123')
        url = reverse('content:articles_api_archive', kwargs={'pk': self.draft_article.pk})
        
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertFalse(data['success'])

    def test_restore_archived_article_success(self):
        """Test restoring an archived article succeeds."""
        self.client.login(username='admin', password='adminpass123')
        url = reverse('content:articles_api_restore', kwargs={'pk': self.archived_article.pk})
        
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['article']['status'], ArticleStatus.PUBLISHED)
        
        # Verify database was updated
        self.archived_article.refresh_from_db()
        self.assertEqual(self.archived_article.status, ArticleStatus.PUBLISHED)

    def test_restore_published_article_fails(self):
        """Test restoring a published article fails."""
        self.client.login(username='admin', password='adminpass123')
        url = reverse('content:articles_api_restore', kwargs={'pk': self.published_article.pk})
        
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertFalse(data['success'])

    def test_non_admin_user_cannot_change_status(self):
        """Test that regular users cannot change article status."""
        self.client.login(username='user', password='userpass123')
        url = reverse('content:articles_api_publish', kwargs={'pk': self.draft_article.pk})
        
        response = self.client.post(url)
        
        # Should be forbidden or redirected
        self.assertIn(response.status_code, [302, 403])

    def test_unauthenticated_user_cannot_change_status(self):
        """Test that unauthenticated users cannot change article status."""
        url = reverse('content:articles_api_publish', kwargs={'pk': self.draft_article.pk})
        
        response = self.client.post(url)
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)

    def test_article_not_found(self):
        """Test handling of non-existent article."""
        self.client.login(username='admin', password='adminpass123')
        url = reverse('content:articles_api_publish', kwargs={'pk': '00000000-0000-0000-0000-000000000000'})
        
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.content)
        self.assertFalse(data['success'])

    def test_response_contains_status_display(self):
        """Test that response contains human-readable status display."""
        self.client.login(username='admin', password='adminpass123')
        url = reverse('content:articles_api_publish', kwargs={'pk': self.draft_article.pk})
        
        response = self.client.post(url)
        
        data = json.loads(response.content)
        self.assertIn('status_display', data['article'])
        self.assertIsNotNone(data['article']['status_display'])
