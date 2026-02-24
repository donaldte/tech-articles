"""
Account URLs module for Runbookly.
"""

from .auth_urls import urlpatterns as auth_urls
from .profile_urls import urlpatterns as profile_urls
from .user_urls import urlpatterns as user_urls

app_name = "accounts"

urlpatterns = auth_urls + user_urls + profile_urls
