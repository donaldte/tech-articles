"""
Publish article view for dashboard.
"""
import logging

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.translation import gettext_lazy as _, gettext
from django.views import View

from tech_articles.content.models import Article
from tech_articles.utils.enums import ArticleStatus

logger = logging.getLogger(__name__)


class AdminRequiredMixin(UserPassesTestMixin):
    """Mixin that requires user to be an admin or staff."""

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser


class PublishArticleAPIView(LoginRequiredMixin, AdminRequiredMixin, View):
    """
    API view to publish an article.
    Changes status from draft to published and sets published_at timestamp.
    """

    def post(self, request, *args, **kwargs):
        """Handle POST request to publish article."""
        article_pk = kwargs.get("pk")
        article = get_object_or_404(Article, pk=article_pk)

        # Check if article is already published
        if article.status == ArticleStatus.PUBLISHED:
            return JsonResponse({
                "success": False,
                "message": gettext("Article is already published."),
                "status": article.status,
            }, status=400)

        # Check if article is in draft status
        if article.status != ArticleStatus.DRAFT:
            return JsonResponse({
                "success": False,
                "message": gettext("Only draft articles can be published."),
                "status": article.status,
            }, status=400)

        # Publish the article
        article.status = ArticleStatus.PUBLISHED
        if not article.published_at:
            article.published_at = timezone.now()
        article.save(update_fields=["status", "published_at", "updated_at"])

        logger.info(f"Article '{article.title}' (ID: {article.pk}) published by user {request.user.username}")

        return JsonResponse({
            "success": True,
            "message": gettext("Article published successfully."),
            "status": article.status,
            "published_at": article.published_at.isoformat() if article.published_at else None,
        })
