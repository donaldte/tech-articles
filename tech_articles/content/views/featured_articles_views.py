"""
Featured Articles views for dashboard management.
"""
import logging
import uuid

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import UpdateView

from tech_articles.content.forms import FeaturedArticlesForm
from tech_articles.content.models import FeaturedArticles

logger = logging.getLogger(__name__)

# Singleton UUID for FeaturedArticles configuration
FEATURED_ARTICLES_UUID = uuid.UUID('00000000-0000-0000-0000-000000000000')


class AdminRequiredMixin(UserPassesTestMixin):
    """Mixin that requires user to be an admin or staff."""

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser


class FeaturedArticlesManageView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    """
    View for managing featured articles configuration.
    Staff-only access to select which articles appear on the homepage.
    """
    model = FeaturedArticles
    form_class = FeaturedArticlesForm
    template_name = "tech-articles/dashboard/pages/content/featured_articles/manage.html"

    def get_object(self, queryset=None):
        """Get or create the singleton FeaturedArticles instance."""
        obj, created = FeaturedArticles.objects.get_or_create(pk=FEATURED_ARTICLES_UUID)
        return obj

    def get_success_url(self):
        """Redirect back to the same page after successful update."""
        return reverse("content:featured_articles_manage")

    def form_valid(self, form):
        """Handle successful form submission."""
        messages.success(
            self.request,
            _("Featured articles updated successfully.")
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        """Handle failed form submission."""
        messages.error(
            self.request,
            _("There was an error updating featured articles. Please check the form.")
        )
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        """Add additional context for the template."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = _("Manage Featured Articles")
        return context
