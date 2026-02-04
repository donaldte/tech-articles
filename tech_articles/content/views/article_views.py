"""
Article views for dashboard CRUD operations.
"""
import json
import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.utils.translation import gettext_lazy as _, gettext
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView

from tech_articles.content.models import Article, Category
from tech_articles.content.forms import (
    ArticleForm,
    ArticleQuickCreateForm,
    ArticleDetailsForm,
    ArticleSEOForm,
    ArticlePricingForm,
)
from tech_articles.utils.enums import ArticleStatus, LanguageChoices, ArticleAccessType

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
    paginate_by = 9
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = super().get_queryset().prefetch_related("categories")
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
        context["total_count"] = Article.objects.count()
        context["published_count"] = Article.objects.filter(status=ArticleStatus.PUBLISHED).count()
        context["draft_count"] = Article.objects.filter(status=ArticleStatus.DRAFT).count()
        context["status_choices"] = ArticleStatus.choices
        context["language_choices"] = LanguageChoices.choices
        context["access_type_choices"] = ArticleAccessType.choices
        context["categories"] = Category.objects.filter(is_active=True)
        context["quick_create_form"] = ArticleQuickCreateForm()
        return context


class ArticleQuickCreateAPIView(LoginRequiredMixin, AdminRequiredMixin, View):
    """API view for quick article creation."""

    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                "success": False,
                "message": gettext("Invalid JSON data.")
            }, status=400)

        form = ArticleQuickCreateForm(data)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            form.save_m2m()  # Save ManyToMany relationships

            return JsonResponse({
                "success": True,
                "message": gettext("Article created successfully."),
                "redirect_url": reverse("content:articles_dashboard", kwargs={"pk": article.pk}),
                "article": {
                    "id": str(article.pk),
                    "title": article.title,
                    "slug": article.slug,
                }
            })
        else:
            errors = {field: errors[0] for field, errors in form.errors.items()}
            return JsonResponse({
                "success": False,
                "message": gettext("Please correct the errors below."),
                "errors": errors
            }, status=400)


class ArticleDeleteAPIView(LoginRequiredMixin, AdminRequiredMixin, View):
    """API view for article deletion (cascade delete with pages)."""

    def post(self, request, pk):
        try:
            article = Article.objects.get(pk=pk)
            title = article.title
            article.delete()  # This will cascade delete related pages

            return JsonResponse({
                "success": True,
                "message": gettext("Article \"%(title)s\" deleted successfully.") % {"title": title},
            })
        except Article.DoesNotExist:
            return JsonResponse({
                "success": False,
                "message": gettext("Article not found.")
            }, status=404)


class ArticleDashboardView(LoginRequiredMixin, AdminRequiredMixin, DetailView):
    """Mini Dashboard view for managing a specific article."""
    model = Article
    template_name = "tech-articles/dashboard/pages/content/articles/dashboard.html"
    context_object_name = "article"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = self.object
        context["details_form"] = ArticleDetailsForm(instance=article)
        context["seo_form"] = ArticleSEOForm(instance=article)
        context["pricing_form"] = ArticlePricingForm(instance=article)
        context["pages"] = article.pages.all().order_by("page_number")
        context["active_tab"] = self.request.GET.get("tab", "details")
        return context


class ArticleUpdateDetailsAPIView(LoginRequiredMixin, AdminRequiredMixin, View):
    """API view for updating article details."""

    def post(self, request, pk):
        try:
            article = Article.objects.get(pk=pk)
        except Article.DoesNotExist:
            return JsonResponse({
                "success": False,
                "message": gettext("Article not found.")
            }, status=404)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                "success": False,
                "message": gettext("Invalid JSON data.")
            }, status=400)

        form = ArticleDetailsForm(data, instance=article)
        if form.is_valid():
            form.save()
            return JsonResponse({
                "success": True,
                "message": gettext("Article details updated successfully."),
            })
        else:
            errors = {field: errors[0] for field, errors in form.errors.items()}
            return JsonResponse({
                "success": False,
                "message": gettext("Please correct the errors below."),
                "errors": errors
            }, status=400)


class ArticleUpdateSEOAPIView(LoginRequiredMixin, AdminRequiredMixin, View):
    """API view for updating article SEO settings."""

    def post(self, request, pk):
        try:
            article = Article.objects.get(pk=pk)
        except Article.DoesNotExist:
            return JsonResponse({
                "success": False,
                "message": gettext("Article not found.")
            }, status=404)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                "success": False,
                "message": gettext("Invalid JSON data.")
            }, status=400)

        form = ArticleSEOForm(data, instance=article)
        if form.is_valid():
            form.save()
            return JsonResponse({
                "success": True,
                "message": gettext("SEO settings updated successfully."),
            })
        else:
            errors = {field: errors[0] for field, errors in form.errors.items()}
            return JsonResponse({
                "success": False,
                "message": gettext("Please correct the errors below."),
                "errors": errors
            }, status=400)


class ArticleUpdatePricingAPIView(LoginRequiredMixin, AdminRequiredMixin, View):
    """API view for updating article pricing."""

    def post(self, request, pk):
        try:
            article = Article.objects.get(pk=pk)
        except Article.DoesNotExist:
            return JsonResponse({
                "success": False,
                "message": gettext("Article not found.")
            }, status=404)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                "success": False,
                "message": gettext("Invalid JSON data.")
            }, status=400)

        form = ArticlePricingForm(data, instance=article)
        if form.is_valid():
            form.save()
            return JsonResponse({
                "success": True,
                "message": gettext("Pricing settings updated successfully."),
            })
        else:
            errors = {field: errors[0] for field, errors in form.errors.items()}
            return JsonResponse({
                "success": False,
                "message": gettext("Please correct the errors below."),
                "errors": errors
            }, status=400)


class ArticleCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    """Create a new article."""
    model = Article
    form_class = ArticleForm
    template_name = "tech-articles/dashboard/pages/content/articles/create.html"
    success_url = reverse_lazy("content:articles_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.filter(is_active=True)
        context["quick_create_form"] = ArticleQuickCreateForm()
        return context

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


# ===== NEW MINI-DASHBOARD VIEWS =====

class ArticleManageBaseView(LoginRequiredMixin, AdminRequiredMixin, DetailView):
    """Base view for article management mini-dashboard."""
    model = Article
    context_object_name = "article"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pages_count"] = self.object.pages.count()
        return context


class ArticleManageDetailsView(ArticleManageBaseView):
    """View for managing article details."""
    template_name = "tech-articles/dashboard/pages/content/articles/manage/details.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = ArticleDetailsForm(instance=self.object)
        context["categories"] = Category.objects.filter(is_active=True)
        from tech_articles.content.models import Tag
        context["tags"] = Tag.objects.all()
        context["selected_categories"] = list(self.object.categories.values_list('pk', flat=True))
        context["selected_tags"] = list(self.object.tags.values_list('pk', flat=True))
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = ArticleDetailsForm(request.POST, instance=self.object)
        if form.is_valid():
            article = form.save(commit=False)
            article.save()

            # Handle categories
            categories = request.POST.getlist('categories')
            article.categories.set(categories)

            # Handle tags
            tags = request.POST.getlist('tags')
            article.tags.set(tags)

            messages.success(request, _("Article details updated successfully."))
            return redirect('content:article_manage_details', pk=self.object.pk)

        context = self.get_context_data()
        context["form"] = form
        messages.error(request, _("Please correct the errors below."))
        return self.render_to_response(context)


class ArticleManageSEOView(ArticleManageBaseView):
    """View for managing article SEO settings."""
    template_name = "tech-articles/dashboard/pages/content/articles/manage/seo.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = ArticleSEOForm(instance=self.object)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = ArticleSEOForm(request.POST, instance=self.object)
        if form.is_valid():
            form.save()
            messages.success(request, _("SEO settings updated successfully."))
            return redirect('content:article_manage_seo', pk=self.object.pk)

        context = self.get_context_data()
        context["form"] = form
        messages.error(request, _("Please correct the errors below."))
        return self.render_to_response(context)


class ArticleManagePricingView(ArticleManageBaseView):
    """View for managing article pricing settings."""
    template_name = "tech-articles/dashboard/pages/content/articles/manage/pricing.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = ArticlePricingForm(instance=self.object)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = ArticlePricingForm(request.POST, instance=self.object)
        if form.is_valid():
            form.save()
            messages.success(request, _("Pricing settings updated successfully."))
            return redirect('content:article_manage_pricing', pk=self.object.pk)

        context = self.get_context_data()
        context["form"] = form
        messages.error(request, _("Please correct the errors below."))
        return self.render_to_response(context)


class ArticleManageContentView(ArticleManageBaseView):
    """View for managing article content/pages."""
    template_name = "tech-articles/dashboard/pages/content/articles/manage/content.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pages"] = self.object.pages.all().order_by("page_number")
        return context


class ArticleCreateFullView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    """Full page create view for articles (Basic setup only)."""
    model = Article
    template_name = "tech-articles/dashboard/pages/content/articles/create_full.html"

    def get_form_class(self):
        from tech_articles.content.forms import ArticleSetupForm
        return ArticleSetupForm

    def form_valid(self, form):
        article = form.save(commit=False)
        article.author = self.request.user
        article.status = 'draft'  # Always create as draft
        article.save()

        messages.success(self.request, _("Article setup completed successfully. You can now add more details."))
        return redirect('content:article_manage_details', pk=article.pk)

    def form_invalid(self, form):
        messages.error(self.request, _("Please correct the errors below."))
        return super().form_invalid(form)


