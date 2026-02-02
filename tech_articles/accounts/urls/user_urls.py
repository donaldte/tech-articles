"""
Admin user management URLs.
"""
from django.urls import path

from tech_articles.accounts.views import (
    UserListView,
    UserCreateView,
    UserDetailView,
    UserUpdateView,
    UserDeleteView,
    UserPasswordChangeView,
)

app_name = "users"

urlpatterns = [
    path("", UserListView.as_view(), name="list"),
    path("create/", UserCreateView.as_view(), name="create"),
    path("<uuid:pk>/", UserDetailView.as_view(), name="detail"),
    path("<uuid:pk>/edit/", UserUpdateView.as_view(), name="update"),
    path("<uuid:pk>/delete/", UserDeleteView.as_view(), name="delete"),
    path("<uuid:pk>/change-password/", UserPasswordChangeView.as_view(), name="change_password"),
]
