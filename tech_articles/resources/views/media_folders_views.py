"""
Media folders views for dashboard CRUD operations.
"""
import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from tech_articles.resources.models import MediaFolder
from tech_articles.resources.forms import MediaFolderForm
from tech_articles.resources.mixins import AdminRequiredMixin

logger = logging.getLogger(__name__)


class MediaFolderListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    """List all media folders."""
    
    model = MediaFolder
    template_name = "tech-articles/dashboard/pages/media/folders.html"
    context_object_name = "folders"
    
    def get_queryset(self):
        """Get folders with file counts."""
        return MediaFolder.objects.annotate(file_count=Count("files")).order_by("name")


class MediaFolderCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    """Create new media folder."""
    
    model = MediaFolder
    form_class = MediaFolderForm
    template_name = "tech-articles/dashboard/pages/media/folder_form.html"
    success_url = reverse_lazy("dashboard:media:folders")
    
    def form_valid(self, form):
        """Set created_by and generate slug."""
        folder = form.save(commit=False)
        folder.created_by = self.request.user
        folder.slug = slugify(folder.name)
        folder.save()
        messages.success(self.request, _("Folder created successfully."))
        return redirect(self.success_url)


class MediaFolderUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    """Update media folder."""
    
    model = MediaFolder
    form_class = MediaFolderForm
    template_name = "tech-articles/dashboard/pages/media/folder_form.html"
    success_url = reverse_lazy("dashboard:media:folders")
    
    def form_valid(self, form):
        """Update slug if name changed."""
        folder = form.save(commit=False)
        folder.slug = slugify(folder.name)
        folder.save()
        messages.success(self.request, _("Folder updated successfully."))
        return redirect(self.success_url)


class MediaFolderDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    """Delete media folder."""
    
    model = MediaFolder
    success_url = reverse_lazy("dashboard:media:folders")
    
    def delete(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Delete folder after checking for files."""
        self.object = self.get_object()
        
        # Check if folder has files
        if self.object.files.exists():
            messages.error(request, _("Cannot delete folder with files. Move or delete files first."))
            return redirect(self.success_url)
        
        self.object.delete()
        messages.success(request, _("Folder deleted successfully."))
        return redirect(self.success_url)
