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

urlpatterns = [
    path("users/", UserListView.as_view(), name="users_list"),
    path("users/create/", UserCreateView.as_view(), name="users_create"),
    path("users/<uuid:pk>/", UserDetailView.as_view(), name="users_detail"),
    path("users/<uuid:pk>/edit/", UserUpdateView.as_view(), name="users_update"),
    path("users/<uuid:pk>/delete/", UserDeleteView.as_view(), name="users_delete"),
    path(
        "users/<uuid:pk>/change-password/",
        UserPasswordChangeView.as_view(),
        name="users_change_password",
    ),
]
