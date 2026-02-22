from contextlib import suppress

from django.apps import AppConfig


class ContentConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "tech_articles.content"

    def ready(self):
        # Import signal handlers to ensure they are registered
        # Use contextlib.suppress to avoid noisy exceptions during migrations/tests
        with suppress(Exception, ImportError):
            from . import signals  # noqa: F401
