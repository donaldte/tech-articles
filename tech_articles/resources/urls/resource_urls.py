"""
Resource URL patterns for dashboard CRUD operations and S3 multipart upload API.
"""
from django.urls import path

from tech_articles.resources.views.resource_views import (
    ResourceListView,
    ResourceCreateView,
    ResourceCreatePopupView,
    ResourceUpdateView,
    ResourceDeleteView,
    GetArticlesByCategoryView,
    GenerateResourceDownloadUrlView,
)
from tech_articles.resources.views.api_views import (
    create_multipart_upload,
    generate_presigned_urls,
    complete_multipart_upload,
    abort_multipart_upload,
    generate_download_url,
)

urlpatterns = [
    # Resource CRUD views
    path("", ResourceListView.as_view(), name="resources_list"),
    path("create/", ResourceCreateView.as_view(), name="resources_create"),
    path("create/popup/", ResourceCreatePopupView.as_view(), name="resources_create_popup"),
    path("<uuid:pk>/edit/", ResourceUpdateView.as_view(), name="resources_update"),
    path("<uuid:pk>/delete/", ResourceDeleteView.as_view(), name="resources_delete"),
    path("<uuid:pk>/download-url/", GenerateResourceDownloadUrlView.as_view(), name="resources_download_url"),

    # Dynamic form helpers
    path("api/articles-by-category/", GetArticlesByCategoryView.as_view(), name="articles_by_category"),

    # S3 multipart upload API
    path("api/upload/create/", create_multipart_upload, name="api_create_multipart_upload"),
    path("api/upload/presigned-urls/", generate_presigned_urls, name="api_generate_presigned_urls"),
    path("api/upload/complete/", complete_multipart_upload, name="api_complete_multipart_upload"),
    path("api/upload/abort/", abort_multipart_upload, name="api_abort_multipart_upload"),
    path("api/download-url/", generate_download_url, name="api_generate_download_url"),
]


