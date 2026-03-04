"""
Forum group access URL patterns (subscription requests + admin approval).
"""
from django.urls import path

from tech_articles.forums.views import (
    ForumGroupAccessListView,
    GroupAccessRequestView,
    ForumGroupAccessApproveView,
    ForumGroupAccessRejectView,
)

urlpatterns = [
    # Admin
    path(
        "dashboard/access/",
        ForumGroupAccessListView.as_view(),
        name="access_list",
    ),
    path(
        "dashboard/access/<uuid:pk>/approve/",
        ForumGroupAccessApproveView.as_view(),
        name="access_approve",
    ),
    path(
        "dashboard/access/<uuid:pk>/reject/",
        ForumGroupAccessRejectView.as_view(),
        name="access_reject",
    ),

    # User-facing
    path(
        "<slug:category_slug>/request-access/",
        GroupAccessRequestView.as_view(),
        name="access_request",
    ),
]
