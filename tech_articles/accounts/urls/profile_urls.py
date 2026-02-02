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

app_name = "profile"

urlpatterns = [
    path("", ProfileEditView.as_view(), name="edit"),
    path("security/", ProfileSecurityView.as_view(), name="security"),
    path("avatar/upload/", ProfileAvatarUploadView.as_view(), name="avatar_upload"),
    path("avatar/delete/", ProfileAvatarDeleteView.as_view(), name="avatar_delete"),
]
