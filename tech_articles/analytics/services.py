"""
Analytics services: article reading tracking and session sync.
"""
from __future__ import annotations

import hashlib
import json
import logging
from datetime import timedelta

from django.db.models import Count, Sum as models_Sum
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth
from django.utils import timezone

from tech_articles.analytics.models import Event
from tech_articles.content.models import Article
from tech_articles.utils.enums import EventType

logger = logging.getLogger(__name__)

SESSION_KEY = "read_articles"


def _hash_ip(ip: str) -> str:
    """Return a SHA-256 hash of the IP address for privacy."""
    if not ip:
        return ""
    return hashlib.sha256(ip.encode()).hexdigest()[:64]


def _get_client_ip(request) -> str:
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


def create_event(
    event_type: str,
    user=None,
    metadata: dict | None = None,
    request=None,
) -> Event:
    """
    Create an analytics Event with optional request context.

    Args:
        event_type: One of EventType choices.
        user: The authenticated user, or None for anonymous events.
        metadata: Dictionary of extra data to store as JSON.
        request: Optional HttpRequest for extracting path, referrer, etc.

    Returns:
        The created Event instance.
    """
    kwargs = {
        "event_type": event_type,
        "user": user,
        "metadata_json": json.dumps(metadata or {}),
    }
    if request is not None:
        kwargs["path"] = request.get_full_path()[:512]
        kwargs["referrer"] = request.META.get("HTTP_REFERER", "")[:512]
        kwargs["user_agent"] = request.META.get("HTTP_USER_AGENT", "")[:512]
        kwargs["ip_hash"] = _hash_ip(_get_client_ip(request))

    event = Event.objects.create(**kwargs)
    logger.info("Created event %s (%s) for user %s", event.id, event_type, user)
    return event


class ReadingTracker:
    """Handles article reading tracking for authenticated and anonymous users."""

    # ------------------------------------------------------------------
    # Track a read event
    # ------------------------------------------------------------------

    @staticmethod
    def track(request, article: Article) -> None:
        """
        Track an article read event.

        - Authenticated users: create an Event in DB (deduplicated per user+article+day).
        - Anonymous users: store in session for later sync.
        """
        if request.user.is_authenticated:
            ReadingTracker._track_authenticated(request, article)
        else:
            ReadingTracker._track_anonymous(request, article)

    @staticmethod
    def _track_authenticated(request, article: Article) -> None:
        """Create an Event record, deduplicated per user + article + day."""
        today = timezone.now().date()
        already = Event.objects.filter(
            user=request.user,
            event_type=EventType.ARTICLE_READ,
            metadata_json__contains=str(article.id),
            created_at__date=today,
        ).exists()
        if already:
            return

        Event.objects.create(
            event_type=EventType.ARTICLE_READ,
            user=request.user,
            path=request.get_full_path(),
            referrer=request.META.get("HTTP_REFERER", "")[:512],
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:512],
            ip_hash=_hash_ip(_get_client_ip(request)),
            metadata_json=json.dumps({
                "article_id": str(article.id),
                "article_slug": article.slug,
                "article_title": article.title,
            }),
        )

    @staticmethod
    def _track_anonymous(request, article: Article) -> None:
        """Store article read in session for sync after login."""
        reads: list[dict] = request.session.get(SESSION_KEY, [])

        # Deduplicate: one entry per article per day
        today_str = timezone.now().date().isoformat()
        for entry in reads:
            if entry.get("article_id") == str(article.id) and entry.get("date") == today_str:
                return

        reads.append({
            "article_id": str(article.id),
            "article_slug": article.slug,
            "article_title": article.title,
            "date": today_str,
            "path": request.get_full_path(),
        })
        # Keep only last 50 entries in session
        request.session[SESSION_KEY] = reads[-50:]

    # ------------------------------------------------------------------
    # Sync session reads to DB on login
    # ------------------------------------------------------------------

    @staticmethod
    def sync_session_to_db(request, user) -> int:
        """
        Transfer anonymous reads stored in session to the database.
        Called after successful login. Returns the number of synced events.
        """
        reads: list[dict] = request.session.pop(SESSION_KEY, [])
        if not reads:
            return 0

        synced = 0
        for entry in reads:
            article_id = entry.get("article_id")
            read_date = entry.get("date", "")
            if not article_id:
                continue

            # Deduplicate against existing events
            already = Event.objects.filter(
                user=user,
                event_type=EventType.ARTICLE_READ,
                metadata_json__contains=article_id,
                created_at__date=read_date,
            ).exists()
            if already:
                continue

            Event.objects.create(
                event_type=EventType.ARTICLE_READ,
                user=user,
                path=entry.get("path", ""),
                metadata_json=json.dumps({
                    "article_id": article_id,
                    "article_slug": entry.get("article_slug", ""),
                    "article_title": entry.get("article_title", ""),
                }),
            )
            synced += 1

        logger.info("Synced %d article reads from session for user %s", synced, user.id)
        return synced

    # ------------------------------------------------------------------
    # Reading stats for dashboards
    # ------------------------------------------------------------------

    @staticmethod
    def get_user_read_count(user, *, days: int | None = None) -> int:
        """Return total article reads for a user, optionally within last N days."""
        qs = Event.objects.filter(user=user, event_type=EventType.ARTICLE_READ)
        if days is not None:
            since = timezone.now() - timedelta(days=days)
            qs = qs.filter(created_at__gte=since)
        return qs.count()

    @staticmethod
    def get_user_reads_this_month(user) -> int:
        """Return article reads for the current month."""
        now = timezone.now()
        return Event.objects.filter(
            user=user,
            event_type=EventType.ARTICLE_READ,
            created_at__year=now.year,
            created_at__month=now.month,
        ).count()

    @staticmethod
    def get_user_reads_last_month(user) -> int:
        """Return article reads for the previous month."""
        now = timezone.now()
        first_of_month = now.replace(day=1)
        last_month_end = first_of_month - timedelta(days=1)
        return Event.objects.filter(
            user=user,
            event_type=EventType.ARTICLE_READ,
            created_at__year=last_month_end.year,
            created_at__month=last_month_end.month,
        ).count()

    @staticmethod
    def get_recent_reads(user, limit: int = 5):
        """Return recent article read events with article info."""
        events = (
            Event.objects.filter(user=user, event_type=EventType.ARTICLE_READ)
            .order_by("-created_at")[:limit]
        )
        result = []
        for event in events:
            try:
                meta = json.loads(event.metadata_json) if event.metadata_json else {}
            except (json.JSONDecodeError, TypeError):
                meta = {}
            article_slug = meta.get("article_slug", "")
            article = None
            if article_slug:
                article = Article.objects.filter(slug=article_slug).first()
            result.append({
                "event": event,
                "meta": meta,
                "article": article,
            })
        return result

    @staticmethod
    def get_user_chart_data(user) -> dict:
        """
        Return chart data for user dashboard: reads per day/week/month.

        Returns dict with keys 'week', 'month', 'year',
        each containing {'labels': [...], 'values': [...]}.
        """
        now = timezone.now()
        base_qs = Event.objects.filter(user=user, event_type=EventType.ARTICLE_READ)

        # --- Week data (last 7 days, one bar per day) ---
        week_start = (now - timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)
        week_qs = (
            base_qs.filter(created_at__gte=week_start)
            .annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(count=Count("id"))
            .order_by("day")
        )
        week_map = {row["day"]: row["count"] for row in week_qs}
        week_labels = []
        week_values = []
        for i in range(7):
            d = (week_start + timedelta(days=i)).date()
            week_labels.append(d.isoformat())
            week_values.append(week_map.get(d, 0))

        # --- Month data (4-5 weeks of current month) ---
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_qs = (
            base_qs.filter(created_at__gte=month_start)
            .annotate(week=TruncWeek("created_at"))
            .values("week")
            .annotate(count=Count("id"))
            .order_by("week")
        )
        month_map = {row["week"].date(): row["count"] for row in month_qs}
        # Build 4 or 5 week buckets
        month_labels = []
        month_values = []
        week_cursor = month_start.date()
        week_num = 1
        while week_cursor <= now.date():
            # Find the Monday of this week
            monday = week_cursor - timedelta(days=week_cursor.weekday())
            label = f"W{week_num}"
            month_labels.append(label)
            month_values.append(month_map.get(monday, 0))
            week_cursor += timedelta(days=7)
            week_num += 1

        # --- Year data (12 months) ---
        year_start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        year_qs = (
            base_qs.filter(created_at__gte=year_start)
            .annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(count=Count("id"))
            .order_by("month")
        )
        year_map = {row["month"].month: row["count"] for row in year_qs}
        year_labels = []
        year_values = []
        for m in range(1, 13):
            year_labels.append(str(m))  # month number as string, JS will localize
            year_values.append(year_map.get(m, 0))

        return {
            "week": {"labels": week_labels, "values": week_values},
            "month": {"labels": month_labels, "values": month_values},
            "year": {"labels": year_labels, "values": year_values},
        }

    # ------------------------------------------------------------------
    # Platform-wide stats for admin dashboard
    # ------------------------------------------------------------------

    @staticmethod
    def get_platform_reads_this_month() -> int:
        now = timezone.now()
        return Event.objects.filter(
            event_type=EventType.ARTICLE_READ,
            created_at__year=now.year,
            created_at__month=now.month,
        ).count()

    @staticmethod
    def get_platform_chart_data() -> dict:
        """
        Return revenue/activity chart data for admin dashboard.
        Returns dict with keys 'week', 'month', 'year'.
        """
        from tech_articles.billing.models import PaymentTransaction
        from tech_articles.utils.enums import PaymentStatus as PS

        now = timezone.now()
        base_qs = PaymentTransaction.objects.filter(status=PS.SUCCEEDED)

        # --- Week data (last 7 days) ---
        week_start = (now - timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)
        week_qs = (
            base_qs.filter(created_at__gte=week_start)
            .annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(total=Count("id"), revenue=models_Sum("amount"))
            .order_by("day")
        )
        week_map = {row["day"]: float(row["revenue"] or 0) for row in week_qs}
        week_labels = []
        week_values = []
        for i in range(7):
            d = (week_start + timedelta(days=i)).date()
            week_labels.append(d.isoformat())
            week_values.append(week_map.get(d, 0))

        # --- Month data (weeks of current month) ---
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_qs = (
            base_qs.filter(created_at__gte=month_start)
            .annotate(week=TruncWeek("created_at"))
            .values("week")
            .annotate(revenue=models_Sum("amount"))
            .order_by("week")
        )
        month_map = {row["week"].date(): float(row["revenue"] or 0) for row in month_qs}
        month_labels = []
        month_values = []
        week_cursor = month_start.date()
        week_num = 1
        while week_cursor <= now.date():
            monday = week_cursor - timedelta(days=week_cursor.weekday())
            month_labels.append(f"W{week_num}")
            month_values.append(month_map.get(monday, 0))
            week_cursor += timedelta(days=7)
            week_num += 1

        # --- Year data (12 months) ---
        year_start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        year_qs = (
            base_qs.filter(created_at__gte=year_start)
            .annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(revenue=models_Sum("amount"))
            .order_by("month")
        )
        year_map = {row["month"].month: float(row["revenue"] or 0) for row in year_qs}
        year_labels = []
        year_values = []
        for m in range(1, 13):
            year_labels.append(str(m))
            year_values.append(year_map.get(m, 0))

        return {
            "week": {"labels": week_labels, "values": week_values},
            "month": {"labels": month_labels, "values": month_values},
            "year": {"labels": year_labels, "values": year_values},
        }

    @staticmethod
    def get_recent_platform_activity(limit: int = 10) -> list[dict]:
        """Return recent platform-wide events for admin dashboard."""
        events = Event.objects.select_related("user").order_by("-created_at")[:limit]
        result = []
        for event in events:
            try:
                meta = json.loads(event.metadata_json) if event.metadata_json else {}
            except (json.JSONDecodeError, TypeError):
                meta = {}
            result.append({
                "event": event,
                "meta": meta,
                "user_name": event.user.get_full_name() if event.user else "Anonymous",
            })
        return result


# ======================================================================
# Analytics KPI helpers (admin dashboard)
# ======================================================================


class AnalyticsKPI:
    """Compute KPIs and chart data for the admin analytics overview."""

    @staticmethod
    def get_total_events(days: int | None = None) -> int:
        qs = Event.objects.all()
        if days is not None:
            qs = qs.filter(created_at__gte=timezone.now() - timedelta(days=days))
        return qs.count()

    @staticmethod
    def get_events_this_month() -> int:
        now = timezone.now()
        return Event.objects.filter(
            created_at__year=now.year, created_at__month=now.month
        ).count()

    @staticmethod
    def get_event_type_distribution() -> list[dict]:
        """Return [{event_type, label, count}, …] for all types."""
        rows = (
            Event.objects.values("event_type")
            .annotate(count=Count("id"))
            .order_by("-count")
        )
        label_map = dict(EventType.choices)
        return [
            {
                "event_type": r["event_type"],
                "label": str(label_map.get(r["event_type"], r["event_type"])),
                "count": r["count"],
            }
            for r in rows
        ]

    @staticmethod
    def get_events_over_time(days: int = 30) -> dict:
        """Events per day for the last N days, grouped by event_type."""
        since = (timezone.now() - timedelta(days=days - 1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        rows = (
            Event.objects.filter(created_at__gte=since)
            .annotate(day=TruncDate("created_at"))
            .values("day", "event_type")
            .annotate(count=Count("id"))
            .order_by("day")
        )

        # Build {event_type: {date: count}}
        type_map: dict[str, dict] = {}
        for r in rows:
            et = r["event_type"]
            type_map.setdefault(et, {})[r["day"]] = r["count"]

        dates = []
        for i in range(days):
            dates.append((since + timedelta(days=i)).date())

        series = {}
        label_map = dict(EventType.choices)
        for et, day_counts in type_map.items():
            series[str(label_map.get(et, et))] = [day_counts.get(d, 0) for d in dates]

        return {
            "dates": [d.isoformat() for d in dates],
            "series": series,
        }

    @staticmethod
    def get_top_articles(limit: int = 10) -> list[dict]:
        """Top articles by read count."""
        from tech_articles.content.models import Article

        rows = (
            Event.objects.filter(event_type=EventType.ARTICLE_READ)
            .values("metadata_json")
            .annotate(count=Count("id"))
            .order_by("-count")[:limit * 3]  # over-fetch for dedup
        )

        slug_counts: dict[str, int] = {}
        slug_titles: dict[str, str] = {}
        for r in rows:
            try:
                meta = json.loads(r["metadata_json"]) if r["metadata_json"] else {}
            except (json.JSONDecodeError, TypeError):
                continue
            slug = meta.get("article_slug", "")
            if not slug:
                continue
            slug_counts[slug] = slug_counts.get(slug, 0) + r["count"]
            if slug not in slug_titles:
                slug_titles[slug] = meta.get("article_title", slug)

        sorted_slugs = sorted(slug_counts, key=slug_counts.get, reverse=True)[:limit]
        return [
            {"slug": s, "title": slug_titles.get(s, s), "count": slug_counts[s]}
            for s in sorted_slugs
        ]

    @staticmethod
    def get_user_growth(months: int = 12) -> dict:
        """New users per month for the last N months."""
        from tech_articles.accounts.models import User

        now = timezone.now()
        # Go back N months
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        for _ in range(months - 1):
            start = (start - timedelta(days=1)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        rows = (
            User.objects.filter(date_joined__gte=start)
            .annotate(month=TruncMonth("date_joined"))
            .values("month")
            .annotate(count=Count("id"))
            .order_by("month")
        )
        month_map = {r["month"].month: r["count"] for r in rows}

        labels = []
        values = []
        cursor = start
        for _ in range(months):
            labels.append(cursor.strftime("%Y-%m"))
            values.append(month_map.get(cursor.month, 0))
            # Advance to next month
            if cursor.month == 12:
                cursor = cursor.replace(year=cursor.year + 1, month=1)
            else:
                cursor = cursor.replace(month=cursor.month + 1)

        return {"labels": labels, "values": values}

    @staticmethod
    def get_revenue_over_time(days: int = 30) -> dict:
        """Revenue per day for the last N days."""
        from tech_articles.billing.models import PaymentTransaction
        from tech_articles.utils.enums import PaymentStatus as PS

        since = (timezone.now() - timedelta(days=days - 1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        rows = (
            PaymentTransaction.objects.filter(
                status=PS.SUCCEEDED, created_at__gte=since
            )
            .annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(revenue=models_Sum("amount"))
            .order_by("day")
        )
        day_map = {r["day"]: float(r["revenue"] or 0) for r in rows}

        dates = []
        values = []
        for i in range(days):
            d = (since + timedelta(days=i)).date()
            dates.append(d.isoformat())
            values.append(day_map.get(d, 0))

        return {"dates": dates, "values": values}




