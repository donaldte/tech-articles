"""
Media tags views for dashboard CRUD operations.
"""
import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from tech_articles.resources.models import MediaTag
from tech_articles.resources.forms import MediaTagForm

logger = logging.getLogger(__name__)


class AdminRequiredMixin(UserPassesTestMixin):
    """Mixin that requires user to be an admin or staff."""
    
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser


class MediaTagListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    """List all media tags with file counts."""
    
    model = MediaTag
    template_name = "tech-articles/dashboard/pages/media/tags_list.html"
    context_object_name = "tags"
    paginate_by = 20
    
    def get_queryset(self):
        """Get tags with file counts."""
        return MediaTag.objects.annotate(file_count=Count("files")).order_by("name")


class MediaTagCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    """Create new media tag."""
    
    model = MediaTag
    form_class = MediaTagForm
    template_name = "tech-articles/dashboard/pages/media/tag_form.html"
    success_url = reverse_lazy("dashboard:media:tags_list")
    
    def form_valid(self, form):
        """Generate slug and save."""
        tag = form.save(commit=False)
        tag.slug = slugify(tag.name)
        tag.save()
        messages.success(self.request, _("Tag created successfully."))
        return super().form_valid(form)


class MediaTagUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    """Update media tag."""
    
    model = MediaTag
    form_class = MediaTagForm
    template_name = "tech-articles/dashboard/pages/media/tag_form.html"
    success_url = reverse_lazy("dashboard:media:tags_list")
    
    def form_valid(self, form):
        """Update slug if name changed."""
        tag = form.save(commit=False)
        tag.slug = slugify(tag.name)
        tag.save()
        messages.success(self.request, _("Tag updated successfully."))
        return super().form_valid(form)


class MediaTagDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    """Delete media tag."""
    
    model = MediaTag
    success_url = reverse_lazy("dashboard:media:tags_list")
    
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
