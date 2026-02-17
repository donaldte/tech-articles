import json
import logging

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone

from tech_articles.content.models import Article, Category, FeaturedArticles
from tech_articles.utils.constants import FEATURED_ARTICLES_UUID
from tech_articles.utils.enums import ArticleStatus, LanguageChoices

logger = logging.getLogger(__name__)
User = get_user_model()


class ArticlesApiViewTest(TestCase):
    """Test cases for the paginated articles API endpoint."""

    def setUp(self):
        self.client = Client()
        self.author = User.objects.create_user(
            username='testauthor',
            email='author@example.com',
            password='testpass123',
        )
        self.category1 = Category.objects.create(
            name='DevOps', is_active=True, sort_order=1,
        )
        self.category2 = Category.objects.create(
            name='Backend', is_active=True, sort_order=2,
        )

        for i in range(8):
            article = Article.objects.create(
                title=f'Article {i + 1}',
                summary=f'Summary for article {i + 1}',
                author=self.author,
                status=ArticleStatus.PUBLISHED,
                language=LanguageChoices.EN,
                reading_time_minutes=5 + i,
                published_at=timezone.now(),
            )
            article.categories.add(
                self.category1 if i % 2 == 0 else self.category2,
            )

    def test_articles_api_returns_json(self):
        response = self.client.get(reverse('common:api_articles'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_articles_api_pagination_structure(self):
        response = self.client.get(reverse('common:api_articles'))
        data = json.loads(response.content)
        self.assertIn('articles', data)
        self.assertIn('pagination', data)
        pagination = data['pagination']
        self.assertIn('current_page', pagination)
        self.assertIn('total_pages', pagination)
        self.assertIn('total_count', pagination)
        self.assertIn('has_previous', pagination)
        self.assertIn('has_next', pagination)

    def test_articles_api_default_page_size(self):
        response = self.client.get(reverse('common:api_articles'))
        data = json.loads(response.content)
        self.assertEqual(len(data['articles']), 6)
        self.assertEqual(data['pagination']['total_count'], 8)
        self.assertEqual(data['pagination']['total_pages'], 2)

    def test_articles_api_page_2(self):
        response = self.client.get(reverse('common:api_articles'), {'page': 2})
        data = json.loads(response.content)
        self.assertEqual(len(data['articles']), 2)
        self.assertEqual(data['pagination']['current_page'], 2)
        self.assertFalse(data['pagination']['has_next'])
        self.assertTrue(data['pagination']['has_previous'])

    def test_articles_api_search(self):
        response = self.client.get(
            reverse('common:api_articles'), {'search': 'Article 1'},
        )
        data = json.loads(response.content)
        self.assertGreater(len(data['articles']), 0)
        for article in data['articles']:
            self.assertIn('Article 1', article['title'])

    def test_articles_api_category_filter(self):
        response = self.client.get(
            reverse('common:api_articles'),
            {'categories': str(self.category1.id)},
        )
        data = json.loads(response.content)
        self.assertGreater(len(data['articles']), 0)

    def test_articles_api_sort_oldest(self):
        response = self.client.get(
            reverse('common:api_articles'), {'sort': 'oldest'},
        )
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(data['articles']), 0)

    def test_articles_api_excludes_drafts(self):
        Article.objects.create(
            title='Draft Article',
            summary='Draft summary',
            author=self.author,
            status=ArticleStatus.DRAFT,
            language=LanguageChoices.EN,
        )
        response = self.client.get(reverse('common:api_articles'))
        data = json.loads(response.content)
        titles = [a['title'] for a in data['articles']]
        self.assertNotIn('Draft Article', titles)

    def test_articles_api_article_fields(self):
        response = self.client.get(reverse('common:api_articles'))
        data = json.loads(response.content)
        article = data['articles'][0]
        expected_fields = [
            'id', 'title', 'slug', 'summary', 'language',
            'reading_time_minutes', 'cover_image_url', 'categories',
            'published_at', 'access_type', 'difficulty',
        ]
        for field in expected_fields:
            self.assertIn(field, article)

    def test_articles_api_invalid_page(self):
        response = self.client.get(
            reverse('common:api_articles'), {'page': 'abc'},
        )
        data = json.loads(response.content)
        self.assertEqual(data['pagination']['current_page'], 1)

    def test_articles_api_empty_search(self):
        response = self.client.get(
            reverse('common:api_articles'), {'search': 'nonexistent xyz'},
        )
        data = json.loads(response.content)
        self.assertEqual(len(data['articles']), 0)
        self.assertEqual(data['pagination']['total_count'], 0)


class FeaturedArticlesApiViewTest(TestCase):
    """Test cases for the featured articles API endpoint."""

    def setUp(self):
        self.client = Client()
        self.author = User.objects.create_user(
            username='testauthor',
            email='author@example.com',
            password='testpass123',
        )

    def test_featured_api_returns_json(self):
        response = self.client.get(reverse('common:api_featured_articles'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_featured_api_empty_config(self):
        response = self.client.get(reverse('common:api_featured_articles'))
        data = json.loads(response.content)
        self.assertIn('featured', data)
        self.assertEqual(len(data['featured']), 0)

    def test_featured_api_with_articles(self):
        article1 = Article.objects.create(
            title='Featured 1',
            summary='Summary 1',
            author=self.author,
            status=ArticleStatus.PUBLISHED,
            language=LanguageChoices.EN,
            published_at=timezone.now(),
        )
        article2 = Article.objects.create(
            title='Featured 2',
            summary='Summary 2',
            author=self.author,
            status=ArticleStatus.PUBLISHED,
            language=LanguageChoices.FR,
            published_at=timezone.now(),
        )
        featured, _ = FeaturedArticles.objects.get_or_create(
            pk=FEATURED_ARTICLES_UUID,
        )
        featured.first_feature = article1
        featured.second_feature = article2
        featured.save()

        response = self.client.get(reverse('common:api_featured_articles'))
        data = json.loads(response.content)
        self.assertEqual(len(data['featured']), 2)
        self.assertEqual(data['featured'][0]['title'], 'Featured 1')

    def test_featured_api_excludes_draft_articles(self):
        draft = Article.objects.create(
            title='Draft Featured',
            summary='Draft summary',
            author=self.author,
            status=ArticleStatus.DRAFT,
            language=LanguageChoices.EN,
        )
        featured, _ = FeaturedArticles.objects.get_or_create(
            pk=FEATURED_ARTICLES_UUID,
        )
        featured.first_feature = draft
        featured.save()

        response = self.client.get(reverse('common:api_featured_articles'))
        data = json.loads(response.content)
        self.assertEqual(len(data['featured']), 0)


class RelatedArticlesApiViewTest(TestCase):
    """Test cases for the related articles API endpoint."""

    def setUp(self):
        self.client = Client()
        self.author = User.objects.create_user(
            username='testauthor',
            email='author@example.com',
            password='testpass123',
        )

    def test_related_api_returns_json(self):
        response = self.client.get(reverse('common:api_related_articles'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_related_api_empty(self):
        response = self.client.get(reverse('common:api_related_articles'))
        data = json.loads(response.content)
        self.assertIn('related', data)
        self.assertEqual(len(data['related']), 0)

    def test_related_api_max_four(self):
        for i in range(6):
            Article.objects.create(
                title=f'Related {i + 1}',
                summary=f'Summary {i + 1}',
                author=self.author,
                status=ArticleStatus.PUBLISHED,
                language=LanguageChoices.EN,
                reading_time_minutes=5,
                published_at=timezone.now(),
            )
        response = self.client.get(reverse('common:api_related_articles'))
        data = json.loads(response.content)
        self.assertEqual(len(data['related']), 4)

    def test_related_api_article_fields(self):
        Article.objects.create(
            title='Test Related',
            summary='Summary',
            author=self.author,
            status=ArticleStatus.PUBLISHED,
            language=LanguageChoices.EN,
            reading_time_minutes=5,
            published_at=timezone.now(),
        )
        response = self.client.get(reverse('common:api_related_articles'))
        data = json.loads(response.content)
        article = data['related'][0]
        self.assertIn('title', article)
        self.assertIn('reading_time_minutes', article)
        self.assertIn('categories', article)


class CategoriesApiViewTest(TestCase):
    """Test cases for the categories API endpoint."""

    def setUp(self):
        self.client = Client()

    def test_categories_api_returns_json(self):
        response = self.client.get(reverse('common:api_categories'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_categories_api_returns_active_only(self):
        Category.objects.create(name='Active Cat', is_active=True)
        Category.objects.create(name='Inactive Cat', is_active=False)

        response = self.client.get(reverse('common:api_categories'))
        data = json.loads(response.content)
        names = [c['name'] for c in data['categories']]
        self.assertIn('Active Cat', names)
        self.assertNotIn('Inactive Cat', names)

    def test_categories_api_fields(self):
        Category.objects.create(name='Test Cat', is_active=True)
        response = self.client.get(reverse('common:api_categories'))
        data = json.loads(response.content)
        cat = data['categories'][0]
        self.assertIn('id', cat)
        self.assertIn('name', cat)
        self.assertIn('slug', cat)


class ArticlesListViewTest(TestCase):
    """Test cases for the articles listing template view."""

    def test_articles_list_status_code(self):
        response = self.client.get(reverse('common:articles_list'))
        self.assertEqual(response.status_code, 200)

    def test_articles_list_template(self):
        response = self.client.get(reverse('common:articles_list'))
        self.assertTemplateUsed(
            response,
            'tech-articles/home/pages/articles/articles_list.html',
        )
