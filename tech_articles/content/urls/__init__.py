"""
Content URLs module.
Main URL configuration for content management (categories, tags, articles).
Accessible at /content/ (after i18n prefix)
"""

from .categories_urls import urlpatterns as categories_urls
from .tags_urls import urlpatterns as tags_urls
from .article_urls import urlpatterns as article_urls

app_name = "content"

urlpatterns = categories_urls + tags_urls + article_urls
