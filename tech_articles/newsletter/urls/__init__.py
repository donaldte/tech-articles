"""
Newsletter URLs module.
Main URL configuration for newsletter management.
"""
from django.urls import path

from tech_articles.newsletter.views import (
    # Public views
    NewsletterSubscribeView,
    NewsletterSubscribePendingView,
    NewsletterConfirmView,
    NewsletterUnsubscribeView,
    NewsletterUnsubscribeSuccessView,
    # Subscriber views
    SubscriberListView,
    SubscriberExportView,
    SubscriberImportView,
    SubscriberDetailView,
    SubscriberEditView,
)

app_name = "newsletter"

urlpatterns = [
    # =====================
    # PUBLIC NEWSLETTER
    # =====================
    path("subscribe/", NewsletterSubscribeView.as_view(), name="subscribe"),
    path("subscribe/pending/", NewsletterSubscribePendingView.as_view(), name="subscribe_pending"),
    path("confirm/<str:token>/", NewsletterConfirmView.as_view(), name="confirm"),
    path("unsubscribe/<str:token>/", NewsletterUnsubscribeView.as_view(), name="unsubscribe"),
    path("unsubscribe/success/", NewsletterUnsubscribeSuccessView.as_view(), name="unsubscribe_success"),
    
    # =====================
    # ADMIN SUBSCRIBERS
    # =====================
    path("admin/subscribers/", SubscriberListView.as_view(), name="admin_list"),
    path("admin/subscribers/export/", SubscriberExportView.as_view(), name="admin_export"),
    path("admin/subscribers/import/", SubscriberImportView.as_view(), name="admin_import"),
    path("admin/subscribers/<uuid:subscriber_id>/", SubscriberDetailView.as_view(), name="admin_detail"),
    path("admin/subscribers/<uuid:subscriber_id>/edit/", SubscriberEditView.as_view(), name="admin_edit"),
]
