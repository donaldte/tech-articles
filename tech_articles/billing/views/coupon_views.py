"""
Coupon views for dashboard CRUD operations.
"""
import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from tech_articles.billing.models import Coupon
from tech_articles.billing.forms import CouponForm
from tech_articles.utils.mixins import AdminRequiredMixin

logger = logging.getLogger(__name__)


class CouponListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    """List all coupons with search and filtering."""
    model = Coupon
    template_name = "tech-articles/dashboard/pages/billing/coupons/list.html"
    context_object_name = "coupons"
    paginate_by = 20
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get("search", "").strip()
        status = self.request.GET.get("status", "")

        if search:
            queryset = queryset.filter(code__icontains=search)
        if status == "active":
            queryset = queryset.filter(is_active=True)
        elif status == "inactive":
            queryset = queryset.filter(is_active=False)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search"] = self.request.GET.get("search", "")
        context["status"] = self.request.GET.get("status", "")
        context["total_count"] = Coupon.objects.count()
        context["active_count"] = Coupon.objects.filter(is_active=True).count()
        return context


class CouponCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    """Create a new coupon."""
    model = Coupon
    form_class = CouponForm
    template_name = "tech-articles/dashboard/pages/billing/coupons/create.html"
    success_url = reverse_lazy("billing:coupons_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Create Coupon")
        context["is_edit"] = False
        return context

    def form_valid(self, form):
        messages.success(self.request, _("Coupon created successfully."))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _("Please correct the errors below."))
        return super().form_invalid(form)


class CouponUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    """Update an existing coupon."""
    model = Coupon
    form_class = CouponForm
    template_name = "tech-articles/dashboard/pages/billing/coupons/edit.html"
    success_url = reverse_lazy("billing:coupons_list")
    context_object_name = "coupon"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Edit Coupon")
        context["is_edit"] = True
        return context

    def form_valid(self, form):
        messages.success(self.request, _("Coupon updated successfully."))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _("Please correct the errors below."))
        return super().form_invalid(form)


class CouponDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    """Delete a coupon."""
    model = Coupon
    success_url = reverse_lazy("billing:coupons_list")

    def delete(self, request, *args, **kwargs):
        """Handle both AJAX and regular delete requests."""
        self.object = self.get_object()
        coupon_code = self.object.code

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            self.object.delete()
            return JsonResponse({
                "success": True,
                "message": str(_("Coupon '%(code)s' deleted successfully.") % {"code": coupon_code})
            })

        messages.success(request, _("Coupon '%(code)s' deleted successfully.") % {"code": coupon_code})
        return super().delete(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Handle POST request for deletion."""
        return self.delete(request, *args, **kwargs)
