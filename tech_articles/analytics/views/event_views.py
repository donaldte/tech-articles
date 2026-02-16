"""
Event views for dashboard analytics.
"""
import logging

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView

from tech_articles.analytics.models import Event
from tech_articles.utils.mixins import AdminRequiredMixin

logger = logging.getLogger(__name__)


class EventsListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    """List tracked events."""
    model = Event
    template_name = "tech-articles/dashboard/pages/analytics/events.html"
    context_object_name = "events"
    paginate_by = 20
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        event_type = self.request.GET.get("event_type", "")

        if event_type:
            queryset = queryset.filter(event_type=event_type)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["event_type"] = self.request.GET.get("event_type", "")
        return context
