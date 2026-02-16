"""
Tag views for dashboard CRUD operations.
"""
import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from tech_articles.content.models import Tag
from tech_articles.content.forms import TagForm
from tech_articles.utils.mixins import AdminRequiredMixin

logger = logging.getLogger(__name__)


class TagListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    """List all tags with search functionality."""
    model = Tag
    template_name = "tech-articles/dashboard/pages/content/tags/list.html"
    context_object_name = "tags"
    paginate_by = 20
    ordering = ["name"]

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get("search", "").strip()

        if search:
            queryset = queryset.filter(name__icontains=search)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search"] = self.request.GET.get("search", "")
        context["total_count"] = Tag.objects.count()
        return context


class TagCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    """Create a new tag."""
    model = Tag
    form_class = TagForm
    template_name = "tech-articles/dashboard/pages/content/tags/form.html"
    success_url = reverse_lazy("content:tags_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Create Tag")
        context["is_edit"] = False
        return context

    def form_valid(self, form):
        messages.success(self.request, _("Tag created successfully."))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _("Please correct the errors below."))
        return super().form_invalid(form)


class TagUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    """Update an existing tag."""
    model = Tag
    form_class = TagForm
    template_name = "tech-articles/dashboard/pages/content/tags/form.html"
    success_url = reverse_lazy("content:tags_list")
    context_object_name = "tag"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Edit Tag")
        context["is_edit"] = True
        return context

    def form_valid(self, form):
        messages.success(self.request, _("Tag updated successfully."))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _("Please correct the errors below."))
        return super().form_invalid(form)


class TagDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    """Delete a tag."""
    model = Tag
    success_url = reverse_lazy("content:tags_list")

    def delete(self, request, *args, **kwargs):
        """Handle both AJAX and regular delete requests."""
        self.object = self.get_object()
        tag_name = self.object.name

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            self.object.delete()
            return JsonResponse({
                "success": True,
                "message": str(_("Tag '%(name)s' deleted successfully.") % {"name": tag_name})
            })

        messages.success(request, _("Tag '%(name)s' deleted successfully.") % {"name": tag_name})
        return super().delete(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Handle POST request for deletion."""
        return self.delete(request, *args, **kwargs)
