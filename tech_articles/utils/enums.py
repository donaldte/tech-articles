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

