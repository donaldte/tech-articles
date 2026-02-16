import logging

from django.urls import reverse
from django.views.generic import TemplateView

from tech_articles.billing.models import Plan
from tech_articles.content.models import FeaturedArticles

logger = logging.getLogger(__name__)


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
        featured_config, created = FeaturedArticles.objects.get_or_create(pk=1)
        context["first_featured_article"] = featured_config.first_feature
        context["second_featured_article"] = featured_config.second_feature
        context["third_featured_article"] = featured_config.third_feature
        
        return context


class ArticlesListView(TemplateView):
    """Articles listing page (design-only for now)."""

    template_name = "tech-articles/home/pages/articles/articles_list.html"

    def get_context_data(self, **kwargs):
        """Add active plans to context."""
        context = super().get_context_data(**kwargs)
        context["article_detail_url"] = reverse('common:article_detail')
        return context


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

