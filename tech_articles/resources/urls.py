"""URL configuration for media library."""
from django.urls import path

from . import views

app_name = "media"

urlpatterns = [
    # Media library main views
    path("", views.MediaLibraryView.as_view(), name="library"),
    path("upload/", views.MediaFileUploadView.as_view(), name="upload"),
    path("file/<uuid:pk>/", views.MediaFileDetailView.as_view(), name="file_detail"),
    path("file/<uuid:pk>/edit/", views.MediaFileUpdateView.as_view(), name="file_edit"),
    path("file/<uuid:pk>/delete/", views.MediaFileDeleteView.as_view(), name="file_delete"),
    
    # Folder management
    path("folders/", views.MediaFolderListView.as_view(), name="folders"),
    path("folders/create/", views.MediaFolderCreateView.as_view(), name="folder_create"),
    path("folders/<uuid:pk>/edit/", views.MediaFolderUpdateView.as_view(), name="folder_edit"),
    path("folders/<uuid:pk>/delete/", views.MediaFolderDeleteView.as_view(), name="folder_delete"),
    
    # AJAX/API endpoints
    path("api/bulk-upload/", views.MediaFileBulkUploadView.as_view(), name="api_bulk_upload"),
    path("api/search/", views.MediaFileSearchView.as_view(), name="api_search"),
]
