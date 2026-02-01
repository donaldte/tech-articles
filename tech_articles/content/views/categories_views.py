"""
Category views for dashboard CRUD operations.
"""
import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from tech_articles.content.models import Category
from tech_articles.content.forms import CategoryForm

logger = logging.getLogger(__name__)


class AdminRequiredMixin(UserPassesTestMixin):
    """Mixin that requires user to be an admin or staff."""

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser


class CategoryListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    """List all categories with search and filtering."""
    model = Category
    template_name = "tech-articles/dashboard/pages/content/categories/list.html"
    context_object_name = "categories"
    paginate_by = 10
    ordering = ["sort_order", "name"]

    def get_queryset(self):
        queryset = super().get_queryset()
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
        context["total_count"] = Category.objects.count()
        context["active_count"] = Category.objects.filter(is_active=True).count()
        return context


class CategoryCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    """Create a new category."""
    model = Category
    form_class = CategoryForm
    template_name = "tech-articles/dashboard/pages/content/categories/form.html"
    success_url = reverse_lazy("content:categories_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Create Category")
        context["is_edit"] = False
        return context

    def form_valid(self, form):
        messages.success(self.request, _("Category created successfully."))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _("Please correct the errors below."))
        return super().form_invalid(form)


class CategoryUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    """Update an existing category."""
    model = Category
    form_class = CategoryForm
    template_name = "tech-articles/dashboard/pages/content/categories/form.html"
    success_url = reverse_lazy("content:categories_list")
    context_object_name = "category"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Edit Category")
        context["is_edit"] = True
        return context

    def form_valid(self, form):
        messages.success(self.request, _("Category updated successfully."))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _("Please correct the errors below."))
        return super().form_invalid(form)


class CategoryDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    """Delete a category."""
    model = Category
    success_url = reverse_lazy("content:categories_list")

    def delete(self, request, *args, **kwargs):
        """Handle both AJAX and regular delete requests."""
        self.object = self.get_object()
        category_name = self.object.name

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            self.object.delete()
            return JsonResponse({
                "success": True,
                "message": str(_("Category '%(name)s' deleted successfully.") % {"name": category_name})
            })

        messages.success(request, _("Category '%(name)s' deleted successfully.") % {"name": category_name})
        return super().delete(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Handle POST request for deletion."""
        return self.delete(request, *args, **kwargs)
