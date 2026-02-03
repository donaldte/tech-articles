"""
Article views for dashboard CRUD operations.
"""
import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView

from tech_articles.content.models import Article
from tech_articles.content.forms import ArticleForm

logger = logging.getLogger(__name__)


class AdminRequiredMixin(UserPassesTestMixin):
    """Mixin that requires user to be an admin or staff."""

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser


class ArticleListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    """List all articles with search and filtering."""
    model = Article
    template_name = "tech-articles/dashboard/pages/content/articles/list.html"
    context_object_name = "articles"
    paginate_by = 10
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get("search", "").strip()
        status = self.request.GET.get("status", "")
        language = self.request.GET.get("language", "")
        access_type = self.request.GET.get("access_type", "")

        if search:
            queryset = queryset.filter(title__icontains=search)
        if status:
            queryset = queryset.filter(status=status)
        if language:
            queryset = queryset.filter(language=language)
        if access_type:
            queryset = queryset.filter(access_type=access_type)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search"] = self.request.GET.get("search", "")
        context["status"] = self.request.GET.get("status", "")
        context["language"] = self.request.GET.get("language", "")
        context["access_type"] = self.request.GET.get("access_type", "")
        return context


class ArticleCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    """Create a new article."""
    model = Article
    form_class = ArticleForm
    template_name = "tech-articles/dashboard/pages/content/articles/create.html"
    success_url = reverse_lazy("content:articles_list")

    def form_valid(self, form):
        messages.success(self.request, _("Article created successfully."))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _("Please correct the errors below."))
        return super().form_invalid(form)


class ArticleUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    """Update an existing article."""
    model = Article
    form_class = ArticleForm
    template_name = "tech-articles/dashboard/pages/content/articles/edit.html"
    success_url = reverse_lazy("content:articles_list")

    def form_valid(self, form):
        messages.success(self.request, _("Article updated successfully."))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _("Please correct the errors below."))
        return super().form_invalid(form)


class ArticleDetailView(LoginRequiredMixin, AdminRequiredMixin, DetailView):
    """View article details."""
    model = Article
    template_name = "tech-articles/dashboard/pages/content/articles/detail.html"
    context_object_name = "article"


class ArticleDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    """Delete an article."""
    model = Article
    template_name = "tech-articles/dashboard/pages/content/articles/delete.html"
    success_url = reverse_lazy("content:articles_list")

    def form_valid(self, form):
        messages.success(self.request, _("Article deleted successfully."))
        return super().form_valid(form)
