"""
Public-facing article views for displaying articles to end users.

This module contains views for:
- Article listing page
- Article detail page with pagination support
- Article preview page (for premium content)
- Interactive API endpoints (claps, likes, comments)
- Article-related API endpoints (list, featured, related, categories)
"""

import logging
import math

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.views import View
from django.views.generic import TemplateView

from tech_articles.content.models import (
    Article,
    Category,
    Clap,
    Comment,
    CommentLike,
    FeaturedArticles,
    Like,
    TableOfContents,
)
from tech_articles.utils.enums import ArticleStatus, ArticleAccessType

logger = logging.getLogger(__name__)


def _serialize_article(article, fields=None):
    """Serialize an Article instance to a JSON-safe dict.

    Args:
        article: Article model instance.
        fields: Optional set of field names to include. If ``None``,
                all available fields are returned.
    """
    categories = list(article.categories.values_list("name", flat=True))
    all_fields = {
        "id": str(article.id),
        "title": article.title,
        "slug": article.slug,
        "summary": article.summary,
        "language": article.language,
        "reading_time_minutes": article.reading_time_minutes,
        "cover_image_url": article.get_cover_image_url(),
        "cover_alt_text": article.cover_alt_text,
        "access_type": article.access_type,
        "difficulty": article.difficulty,
        "categories": categories,
        "published_at": (
            article.published_at.isoformat() if article.published_at else None
        ),
    }
    if fields is None:
        return all_fields
    return {k: v for k, v in all_fields.items() if k in fields}


class ArticlesListView(TemplateView):
    """Articles listing page with lazy-loaded dynamic content."""

    template_name = "tech-articles/home/pages/articles/articles_list.html"


class ArticleDetailView(TemplateView):
    """
    Unified article detail/preview view with access control and pagination support.

    Access logic:
    - Unauthenticated + Premium → Show preview template
    - Unauthenticated + Free → Show full detail template
    - Authenticated + Free → Show full detail (all users)
    - Authenticated + Premium + Active subscription → Show full detail
    - Authenticated + Premium + Article purchased → Show full detail
    - Authenticated + Premium + No subscription/purchase → Show preview

    Pagination:
    - Articles can have multiple pages (ArticlePage model)
    - URL parameter ?page=N determines which page to display
    - Navigation buttons (prev/next) are shown
    - Comments section only appears on the last page
    """

    def get_template_names(self):
        """Return appropriate template based on access control."""
        article = self.get_article()
        if self.user_has_access(article):
            return ["tech-articles/home/pages/articles/article_detail.html"]
        return ["tech-articles/home/pages/articles/article_preview.html"]

    def get_article(self):
        """Get article by slug from URL or return None."""
        slug = self.request.GET.get("slug") or self.kwargs.get("slug")
        if not slug:
            return None
        try:
            return Article.objects.prefetch_related("categories", "tags", "pages").get(
                slug=slug, status=ArticleStatus.PUBLISHED
            )
        except Article.DoesNotExist:
            return None

    def user_has_access(self, article):
        """
        Determine if the current user has access to the full article.

        Returns True if:
        - Article is free (access_type='free')
        - User has active subscription (any plan)
        - User has purchased this specific article
        """
        if not article:
            return False

        # Free articles are accessible to everyone
        if article.access_type == ArticleAccessType.FREE:
            return True

        # Premium articles require authentication + (subscription OR purchase)
        if not self.request.user.is_authenticated:
            return False

        # Check if user has active subscription (from context processor)
        if getattr(self.request, "has_active_subscription", False):
            return True

        # Check if user purchased this article (from context processor)
        purchased_ids = getattr(self.request, "purchased_article_ids", set())
        if article.id in purchased_ids:
            return True

        return False

    def get_context_data(self, **kwargs):
        """Add article data, pagination info, and interaction counts to context."""
        context = super().get_context_data(**kwargs)
        article = self.get_article()

        if not article:
            # Redirect to 404 or articles list
            context["article"] = None
            return context

        context["article"] = article
        context["has_access"] = self.user_has_access(article)

        # Add featured articles map to context (cached)
        try:
            context["featured_map"] = (
                FeaturedArticles.get_featured_articles_from_cache()
            )
        except Exception:
            context["featured_map"] = {"first": None, "second": None, "third": None}

        # Get interaction counts
        context["clap_count"] = Clap.objects.filter(article=article).count()
        context["like_count"] = Like.objects.filter(article=article).count()
        context["comment_count"] = Comment.objects.filter(article=article).count()

        # Check if current user has liked (for authenticated users)
        context["user_has_liked"] = False
        context["user_liked_comment_ids"] = set()
        if self.request.user.is_authenticated:
            context["user_has_liked"] = Like.objects.filter(
                article=article, user=self.request.user
            ).exists()
            liked_ids = CommentLike.objects.filter(
                comment__article=article, user=self.request.user
            ).values_list("comment_id", flat=True)
            context["user_liked_comment_ids"] = set(liked_ids)

        # Pagination logic for multi-page articles
        pages = list(article.pages.all().order_by("page_number"))
        total_pages = len(pages)

        # Get current page number from query param (default to 1)
        try:
            current_page = int(self.request.GET.get("page", 1))
        except (ValueError, TypeError):
            current_page = 1

        # Ensure page number is valid
        current_page = max(1, min(current_page, total_pages if total_pages > 0 else 1))

        context["total_pages"] = total_pages
        context["current_page"] = current_page
        context["has_multiple_pages"] = total_pages > 1
        context["is_last_page"] = (
            current_page == total_pages if total_pages > 0 else True
        )
        context["has_next_page"] = current_page < total_pages
        context["has_prev_page"] = current_page > 1
        context["next_page"] = current_page + 1 if context["has_next_page"] else None
        context["prev_page"] = current_page - 1 if context["has_prev_page"] else None

        # Get the current page content
        if pages and 0 < current_page <= total_pages:
            context["current_page_content"] = pages[current_page - 1]
        else:
            context["current_page_content"] = None

        # Get comments (only if user has access and on last page)
        if context["has_access"]:
            context["comments"] = (
                Comment.objects.filter(article=article)
                .select_related("user")
                .prefetch_related("likes")
                .order_by("-created_at")[:50]
            )
        else:
            context["comments"] = []

        # Add TOC if exists
        try:
            toc = TableOfContents.objects.get(article=article)
            context["toc"] = toc.structure if toc.structure else []
        except TableOfContents.DoesNotExist:
            context["toc"] = []

        return context


# ============================================================================
# Article API Endpoints
# ============================================================================


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
    ARTICLES_PER_PAGE = 6

    def get(self, request):
        qs = Article.objects.filter(
            status=ArticleStatus.PUBLISHED,
        ).prefetch_related("categories")

        # Search
        search = request.GET.get("search", "").strip()
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(summary__icontains=search))

        # Category filter
        categories_param = request.GET.get("categories", "").strip()
        if categories_param:
            category_ids = [
                cid.strip() for cid in categories_param.split(",") if cid.strip()
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
        total_pages = max(1, math.ceil(total_count / self.ARTICLES_PER_PAGE))

        try:
            page = int(request.GET.get("page", 1))
        except (ValueError, TypeError):
            page = 1
        page = max(1, min(page, total_pages))

        start = (page - 1) * self.ARTICLES_PER_PAGE
        end = start + self.ARTICLES_PER_PAGE
        articles = qs[start:end]

        return JsonResponse(
            {
                "articles": [_serialize_article(a) for a in articles],
                "pagination": {
                    "current_page": page,
                    "total_pages": total_pages,
                    "total_count": total_count,
                    "per_page": self.ARTICLES_PER_PAGE,
                    "has_previous": page > 1,
                    "has_next": page < total_pages,
                },
            }
        )


class FeaturedArticlesApiView(View):
    """API endpoint returning the three featured articles."""

    http_method_names = ["get"]

    def get(self, request):
        featured_fields = {
            "id",
            "title",
            "slug",
            "summary",
            "cover_image_url",
            "cover_alt_text",
            "categories",
        }
        result = []
        try:
            featured = FeaturedArticles.get_featured_articles_from_cache()
        except Exception:
            featured = {"first": None, "second": None, "third": None}

        for key in ("first", "second", "third"):
            article = featured.get(key)
            if article and getattr(article, "status", None) == ArticleStatus.PUBLISHED:
                result.append(_serialize_article(article, fields=featured_fields))

        return JsonResponse({"featured": result})


class RelatedArticlesApiView(View):
    """API endpoint returning related (recent) articles for the sidebar."""

    http_method_names = ["get"]

    def get(self, request):
        related_fields = {
            "id",
            "title",
            "slug",
            "summary",
            "reading_time_minutes",
            "categories",
        }
        articles = (
            Article.objects.filter(status=ArticleStatus.PUBLISHED)
            .prefetch_related("categories")
            .order_by("-published_at", "-created_at")[:4]
        )
        result = [_serialize_article(a, fields=related_fields) for a in articles]
        return JsonResponse({"related": result})


class CategoriesApiView(View):
    """API endpoint returning active categories for filter dropdowns."""

    http_method_names = ["get"]

    def get(self, request):
        categories = Category.objects.filter(is_active=True).order_by(
            "sort_order", "name"
        )
        result = [{"id": str(c.id), "name": c.name, "slug": c.slug} for c in categories]
        return JsonResponse({"categories": result})


# ============================================================================
# Interactive Article APIs (Claps, Likes, Comments)
# ============================================================================


class ArticleClapApiView(View):
    """
    API endpoint for adding claps to an article.
    Anyone can clap (authenticated or anonymous), but limited to 50 claps per user/session.
    """

    http_method_names = ["post"]

    def post(self, request, article_id):
        """Add a clap to the article."""
        try:
            article = Article.objects.get(id=article_id, status=ArticleStatus.PUBLISHED)
        except Article.DoesNotExist:
            return JsonResponse({"error": "Article not found"}, status=404)

        # Get or create clap record
        if request.user.is_authenticated:
            clap, created = Clap.objects.get_or_create(
                article=article, user=request.user, defaults={"count": 1}
            )
        else:
            # Use session key for anonymous users
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
                session_key = request.session.session_key

            clap, created = Clap.objects.get_or_create(
                article=article, session_key=session_key, defaults={"count": 1}
            )

        # Increment count (max 50)
        if not created and clap.count < 50:
            clap.count += 1
            clap.save()
        elif not created and clap.count >= 50:
            return JsonResponse(
                {
                    "error": "Maximum claps reached (50)",
                    "count": clap.count,
                    "total": Clap.objects.filter(article=article).count(),
                },
                status=400,
            )

        # Return total clap count for this article
        total_claps = Clap.objects.filter(article=article).count()
        return JsonResponse(
            {"success": True, "count": clap.count, "total": total_claps}
        )


class ArticleLikeApiView(LoginRequiredMixin, View):
    """
    API endpoint for toggling likes on an article.
    Only authenticated users can like articles.
    """

    http_method_names = ["post"]

    def post(self, request, article_id):
        """Toggle like on the article."""
        try:
            article = Article.objects.get(id=article_id, status=ArticleStatus.PUBLISHED)
        except Article.DoesNotExist:
            return JsonResponse({"error": "Article not found"}, status=404)

        # Toggle like
        like, created = Like.objects.get_or_create(article=article, user=request.user)

        if not created:
            # Unlike
            like.delete()
            liked = False
        else:
            # Liked
            liked = True

        # Return total like count
        total_likes = Like.objects.filter(article=article).count()
        return JsonResponse({"success": True, "liked": liked, "total": total_likes})


class ArticleCommentApiView(LoginRequiredMixin, View):
    """
    API endpoint for creating and retrieving comments on an article.
    Only authenticated users can comment.
    """

    http_method_names = ["post", "get"]

    def get(self, request, article_id):
        """Get comments for an article."""
        try:
            article = Article.objects.get(id=article_id, status=ArticleStatus.PUBLISHED)
        except Article.DoesNotExist:
            return JsonResponse({"error": "Article not found"}, status=404)

        comments = (
            Comment.objects.filter(article=article)
            .select_related("user")
            .order_by("-created_at")[:50]
        )
        result = []
        for comment in comments:
            likes_count = CommentLike.objects.filter(comment=comment).count()
            user_liked = (
                CommentLike.objects.filter(comment=comment, user=request.user).exists()
                if request.user.is_authenticated
                else False
            )

            result.append(
                {
                    "id": str(comment.id),
                    "content": comment.content,
                    "user": {
                        "email": comment.user.email,
                        "name": comment.user.name,
                    },
                    "created_at": comment.created_at.isoformat(),
                    "is_edited": comment.is_edited,
                    "likes_count": likes_count,
                    "user_liked": user_liked,
                }
            )

        return JsonResponse({"comments": result, "total": len(result)})

    def post(self, request, article_id):
        """Create a new comment on the article."""
        try:
            article = Article.objects.get(id=article_id, status=ArticleStatus.PUBLISHED)
        except Article.DoesNotExist:
            return JsonResponse({"error": "Article not found"}, status=404)

        # Get comment content from request
        import json

        try:
            data = json.loads(request.body)
            content = data.get("content", "").strip()
        except json.JSONDecodeError:
            content = request.POST.get("content", "").strip()

        if not content:
            return JsonResponse({"error": "Comment content is required"}, status=400)

        if len(content) > 2000:
            return JsonResponse(
                {"error": "Comment too long (max 2000 characters)"}, status=400
            )

        # Create comment
        comment = Comment.objects.create(
            article=article, user=request.user, content=content
        )

        return JsonResponse(
            {
                "success": True,
                "comment": {
                    "id": str(comment.id),
                    "content": comment.content,
                    "user": {
                        "email": comment.user.email,
                        "name": comment.user.name,
                    },
                    "created_at": comment.created_at.isoformat(),
                    "is_edited": comment.is_edited,
                    "likes_count": 0,
                    "user_liked": False,
                },
            },
            status=201,
        )


class CommentLikeApiView(LoginRequiredMixin, View):
    """
    API endpoint for toggling likes on comments.
    Only authenticated users can like comments.
    """

    http_method_names = ["post"]

    def post(self, request, comment_id):
        """Toggle like on a comment."""
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return JsonResponse({"error": "Comment not found"}, status=404)

        # Toggle like
        comment_like, created = CommentLike.objects.get_or_create(
            comment=comment, user=request.user
        )

        if not created:
            # Unlike
            comment_like.delete()
            liked = False
        else:
            # Liked
            liked = True

        # Return total like count
        total_likes = CommentLike.objects.filter(comment=comment).count()
        return JsonResponse({"success": True, "liked": liked, "total": total_likes})
