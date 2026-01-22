from django.db.models import TextChoices


class UserRole(TextChoices):
    USER = "user", "User"
    ADMIN = "admin", "Admin"
    SUPPORT = "support", "Support"


class LanguageChoices(TextChoices):
    FR = "fr", "Français"
    EN = "en", "English"
    ES = "es", "Español"


class DifficultyChoices(TextChoices):
    BEGINNER = "beginner", "Débutant"
    INTERMEDIATE = "intermediate", "Intermédiaire"
    ADVANCED = "advanced", "Avancé"


class ResourceAccessLevel(TextChoices):
    FREE = "free", "Free"
    PREMIUM = "premium", "Premium"
    PURCHASE_REQUIRED = "purchase_required", "Purchase required"


class EmailStatus(TextChoices):
    QUEUED = "queued", "Queued"
    SENT = "sent", "Sent"
    FAILED = "failed", "Failed"


class ScheduleMode(TextChoices):
    DAILY_5AM = "daily_5am", "Daily 5AM"
    EVERY_5_DAYS_5AM = "every_5_days_5am", "Every 5 days 5AM"


class ArticleStatus(TextChoices):
    DRAFT = "draft", "Brouillon"
    PUBLISHED = "published", "Publié"
    ARCHIVED = "archived", "Archivé"


class ArticleAccessType(TextChoices):
    FREE = "free", "Gratuit"
    PAID = "paid", "Payant"


class PaymentProvider(TextChoices):
    STRIPE = "stripe", "Stripe"
    PAYPAL = "paypal", "PayPal"


class PaymentStatus(TextChoices):
    PENDING = "pending", "Pending"
    SUCCEEDED = "succeeded", "Succeeded"
    FAILED = "failed", "Failed"
    REFUNDED = "refunded", "Refunded"


class PlanInterval(TextChoices):
    MONTH = "month", "Monthly"
    YEAR = "year", "Yearly"


class CouponType(TextChoices):
    PERCENT = "percent", "Percent"
    AMOUNT = "amount", "Amount"


class AppointmentStatus(TextChoices):
    PENDING = "pending", "Pending"
    CONFIRMED = "confirmed", "Confirmed"
    CANCELLED = "cancelled", "Cancelled"
    COMPLETED = "completed", "Completed"
    NO_SHOW = "no_show", "No show"


class WeekdayChoices(TextChoices):
    MON = "mon", "Monday"
    TUE = "tue", "Tuesday"
    WED = "wed", "Wednesday"
    THU = "thu", "Thursday"
    FRI = "fri", "Friday"
    SAT = "sat", "Saturday"
    SUN = "sun", "Sunday"


class EventType(TextChoices):
    PAGE_VIEW = "page_view", "Page view"
    ARTICLE_VIEW = "article_view", "Article view"
    ARTICLE_PURCHASE = "article_purchase", "Article purchase"
    SUBSCRIPTION_STARTED = "subscription_started", "Subscription started"
    APPOINTMENT_BOOKED = "appointment_booked", "Appointment booked"
