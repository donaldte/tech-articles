"""
API views for AJAX operations in media library.
"""
import logging
import mimetypes

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.views.generic import View

from tech_articles.resources.models import MediaFile, MediaFolder
from tech_articles.resources.storage import MediaStorage, ImageOptimizer, validate_file_size, validate_file_type
from tech_articles.resources.mixins import AdminRequiredMixin

logger = logging.getLogger(__name__)


class MediaFileBulkUploadView(LoginRequiredMixin, AdminRequiredMixin, View):
    """Handle bulk file uploads via AJAX."""
    
    def post(self, request):
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
                    
                    base_key = MediaStorage.get_base_key(file_key)
                    
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
                
            except ValueError as e:
                logger.error(f"Validation error in bulk upload for {file_obj.name}: {e}")
                errors.append({"file": file_obj.name, "error": _("Invalid file format or data")})
            except IOError as e:
                logger.error(f"Storage error in bulk upload for {file_obj.name}: {e}")
                errors.append({"file": file_obj.name, "error": _("Error saving file to storage")})
            except Exception as e:
                logger.error(f"Unexpected error uploading file {file_obj.name}: {e}")
                errors.append({"file": file_obj.name, "error": _("An unexpected error occurred")})
        
        return JsonResponse({
            "uploaded": uploaded_files,
            "errors": errors,
            "success_count": len(uploaded_files),
            "error_count": len(errors),
        })


class MediaFileSearchView(LoginRequiredMixin, AdminRequiredMixin, View):
    """AJAX search for media files."""
    
    def get(self, request):
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
