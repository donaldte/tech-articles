"""
Content URLs module.
Main URL configuration that includes all feature-specific URL patterns.
"""
from django.urls import path, include

app_name = "content"

urlpatterns = [
    path("categories/", include("tech_articles.content.urls.categories_urls")),
    path("tags/", include("tech_articles.content.urls.tags_urls")),
]
