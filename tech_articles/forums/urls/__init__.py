"""
Forums URLs module.
Main URL configuration for the forums application.
Accessible at /forums/ (after i18n prefix).
"""
from .category_urls import urlpatterns as category_urls
from .thread_urls import urlpatterns as thread_urls
from .access_urls import urlpatterns as access_urls

app_name = "forums"

urlpatterns = (
    category_urls
    + thread_urls
    + access_urls
)
