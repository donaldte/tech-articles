"""
Management command to load subscription plans and features from JSON data.
"""
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from tech_articles.billing.models import Plan, PlanFeature
from tech_articles.utils.enums import PaymentProvider, PlanInterval, CurrencyChoices


class Command(BaseCommand):
    """Command to create subscription plans and their features."""

    help = _("Load subscription plans and features from JSON data")

    # Plan data (extracted from billing_plan.json)
    PLANS_DATA = [
        {
            "name": "Free",
            "slug": "free",
            "is_active": True,
            "price": Decimal("0.00"),
            "currency": CurrencyChoices.USD,
            "interval": PlanInterval.MONTH,
            "description": "To discover the platform and the content style",
            "display_order": 0,
            "is_popular": False,
            "max_articles": None,
            "max_resources": None,
            "max_appointments": None,
            "trial_period_days": None,
            "pricing_discount": 0,
            "provider": PaymentProvider.STRIPE,
            "provider_price_id": "",
        },
        {
            "name": "Monthly",
            "slug": "monthly",
            "is_active": True,
            "price": Decimal("10.00"),
            "currency": CurrencyChoices.USD,
            "interval": PlanInterval.MONTH,
            "description": "To learn regularly and access premium content",
            "display_order": 1,
            "is_popular": True,
            "max_articles": None,
            "max_resources": None,
            "max_appointments": None,
            "trial_period_days": None,
            "pricing_discount": 0,
            "provider": PaymentProvider.STRIPE,
            "provider_price_id": "",
        },
        {
            "name": "Annual",
            "slug": "annual",
            "is_active": True,
            "price": Decimal("96.00"),
            "currency": CurrencyChoices.USD,
            "interval": PlanInterval.YEAR,
            "description": "Best value – for committed developers",
            "display_order": 2,
            "is_popular": False,
            "max_articles": None,
            "max_resources": None,
            "max_appointments": None,
            "trial_period_days": None,
            "pricing_discount": 20,
            "provider": PaymentProvider.STRIPE,
            "provider_price_id": "",
        },
    ]

    # Features data (extracted from billing_planfeature.json)
    FEATURES_DATA = {
        "free": [
            {
                "name": "Access to free articles",
                "description": "",
                "is_included": True,
                "display_order": 0,
            },
            {
                "name": "Preview of premium articles",
                "description": "",
                "is_included": True,
                "display_order": 1,
            },
            {
                "name": "Newsletter subscription",
                "description": "",
                "is_included": True,
                "display_order": 2,
            },
            {
                "name": "Account creation",
                "description": "",
                "is_included": True,
                "display_order": 3,
            },
            {
                "name": "Limited access to premium content",
                "description": "",
                "is_included": False,
                "display_order": 4,
            },
            {
                "name": "No downloadable resources",
                "description": "",
                "is_included": False,
                "display_order": 5,
            },
            {
                "name": "No appointments",
                "description": "",
                "is_included": False,
                "display_order": 6,
            },
        ],
        "monthly": [
            {
                "name": "Access to all premium articles",
                "description": "",
                "is_included": True,
                "display_order": 0,
            },
            {
                "name": "Integrated premium resources (secure viewer)",
                "description": "",
                "is_included": True,
                "display_order": 1,
            },
            {
                "name": "Multi-page reading with automatic resume",
                "description": "",
                "is_included": True,
                "display_order": 2,
            },
            {
                "name": "Access to article updates",
                "description": "",
                "is_included": True,
                "display_order": 3,
            },
            {
                "name": "Priority support",
                "description": "",
                "is_included": True,
                "display_order": 4,
            },
            {
                "name": "Regular updates",
                "description": "",
                "is_included": True,
                "display_order": 5,
            },
        ],
        "annual": [
            {
                "name": "Everything in Monthly plan",
                "description": "",
                "is_included": True,
                "display_order": 0,
            },
            {
                "name": "Early access to new content",
                "description": "",
                "is_included": True,
                "display_order": 1,
            },
            {
                "name": "Advanced premium resources",
                "description": "",
                "is_included": True,
                "display_order": 2,
            },
            {
                "name": "Priority on updates",
                "description": "",
                "is_included": True,
                "display_order": 3,
            },
            {
                "name": "Preferential access to appointments",
                "description": "",
                "is_included": True,
                "display_order": 4,
            },
        ],
    }

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear all existing plans and features before loading",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        """Execute the command."""
        clear = options.get("clear", False)

        if clear:
            self.clear_existing_data()

        self.load_plans()
        self.stdout.write(
            self.style.SUCCESS("✓ Subscription plans loaded successfully!")
        )

    def clear_existing_data(self):
        """Clear all existing plans and features."""
        self.stdout.write("Clearing existing plans and features...")

        # First delete related Subscription objects (they have PROTECT FK)
        from tech_articles.billing.models import Subscription
        deleted_subscriptions, _ = Subscription.objects.all().delete()
        self.stdout.write(f"  ✓ Deleted {deleted_subscriptions} subscriptions")

        # Then delete features and plans
        deleted_features, _ = PlanFeature.objects.all().delete()
        self.stdout.write(f"  ✓ Deleted {deleted_features} plan features")

        deleted_plans, _ = Plan.objects.all().delete()
        self.stdout.write(f"  ✓ Deleted {deleted_plans} plans")

        self.stdout.write(self.style.SUCCESS("✓ Existing data cleared"))

    def load_plans(self):
        """Load all plans and their features."""
        for plan_data in self.PLANS_DATA:
            slug = plan_data["slug"]
            self.stdout.write(f"Creating plan: {plan_data['name']}...", ending=" ")

            plan, created = Plan.objects.update_or_create(
                slug=slug,
                defaults={
                    "name": plan_data["name"],
                    "is_active": plan_data["is_active"],
                    "price": plan_data["price"],
                    "currency": plan_data["currency"],
                    "interval": plan_data["interval"],
                    "description": plan_data["description"],
                    "display_order": plan_data["display_order"],
                    "is_popular": plan_data["is_popular"],
                    "max_articles": plan_data["max_articles"],
                    "max_resources": plan_data["max_resources"],
                    "max_appointments": plan_data["max_appointments"],
                    "trial_period_days": plan_data["trial_period_days"],
                    "pricing_discount": plan_data["pricing_discount"],
                    "provider": plan_data["provider"],
                    "provider_price_id": plan_data["provider_price_id"],
                },
            )

            if created:
                self.stdout.write(self.style.SUCCESS("Created"))
            else:
                self.stdout.write(self.style.WARNING("Updated"))

            # Load features for this plan
            self.load_plan_features(plan, slug)

    def load_plan_features(self, plan: Plan, plan_slug: str):
        """Load features for a specific plan."""
        features = self.FEATURES_DATA.get(plan_slug, [])

        if not features:
            self.stdout.write(
                self.style.WARNING(f"  ⚠ No features found for plan '{plan_slug}'")
            )
            return

        for feature_data in features:
            feature, created = PlanFeature.objects.update_or_create(
                plan=plan,
                name=feature_data["name"],
                defaults={
                    "description": feature_data.get("description", ""),
                    "is_included": feature_data["is_included"],
                    "display_order": feature_data["display_order"],
                },
            )

            status = "✓" if created else "↻"
            self.stdout.write(
                f"  {status} Feature: {feature_data['name'][:50]}...",
                ending="\n",
            )

        self.stdout.write(
            self.style.SUCCESS(f"  ✓ {len(features)} features loaded for {plan.name}")
        )

