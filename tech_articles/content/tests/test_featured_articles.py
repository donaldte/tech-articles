"""
Tests for Featured Articles functionality.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from tech_articles.content.models import Article, FeaturedArticles
from tech_articles.utils.enums import ArticleStatus, LanguageChoices, DifficultyChoices, ArticleAccessType

User = get_user_model()


class FeaturedArticlesModelTest(TestCase):
    """Test cases for FeaturedArticles model."""

    def setUp(self):
        """Set up test data."""
        # Create test articles
        self.article1 = Article.objects.create(
            title="Test Article 1",
            slug="test-article-1",
            language=LanguageChoices.ENGLISH,
            status=ArticleStatus.PUBLISHED,
            difficulty=DifficultyChoices.BEGINNER,
            access_type=ArticleAccessType.FREE,
        )
        self.article2 = Article.objects.create(
            title="Test Article 2",
            slug="test-article-2",
            language=LanguageChoices.ENGLISH,
            status=ArticleStatus.PUBLISHED,
            difficulty=DifficultyChoices.INTERMEDIATE,
            access_type=ArticleAccessType.FREE,
        )
        self.article3 = Article.objects.create(
            title="Test Article 3",
            slug="test-article-3",
            language=LanguageChoices.ENGLISH,
            status=ArticleStatus.PUBLISHED,
            difficulty=DifficultyChoices.ADVANCED,
            access_type=ArticleAccessType.FREE,
        )

    def test_featured_articles_creation(self):
        """Test creating FeaturedArticles instance."""
        featured = FeaturedArticles.objects.create(
            first_feature=self.article1,
            second_feature=self.article2,
            third_feature=self.article3,
        )
        
        self.assertEqual(featured.first_feature, self.article1)
        self.assertEqual(featured.second_feature, self.article2)
        self.assertEqual(featured.third_feature, self.article3)

    def test_featured_articles_nullable_fields(self):
        """Test that all featured article fields are nullable."""
        featured = FeaturedArticles.objects.create()
        
        self.assertIsNone(featured.first_feature)
        self.assertIsNone(featured.second_feature)
        self.assertIsNone(featured.third_feature)

    def test_featured_articles_set_null_on_delete(self):
        """Test that featured articles are set to NULL when article is deleted."""
        featured = FeaturedArticles.objects.create(
            first_feature=self.article1,
            second_feature=self.article2,
        )
        
        # Delete article1
        self.article1.delete()
        
        # Refresh from database
        featured.refresh_from_db()
        
        # First feature should be None, second should still exist
        self.assertIsNone(featured.first_feature)
        self.assertEqual(featured.second_feature, self.article2)

    def test_featured_articles_str(self):
        """Test string representation of FeaturedArticles."""
        featured = FeaturedArticles.objects.create()
        self.assertIn("Featured Articles", str(featured))


class FeaturedArticlesViewTest(TestCase):
    """Test cases for FeaturedArticles management view."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        
        # Create staff user
        self.staff_user = User.objects.create_user(
            username='staff_user',
            email='staff@example.com',
            password='testpass123',
            is_staff=True,
        )
        
        # Create regular user
        self.regular_user = User.objects.create_user(
            username='regular_user',
            email='regular@example.com',
            password='testpass123',
            is_staff=False,
        )
        
        # Create test articles
        self.article1 = Article.objects.create(
            title="Test Article 1",
            slug="test-article-1",
            language=LanguageChoices.ENGLISH,
            status=ArticleStatus.PUBLISHED,
            difficulty=DifficultyChoices.BEGINNER,
            access_type=ArticleAccessType.FREE,
        )
        
        self.url = reverse('content:featured_articles_manage')

    def test_view_requires_authentication(self):
        """Test that view requires authentication."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_view_requires_staff_permission(self):
        """Test that only staff users can access the view."""
        # Login as regular user
        self.client.login(username='regular_user', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)  # Forbidden

    def test_staff_can_access_view(self):
        """Test that staff users can access the view."""
        # Login as staff user
        self.client.login(username='staff_user', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tech-articles/dashboard/pages/featured_articles/manage.html')

    def test_view_creates_featured_articles_on_first_access(self):
        """Test that view creates FeaturedArticles instance if it doesn't exist."""
        # Login as staff user
        self.client.login(username='staff_user', password='testpass123')
        
        # Ensure no FeaturedArticles exists
        FeaturedArticles.objects.all().delete()
        
        # Access the view
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        
        # Check that FeaturedArticles was created
        self.assertTrue(FeaturedArticles.objects.exists())

    def test_staff_can_update_featured_articles(self):
        """Test that staff users can update featured articles."""
        # Login as staff user
        self.client.login(username='staff_user', password='testpass123')
        
        # Post update
        response = self.client.post(self.url, {
            'first_feature': self.article1.pk,
        })
        
        # Check redirect
        self.assertEqual(response.status_code, 302)
        
        # Check that featured articles were updated
        featured = FeaturedArticles.objects.first()
        self.assertEqual(featured.first_feature, self.article1)


class FeaturedArticlesHomeViewTest(TestCase):
    """Test cases for home view with featured articles."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        
        # Create test articles
        self.article1 = Article.objects.create(
            title="Featured Article 1",
            slug="featured-article-1",
            language=LanguageChoices.ENGLISH,
            status=ArticleStatus.PUBLISHED,
            difficulty=DifficultyChoices.BEGINNER,
            access_type=ArticleAccessType.FREE,
        )
        
        # Create featured articles configuration
        self.featured = FeaturedArticles.objects.create(
            first_feature=self.article1,
        )
        
        self.url = reverse('common:home')

    def test_home_view_includes_featured_articles(self):
        """Test that home view includes featured articles in context."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        
        # Check context includes featured articles
        self.assertIn('first_featured_article', response.context)
        self.assertIn('second_featured_article', response.context)
        self.assertIn('third_featured_article', response.context)
        
        # Check that first featured article is correct
        self.assertEqual(response.context['first_featured_article'], self.article1)
        self.assertIsNone(response.context['second_featured_article'])
        self.assertIsNone(response.context['third_featured_article'])
