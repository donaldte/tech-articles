from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from tech_articles.common.models import UUIDModel, TimeStampedModel, SoftDeleteModel
from tech_articles.utils.enums import (
    CurrencyChoices,
    ForumAccessStatus,
    ForumFeedbackValue,
    ForumGroupAccessType,
    ForumVoteValue,
    PaymentProvider,
    PaymentStatus,
)


# ============================================================================
# FORUM CATEGORY (GROUP)
# ============================================================================


class ForumCategory(UUIDModel, TimeStampedModel):
    """
    A forum category (group) that users can join and discuss topics.

    Access model (three tiers):
    ─────────────────────────────────────────────────────────────────
    Free plan:
        • Can see the public category list.
        • Cannot view thread content, create threads, reply, or vote.

    Premium subscription (Option A):
        • Subscriber requests access to a specific group.
        • Admin validates the request (ForumGroupAccess status → APPROVED).
        • Access is valid only while the subscription remains active.
        • If the subscription expires the user loses participation rights
          but keeps any groups they purchased individually.

    One-time group purchase (Option B):
        • User pays once for a specific group.
        • Access is permanent (not tied to a subscription).
        • Admin validation can be required or skipped
          (see ``requires_admin_approval``).
    ─────────────────────────────────────────────────────────────────
    Dynamic access check:
        can_participate = (
            ForumGroupAccess(SUBSCRIPTION, APPROVED) AND subscription.is_active
        ) OR (
            ForumGroupAccess(PURCHASE, APPROVED, payment SUCCEEDED)
        )

    Use ``category.has_access(user)`` in views / templates.

    Each category can display an SVG illustration stored as raw markup
    so that colours and sizing are controlled via CSS at runtime.
    See FORUMS_SVG_GUIDE.md at the project root.
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
    requires_admin_approval = models.BooleanField(
        _("requires admin approval"),
        default=True,
        help_text=_(
            "If True, an admin must manually approve every access request "
            "(both subscription-based and purchase-based) before the user "
            "can participate. If False, a completed payment or valid "
            "subscription immediately grants access."
        ),
    )

    class Meta:
        verbose_name = _("forum category")
        verbose_name_plural = _("forum categories")
        ordering = ["display_order", "name"]

    def __str__(self) -> str:
        return self.name

    # ------------------------------------------------------------------
    # Access helpers (called from views, templates, and API endpoints)
    # ------------------------------------------------------------------

    def has_access(self, user) -> bool:
        """
        Return True if *user* is allowed to participate in this category
        (read threads, create threads, reply, vote, upload documents).

        Two independent paths can grant access:

        Path 1 — Subscription-based (temporary):
            • A ForumGroupAccess record exists with access_type=SUBSCRIPTION
              and status=APPROVED for this user+category.
            • AND the user currently has at least one active billing
              Subscription.  If the subscription expires this path returns
              False even if the ForumGroupAccess record remains.

        Path 2 — One-time purchase (permanent):
            • A ForumGroupAccess record exists with access_type=PURCHASE,
              status=APPROVED, and payment_status=SUCCEEDED.
            • This path is not tied to a subscription and never expires.
        """
        if not user or not getattr(user, "is_authenticated", False):
            return False

        # Path 2 — permanent purchase access
        purchase_approved = self.group_accesses.filter(
            user=user,
            access_type=ForumGroupAccessType.PURCHASE,
            status=ForumAccessStatus.APPROVED,
            payment_status=PaymentStatus.SUCCEEDED,
        ).exists()
        if purchase_approved:
            return True

        # Path 1 — subscription-based access (requires active subscription)
        subscription_approved = self.group_accesses.filter(
            user=user,
            access_type=ForumGroupAccessType.SUBSCRIPTION,
            status=ForumAccessStatus.APPROVED,
        ).exists()
        if subscription_approved:
            from tech_articles.billing.models import Subscription  # noqa: PLC0415
            return Subscription.objects.filter(
                user=user,
                status=PaymentStatus.SUCCEEDED,
                current_period_end__gt=timezone.now(),
            ).exists()

        return False

    def can_request_subscription_access(self, user) -> bool:
        """
        Return True if *user* can submit a subscription-based access request
        for this category (i.e. they have an active subscription but have
        not yet made a request).

        A user who already has a pending, approved, or rejected request
        cannot submit another one.
        """
        if not user or not getattr(user, "is_authenticated", False):
            return False
        if not self.requires_subscription:
            return False
        already_requested = self.group_accesses.filter(user=user).exists()
        if already_requested:
            return False
        from tech_articles.billing.models import Subscription  # noqa: PLC0415
        return Subscription.objects.filter(
            user=user,
            status=PaymentStatus.SUCCEEDED,
            current_period_end__gt=timezone.now(),
        ).exists()


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
    votes_count = models.IntegerField(
        _("votes count"),
        default=0,
        db_index=True,
        help_text=_(
            "Cached sum of up-votes minus down-votes cast directly on this "
            "thread (the opening question).  Updated atomically by ForumVote."
        ),
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
    """
    A reply posted inside a forum thread, or a comment on another reply.

    Hierarchy (max 2 levels)
    ──────────────────────────────────────────────────────────────────
    Level 0 — ForumThread   (the original question / post)
    Level 1 — ThreadReply   (parent=None)  — answers / top-level replies
    Level 2 — ThreadReply   (parent=<level-1 pk>) — comments on an answer

    Only level-1 replies are voteable, can be marked as best answer, and
    can receive "helpful?" feedback.  Level-2 replies (comments) are
    lightweight annotations; they inherit the thread FK for efficient
    filtering but their parent FK always points to a level-1 reply.

    The view layer is responsible for not rendering a reply form on a
    level-2 reply (i.e. no infinite nesting).
    """

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
    parent = models.ForeignKey(
        "self",
        verbose_name=_("parent reply"),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="comments",
        help_text=_(
            "Set this to turn the reply into a comment on another reply "
            "(level 2). Leave blank for a top-level answer (level 1)."
        ),
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
# FORUM VOTE  (threads AND replies)
# ============================================================================


class ForumVote(UUIDModel, TimeStampedModel):
    """
    A vote cast by a user on a forum thread or on a top-level thread reply.

    Design rationale — why vote on threads *and* replies?
    ──────────────────────────────────────────────────────
    On Q&A platforms (Stack Overflow, Discourse, Reddit), both the opening
    question *and* the answers (replies) can be voted independently:

    • Voting on the *thread* (question) signals whether the question itself
      is well-posed, useful, and worth preserving in the knowledge-base.
      A heavily up-voted question surfaces naturally in search results and
      the category feed.

    • Voting on a *reply* (answer) signals quality.  The reply with the
      highest score floats to the top below the accepted answer; community
      consensus shapes the order without admin intervention.

    Both vote types share the same ±1 semantic (ForumVoteValue) and the same
    toggle/direction-switch behaviour in the AJAX endpoint.

    Constraints
    ──────────────────────────────────────────────────────
    Exactly one of `thread` or `reply` must be set — enforced by a
    CheckConstraint.  Per-user uniqueness is enforced by two conditional
    UniqueConstraints (one for thread votes, one for reply votes).

    The cached `votes_count` field on ForumThread / ThreadReply is updated
    atomically by the vote AJAX view (ForumVoteView).
    """

    thread = models.ForeignKey(
        ForumThread,
        verbose_name=_("thread"),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="votes",
        help_text=_("Thread being voted on (set this OR reply, not both)"),
    )
    reply = models.ForeignKey(
        ThreadReply,
        verbose_name=_("reply"),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="votes",
        help_text=_("Reply being voted on (set this OR thread, not both)"),
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
        choices=ForumVoteValue.choices,
        help_text=_("1 = up-vote, -1 = down-vote"),
    )

    class Meta:
        verbose_name = _("forum vote")
        verbose_name_plural = _("forum votes")
        constraints = [
            # Exactly one of thread / reply must be set
            models.CheckConstraint(
                check=(
                    models.Q(thread__isnull=False, reply__isnull=True)
                    | models.Q(thread__isnull=True, reply__isnull=False)
                ),
                name="forums_vote_exactly_one_target",
            ),
            # One vote per user per thread
            models.UniqueConstraint(
                fields=["thread", "voter"],
                condition=models.Q(thread__isnull=False),
                name="forums_unique_thread_vote",
            ),
            # One vote per user per reply
            models.UniqueConstraint(
                fields=["reply", "voter"],
                condition=models.Q(reply__isnull=False),
                name="forums_unique_reply_vote",
            ),
        ]

    def __str__(self) -> str:
        label = "up" if self.value == ForumVoteValue.UPVOTE else "down"
        if self.thread_id:
            target = f"thread {self.thread_id}"
        elif self.reply_id:
            target = f"reply {self.reply_id}"
        else:
            target = "unset target"
        return f"{label} by {self.voter_id} on {target}"





# ============================================================================
# THREAD REPLY FEEDBACK  (helpful / not helpful on best answers)
# ============================================================================


class ThreadReplyFeedback(UUIDModel, TimeStampedModel):
    """
    Qualitative feedback on a reply that has been marked as the best answer.

    Inspired by GitHub's "Was this helpful? 👍 👎" widget displayed below
    the accepted answer.  Unlike votes (which affect ranking), feedback is
    purely informational and is never displayed as a public score — it is
    visible only to the thread author and staff.

    Only one feedback record per user per reply is allowed (unique_together).
    The view layer should restrict the form to replies where is_best_answer=True,
    but the model itself does not enforce this so that the constraint can be
    relaxed in the future without a migration.
    """

    reply = models.ForeignKey(
        ThreadReply,
        verbose_name=_("reply"),
        on_delete=models.CASCADE,
        related_name="feedbacks",
        help_text=_("The reply (best answer) being evaluated"),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("user"),
        on_delete=models.CASCADE,
        related_name="forum_reply_feedbacks",
        help_text=_("User who submitted the feedback"),
    )
    value = models.CharField(
        _("value"),
        max_length=20,
        choices=ForumFeedbackValue.choices,
        help_text=_("Was this answer helpful?"),
    )
    comment = models.TextField(
        _("comment"),
        blank=True,
        default="",
        help_text=_(
            "Optional short comment explaining the feedback "
            "(e.g. 'Missing code example'). Not shown publicly."
        ),
    )

    class Meta:
        verbose_name = _("thread reply feedback")
        verbose_name_plural = _("thread reply feedbacks")
        unique_together = [("reply", "user")]

    def __str__(self) -> str:
        return f"{self.value} by {self.user_id} on reply {self.reply_id}"


# ============================================================================
# FORUM GROUP ACCESS
# ============================================================================


class ForumGroupAccess(UUIDModel, TimeStampedModel):
    """
    Tracks a user's access request (and its outcome) for a specific
    forum category.

    Both access paths — subscription-based and one-time purchase — go
    through this model so that admin approval is centralised.

    Workflow
    ────────
    Subscription path (access_type = SUBSCRIPTION):
        1. User with active subscription clicks "Request access" on a group.
        2. ForumGroupAccess is created with status=PENDING.
        3. Admin reviews the request and sets status=APPROVED or REJECTED.
        4. If approved, user can participate as long as the subscription
           remains active.  If the subscription expires the user loses
           participation rights but this record is kept.
        5. If the subscription is renewed, access is automatically restored
           (the APPROVED record still exists).

    Purchase path (access_type = PURCHASE):
        1. User pays for permanent access to the group.
        2. ForumGroupAccess is created with status=PENDING,
           payment_status=PENDING.
        3. After successful payment confirmation (webhook), payment_status
           is updated to SUCCEEDED.
        4. If requires_admin_approval is True on the category, an admin
           must set status=APPROVED. Otherwise access is granted immediately
           (auto-approve flow sets status=APPROVED on payment confirmation).
        5. Approved purchase access is permanent and independent of any
           subscription.

    Access check:
        ``ForumCategory.has_access(user)`` encodes the full logic.
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
    rejection_reason = models.TextField(
        _("rejection reason"),
        blank=True,
        default="",
        help_text=_(
            "Optional explanation provided by the admin when rejecting "
            "an access request. Displayed to the user."
        ),
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
