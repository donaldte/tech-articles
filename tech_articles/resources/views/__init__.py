"""
Resources views module.
Exports all views from feature-specific modules.
"""
from .media_files_views import (
    MediaLibraryView,
    MediaFileUploadView,
    MediaFileDetailView,
    MediaFileUpdateView,
    MediaFileDeleteView,
)
from .media_folders_views import (
    MediaFolderListView,
    MediaFolderCreateView,
    MediaFolderUpdateView,
    MediaFolderDeleteView,
)
from .media_tags_views import (
    MediaTagListView,
    MediaTagCreateView,
    MediaTagUpdateView,
    MediaTagDeleteView,
)
from .api_views import (
    MediaFileBulkUploadView,
    MediaFileSearchView,
)

__all__ = [
    # Media Files
    "MediaLibraryView",
    "MediaFileUploadView",
    "MediaFileDetailView",
    "MediaFileUpdateView",
    "MediaFileDeleteView",
    # Media Folders
    "MediaFolderListView",
    "MediaFolderCreateView",
    "MediaFolderUpdateView",
    "MediaFolderDeleteView",
    # Media Tags
    "MediaTagListView",
    "MediaTagCreateView",
    "MediaTagUpdateView",
    "MediaTagDeleteView",
    # API
    "MediaFileBulkUploadView",
    "MediaFileSearchView",
]
