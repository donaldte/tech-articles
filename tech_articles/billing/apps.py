from django.apps import AppConfig


class BillingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "tech_articles.billing"

    def ready(self):
        import tech_articles.billing.signals  # noqa: F401
