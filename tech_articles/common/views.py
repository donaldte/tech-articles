import logging

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
        context["active_plans"] = Plan.objects.filter(is_active=True).prefetch_related(
            "plan_features"
        )

        # Get featured articles from cache helper (ensures singleton and prefetch)
        try:
            featured_map = FeaturedArticles.get_featured_articles_from_cache()
        except Exception:
            featured_map = {"first": None, "second": None, "third": None}

        context["first_featured_article"] = featured_map.get("first")
        context["second_featured_article"] = featured_map.get("second")
        context["third_featured_article"] = featured_map.get("third")

        return context


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
