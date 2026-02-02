"""Views for media library management."""
from __future__ import annotations

import logging
import mimetypes
from typing import TYPE_CHECKING

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q, Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, View

from .models import MediaFile, MediaFolder, MediaTag
from .forms import MediaFileForm, MediaFileMetadataForm, MediaFolderForm, MediaTagForm
from .storage import MediaStorage, ImageOptimizer, validate_file_size, validate_file_type

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse

logger = logging.getLogger(__name__)


class AdminRequiredMixin(UserPassesTestMixin):
    """Mixin that requires user to be an admin or staff."""
    
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser


# ============================================================================
# MEDIA FILE VIEWS
# ============================================================================

class MediaLibraryView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    """Main media library view with grid display."""
    
    model = MediaFile
    template_name = "tech-articles/dashboard/pages/media/library.html"
    context_object_name = "media_files"
    paginate_by = 24
    
    def get_queryset(self):
        """Filter media files based on search, folder, and file type."""
        queryset = MediaFile.objects.select_related("folder", "uploaded_by").prefetch_related("tags")
        
        # Search
        search_query = self.request.GET.get("q", "").strip()
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(file_name__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        # Filter by folder
        folder_id = self.request.GET.get("folder")
        if folder_id:
            try:
                queryset = queryset.filter(folder_id=folder_id)
            except ValueError:
                pass  # Invalid folder_id format, ignore filter
        
        # Filter by file type
        file_type = self.request.GET.get("type")
        if file_type:
            queryset = queryset.filter(file_type=file_type)
        
        # Filter by tag
        tag_id = self.request.GET.get("tag")
        if tag_id:
            queryset = queryset.filter(tags__id=tag_id)
        
        return queryset.order_by("-created_at")
    
    def get_context_data(self, **kwargs):
        """Add extra context for filters."""
        context = super().get_context_data(**kwargs)
        context["folders"] = MediaFolder.objects.all().order_by("name")
        context["tags"] = MediaTag.objects.annotate(file_count=Count("files")).order_by("name")
        context["current_folder"] = self.request.GET.get("folder")
        context["current_type"] = self.request.GET.get("type")
        context["search_query"] = self.request.GET.get("q", "")
        return context


class MediaFileUploadView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    """Upload new media files."""
    
    model = MediaFile
    form_class = MediaFileForm
    template_name = "tech-articles/dashboard/pages/media/upload.html"
    success_url = reverse_lazy("dashboard:media:library")
    
    def form_valid(self, form):
        """Handle file upload with validation and optimization."""
        file_obj = self.request.FILES.get("file")
        
        if not file_obj:
            messages.error(self.request, _("No file was uploaded."))
            return self.form_invalid(form)
        
        # Validate file size
        is_valid, error_msg = validate_file_size(file_obj, max_size_mb=50)
        if not is_valid:
            messages.error(self.request, error_msg)
            return self.form_invalid(form)
        
        # Validate file type
        is_valid, error_msg = validate_file_type(file_obj)
        if not is_valid:
            messages.error(self.request, error_msg)
            return self.form_invalid(form)
        
        try:
            # Get MIME type
            mime_type = file_obj.content_type or mimetypes.guess_type(file_obj.name)[0] or "application/octet-stream"
            file_type = MediaStorage.get_file_type(mime_type)
            
            # Generate file key
            folder = form.cleaned_data.get("folder")
            folder_path = folder.get_full_path() if folder else ""
            file_key = MediaStorage.generate_file_key(file_obj.name, folder_path)
            
            # Save media file instance
            media_file = form.save(commit=False)
            media_file.file_name = file_obj.name
            media_file.file_type = file_type
            media_file.mime_type = mime_type
            media_file.file_size = file_obj.size
            media_file.file_key = file_key
            media_file.uploaded_by = self.request.user
            
            # Handle image-specific processing
            if file_type == "image":
                # Get dimensions
                width, height = ImageOptimizer.get_image_dimensions(file_obj)
                media_file.width = width
                media_file.height = height
                
                # Optimize image
                optimized_file = ImageOptimizer.optimize_image(file_obj)
                base_key = file_key.rsplit(".", 1)[0] if "." in file_key else file_key
                optimized_key = base_key + ".optimized.jpg"
                MediaStorage.save_to_s3(optimized_file, optimized_key)
                media_file.optimized_key = optimized_key
                
                # Create thumbnail
                file_obj.seek(0)  # Reset file pointer
                thumbnail_file = ImageOptimizer.create_thumbnail(file_obj)
                thumbnail_key = base_key + ".thumb.jpg"
                MediaStorage.save_to_s3(thumbnail_file, thumbnail_key)
                media_file.thumbnail_key = thumbnail_key
            
            # Upload original file to S3
            file_obj.seek(0)
            MediaStorage.save_to_s3(file_obj, file_key)
            
            # Save media file
            media_file.save()
            form.save_m2m()  # Save many-to-many relationships
            
            messages.success(self.request, _("File uploaded successfully."))
            return redirect(self.success_url)
            
        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            messages.error(self.request, _("Error uploading file. Please try again."))
            return self.form_invalid(form)
    
    def get_context_data(self, **kwargs):
        """Add folders to context."""
        context = super().get_context_data(**kwargs)
        context["folders"] = MediaFolder.objects.all().order_by("name")
        return context


class MediaFileDetailView(LoginRequiredMixin, AdminRequiredMixin, DetailView):
    """View and edit media file details."""
    
    model = MediaFile
    template_name = "tech-articles/dashboard/pages/media/detail.html"
    context_object_name = "media_file"
    
    def get_context_data(self, **kwargs):
        """Add metadata form to context."""
        context = super().get_context_data(**kwargs)
        context["form"] = MediaFileMetadataForm(instance=self.object)
        context["file_url"] = MediaStorage.get_file_url(self.object.file_key)
        if self.object.thumbnail_key:
            context["thumbnail_url"] = MediaStorage.get_file_url(self.object.thumbnail_key)
        return context


class MediaFileUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    """Update media file metadata."""
    
    model = MediaFile
    form_class = MediaFileMetadataForm
    template_name = "tech-articles/dashboard/pages/media/edit.html"
    
    def get_success_url(self):
        """Redirect to detail view."""
        return reverse_lazy("dashboard:media:file_detail", kwargs={"pk": self.object.pk})
    
    def form_valid(self, form):
        """Handle successful form submission."""
        messages.success(self.request, _("Media file updated successfully."))
        return super().form_valid(form)


class MediaFileDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    """Delete media file and its S3 objects."""
    
    model = MediaFile
    success_url = reverse_lazy("dashboard:media:library")
    
    def delete(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Delete file from S3 and database."""
        self.object = self.get_object()
        
        try:
            # Delete from S3
            MediaStorage.delete_from_s3(self.object.file_key)
            if self.object.thumbnail_key:
                MediaStorage.delete_from_s3(self.object.thumbnail_key)
            if self.object.optimized_key:
                MediaStorage.delete_from_s3(self.object.optimized_key)
            
            # Delete from database
            self.object.delete()
            
            messages.success(request, _("Media file deleted successfully."))
        except Exception as e:
            logger.error(f"Error deleting media file: {e}")
            messages.error(request, _("Error deleting media file."))
        
        return redirect(self.success_url)


# ============================================================================
# FOLDER VIEWS
# ============================================================================

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


# ============================================================================
# AJAX/API VIEWS
# ============================================================================

class MediaFileBulkUploadView(LoginRequiredMixin, AdminRequiredMixin, View):
    """Handle bulk file uploads via AJAX."""
    
    def post(self, request: HttpRequest) -> JsonResponse:
        """Process multiple file uploads."""
        files = request.FILES.getlist("files[]")
        folder_id = request.POST.get("folder_id")
        
        if not files:
            return JsonResponse({"error": _("No files uploaded")}, status=400)
        
        folder = None
        if folder_id:
            folder = get_object_or_404(MediaFolder, id=folder_id)
        
        uploaded_files = []
        errors = []
        
        for file_obj in files:
            try:
                # Validate
                is_valid, error_msg = validate_file_size(file_obj, max_size_mb=50)
                if not is_valid:
                    errors.append({"file": file_obj.name, "error": error_msg})
                    continue
                
                is_valid, error_msg = validate_file_type(file_obj)
                if not is_valid:
                    errors.append({"file": file_obj.name, "error": error_msg})
                    continue
                
                # Process file
                mime_type = file_obj.content_type or mimetypes.guess_type(file_obj.name)[0] or "application/octet-stream"
                file_type = MediaStorage.get_file_type(mime_type)
                folder_path = folder.get_full_path() if folder else ""
                file_key = MediaStorage.generate_file_key(file_obj.name, folder_path)
                
                # Create media file
                media_file = MediaFile.objects.create(
                    title=file_obj.name,
                    file_name=file_obj.name,
                    file_type=file_type,
                    mime_type=mime_type,
                    file_size=file_obj.size,
                    file_key=file_key,
                    folder=folder,
                    uploaded_by=request.user,
                )
                
                # Handle image optimization
                if file_type == "image":
                    width, height = ImageOptimizer.get_image_dimensions(file_obj)
                    media_file.width = width
                    media_file.height = height
                    
                    base_key = file_key.rsplit(".", 1)[0] if "." in file_key else file_key
                    
                    optimized_file = ImageOptimizer.optimize_image(file_obj)
                    optimized_key = base_key + ".optimized.jpg"
                    MediaStorage.save_to_s3(optimized_file, optimized_key)
                    media_file.optimized_key = optimized_key
                    
                    file_obj.seek(0)
                    thumbnail_file = ImageOptimizer.create_thumbnail(file_obj)
                    thumbnail_key = base_key + ".thumb.jpg"
                    MediaStorage.save_to_s3(thumbnail_file, thumbnail_key)
                    media_file.thumbnail_key = thumbnail_key
                    
                    media_file.save()
                
                # Upload to S3
                file_obj.seek(0)
                MediaStorage.save_to_s3(file_obj, file_key)
                
                uploaded_files.append({
                    "id": str(media_file.id),
                    "title": media_file.title,
                    "file_name": media_file.file_name,
                    "file_type": media_file.file_type,
                    "file_size": media_file.file_size_mb,
                })
                
            except Exception as e:
                logger.error(f"Error uploading file {file_obj.name}: {e}")
                errors.append({"file": file_obj.name, "error": str(e)})
        
        return JsonResponse({
            "uploaded": uploaded_files,
            "errors": errors,
            "success_count": len(uploaded_files),
            "error_count": len(errors),
        })


class MediaFileSearchView(LoginRequiredMixin, AdminRequiredMixin, View):
    """AJAX search for media files."""
    
    def get(self, request: HttpRequest) -> JsonResponse:
        """Search media files."""
        query = request.GET.get("q", "").strip()
        file_type = request.GET.get("type", "")
        
        media_files = MediaFile.objects.all()
        
        if query:
            media_files = media_files.filter(
                Q(title__icontains=query) |
                Q(file_name__icontains=query)
            )
        
        if file_type:
            media_files = media_files.filter(file_type=file_type)
        
        media_files = media_files[:20]  # Limit results
        
        results = [
            {
                "id": str(mf.id),
                "title": mf.title,
                "file_name": mf.file_name,
                "file_type": mf.file_type,
                "file_url": MediaStorage.get_file_url(mf.file_key),
                "thumbnail_url": MediaStorage.get_file_url(mf.thumbnail_key) if mf.thumbnail_key else None,
            }
            for mf in media_files
        ]
        
        return JsonResponse({"results": results})
