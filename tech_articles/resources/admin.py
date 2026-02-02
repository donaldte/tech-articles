"""Admin registration for resources app."""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import ResourceDocument, MediaFile, MediaFolder, MediaTag


@admin.register(ResourceDocument)
class ResourceDocumentAdmin(admin.ModelAdmin):
    """Admin for ResourceDocument model."""
    
    list_display = ["title", "access_level", "article", "category", "created_at"]
    list_filter = ["access_level", "watermark_enabled", "created_at"]
    search_fields = ["title", "description"]
    date_hierarchy = "created_at"
    readonly_fields = ["created_at", "updated_at"]


@admin.register(MediaFile)
class MediaFileAdmin(admin.ModelAdmin):
    """Admin for MediaFile model."""
    
    list_display = ["title", "file_name", "file_type", "file_size_display", "folder", "uploaded_by", "created_at"]
    list_filter = ["file_type", "access_level", "created_at", "folder"]
    search_fields = ["title", "file_name", "description", "alt_text"]
    date_hierarchy = "created_at"
    readonly_fields = ["created_at", "updated_at", "file_size", "width", "height", "download_count"]
    filter_horizontal = ["tags"]
    
    fieldsets = (
        (_("Basic Information"), {
            "fields": ("title", "description", "alt_text"),
        }),
        (_("File Information"), {
            "fields": ("file_name", "file_type", "mime_type", "file_size", "width", "height"),
        }),
        (_("Storage"), {
            "fields": ("file_key", "thumbnail_key", "optimized_key"),
        }),
        (_("Organization"), {
            "fields": ("folder", "tags", "access_level"),
        }),
        (_("Metadata"), {
            "fields": ("uploaded_by", "download_count", "created_at", "updated_at"),
        }),
    )
    
    def file_size_display(self, obj):
        """Display file size in human-readable format."""
        return f"{obj.file_size_mb} MB"
    file_size_display.short_description = _("Size")


@admin.register(MediaFolder)
class MediaFolderAdmin(admin.ModelAdmin):
    """Admin for MediaFolder model."""
    
    list_display = ["name", "parent", "created_by", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["name", "description"]
    date_hierarchy = "created_at"
    readonly_fields = ["slug", "created_at", "updated_at"]


@admin.register(MediaTag)
class MediaTagAdmin(admin.ModelAdmin):
    """Admin for MediaTag model."""
    
    list_display = ["name", "slug", "created_at"]
    search_fields = ["name"]
    readonly_fields = ["slug", "created_at", "updated_at"]
