import logging
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone

from tech_articles.content.models import Article, Category, Tag
from tech_articles.utils.enums import ArticleStatus

logger = logging.getLogger(__name__)
User = get_user_model()


class HomePageViewTest(TestCase):
    """Test cases for HomePageView."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()

        # Create a test author
        self.author = User.objects.create_user(
            username='testauthor',
            email='author@example.com',
            password='testpass123'
        )

        # Create categories
        self.category1 = Category.objects.create(
            name='Python',
            is_active=True,
            sort_order=1
        )
        self.category2 = Category.objects.create(
            name='Django',
            is_active=True,
            sort_order=2
        )
        self.category3 = Category.objects.create(
            name='Inactive Category',
            is_active=False,
            sort_order=3
        )

        # Create tags
        self.tag1 = Tag.objects.create(name='Web Development')
        self.tag2 = Tag.objects.create(name='Backend')
        self.tag3 = Tag.objects.create(name='REST API')

        # Create published articles
        for i in range(15):
            article = Article.objects.create(
                title=f'Test Article {i+1}',
                description=f'Description for article {i+1}',
                author=self.author,
                status=ArticleStatus.PUBLISHED,
                is_published=True,
                published_at=timezone.now()
            )
            article.categories.add(self.category1 if i % 2 == 0 else self.category2)
            article.tags.add(self.tag1)
            if i % 2 == 0:
                article.tags.add(self.tag2)

    def test_home_page_status_code(self):
        """Test that home page returns 200 OK."""
        response = self.client.get(reverse('common:home'))
        self.assertEqual(response.status_code, 200)

    def test_home_page_template_used(self):
        """Test that correct template is used."""
        response = self.client.get(reverse('common:home'))
        self.assertTemplateUsed(response, 'pages/index.html')

    def test_context_contains_featured_articles(self):
        """Test that context contains featured articles."""
        response = self.client.get(reverse('common:home'))
        self.assertIn('featured_articles', response.context)
        articles = list(response.context['featured_articles'])
        self.assertEqual(len(articles), 12)  # Default limit

    def test_context_contains_categories(self):
        """Test that context contains active categories."""
        response = self.client.get(reverse('common:home'))
        self.assertIn('categories', response.context)
        categories = list(response.context['categories'])
        # Should have 2 active categories (not the inactive one)
        self.assertLessEqual(len(categories), 2)
        # All should be active
        for cat in categories:
            self.assertTrue(cat.is_active)

    def test_context_contains_popular_tags(self):
        """Test that context contains popular tags."""
        response = self.client.get(reverse('common:home'))
        self.assertIn('popular_tags', response.context)
        tags = list(response.context['popular_tags'])
        self.assertGreater(len(tags), 0)

    def test_context_contains_page_metadata(self):
        """Test that context contains page metadata."""
        response = self.client.get(reverse('common:home'))
        self.assertIn('page_title', response.context)
        self.assertIn('page_description', response.context)

    def test_featured_articles_are_published(self):
        """Test that only published articles are shown."""
        # Create an unpublished article
        unpublished = Article.objects.create(
            title='Unpublished Article',
            description='This should not appear',
            author=self.author,
            status=ArticleStatus.DRAFT,
            is_published=False,
        )

        response = self.client.get(reverse('common:home'))
        articles = list(response.context['featured_articles'])
        article_ids = [a.id for a in articles]

        self.assertNotIn(unpublished.id, article_ids)

    def test_featured_articles_ordered_by_published_date(self):
        """Test that featured articles are ordered by published date."""
        response = self.client.get(reverse('common:home'))
        articles = list(response.context['featured_articles'])

        # Check that articles are ordered by published_at (descending)
        for i in range(len(articles) - 1):
            self.assertGreaterEqual(
                articles[i].published_at,
                articles[i+1].published_at
            )

    def test_categories_have_article_count(self):
        """Test that categories have article_count annotation."""
        response = self.client.get(reverse('common:home'))
        categories = list(response.context['categories'])

        for cat in categories:
            self.assertTrue(hasattr(cat, 'article_count'))
            self.assertGreaterEqual(cat.article_count, 0)

    def test_tags_have_article_count(self):
        """Test that tags have article_count annotation."""
        response = self.client.get(reverse('common:home'))
        tags = list(response.context['popular_tags'])

        for tag in tags:
            self.assertTrue(hasattr(tag, 'article_count'))
            self.assertGreater(tag.article_count, 0)

    def test_empty_database(self):
        """Test view handles empty database gracefully."""
        # Clear all data
        Article.objects.all().delete()
        Category.objects.all().delete()
        Tag.objects.all().delete()

        response = self.client.get(reverse('common:home'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('featured_articles', response.context)
        self.assertEqual(len(response.context['featured_articles']), 0)

    def test_featured_articles_limit(self):
        """Test that featured articles respects the limit."""
        # Create 20 more articles (total 35)
        for i in range(20):
            Article.objects.create(
                title=f'Extra Article {i+1}',
                author=self.author,
                status=ArticleStatus.PUBLISHED,
                is_published=True,
                published_at=timezone.now()
            )

        response = self.client.get(reverse('common:home'))
        articles = list(response.context['featured_articles'])
        self.assertEqual(len(articles), 12)  # Default limit

    def test_categories_limit(self):
        """Test that categories respects the limit."""
        response = self.client.get(reverse('common:home'))
        categories = list(response.context['categories'])
        self.assertLessEqual(len(categories), 8)  # Default limit

    def test_tags_limit(self):
        """Test that tags respects the limit."""
        response = self.client.get(reverse('common:home'))
        tags = list(response.context['popular_tags'])
        self.assertLessEqual(len(tags), 20)  # Default limit

    def test_response_contains_article_title(self):
        """Test that response contains article titles."""
        response = self.client.get(reverse('common:home'))
        self.assertEqual(response.status_code, 200)
        # Check that at least one article title is in the response content
        self.assertContains(response, 'Test Article')

    def test_author_relationship(self):
        """Test that author relationship is properly loaded."""
        response = self.client.get(reverse('common:home'))
        articles = list(response.context['featured_articles'])

        for article in articles:
            self.assertIsNotNone(article.author)
            self.assertEqual(article.author.username, 'testauthor')

    def test_category_relationship(self):
        """Test that category relationships are properly loaded."""
        response = self.client.get(reverse('common:home'))
        articles = list(response.context['featured_articles'])

        for article in articles:
            categories = list(article.categories.all())
            self.assertGreater(len(categories), 0)

    def test_tag_relationship(self):
        """Test that tag relationships are properly loaded."""
        response = self.client.get(reverse('common:home'))
        articles = list(response.context['featured_articles'])

        for article in articles:
            tags = list(article.tags.all())
            self.assertGreater(len(tags), 0)
