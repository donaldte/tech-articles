"""
Profile management URLs.
"""

from django.urls import path

from tech_articles.accounts.views import (
    ProfileEditView,
    ProfileSecurityView,
    ProfileAvatarUploadView,
    ProfileAvatarDeleteView,
)

urlpatterns = [
    path("profile/", ProfileEditView.as_view(), name="profile_edit"),
    path("profile/security/", ProfileSecurityView.as_view(), name="profile_security"),
    path(
        "profile/avatar/upload/",
        ProfileAvatarUploadView.as_view(),
        name="profile_avatar_upload",
    ),
    path(
        "profile/avatar/delete/",
        ProfileAvatarDeleteView.as_view(),
        name="profile_avatar_delete",
    ),
]
