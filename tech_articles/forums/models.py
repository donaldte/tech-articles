from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from tech_articles.common.models import UUIDModel, TimeStampedModel, SoftDeleteModel
from tech_articles.utils.enums import CurrencyChoices, PaymentProvider, PaymentStatus


# ============================================================================
# ENUMS
# ============================================================================


class ForumAccessStatus(models.TextChoices):
    """Membership validation status for a forum group."""

    PENDING = "pending", _("Pending")
    APPROVED = "approved", _("Approved")
    REJECTED = "rejected", _("Rejected")


class ForumGroupAccessType(models.TextChoices):
    """How the user gained access to the group."""

    SUBSCRIPTION = "subscription", _("Subscription")
    PURCHASE = "purchase", _("One-time purchase")


# ============================================================================
# FORUM CATEGORY (GROUP)
# ============================================================================


class ForumCategory(UUIDModel, TimeStampedModel):
    """
    A forum category (group) that users can join and discuss topics.

    Access can be gained via an active premium subscription or a one-time
    group purchase. Each category can display an SVG illustration stored
    as raw markup so that colours and sizing can be controlled via CSS /
    template variables at runtime.
    """

    name = models.CharField(
        _("name"),
        max_length=150,
        unique=True,
        help_text=_("Category name"),
    )
    slug = models.SlugField(
        _("slug"),
        max_length=170,
        unique=True,
        db_index=True,
        help_text=_("URL-friendly identifier (auto-generated)"),
    )
    description = models.TextField(
        _("description"),
        blank=True,
        default="",
        help_text=_("Short description of the category"),
    )

    # ------------------------------------------------------------------
    # SVG illustration
    # ------------------------------------------------------------------
    # We store the raw SVG markup rather than a file path so that:
    #   * colours and stroke widths can be overridden by CSS custom
    #     properties (e.g. `fill: var(--icon-color)`).
    #   * templates can inject the markup inline and control `width` /
    #     `height` directly.
    #   * dark-mode / light-mode switching works without extra assets.
    # See FORUMS_SVG_GUIDE.md at the project root for usage instructions.
    svg_icon = models.TextField(
        _("SVG icon"),
        blank=True,
        default="",
        help_text=_(
            "Raw SVG markup for the category icon. "
            "Use `currentColor` for fills/strokes so the icon inherits "
            "the surrounding text colour and adapts to dark/light mode."
        ),
    )

    # ------------------------------------------------------------------
    # Access / pricing
    # ------------------------------------------------------------------
    is_active = models.BooleanField(
        _("is active"),
        default=True,
        db_index=True,
        help_text=_("Whether the category is publicly visible"),
    )
    requires_subscription = models.BooleanField(
        _("requires subscription"),
        default=True,
        help_text=_(
            "If True, an active premium subscription grants access "
            "(subject to admin approval)."
        ),
    )
    is_purchasable = models.BooleanField(
        _("is purchasable"),
        default=False,
        help_text=_("Allow users to buy permanent access to this group."),
    )
    purchase_price = models.DecimalField(
        _("purchase price"),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text=_("One-time price to unlock this group (if purchasable)."),
    )
    purchase_currency = models.CharField(
        _("purchase currency"),
        max_length=3,
        choices=CurrencyChoices.choices,
        default=CurrencyChoices.USD,
        help_text=_("Currency for the one-time purchase price."),
    )
    display_order = models.PositiveIntegerField(
        _("display order"),
        default=0,
        help_text=_("Lower numbers appear first."),
    )

    class Meta:
        verbose_name = _("forum category")
        verbose_name_plural = _("forum categories")
        ordering = ["display_order", "name"]

    def __str__(self) -> str:
        return self.name


# ============================================================================
# FORUM THREAD
# ============================================================================


class ForumThread(UUIDModel, TimeStampedModel, SoftDeleteModel):
    """A discussion thread inside a forum category."""

    category = models.ForeignKey(
        ForumCategory,
        verbose_name=_("category"),
        on_delete=models.CASCADE,
        related_name="threads",
        help_text=_("Category this thread belongs to"),
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("author"),
        on_delete=models.CASCADE,
        related_name="forum_threads",
        help_text=_("User who created the thread"),
    )
    title = models.CharField(
        _("title"),
        max_length=255,
        help_text=_("Thread title"),
    )
    content = models.TextField(
        _("content"),
        help_text=_("Thread body (supports Markdown)"),
    )
    is_pinned = models.BooleanField(
        _("is pinned"),
        default=False,
        db_index=True,
        help_text=_("Pinned threads appear at the top of the category."),
    )
    is_closed = models.BooleanField(
        _("is closed"),
        default=False,
        help_text=_("Closed threads cannot receive new replies."),
    )
    views_count = models.PositiveIntegerField(
        _("views count"),
        default=0,
        help_text=_("Number of times this thread has been viewed"),
    )

    class Meta:
        verbose_name = _("forum thread")
        verbose_name_plural = _("forum threads")
        ordering = ["-is_pinned", "-created_at"]
        indexes = [
            models.Index(fields=["category", "deleted_at"]),
        ]

    def __str__(self) -> str:
        return self.title


# ============================================================================
# THREAD ATTACHMENT
# ============================================================================


class ThreadAttachment(UUIDModel, TimeStampedModel):
    """File attachment linked to a forum thread or a reply."""

    thread = models.ForeignKey(
        ForumThread,
        verbose_name=_("thread"),
        on_delete=models.CASCADE,
        related_name="attachments",
        null=True,
        blank=True,
        help_text=_("Parent thread (leave blank if attached to a reply)"),
    )
    reply = models.ForeignKey(
        "ThreadReply",
        verbose_name=_("reply"),
        on_delete=models.CASCADE,
        related_name="attachments",
        null=True,
        blank=True,
        help_text=_("Parent reply (leave blank if attached to a thread)"),
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("uploaded by"),
        on_delete=models.CASCADE,
        related_name="forum_attachments",
        help_text=_("User who uploaded the file"),
    )
    file = models.FileField(
        _("file"),
        upload_to="forums/attachments/%Y/%m/",
        help_text=_("Attached document or image"),
    )
    original_filename = models.CharField(
        _("original filename"),
        max_length=255,
        blank=True,
        default="",
        help_text=_("Original name of the uploaded file"),
    )

    class Meta:
        verbose_name = _("thread attachment")
        verbose_name_plural = _("thread attachments")
        ordering = ["created_at"]

    def __str__(self) -> str:
        return self.original_filename or str(self.file)


# ============================================================================
# THREAD REPLY
# ============================================================================


class ThreadReply(UUIDModel, TimeStampedModel, SoftDeleteModel):
    """A reply to a forum thread."""

    thread = models.ForeignKey(
        ForumThread,
        verbose_name=_("thread"),
        on_delete=models.CASCADE,
        related_name="replies",
        help_text=_("Thread this reply belongs to"),
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("author"),
        on_delete=models.CASCADE,
        related_name="forum_replies",
        help_text=_("User who wrote the reply"),
    )
    content = models.TextField(
        _("content"),
        help_text=_("Reply body (supports Markdown)"),
    )
    is_best_answer = models.BooleanField(
        _("is best answer"),
        default=False,
        db_index=True,
        help_text=_(
            "Marked by the thread author or an admin as the best answer. "
            "Best answers are displayed at the top."
        ),
    )
    votes_count = models.IntegerField(
        _("votes count"),
        default=0,
        db_index=True,
        help_text=_("Cached sum of up-votes minus down-votes"),
    )

    class Meta:
        verbose_name = _("thread reply")
        verbose_name_plural = _("thread replies")
        ordering = ["-is_best_answer", "-votes_count", "created_at"]
        indexes = [
            models.Index(fields=["thread", "deleted_at"]),
        ]

    def __str__(self) -> str:
        return f"Reply by {self.author_id} on {self.thread_id}"


# ============================================================================
# THREAD VOTE
# ============================================================================


class ThreadVote(UUIDModel, TimeStampedModel):
    """
    A vote cast by a user on a thread reply.

    Each user can vote at most once per reply (unique_together constraint).
    votes_count on ThreadReply is updated via a signal or view logic.
    """

    UPVOTE = 1
    DOWNVOTE = -1
    VOTE_CHOICES = [
        (UPVOTE, _("Up-vote")),
        (DOWNVOTE, _("Down-vote")),
    ]

    reply = models.ForeignKey(
        ThreadReply,
        verbose_name=_("reply"),
        on_delete=models.CASCADE,
        related_name="votes",
        help_text=_("Reply being voted on"),
    )
    voter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("voter"),
        on_delete=models.CASCADE,
        related_name="forum_votes",
        help_text=_("User who cast the vote"),
    )
    value = models.SmallIntegerField(
        _("value"),
        choices=VOTE_CHOICES,
        help_text=_("1 = up-vote, -1 = down-vote"),
    )

    class Meta:
        verbose_name = _("thread vote")
        verbose_name_plural = _("thread votes")
        unique_together = [("reply", "voter")]

    def __str__(self) -> str:
        label = "up" if self.value == self.UPVOTE else "down"
        return f"{label} by {self.voter_id} on reply {self.reply_id}"


# ============================================================================
# FORUM GROUP ACCESS (ONE-TIME PURCHASE)
# ============================================================================


class ForumGroupAccess(UUIDModel, TimeStampedModel):
    """
    Permanent access to a specific forum category granted via a one-time
    purchase (Option B in the access model).

    Access rule:
        user can participate  <->  subscription.is_active
                                   OR  ForumGroupAccess(user, category, approved)

    This model only covers the purchase path. Subscription-based access is
    checked at view/permission level against the billing.Subscription model.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("user"),
        on_delete=models.CASCADE,
        related_name="forum_group_accesses",
        help_text=_("User who purchased the group"),
    )
    category = models.ForeignKey(
        ForumCategory,
        verbose_name=_("category"),
        on_delete=models.CASCADE,
        related_name="group_accesses",
        help_text=_("Forum category purchased"),
    )
    status = models.CharField(
        _("status"),
        max_length=20,
        choices=ForumAccessStatus.choices,
        default=ForumAccessStatus.PENDING,
        db_index=True,
        help_text=_(
            "Admin must approve before granting access "
            "(can be set to auto-approve via settings)."
        ),
    )
    access_type = models.CharField(
        _("access type"),
        max_length=20,
        choices=ForumGroupAccessType.choices,
        default=ForumGroupAccessType.PURCHASE,
        help_text=_("How the user obtained access."),
    )

    # Payment information (filled when access_type == PURCHASE)
    provider = models.CharField(
        _("payment provider"),
        max_length=20,
        choices=PaymentProvider.choices,
        blank=True,
        default="",
        help_text=_("Payment provider used for the purchase"),
    )
    payment_status = models.CharField(
        _("payment status"),
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        db_index=True,
        help_text=_("Status of the payment transaction"),
    )
    amount_paid = models.DecimalField(
        _("amount paid"),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text=_("Amount paid for this access"),
    )
    currency = models.CharField(
        _("currency"),
        max_length=3,
        choices=CurrencyChoices.choices,
        default=CurrencyChoices.USD,
        help_text=_("Currency of the payment"),
    )
    provider_payment_id = models.CharField(
        _("provider payment ID"),
        max_length=160,
        blank=True,
        default="",
        help_text=_("Stripe PaymentIntent ID, Flutterwave transaction ID, etc."),
    )
    approved_at = models.DateTimeField(
        _("approved at"),
        null=True,
        blank=True,
        help_text=_("Timestamp when an admin approved the access request"),
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("approved by"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="forum_approvals",
        help_text=_("Admin who approved the access"),
    )

    class Meta:
        verbose_name = _("forum group access")
        verbose_name_plural = _("forum group accesses")
        unique_together = [("user", "category")]
        indexes = [
            models.Index(fields=["user", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.user_id} -> {self.category} ({self.status})"

    @property
    def is_approved(self) -> bool:
        return self.status == ForumAccessStatus.APPROVED
