import logging
import math
import uuid

from django.db.models import Q
from django.http import JsonResponse
from django.views import View
from django.views.generic import TemplateView

from tech_articles.billing.models import Plan
from tech_articles.content.models import Article, Category, FeaturedArticles
from tech_articles.utils.enums import ArticleStatus

logger = logging.getLogger(__name__)

# Singleton UUID for FeaturedArticles configuration
FEATURED_ARTICLES_UUID = uuid.UUID('00000000-0000-0000-0000-000000000000')

ARTICLES_PER_PAGE = 6


def _serialize_article(article):
    """Serialize an Article instance to a JSON-safe dict."""
    categories = list(
        article.categories.values_list("name", flat=True)
    )
    return {
        "id": str(article.id),
        "title": article.title,
        "slug": article.slug,
        "summary": article.summary,
        "language": article.language,
        "reading_time_minutes": article.reading_time_minutes,
        "cover_image_key": article.cover_image_key,
        "cover_alt_text": article.cover_alt_text,
        "access_type": article.access_type,
        "difficulty": article.difficulty,
        "categories": categories,
        "published_at": (
            article.published_at.isoformat() if article.published_at else None
        ),
    }


class HomePageView(TemplateView):
    """
    Home page view that displays featured articles, categories, and popular tags.

    This view uses class-based view (CBV) for better organization and reusability.
    It retrieves and filters content based on publication status and active state.
    Featured articles are retrieved from the FeaturedArticles configuration model.
    """

    template_name = "tech-articles/home/pages/index.html"

    def get_context_data(self, **kwargs):
        """Add active plans and featured articles to context."""
        context = super().get_context_data(**kwargs)
        context["active_plans"] = Plan.objects.filter(is_active=True).prefetch_related("plan_features")
        
        # Get featured articles configuration (create if doesn't exist)
        featured_config, created = FeaturedArticles.objects.get_or_create(pk=FEATURED_ARTICLES_UUID)
        context["first_featured_article"] = featured_config.first_feature
        context["second_featured_article"] = featured_config.second_feature
        context["third_featured_article"] = featured_config.third_feature
        
        return context


class ArticlesListView(TemplateView):
    """Articles listing page with lazy-loaded dynamic content."""

    template_name = "tech-articles/home/pages/articles/articles_list.html"


class ArticlesApiView(View):
    """
    API endpoint for paginated articles listing with search, sort, and filter.

    Query parameters:
      - page (int): page number (default 1)
      - search (str): search term for title/summary
      - sort (str): 'recent' | 'oldest' | 'popular' (default 'recent')
      - categories (str): comma-separated category IDs (UUIDs)
    """

    http_method_names = ["get"]

    def get(self, request):
        qs = Article.objects.filter(
            status=ArticleStatus.PUBLISHED,
        ).prefetch_related("categories")

        # Search
        search = request.GET.get("search", "").strip()
        if search:
            qs = qs.filter(
                Q(title__icontains=search) | Q(summary__icontains=search)
            )

        # Category filter
        categories_param = request.GET.get("categories", "").strip()
        if categories_param:
            category_ids = [
                cid.strip()
                for cid in categories_param.split(",")
                if cid.strip()
            ]
            if category_ids:
                qs = qs.filter(categories__id__in=category_ids).distinct()

        # Sort
        sort = request.GET.get("sort", "recent")
        if sort == "oldest":
            qs = qs.order_by("published_at", "created_at")
        elif sort == "popular":
            qs = qs.order_by("-reading_time_minutes", "-published_at")
        else:
            qs = qs.order_by("-published_at", "-created_at")

        # Pagination
        total_count = qs.count()
        total_pages = max(1, math.ceil(total_count / ARTICLES_PER_PAGE))

        try:
            page = int(request.GET.get("page", 1))
        except (ValueError, TypeError):
            page = 1
        page = max(1, min(page, total_pages))

        start = (page - 1) * ARTICLES_PER_PAGE
        end = start + ARTICLES_PER_PAGE
        articles = qs[start:end]

        return JsonResponse({
            "articles": [_serialize_article(a) for a in articles],
            "pagination": {
                "current_page": page,
                "total_pages": total_pages,
                "total_count": total_count,
                "per_page": ARTICLES_PER_PAGE,
                "has_previous": page > 1,
                "has_next": page < total_pages,
            },
        })


class FeaturedArticlesApiView(View):
    """API endpoint returning the three featured articles."""

    http_method_names = ["get"]

    def get(self, request):
        featured_config, _ = FeaturedArticles.objects.get_or_create(
            pk=FEATURED_ARTICLES_UUID
        )
        result = []
        for attr in ("first_feature", "second_feature", "third_feature"):
            article = getattr(featured_config, attr)
            if article and article.status == ArticleStatus.PUBLISHED:
                categories = list(
                    article.categories.values_list("name", flat=True)
                )
                result.append({
                    "id": str(article.id),
                    "title": article.title,
                    "slug": article.slug,
                    "summary": article.summary,
                    "cover_image_key": article.cover_image_key,
                    "cover_alt_text": article.cover_alt_text,
                    "categories": categories,
                })
        return JsonResponse({"featured": result})


class RelatedArticlesApiView(View):
    """API endpoint returning related (recent) articles for the sidebar."""

    http_method_names = ["get"]

    def get(self, request):
        articles = (
            Article.objects.filter(status=ArticleStatus.PUBLISHED)
            .prefetch_related("categories")
            .order_by("-published_at", "-created_at")[:4]
        )
        result = []
        for article in articles:
            categories = list(
                article.categories.values_list("name", flat=True)
            )
            result.append({
                "id": str(article.id),
                "title": article.title,
                "slug": article.slug,
                "summary": article.summary,
                "reading_time_minutes": article.reading_time_minutes,
                "categories": categories,
            })
        return JsonResponse({"related": result})


class CategoriesApiView(View):
    """API endpoint returning active categories for filter dropdowns."""

    http_method_names = ["get"]

    def get(self, request):
        categories = Category.objects.filter(is_active=True).order_by(
            "sort_order", "name"
        )
        result = [
            {"id": str(c.id), "name": c.name, "slug": c.slug}
            for c in categories
        ]
        return JsonResponse({"categories": result})


class ArticleDetailView(TemplateView):
    """
    Article detail page (design-only template view).

    No query parameters or slug routing needed at this stage —
    the view simply renders the static detail template as a design preview.
    """

    template_name = "tech-articles/home/pages/articles/article_detail.html"


class ArticlePreviewView(TemplateView):
    """
    Article preview page — locked / paywall experience.

    Shows the article hero, cover image, and the first two intro paragraphs,
    then overlays a gradient-fade + "Unlock the full article" CTA panel.

    This is a standalone template (article_preview.html) intentionally separate
    from article_detail.html so the two experiences can evolve independently.
    It contains no comments, no pagination, and no resources section.
    """

    template_name = "tech-articles/home/pages/articles/article_preview.html"


class AppointmentListHomeView(TemplateView):
    """
    Display available appointment time slots in a weekly calendar view.
    Users can browse and select available time slots.
    """
    template_name = "tech-articles/home/pages/appointments/list.html"


class AppointmentDetailHomeView(TemplateView):
    """
    Display appointment details including time, duration, and amount.
    Users can review and confirm the appointment before payment.
    """
    template_name = "tech-articles/home/pages/appointments/detail.html"


class AppointmentPaymentHomeView(TemplateView):
    """
    Payment page for confirmed appointments.
    Final step in the appointment booking flow.
    """
    template_name = "tech-articles/home/pages/appointments/payment.html"

