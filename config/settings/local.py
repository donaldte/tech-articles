from decouple import config

from .base import *  # noqa: F403
from .base import INSTALLED_APPS
from .base import MIDDLEWARE

# ============================================================================
# GENERAL
# ============================================================================
DEBUG = True
SECRET_KEY = config(
    "DJANGO_SECRET_KEY",
    default="LEu9JK5OKBkqlGH2MszOa8Q8BMHqPEpScNnDUnS74DhNbdYScYieCuzoL36ExhI7",
)
ALLOWED_HOSTS = ["localhost", "0.0.0.0", "127.0.0.1"]  # noqa: S104

# ============================================================================
# CACHES
# ============================================================================
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "",
    },
}

# ============================================================================
# EMAIL
# ============================================================================
EMAIL_BACKEND = config(
    "DJANGO_EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend",
)

# ============================================================================
# STATIC FILES
# ============================================================================
INSTALLED_APPS = ["whitenoise.runserver_nostatic", *INSTALLED_APPS]

# ============================================================================
# DEBUG TOOLBAR
# ============================================================================
INSTALLED_APPS += ["debug_toolbar"]
MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]
DEBUG_TOOLBAR_CONFIG = {
    "DISABLE_PANELS": [
        "debug_toolbar.panels.redirects.RedirectsPanel",
        "debug_toolbar.panels.profiling.ProfilingPanel",
    ],
    "SHOW_TEMPLATE_CONTEXT": True,
}
INTERNAL_IPS = ["127.0.0.1", "10.0.2.2"]
if config("USE_DOCKER", default="no") == "yes":
    import socket

    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS += [".".join([*ip.split(".")[:-1], "1"]) for ip in ips]

# ============================================================================
# DJANGO EXTENSIONS
# ============================================================================
INSTALLED_APPS += ["django_extensions"]

# ============================================================================
# CELERY
# ============================================================================
CELERY_TASK_EAGER_PROPAGATES = True

# ============================================================================
# AWS S3 STORAGE
# ============================================================================
AWS_ACCESS_KEY_ID = config("DJANGO_AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = config("DJANGO_AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = config("DJANGO_AWS_STORAGE_BUCKET_NAME")
AWS_QUERYSTRING_AUTH = False
_AWS_EXPIRY = 60 * 60 * 24 * 7
AWS_S3_OBJECT_PARAMETERS = {
    "CacheControl": f"max-age={_AWS_EXPIRY}, s-maxage={_AWS_EXPIRY}, must-revalidate",
}
AWS_S3_MAX_MEMORY_SIZE = config(
    "DJANGO_AWS_S3_MAX_MEMORY_SIZE",
    default=100_000_000,
    cast=int,
)
AWS_S3_REGION_NAME = config("DJANGO_AWS_S3_REGION_NAME", default=None)
AWS_S3_CUSTOM_DOMAIN = config("DJANGO_AWS_S3_CUSTOM_DOMAIN", default=None)
aws_s3_domain = AWS_S3_CUSTOM_DOMAIN or f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"
