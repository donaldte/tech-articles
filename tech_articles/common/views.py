import logging

from django.views.generic import TemplateView

from tech_articles.billing.models import Plan

logger = logging.getLogger(__name__)


class HomePageView(TemplateView):
    """
    Home page view that displays featured articles, categories, and popular tags.

    This view uses class-based view (CBV) for better organization and reusability.
    It retrieves and filters content based on publication status and active state.
    """

    template_name = "tech-articles/home/pages/index.html"

    def get_context_data(self, **kwargs):
        """Add active plans to context."""
        context = super().get_context_data(**kwargs)
        context["active_plans"] = Plan.objects.filter(is_active=True).prefetch_related("plan_features")
        return context


class ArticlesListView(TemplateView):
    """Articles listing page (design-only for now)."""

    template_name = "tech-articles/home/pages/articles_list.html"
