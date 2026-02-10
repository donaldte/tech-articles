"""
Resource document views for dashboard CRUD operations with S3 multipart upload support.
"""
import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View
from django.shortcuts import get_object_or_404

from tech_articles.resources.models import ResourceDocument
from tech_articles.resources.forms.resource_forms import ResourceDocumentForm, ResourceDocumentPopupForm
from tech_articles.content.models import Article, Category
from tech_articles.resources.utils.s3_manager import s3_resource_manager

logger = logging.getLogger(__name__)


class AdminRequiredMixin(UserPassesTestMixin):
    """Mixin that requires user to be an admin or staff."""

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser


class ResourceListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    """List all resource documents with search and filtering."""
    model = ResourceDocument
    template_name = "tech-articles/dashboard/pages/resources/list.html"
    context_object_name = "resources"
    paginate_by = 12
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get("search", "").strip()
        access_level = self.request.GET.get("access_level", "")
        article_id = self.request.GET.get("article", "")
        category_id = self.request.GET.get("category", "")

        if search:
            queryset = queryset.filter(title__icontains=search)
        if access_level:
            queryset = queryset.filter(access_level=access_level)
        if article_id:
            queryset = queryset.filter(article_id=article_id)
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        return queryset.select_related('article', 'category', 'uploaded_by')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search"] = self.request.GET.get("search", "")
        context["access_level"] = self.request.GET.get("access_level", "")
        context["articles"] = Article.objects.all().order_by('-created_at')[:50]
        context["categories"] = Category.objects.filter(is_active=True).order_by('name')
        return context


class ResourceCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    """Create a new resource document with multipart upload support."""
    model = ResourceDocument
    form_class = ResourceDocumentForm
    template_name = "tech-articles/dashboard/pages/resources/create.html"
    success_url = reverse_lazy("resources:resources_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Get category from URL for filtering articles
        category_id = self.request.GET.get('category')
        if category_id:
            try:
                category = Category.objects.get(pk=category_id)
                kwargs['category_filter'] = category
            except Category.DoesNotExist:
                pass
        return kwargs

    def form_valid(self, form):
        # Set uploaded_by to current user
        form.instance.uploaded_by = self.request.user

        # Update file metadata
        form.instance.file_key = self.request.POST.get('file_key', '')
        form.instance.file_name = self.request.POST.get('file_name', '')
        form.instance.file_size = int(self.request.POST.get('file_size', 0))
        form.instance.content_type = self.request.POST.get('content_type', '')

        response = super().form_valid(form)
        messages.success(self.request, _("Resource document created successfully."))
        return response

    def form_invalid(self, form):
        messages.error(self.request, _("Please correct the errors below."))
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['s3_configured'] = s3_resource_manager.is_configured()
        return context


class ResourceCreatePopupView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    """
    Create resource document in popup mode (for article creation/editing).
    This view is opened in a popup window and communicates with parent window.
    """
    model = ResourceDocument
    form_class = ResourceDocumentPopupForm
    template_name = "tech-articles/dashboard/pages/resources/create_popup.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Get article categories from query parameters
        article_categories_param = self.request.GET.get('article_categories', '')
        if article_categories_param:
            try:
                article_categories = [cat.strip() for cat in article_categories_param.split(',') if cat.strip()]
                kwargs['article_categories'] = article_categories
            except Exception:
                pass
        return kwargs

    def form_valid(self, form):
        # Set uploaded_by to current user
        form.instance.uploaded_by = self.request.user

        # Save the instance
        self.object = form.save()

        # Return JSON response for popup
        return JsonResponse({
            'success': True,
            'resource': {
                'id': str(self.object.pk),
                'title': self.object.title,
                'file_key': self.object.file_key,
                'file_name': self.object.file_name,
                'file_size': self.object.file_size,
                'file_size_display': self.object.get_file_size_display(),
                'content_type': self.object.content_type,
                'access_level': self.object.access_level,
                'category_id': str(self.object.category_id) if self.object.category else None,
                'category_name': self.object.category.name if self.object.category else None,
            }
        })

    def form_invalid(self, form):
        # Return JSON with errors for popup
        return JsonResponse({
            'success': False,
            'errors': form.errors
        }, status=400)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['s3_configured'] = s3_resource_manager.is_configured()
        context['is_popup'] = True

        # Get article categories if provided
        article_categories_param = self.request.GET.get('article_categories', '')
        if article_categories_param:
            try:
                category_ids = [cat.strip() for cat in article_categories_param.split(',') if cat.strip()]
                context['article_categories'] = Category.objects.filter(pk__in=category_ids)
            except Exception:
                context['article_categories'] = []
        else:
            context['article_categories'] = []

        return context


class ResourceUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    """Update an existing resource document."""
    model = ResourceDocument
    form_class = ResourceDocumentForm
    template_name = "tech-articles/dashboard/pages/resources/edit.html"
    success_url = reverse_lazy("resources:resources_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Get category from instance for filtering articles
        if self.object and self.object.category:
            kwargs['category_filter'] = self.object.category
        return kwargs

    def form_valid(self, form):
        # Store old file key before update
        old_file_key = self.object.file_key if self.object else None

        # Check if file has changed
        new_file_key = self.request.POST.get('file_key', '').strip()
        file_changed = new_file_key and new_file_key != old_file_key

        # Update file metadata if file changed
        if file_changed:
            form.instance.file_key = new_file_key
            form.instance.file_name = self.request.POST.get('file_name', '')
            form.instance.file_size = int(self.request.POST.get('file_size', 0))
            form.instance.content_type = self.request.POST.get('content_type', '')

        response = super().form_valid(form)

        # Delete old file from S3 if file changed
        if file_changed and old_file_key and s3_resource_manager.is_configured():
            try:
                s3_resource_manager.delete_object(old_file_key)
                logger.info(f"Deleted old S3 object: {old_file_key}")
            except Exception as e:
                logger.error(f"Failed to delete old S3 object: {e}")

        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': _("Resource document updated successfully."),
                'resource': {
                    'id': str(self.object.pk),
                    'title': self.object.title,
                }
            })

        messages.success(self.request, _("Resource document updated successfully."))
        return response

    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)

        messages.error(self.request, _("Please correct the errors below."))
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['s3_configured'] = s3_resource_manager.is_configured()
        # Generate temporary download URL for existing file
        if self.object and self.object.file_key:
            context['download_url'] = s3_resource_manager.generate_signed_download_url(
                self.object.file_key,
                expires_in=300
            )
        return context


class ResourceDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    """Delete a resource document."""
    model = ResourceDocument
    success_url = reverse_lazy("resources:resources_list")

    def post(self, request, *args, **kwargs):
        """Handle DELETE via POST with proper cleanup"""
        self.object = self.get_object()

        # Store file key before deletion
        file_key = self.object.file_key

        # Delete from database first
        self.object.delete()

        # Delete from S3 if configured
        if s3_resource_manager.is_configured() and file_key:
            try:
                s3_resource_manager.delete_object(file_key)
                logger.info(f"Deleted S3 object: {file_key}")
            except Exception as e:
                logger.error(f"Failed to delete S3 object: {e}")
                # Continue anyway since DB record is already deleted

        messages.success(request, _("Resource document deleted successfully."))

        # Return JSON if AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})

        # Redirect for normal requests
        from django.shortcuts import redirect
        return redirect(self.success_url)




class GetArticlesByCategoryView(LoginRequiredMixin, AdminRequiredMixin, View):
    """
    API endpoint to get articles filtered by category (for dynamic form field).
    Used when selecting a category to filter available articles.
    """

    def get(self, request):
        category_id = request.GET.get('category_id')

        if not category_id:
            return JsonResponse({
                'articles': []
            })

        try:
            category = Category.objects.get(pk=category_id)
            articles = Article.objects.filter(
                categories=category
            ).distinct().values('id', 'title').order_by('-created_at')[:50]

            return JsonResponse({
                'articles': list(articles)
            })
        except Category.DoesNotExist:
            return JsonResponse({
                'articles': []
            })
        except Exception as e:
            logger.error(f"Error fetching articles by category: {e}")
            return JsonResponse({
                'error': str(e)
            }, status=500)


class GenerateResourceDownloadUrlView(LoginRequiredMixin, View):
    """Generate temporary signed download URL for a resource"""

    def get(self, request, pk):
        from django.http import Http404, HttpResponseForbidden, HttpResponseServerError
        from django.shortcuts import redirect

        # Get resource or 404
        try:
            resource = ResourceDocument.objects.get(pk=pk)
        except ResourceDocument.DoesNotExist:
            raise Http404(_("Resource not found"))

        # Check permissions
        if not (request.user.is_staff or request.user.is_superuser or resource.uploaded_by == request.user):
            return HttpResponseForbidden(_('You do not have permission to download this resource'))

        # Check if file exists
        if not resource.file_key:
            raise Http404(_('Resource file not found'))

        # Generate signed URL
        url = s3_resource_manager.generate_signed_download_url(
            resource.file_key,
            expires_in=300  # 5 minutes
        )

        if not url:
            return HttpResponseServerError(_('Failed to generate download URL'))

        # Increment download count
        resource.download_count += 1
        resource.save(update_fields=['download_count'])

        # Redirect to signed URL
        return redirect(url)

