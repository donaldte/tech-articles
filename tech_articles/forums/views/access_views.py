"""
Forum group access views (subscription request + one-time purchase flows).
"""

import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import ListView, CreateView

from tech_articles.forums.forms import GroupAccessRequestForm
from tech_articles.forums.models import ForumCategory, ForumGroupAccess, ForumAccessStatus, ForumGroupAccessType

logger = logging.getLogger(__name__)


class ForumGroupAccessListView(LoginRequiredMixin, ListView):
    """
    Admin view — list all pending/approved/rejected access requests.
    """

    model = ForumGroupAccess
    template_name = "tech-articles/dashboard/pages/forums/access/list.html"
    context_object_name = "accesses"
    paginate_by = 30
    ordering = ["-created_at"]

    def get_queryset(self):
        qs = super().get_queryset().select_related("user", "category")
        status = self.request.GET.get("status", "")
        if status in ForumAccessStatus.values:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_filter"] = self.request.GET.get("status", "")
        context["status_choices"] = ForumAccessStatus.choices
        context["pending_count"] = ForumGroupAccess.objects.filter(
            status=ForumAccessStatus.PENDING
        ).count()
        return context


class GroupAccessRequestView(LoginRequiredMixin, CreateView):
    """
    User-facing view — subscriber requests access to a group.
    The access_type is set to SUBSCRIPTION and status to PENDING.
    """

    model = ForumGroupAccess
    form_class = GroupAccessRequestForm
    template_name = "tech-articles/forums/access/request.html"

    def get_category(self):
        if not hasattr(self, "_category"):
            self._category = get_object_or_404(
                ForumCategory, slug=self.kwargs["category_slug"], is_active=True
            )
        return self._category

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.get_category()
        return context

    def form_valid(self, form):
        category = self.get_category()

        # Guard: user must have an active subscription to request access this way
        if not category.can_request_subscription_access(self.request.user):
            existing = ForumGroupAccess.objects.filter(
                user=self.request.user, category=category
            ).first()
            if existing:
                messages.warning(
                    self.request,
                    _("You already have a pending or active access request for this group."),
                )
            else:
                messages.error(
                    self.request,
                    _(
                        "An active premium subscription is required to request "
                        "access to this group."
                    ),
                )
            return HttpResponseRedirect(reverse_lazy("forums:category_list"))

        form.instance.user = self.request.user
        form.instance.category = category
        form.instance.access_type = ForumGroupAccessType.SUBSCRIPTION
        form.instance.status = ForumAccessStatus.PENDING
        messages.success(
            self.request,
            _("Your access request has been submitted and is pending admin approval."),
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("forums:category_list")


class ForumGroupAccessApproveView(LoginRequiredMixin, View):
    """
    Admin shortcut — approve a pending access request via POST.
    Returns JSON for AJAX or redirects.
    """

    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return JsonResponse({"success": False, "message": str(_("Forbidden"))}, status=403)

        access = get_object_or_404(ForumGroupAccess, pk=kwargs["pk"])
        access.status = ForumAccessStatus.APPROVED
        access.approved_at = timezone.now()
        access.approved_by = request.user
        access.save(update_fields=["status", "approved_at", "approved_by"])

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse(
                {"success": True, "message": str(_("Access approved."))}
            )

        messages.success(request, _("Access approved successfully."))
        return HttpResponseRedirect(reverse_lazy("forums:access_list"))


class ForumGroupAccessRejectView(LoginRequiredMixin, View):
    """
    Admin shortcut — reject a pending access request via POST.
    Accepts an optional ``reason`` field to explain the decision to the user.
    """

    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return JsonResponse({"success": False, "message": str(_("Forbidden"))}, status=403)

        access = get_object_or_404(ForumGroupAccess, pk=kwargs["pk"])
        access.status = ForumAccessStatus.REJECTED
        access.rejection_reason = request.POST.get("reason", "").strip()
        access.save(update_fields=["status", "rejection_reason"])

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse(
                {"success": True, "message": str(_("Access rejected."))}
            )

        messages.success(request, _("Access rejected."))
        return HttpResponseRedirect(reverse_lazy("forums:access_list"))
