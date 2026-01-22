import logging

from django.views.generic import TemplateView

logger = logging.getLogger(__name__)


class DashboardPageView(TemplateView):
    """
    Dashboard page view that displays featured articles, categories, and popular tags.

    This view uses class-based view (CBV) for better organization and reusability.
    It retrieves and filters content based on publication status and active state.
    """

    template_name = "tech-articles/dashboard/pages/index.html"

