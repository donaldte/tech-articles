"""
Plan views for dashboard CRUD operations.
"""
import json
import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView

from tech_articles.billing.models import Plan, PlanFeature, PlanHistory
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

    @transaction.atomic
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Create plan history record
        self._create_history_record("created")
        
        # Handle PlanFeatures from POST data
        self._save_plan_features()
        
        messages.success(self.request, _("Plan created successfully."))
        return response

    def form_invalid(self, form):
        messages.error(self.request, _("Please correct the errors below."))
        return super().form_invalid(form)
    
    def _create_history_record(self, change_type):
        """Create a history record for plan changes."""
        PlanHistory.objects.create(
            plan=self.object,
            changed_by=self.request.user,
            change_type=change_type,
            changes=self._get_change_description(change_type),
            snapshot=self._get_plan_snapshot(),
        )
    
    def _get_change_description(self, change_type):
        """Get a human-readable description of changes."""
        if change_type == "created":
            return _("Plan created with name: %(name)s, price: %(price)s %(currency)s/%(interval)s") % {
                "name": self.object.name,
                "price": self.object.price,
                "currency": self.object.currency,
                "interval": self.object.get_interval_display(),
            }
        return _("Plan modified")
    
    def _get_plan_snapshot(self):
        """Get a JSON snapshot of the plan data."""
        return {
            "name": self.object.name,
            "slug": self.object.slug,
            "description": self.object.description,
            "price": str(self.object.price),
            "currency": self.object.currency,
            "interval": self.object.interval,
            "custom_interval_count": self.object.custom_interval_count,
            "trial_period_days": self.object.trial_period_days,
            "max_articles": self.object.max_articles,
            "max_resources": self.object.max_resources,
            "max_appointments": self.object.max_appointments,
            "is_active": self.object.is_active,
            "is_popular": self.object.is_popular,
            "display_order": self.object.display_order,
            "provider": self.object.provider,
            "provider_price_id": self.object.provider_price_id,
        }
    
    def _save_plan_features(self):
        """Save plan features from POST data."""
        features_data = self.request.POST.get("features_json", "[]")
        try:
            features = json.loads(features_data)
            for idx, feature_data in enumerate(features):
                PlanFeature.objects.create(
                    plan=self.object,
                    name=feature_data.get("name", ""),
                    description=feature_data.get("description", ""),
                    is_included=feature_data.get("is_included", True),
                    display_order=idx,
                )
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Error parsing plan features: {e}")



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
        # Get existing features for the plan
        context["existing_features"] = list(
            self.object.plan_features.values("id", "name", "description", "is_included", "display_order")
            .order_by("display_order")
        )
        return context

    @transaction.atomic
    def form_valid(self, form):
        # Store old values for comparison
        old_plan = Plan.objects.get(pk=self.object.pk)
        old_values = {
            "name": old_plan.name,
            "price": old_plan.price,
            "currency": old_plan.currency,
            "interval": old_plan.interval,
            "is_active": old_plan.is_active,
            "is_popular": old_plan.is_popular,
        }
        
        response = super().form_valid(form)
        
        # Detect changes and create history
        changes = self._detect_changes(old_values)
        if changes:
            self._create_history_record("updated", changes)
        
        # Handle PlanFeatures from POST data
        self._save_plan_features()
        
        messages.success(self.request, _("Plan updated successfully."))
        return response

    def form_invalid(self, form):
        messages.error(self.request, _("Please correct the errors below."))
        return super().form_invalid(form)
    
    def _detect_changes(self, old_values):
        """Detect what changed and create a human-readable description."""
        changes = []
        
        if old_values["name"] != self.object.name:
            changes.append(_("Name: %(old)s → %(new)s") % {"old": old_values["name"], "new": self.object.name})
        
        if old_values["price"] != self.object.price:
            changes.append(
                _("Price: %(old)s → %(new)s %(currency)s") % {
                    "old": old_values["price"],
                    "new": self.object.price,
                    "currency": self.object.currency,
                }
            )
        
        if old_values["interval"] != self.object.interval:
            changes.append(
                _("Interval: %(old)s → %(new)s") % {
                    "old": old_values["interval"],
                    "new": self.object.interval,
                }
            )
        
        if old_values["is_active"] != self.object.is_active:
            status = _("Active") if self.object.is_active else _("Inactive")
            changes.append(_("Status changed to: %(status)s") % {"status": status})
        
        if old_values["is_popular"] != self.object.is_popular:
            popular = _("Yes") if self.object.is_popular else _("No")
            changes.append(_("Popular badge: %(popular)s") % {"popular": popular})
        
        return ", ".join(changes) if changes else None
    
    def _create_history_record(self, change_type, changes=None):
        """Create a history record for plan changes."""
        PlanHistory.objects.create(
            plan=self.object,
            changed_by=self.request.user,
            change_type=change_type,
            changes=changes or _("Plan modified"),
            snapshot=self._get_plan_snapshot(),
        )
    
    def _get_plan_snapshot(self):
        """Get a JSON snapshot of the plan data."""
        return {
            "name": self.object.name,
            "slug": self.object.slug,
            "description": self.object.description,
            "price": str(self.object.price),
            "currency": self.object.currency,
            "interval": self.object.interval,
            "custom_interval_count": self.object.custom_interval_count,
            "trial_period_days": self.object.trial_period_days,
            "max_articles": self.object.max_articles,
            "max_resources": self.object.max_resources,
            "max_appointments": self.object.max_appointments,
            "is_active": self.object.is_active,
            "is_popular": self.object.is_popular,
            "display_order": self.object.display_order,
            "provider": self.object.provider,
            "provider_price_id": self.object.provider_price_id,
        }
    
    def _save_plan_features(self):
        """Save plan features from POST data."""
        features_data = self.request.POST.get("features_json", "[]")
        try:
            features = json.loads(features_data)
            
            # Delete existing features not in the new list
            feature_ids_to_keep = [f.get("id") for f in features if f.get("id")]
            self.object.plan_features.exclude(id__in=feature_ids_to_keep).delete()
            
            # Create or update features
            for idx, feature_data in enumerate(features):
                feature_id = feature_data.get("id")
                if feature_id:
                    # Update existing feature
                    PlanFeature.objects.filter(id=feature_id, plan=self.object).update(
                        name=feature_data.get("name", ""),
                        description=feature_data.get("description", ""),
                        is_included=feature_data.get("is_included", True),
                        display_order=idx,
                    )
                else:
                    # Create new feature
                    PlanFeature.objects.create(
                        plan=self.object,
                        name=feature_data.get("name", ""),
                        description=feature_data.get("description", ""),
                        is_included=feature_data.get("is_included", True),
                        display_order=idx,
                    )
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Error parsing plan features: {e}")



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


class PlanHistoryView(LoginRequiredMixin, AdminRequiredMixin, DetailView):
    """Display the history of changes for a plan."""
    model = Plan
    template_name = "tech-articles/dashboard/pages/billing/plans/history.html"
    context_object_name = "plan"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Plan History")
        context["history_records"] = self.object.history_records.select_related("changed_by").order_by("-created_at")
        return context

