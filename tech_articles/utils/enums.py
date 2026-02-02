from django.db.models import TextChoices


# ============================================================================
# USER
# ============================================================================
class UserRole(TextChoices):
    """User role enumeration for permission management."""

    USER = "user", "User"
    ADMIN = "admin", "Administrator"
    SUPPORT = "support", "Support Agent"


# ============================================================================
# LANGUAGE
# ============================================================================
class LanguageChoices(TextChoices):
    """Available language choices for users and content."""

    FR = "fr", "Français"
    EN = "en", "English"
    ES = "es", "Español"


# ============================================================================
# DIFFICULTY
# ============================================================================
class DifficultyChoices(TextChoices):
    """Article difficulty levels."""

    BEGINNER = "beginner", "Beginner"
    INTERMEDIATE = "intermediate", "Intermediate"
    ADVANCED = "advanced", "Advanced"


# ============================================================================
# RESOURCE ACCESS
# ============================================================================
class ResourceAccessLevel(TextChoices):
    """Access levels for resources."""

    FREE = "free", "Free"
    PREMIUM = "premium", "Premium"
    PURCHASE_REQUIRED = "purchase_required", "Purchase Required"


# ============================================================================
# EMAIL
# ============================================================================
class EmailStatus(TextChoices):
    """Email delivery status for individual email logs."""

    QUEUED = "queued", "Queued"
    SENT = "sent", "Sent"
    FAILED = "failed", "Failed"
    BOUNCED = "bounced", "Bounced"
    UNSUBSCRIBED = "unsubscribed", "Unsubscribed"


class SubscriberStatus(TextChoices):
    """
    Newsletter subscriber status (overall status of a subscriber).
    Note: Some values overlap with EmailStatus but serve different purposes:
    - EmailStatus tracks individual email delivery events
    - SubscriberStatus tracks the subscriber's overall account status
    """

    ACTIVE = "active", "Active"
    INACTIVE = "inactive", "Inactive"
    BOUNCED = "bounced", "Bounced"
    UNSUBSCRIBED = "unsubscribed", "Unsubscribed"


# ============================================================================
# NEWSLETTER SCHEDULE
# ============================================================================
class ScheduleMode(TextChoices):
    """Newsletter scheduling modes."""

    DAILY_5AM = "daily_5am", "Daily at 5 AM"
    EVERY_5_DAYS_5AM = "every_5_days_5am", "Every 5 days at 5 AM"
    WEEKLY_MONDAY_5AM = "weekly_monday_5am", "Weekly on Monday at 5 AM"
    EVERY_2_WEEKS_5AM = "every_2_weeks_5am", "Every 2 weeks at 5 AM"


# ============================================================================
# ARTICLE
# ============================================================================
class ArticleStatus(TextChoices):
    """Article publication status."""

    DRAFT = "draft", "Draft"
    PUBLISHED = "published", "Published"
    ARCHIVED = "archived", "Archived"
    SCHEDULED = "scheduled", "Scheduled"


class ArticleAccessType(TextChoices):
    """Article access type (free or paid)."""

    FREE = "free", "Free"
    PAID = "paid", "Paid"


# ============================================================================
# PAYMENT
# ============================================================================
class PaymentProvider(TextChoices):
    """Payment service providers."""

    STRIPE = "stripe", "Stripe"
    PAYPAL = "paypal", "PayPal"
    SQUARE = "square", "Square"


class PaymentStatus(TextChoices):
    """Payment transaction status."""

    PENDING = "pending", "Pending"
    PROCESSING = "processing", "Processing"
    SUCCEEDED = "succeeded", "Succeeded"
    FAILED = "failed", "Failed"
    REFUNDED = "refunded", "Refunded"
    CANCELLED = "cancelled", "Cancelled"


# ============================================================================
# SUBSCRIPTION
# ============================================================================
class PlanInterval(TextChoices):
    """Billing intervals for subscription plans."""

    WEEK = "week", "Weekly"
    MONTH = "month", "Monthly"
    YEAR = "year", "Yearly"


class CouponType(TextChoices):
    """Coupon discount types."""

    PERCENT = "percent", "Percentage"
    AMOUNT = "amount", "Fixed Amount"


# ============================================================================
# APPOINTMENT
# ============================================================================
class AppointmentStatus(TextChoices):
    """Appointment status."""

    PENDING = "pending", "Pending"
    CONFIRMED = "confirmed", "Confirmed"
    CANCELLED = "cancelled", "Cancelled"
    COMPLETED = "completed", "Completed"
    NO_SHOW = "no_show", "No Show"
    RESCHEDULED = "rescheduled", "Rescheduled"


class WeekdayChoices(TextChoices):
    """Days of the week."""

    MON = "mon", "Monday"
    TUE = "tue", "Tuesday"
    WED = "wed", "Wednesday"
    THU = "thu", "Thursday"
    FRI = "fri", "Friday"
    SAT = "sat", "Saturday"
    SUN = "sun", "Sunday"


# ============================================================================
# ANALYTICS
# ============================================================================
class EventType(TextChoices):
    """User event types for analytics."""

    PAGE_VIEW = "page_view", "Page View"
    ARTICLE_VIEW = "article_view", "Article View"
    ARTICLE_PURCHASE = "article_purchase", "Article Purchase"
    SUBSCRIPTION_STARTED = "subscription_started", "Subscription Started"
    SUBSCRIPTION_CANCELLED = "subscription_cancelled", "Subscription Cancelled"
    APPOINTMENT_BOOKED = "appointment_booked", "Appointment Booked"
    NEWSLETTER_SUBSCRIBED = "newsletter_subscribed", "Newsletter Subscribed"
    NEWSLETTER_UNSUBSCRIBED = "newsletter_unsubscribed", "Newsletter Unsubscribed"
