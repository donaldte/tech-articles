"""
Event views for dashboard analytics.
"""
import json
import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views import View
from django.views.generic import ListView

from tech_articles.analytics.models import Event
from tech_articles.utils.enums import EventType
from tech_articles.utils.mixins import AdminRequiredMixin

logger = logging.getLogger(__name__)


class EventsListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    """List tracked events with filtering and pagination."""
    model = Event
    template_name = "tech-articles/dashboard/pages/analytics/events.html"
    context_object_name = "events"
    paginate_by = 25
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = super().get_queryset().select_related("user")
        event_type = self.request.GET.get("event_type", "")
        search = self.request.GET.get("search", "").strip()

        if event_type:
            queryset = queryset.filter(event_type=event_type)
        if search:
            queryset = queryset.filter(
                metadata_json__icontains=search
            ) | queryset.filter(
                user__email__icontains=search
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["event_type"] = self.request.GET.get("event_type", "")
        context["search"] = self.request.GET.get("search", "")
        context["event_type_choices"] = EventType.choices
        return context


class EventDetailAPIView(LoginRequiredMixin, AdminRequiredMixin, View):
    """Return JSON detail of a single Event by UUID."""

    def get(self, request, pk):
        try:
            event = Event.objects.select_related("user").get(pk=pk)
        except Event.DoesNotExist:
            return JsonResponse({"error": "Event not found"}, status=404)

        # Parse metadata
        try:
            metadata = json.loads(event.metadata_json) if event.metadata_json else {}
        except (json.JSONDecodeError, TypeError):
            metadata = {}

        data = {
            "id": str(event.id),
            "event_type": event.event_type,
            "event_type_display": event.get_event_type_display(),
            "user": {
                "id": str(event.user.id) if event.user else None,
                "email": event.user.email if event.user else None,
                "name": event.user.get_full_name() if event.user else "Anonymous",
            },
            "anonymous_id": event.anonymous_id,
            "path": event.path,
            "referrer": event.referrer,
            "user_agent": event.user_agent,
            "ip_hash": event.ip_hash,
            "metadata": metadata,
            "created_at": event.created_at.isoformat() if event.created_at else None,
        }
        return JsonResponse(data)
