"""
Resources URLs module.
Main URL configuration for media library management.
Accessible at /dashboard/media/ from dashboard
"""
from django.urls import path

from tech_articles.resources.views import (
    # Media Files
    MediaLibraryView,
    MediaFileUploadView,
    MediaFileDetailView,
    MediaFileUpdateView,
    MediaFileDeleteView,
    # Media Folders
    MediaFolderListView,
    MediaFolderCreateView,
    MediaFolderUpdateView,
    MediaFolderDeleteView,
    # Media Tags
    MediaTagListView,
    MediaTagCreateView,
    MediaTagUpdateView,
    MediaTagDeleteView,
    # API
    MediaFileBulkUploadView,
    MediaFileSearchView,
)

app_name = "media"

urlpatterns = [
    # =====================
    # MEDIA FILES
    # =====================
    path("", MediaLibraryView.as_view(), name="library"),
    path("upload/", MediaFileUploadView.as_view(), name="upload"),
    path("file/<uuid:pk>/", MediaFileDetailView.as_view(), name="file_detail"),
    path("file/<uuid:pk>/edit/", MediaFileUpdateView.as_view(), name="file_edit"),
    path("file/<uuid:pk>/delete/", MediaFileDeleteView.as_view(), name="file_delete"),
    
    # =====================
    # FOLDERS
    # =====================
    path("folders/", MediaFolderListView.as_view(), name="folders"),
    path("folders/create/", MediaFolderCreateView.as_view(), name="folder_create"),
    path("folders/<uuid:pk>/edit/", MediaFolderUpdateView.as_view(), name="folder_edit"),
    path("folders/<uuid:pk>/delete/", MediaFolderDeleteView.as_view(), name="folder_delete"),
    
    # =====================
    # TAGS
    # =====================
    path("tags/", MediaTagListView.as_view(), name="tags_list"),
    path("tags/create/", MediaTagCreateView.as_view(), name="tags_create"),
    path("tags/<uuid:pk>/edit/", MediaTagUpdateView.as_view(), name="tags_update"),
    path("tags/<uuid:pk>/delete/", MediaTagDeleteView.as_view(), name="tags_delete"),
    
    # =====================
    # API ENDPOINTS
    # =====================
    path("api/bulk-upload/", MediaFileBulkUploadView.as_view(), name="api_bulk_upload"),
    path("api/search/", MediaFileSearchView.as_view(), name="api_search"),
]
