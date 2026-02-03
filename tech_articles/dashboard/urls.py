"""
Dashboard URL configuration for Runbookly.
Organizes URLs for admin and user dashboard features.
"""
from django.urls import path

from . import views
from tech_articles.accounts.views import (
    UserListView, UserCreateView, UserDetailView, UserUpdateView,
    UserDeleteView, UserPasswordChangeView,
    ProfileEditView, ProfileSecurityView, ProfileAvatarUploadView, ProfileAvatarDeleteView,
)

app_name = "dashboard"

urlpatterns = [
    # =====================
    # MAIN DASHBOARD
    # =====================
    path("", views.DashboardPageView.as_view(), name="home"),

    # =====================
    # CONTENT MANAGEMENT (Admin) - Articles only (no dedicated app yet)
    # =====================
    path("content/articles/", views.ArticleListView.as_view(), name="articles_list"),
    path("content/articles/create/", views.ArticleCreateView.as_view(), name="articles_create"),

    # Note: Categories, Tags moved to content app (/content/)
    # Note: Resources moved to resources app (/resources/)
    # Note: Appointments moved to appointments app (/appointments/)
    # Note: Billing (Transactions, Subscriptions) moved to billing app (/billing/)
    # Note: Newsletter moved to newsletter app (/newsletter/)
    # Note: Analytics moved to analytics app (/analytics/)

    # =====================
    # USER MANAGEMENT (Admin)
    # =====================
    path("users/", UserListView.as_view(), name="users_list"),
    path("users/create/", UserCreateView.as_view(), name="users_create"),
    path("users/<uuid:pk>/", UserDetailView.as_view(), name="users_detail"),
    path("users/<uuid:pk>/edit/", UserUpdateView.as_view(), name="users_update"),
    path("users/<uuid:pk>/delete/", UserDeleteView.as_view(), name="users_delete"),
    path("users/<uuid:pk>/change-password/", UserPasswordChangeView.as_view(), name="users_change_password"),

    # =====================
    # USER PROFILE (All Users)
    # =====================
    path("profile/", ProfileEditView.as_view(), name="profile_edit"),
    path("profile/security/", ProfileSecurityView.as_view(), name="profile_security"),
    path("profile/avatar/upload/", ProfileAvatarUploadView.as_view(), name="profile_avatar_upload"),
    path("profile/avatar/delete/", ProfileAvatarDeleteView.as_view(), name="profile_avatar_delete"),

    # =====================
    # MY SUBSCRIPTION (All Users)
    # =====================
    path("my-subscription/", views.MySubscriptionView.as_view(), name="my_subscription"),
    path("my-subscription/invoices/", views.MyInvoicesView.as_view(), name="my_invoices"),

    # =====================
    # MY APPOINTMENTS (All Users)
    # =====================
    path("my-appointments/", views.MyAppointmentsView.as_view(), name="my_appointments"),
    path("my-appointments/book/", views.BookAppointmentView.as_view(), name="book_appointment"),

    # =====================
    # SUPPORT & HELP
    # =====================
    path("support/", views.SupportView.as_view(), name="support"),
]
