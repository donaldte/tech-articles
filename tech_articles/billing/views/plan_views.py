"""
Plan views for dashboard CRUD operations.
"""
import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from tech_articles.billing.models import Plan
from tech_articles.billing.forms import PlanForm
from tech_articles.billing.mixins import AdminRequiredMixin

logger = logging.getLogger(__name__)


class PlanListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    """List all plans with search and filtering."""
    model = Plan
    template_name = "tech-articles/dashboard/pages/billing/plans/list.html"
    context_object_name = "plans"
    paginate_by = 20
    ordering = ["display_order", "price"]

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get("search", "").strip()
        status = self.request.GET.get("status", "")

        if search:
            queryset = queryset.filter(name__icontains=search)
        if status == "active":
            queryset = queryset.filter(is_active=True)
        elif status == "inactive":
            queryset = queryset.filter(is_active=False)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search"] = self.request.GET.get("search", "")
        context["status"] = self.request.GET.get("status", "")
        context["total_count"] = Plan.objects.count()
        context["active_count"] = Plan.objects.filter(is_active=True).count()
        return context


class PlanCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    """Create a new plan."""
    model = Plan
    form_class = PlanForm
    template_name = "tech-articles/dashboard/pages/billing/plans/create.html"
    success_url = reverse_lazy("billing:plans_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Create Plan")
        context["is_edit"] = False
        return context

    def form_valid(self, form):
        messages.success(self.request, _("Plan created successfully."))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _("Please correct the errors below."))
        return super().form_invalid(form)


class PlanUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    """Update an existing plan."""
    model = Plan
    form_class = PlanForm
    template_name = "tech-articles/dashboard/pages/billing/plans/edit.html"
    success_url = reverse_lazy("billing:plans_list")
    context_object_name = "plan"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Edit Plan")
        context["is_edit"] = True
        return context

    def form_valid(self, form):
        messages.success(self.request, _("Plan updated successfully."))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _("Please correct the errors below."))
        return super().form_invalid(form)


class PlanDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    """Delete a plan."""
    model = Plan
    success_url = reverse_lazy("billing:plans_list")

    def delete(self, request, *args, **kwargs):
        """Handle both AJAX and regular delete requests."""
        self.object = self.get_object()
        plan_name = self.object.name

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            self.object.delete()
            return JsonResponse({
                "success": True,
                "message": str(_("Plan '%(name)s' deleted successfully.") % {"name": plan_name})
            })

        messages.success(request, _("Plan '%(name)s' deleted successfully.") % {"name": plan_name})
        return super().delete(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Handle POST request for deletion."""
        return self.delete(request, *args, **kwargs)
