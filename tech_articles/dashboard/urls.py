"""
Dashboard URL configuration for Runbookly.
Organizes URLs for admin and user dashboard features.
"""
from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    # =====================
    # MAIN DASHBOARD
    # =====================
    path("", views.DashboardPageView.as_view(), name="home"),

    # =====================
    # CONTENT MANAGEMENT (Admin)
    # =====================
    # Articles
    path("content/articles/", views.ArticleListView.as_view(), name="articles_list"),
    path("content/articles/create/", views.ArticleCreateView.as_view(), name="articles_create"),

    # Categories
    path("content/categories/", views.CategoryListView.as_view(), name="categories_list"),
    path("content/categories/create/", views.CategoryCreateView.as_view(), name="categories_create"),

    # Tags
    path("content/tags/", views.TagListView.as_view(), name="tags_list"),
    path("content/tags/create/", views.TagCreateView.as_view(), name="tags_create"),

    # =====================
    # RESOURCES MANAGEMENT (Admin)
    # =====================
    path("resources/", views.ResourceListView.as_view(), name="resources_list"),
    path("resources/create/", views.ResourceCreateView.as_view(), name="resources_create"),

    # =====================
    # APPOINTMENTS MANAGEMENT (Admin)
    # =====================
    path("appointments/", views.AppointmentListView.as_view(), name="appointments_list"),
    path("appointments/types/", views.AppointmentTypeListView.as_view(), name="appointment_types_list"),
    path("appointments/types/create/", views.AppointmentTypeCreateView.as_view(), name="appointment_types_create"),
    path("appointments/availability/", views.AvailabilitySettingsView.as_view(), name="availability_settings"),

    # =====================
    # BILLING & SUBSCRIPTIONS (Admin)
    # =====================
    # Plans
    path("billing/plans/", views.PlanListView.as_view(), name="plans_list"),
    path("billing/plans/create/", views.PlanCreateView.as_view(), name="plans_create"),

    # Coupons
    path("billing/coupons/", views.CouponListView.as_view(), name="coupons_list"),
    path("billing/coupons/create/", views.CouponCreateView.as_view(), name="coupons_create"),

    # Transactions
    path("billing/transactions/", views.TransactionListView.as_view(), name="transactions_list"),

    # Subscriptions (admin view)
    path("billing/subscriptions/", views.SubscriptionListView.as_view(), name="subscriptions_list"),

    # =====================
    # NEWSLETTER MANAGEMENT (Admin)
    # =====================
    path("newsletter/subscribers/", views.SubscriberListView.as_view(), name="subscribers_list"),
    path("newsletter/campaigns/", views.CampaignListView.as_view(), name="campaigns_list"),
    path("newsletter/campaigns/create/", views.CampaignCreateView.as_view(), name="campaigns_create"),

    # =====================
    # ANALYTICS (Admin)
    # =====================
    path("analytics/", views.AnalyticsOverviewView.as_view(), name="analytics_overview"),
    path("analytics/events/", views.EventsListView.as_view(), name="analytics_events"),

    # =====================
    # USER MANAGEMENT (Admin)
    # =====================
    path("users/", views.UserListView.as_view(), name="users_list"),
    path("users/create/", views.UserCreateView.as_view(), name="users_create"),

    # =====================
    # USER PROFILE (All Users)
    # =====================
    path("profile/", views.ProfileEditView.as_view(), name="profile_edit"),
    path("profile/security/", views.ProfileSecurityView.as_view(), name="profile_security"),

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
