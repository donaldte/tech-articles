"""
URL configuration for newsletter app.
"""
from django.urls import path

from tech_articles.newsletter import views

app_name = "newsletter"

urlpatterns = [
    # Public newsletter subscription URLs
    path("subscribe/", views.NewsletterSubscribeView.as_view(), name="subscribe"),
    path("subscribe/pending/", views.NewsletterSubscribePendingView.as_view(), name="subscribe_pending"),
    path("confirm/<str:token>/", views.NewsletterConfirmView.as_view(), name="confirm"),
    path("unsubscribe/<str:token>/", views.NewsletterUnsubscribeView.as_view(), name="unsubscribe"),
    path("unsubscribe/success/", views.NewsletterUnsubscribeSuccessView.as_view(), name="unsubscribe_success"),
    
    # Admin dashboard URLs
    path("admin/subscribers/", views.SubscriberListView.as_view(), name="admin_list"),
    path("admin/subscribers/export/", views.SubscriberExportView.as_view(), name="admin_export"),
    path("admin/subscribers/import/", views.SubscriberImportView.as_view(), name="admin_import"),
    path("admin/subscribers/<uuid:subscriber_id>/", views.SubscriberDetailView.as_view(), name="admin_detail"),
    path("admin/subscribers/<uuid:subscriber_id>/edit/", views.SubscriberEditView.as_view(), name="admin_edit"),
]
