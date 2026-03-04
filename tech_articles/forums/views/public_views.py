"""
Public forum views — visible to all users (including free plan).
Free-plan users can browse the category list but cannot interact.
"""

import logging

from django.views.generic import ListView

from tech_articles.forums.models import ForumCategory

logger = logging.getLogger(__name__)


class ForumCategoryPublicListView(ListView):
    """
    Public listing of all active forum categories.

    Free-plan users can see the list (Option C).
    Action buttons (join / subscribe) are hidden or redirected based on
    the user's plan status in the template.
    """

    model = ForumCategory
    template_name = "tech-articles/forums/categories/list.html"
    context_object_name = "categories"
    ordering = ["display_order", "name"]

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)
