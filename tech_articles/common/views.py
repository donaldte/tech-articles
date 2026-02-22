import logging
import math

from django.db.models import Q
from django.http import JsonResponse
from django.views import View
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from tech_articles.billing.models import Plan
from tech_articles.content.models import Article, Category, FeaturedArticles
from tech_articles.utils.constants import FEATURED_ARTICLES_UUID
from tech_articles.utils.enums import ArticleStatus
from django.utils.translation import gettext_lazy as _

from django.utils import timezone
logger = logging.getLogger(__name__)


def _serialize_article(article, fields=None):
    """Serialize an Article instance to a JSON-safe dict.

    Args:
        article: Article model instance.
        fields: Optional set of field names to include. If ``None``,
                all available fields are returned.
    """
    categories = list(
        article.categories.values_list("name", flat=True)
    )
    all_fields = {
        "id": str(article.id),
        "title": article.title,
        "slug": article.slug,
        "summary": article.summary,
        "language": article.language,
        "reading_time_minutes": article.reading_time_minutes,
        "cover_image_key": article.cover_image_key,
        "cover_alt_text": article.cover_alt_text,
        "access_type": article.access_type,
        "difficulty": article.difficulty,
        "categories": categories,
        "published_at": (
            article.published_at.isoformat() if article.published_at else None
        ),
    }
    if fields is None:
        return all_fields
    return {k: v for k, v in all_fields.items() if k in fields}


class HomePageView(TemplateView):
    """
    Home page view that displays featured articles, categories, and popular tags.

    This view uses class-based view (CBV) for better organization and reusability.
    It retrieves and filters content based on publication status and active state.
    Featured articles are retrieved from the FeaturedArticles configuration model.
    """

    template_name = "tech-articles/home/pages/index.html"

    def get_context_data(self, **kwargs):
        """Add active plans and featured articles to context."""
        context = super().get_context_data(**kwargs)
        context["active_plans"] = Plan.objects.filter(is_active=True).prefetch_related("plan_features")
        
        # Get featured articles configuration (create if doesn't exist)
        featured_config, created = FeaturedArticles.objects.get_or_create(pk=FEATURED_ARTICLES_UUID)
        context["first_featured_article"] = featured_config.first_feature
        context["second_featured_article"] = featured_config.second_feature
        context["third_featured_article"] = featured_config.third_feature
        
        return context


class ArticlesListView(TemplateView):
    """Articles listing page with lazy-loaded dynamic content."""

    template_name = "tech-articles/home/pages/articles/articles_list.html"


class ArticlesApiView(View):
    """
    API endpoint for paginated articles listing with search, sort, and filter.

    Query parameters:
      - page (int): page number (default 1)
      - search (str): search term for title/summary
      - sort (str): 'recent' | 'oldest' | 'popular' (default 'recent')
      - categories (str): comma-separated category IDs (UUIDs)
    """

    http_method_names = ["get"]
    ARTICLES_PER_PAGE = 6

    def get(self, request):
        qs = Article.objects.filter(
            status=ArticleStatus.PUBLISHED,
        ).prefetch_related("categories")

        # Search
        search = request.GET.get("search", "").strip()
        if search:
            qs = qs.filter(
                Q(title__icontains=search) | Q(summary__icontains=search)
            )

        # Category filter
        categories_param = request.GET.get("categories", "").strip()
        if categories_param:
            category_ids = [
                cid.strip()
                for cid in categories_param.split(",")
                if cid.strip()
            ]
            if category_ids:
                qs = qs.filter(categories__id__in=category_ids).distinct()

        # Sort
        sort = request.GET.get("sort", "recent")
        if sort == "oldest":
            qs = qs.order_by("published_at", "created_at")
        elif sort == "popular":
            qs = qs.order_by("-reading_time_minutes", "-published_at")
        else:
            qs = qs.order_by("-published_at", "-created_at")

        # Pagination
        total_count = qs.count()
        total_pages = max(1, math.ceil(total_count / self.ARTICLES_PER_PAGE))

        try:
            page = int(request.GET.get("page", 1))
        except (ValueError, TypeError):
            page = 1
        page = max(1, min(page, total_pages))

        start = (page - 1) * self.ARTICLES_PER_PAGE
        end = start + self.ARTICLES_PER_PAGE
        articles = qs[start:end]

        return JsonResponse({
            "articles": [_serialize_article(a) for a in articles],
            "pagination": {
                "current_page": page,
                "total_pages": total_pages,
                "total_count": total_count,
                "per_page": self.ARTICLES_PER_PAGE,
                "has_previous": page > 1,
                "has_next": page < total_pages,
            },
        })


class FeaturedArticlesApiView(View):
    """API endpoint returning the three featured articles."""

    http_method_names = ["get"]

    def get(self, request):
        featured_config, _ = FeaturedArticles.objects.get_or_create(
            pk=FEATURED_ARTICLES_UUID
        )
        featured_fields = {
            "id", "title", "slug", "summary",
            "cover_image_key", "cover_alt_text", "categories",
        }
        result = []
        for attr in ("first_feature", "second_feature", "third_feature"):
            article = getattr(featured_config, attr)
            if article and article.status == ArticleStatus.PUBLISHED:
                result.append(_serialize_article(article, fields=featured_fields))
        return JsonResponse({"featured": result})


class RelatedArticlesApiView(View):
    """API endpoint returning related (recent) articles for the sidebar."""

    http_method_names = ["get"]

    def get(self, request):
        related_fields = {
            "id", "title", "slug", "summary",
            "reading_time_minutes", "categories",
        }
        articles = (
            Article.objects.filter(status=ArticleStatus.PUBLISHED)
            .prefetch_related("categories")
            .order_by("-published_at", "-created_at")[:4]
        )
        result = [
            _serialize_article(a, fields=related_fields) for a in articles
        ]
        return JsonResponse({"related": result})


class CategoriesApiView(View):
    """API endpoint returning active categories for filter dropdowns."""

    http_method_names = ["get"]

    def get(self, request):
        categories = Category.objects.filter(is_active=True).order_by(
            "sort_order", "name"
        )
        result = [
            {"id": str(c.id), "name": c.name, "slug": c.slug}
            for c in categories
        ]
        return JsonResponse({"categories": result})


class ArticleDetailView(TemplateView):
    """
    Article detail page (design-only template view).

    No query parameters or slug routing needed at this stage —
    the view simply renders the static detail template as a design preview.
    """

    template_name = "tech-articles/home/pages/articles/article_detail.html"


class ArticlePreviewView(TemplateView):
    """
    Article preview page — locked / paywall experience.

    Shows the article hero, cover image, and the first two intro paragraphs,
    then overlays a gradient-fade + "Unlock the full article" CTA panel.

    This is a standalone template (article_preview.html) intentionally separate
    from article_detail.html so the two experiences can evolve independently.
    It contains no comments, no pagination, and no resources section.
    """

    template_name = "tech-articles/home/pages/articles/article_preview.html"


class AppointmentListHomeView(TemplateView):
    """
    Display available appointment time slots in a weekly calendar view.
    Users can browse and select available time slots.
    """
    template_name = "tech-articles/home/pages/appointments/list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from tech_articles.appointments.models import AppointmentSettings
        context["appointment_settings"] = AppointmentSettings.get_settings()
        return context


class AppointmentDetailHomeView(LoginRequiredMixin, TemplateView):
    """
    Display appointment details including time, duration, and amount.
    Users can review and confirm the appointment before payment.
    """
    template_name = "tech-articles/home/pages/appointments/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slot_id = self.kwargs.get('slot_id')
        from tech_articles.appointments.models import Appointment
        # In this context, we expect an Appointment to exist for the slot
        try:
            appointment = Appointment.objects.select_related('slot', 'appointment_type').get(slot_id=slot_id)
            context['appointment'] = appointment
        except Appointment.DoesNotExist:
            context['appointment'] = None
            
        return context

class AppointmentServiceSelectionView(LoginRequiredMixin, TemplateView):
    """
    New professional page for selecting service type and duration.
    """
    template_name = "tech-articles/home/pages/appointments/service_selection.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from tech_articles.appointments.models import AppointmentType
        from django.utils.dateparse import parse_datetime
        
        start_at_str = self.request.GET.get('start')
        end_at_str = self.request.GET.get('end')
        
        start_at = parse_datetime(start_at_str) if start_at_str else None
        end_at = parse_datetime(end_at_str) if end_at_str else None
        
        block_duration_mins = 0
        if start_at and end_at:
            block_duration_mins = (end_at - start_at).total_seconds() / 60

        services = AppointmentType.objects.filter(is_active=True)
        processed_services = []
        
        for service in services:
            # Parse allowed durations
            durations = [int(d.strip()) for d in service.allowed_durations_minutes.split(',') if d.strip().isdigit()]
            # Filter durations that fit in the block
            available_durations = [d for d in durations if d <= block_duration_mins]
            
            processed_services.append({
                'obj': service,
                'available_durations': available_durations,
                'has_available_duration': len(available_durations) > 0,
                'durations_display': durations # Original for reference
            })

        context.update({
            'services': processed_services,
            'start_at': start_at,
            'end_at': end_at,
            'block_duration': block_duration_mins
        })
        return context

    def post(self, request, *args, **kwargs):
        from tech_articles.appointments.models import Appointment, AppointmentSlot, AppointmentType
        from tech_articles.utils.enums import AppointmentStatus, PaymentStatus
        from django.utils.dateparse import parse_datetime
        from datetime import timedelta
        from django.urls import reverse
        from django.http import HttpResponseRedirect
        from django.contrib import messages
        from django.utils.translation import gettext as _
        from decimal import Decimal

        start_at_str = request.POST.get('start_at')
        service_id = request.POST.get('service_id')
        duration = request.POST.get('duration')

        if not all([start_at_str, service_id, duration]):
            messages.error(request, _("Please select a service and duration."))
            return self.get(request, *args, **kwargs)

        dt = parse_datetime(start_at_str)
        service = AppointmentType.objects.get(id=service_id)
        duration_mins = int(duration)
        end_dt = dt + timedelta(minutes=duration_mins)

        # 1. Create/Check Slot
        # Important: Since we support dynamic blocks, we check if this specific range overlaps with any booked slot
        conflicting = AppointmentSlot.objects.filter(
            is_booked=True,
            start_at__lt=end_dt,
            end_at__gt=dt
        ).exists()

        if conflicting:
            messages.error(request, _("This time range is already partially booked. Please choose another."))
            return HttpResponseRedirect(reverse('common:appointments_book'))

        # Create the materialized slot
        slot = AppointmentSlot.objects.create(
            start_at=dt,
            end_at=end_dt,
            is_booked=True,
            booked_at=timezone.now()
        )

        # 2. Create Appointment
        hourly_rate = service.base_hourly_rate
        total_amount = (hourly_rate * Decimal(duration_mins)) / Decimal(60)

        appointment = Appointment.objects.create(
            user=request.user,
            slot=slot,
            appointment_type=service,
            duration_minutes=duration_mins,
            hourly_rate=hourly_rate,
            total_amount=total_amount,
            currency=service.currency,
            status=AppointmentStatus.PENDING,
            payment_status=PaymentStatus.PENDING
        )

        return HttpResponseRedirect(reverse('common:appointments_book_detail', kwargs={'slot_id': str(slot.id)}))

class AppointmentPaymentHomeView(LoginRequiredMixin, TemplateView):
    """
    Payment page for confirmed appointments.
    Final step in the appointment booking flow.
    """
    template_name = "tech-articles/home/pages/appointments/payment.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slot_id = self.kwargs.get('slot_id')
        from tech_articles.appointments.models import Appointment
        try:
            appointment = Appointment.objects.select_related('slot', 'appointment_type').get(slot_id=slot_id)
            context['appointment'] = appointment
        except Appointment.DoesNotExist:
            context['appointment'] = None
        return context

    def post(self, request, *args, **kwargs):
        from tech_articles.appointments.models import Appointment
        from tech_articles.utils.enums import AppointmentStatus, PaymentStatus
        from django.urls import reverse
        from django.http import JsonResponse
        
        slot_id = self.kwargs.get('slot_id')
        try:
            appointment = Appointment.objects.get(slot_id=slot_id)
            
            # Simulate processing time or just succeed
            appointment.payment_status = PaymentStatus.SUCCEEDED
            appointment.status = AppointmentStatus.LINK_PENDING
            appointment.save()
            
            return JsonResponse({
                'status': 'success',
                'redirect_url': reverse('appointments:appointments_list'),
                'message': _("Payment successful! Status updated to Link Pending.")
            })
        except Appointment.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': _("Appointment not found.")}, status=404)

