"""
With these settings, tests run faster.
"""

from decouple import config

from .base import *  # noqa: F403
from .base import TEMPLATES

# ============================================================================
# GENERAL
# ============================================================================
SECRET_KEY = config(
    "DJANGO_SECRET_KEY",
    default="liNsjqDIkgZBr2H2nxhoMEzsZdXuRLBltKU2QyMcTbRWEO465MxziBMComWWxG9C",
)
TEST_RUNNER = "django.test.runner.DiscoverRunner"

# ============================================================================
# PASSWORD VALIDATION
# ============================================================================
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# ============================================================================
# EMAIL
# ============================================================================
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# ============================================================================
# TEMPLATES
# ============================================================================
TEMPLATES[0]["OPTIONS"]["debug"] = True  # type: ignore[index]

# ============================================================================
# MEDIA
# ============================================================================
MEDIA_URL = "http://media.testserver/"
