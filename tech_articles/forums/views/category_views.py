"""
Forum category views for dashboard CRUD operations.
"""

import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from tech_articles.forums.forms import ForumCategoryForm
from tech_articles.forums.models import ForumCategory
from tech_articles.utils.mixins import AdminRequiredMixin

logger = logging.getLogger(__name__)


class ForumCategoryListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    """List all forum categories with thread counts."""

    model = ForumCategory
    template_name = "tech-articles/dashboard/pages/forums/categories/list.html"
    context_object_name = "categories"
    paginate_by = 10
    ordering = ["display_order", "name"]

    def get_queryset(self):
        queryset = super().get_queryset().annotate(
            thread_count=Count("threads"),
        )
        search = self.request.GET.get("search", "").strip()
        status = self.request.GET.get("status", "")
        if search:
            queryset = queryset.filter(name__icontains=search)
        if status == "active":
            queryset = queryset.filter(is_active=True)
        elif status == "inactive":
            queryset = queryset.filter(is_active=False)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search"] = self.request.GET.get("search", "")
        context["status"] = self.request.GET.get("status", "")
        context["total_count"] = ForumCategory.objects.count()
        context["active_count"] = ForumCategory.objects.filter(is_active=True).count()
        return context


class ForumCategoryCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    """Create a new forum category."""

    model = ForumCategory
    form_class = ForumCategoryForm
    template_name = "tech-articles/dashboard/pages/forums/categories/form.html"
    success_url = reverse_lazy("forums:categories_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Create Forum Category")
        context["is_edit"] = False
        return context

    def form_valid(self, form):
        messages.success(self.request, _("Forum category created successfully."))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _("Please correct the errors below."))
        return super().form_invalid(form)


class ForumCategoryUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    """Update an existing forum category."""

    model = ForumCategory
    form_class = ForumCategoryForm
    template_name = "tech-articles/dashboard/pages/forums/categories/form.html"
    success_url = reverse_lazy("forums:categories_list")
    context_object_name = "category"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Edit Forum Category")
        context["is_edit"] = True
        return context

    def form_valid(self, form):
        messages.success(self.request, _("Forum category updated successfully."))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _("Please correct the errors below."))
        return super().form_invalid(form)


class ForumCategoryDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    """Delete a forum category (cascade deletes threads)."""

    model = ForumCategory
    success_url = reverse_lazy("forums:categories_list")

    def get(self, request, *args, **kwargs):
        """Return category info + thread count for AJAX pre-delete check."""
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            category = self.get_object()
            thread_count = category.threads.count()
            return JsonResponse({
                "id": str(category.pk),
                "name": category.name,
                "thread_count": thread_count,
            })
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        category_name = self.object.name
        self.object.delete()

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({
                "success": True,
                "message": str(
                    _("Category '%(name)s' deleted successfully.")
                    % {"name": category_name}
                ),
            })

        messages.success(
            request,
            _("Category '%(name)s' deleted successfully.") % {"name": category_name},
        )
        from django.http import HttpResponseRedirect
        return HttpResponseRedirect(self.success_url)
