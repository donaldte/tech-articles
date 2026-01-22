import logging

from django.views.generic import TemplateView

logger = logging.getLogger(__name__)


class HomePageView(TemplateView):
    """
    Home page view that displays featured articles, categories, and popular tags.

    This view uses class-based view (CBV) for better organization and reusability.
    It retrieves and filters content based on publication status and active state.
    """

    template_name = "tech-articles/home/pages/index.html"

