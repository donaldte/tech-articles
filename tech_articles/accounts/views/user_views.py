"""
Admin user management views.
Views for creating, listing, updating, deleting, and changing passwords for users.
"""

import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
    FormView,
)

from tech_articles.accounts.forms import (
    AdminUserCreateForm,
    AdminUserUpdateForm,
    AdminUserPasswordChangeForm,
)
from tech_articles.accounts.models import User
from tech_articles.utils.enums import UserRole
from tech_articles.utils.mixins import AdminRequiredMixin

logger = logging.getLogger(__name__)


class UserListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    """List all users with search and filtering."""

    model = User
    template_name = "tech-articles/dashboard/pages/users/list.html"
    context_object_name = "users"
    paginate_by = 15
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get("search", "").strip()
        status = self.request.GET.get("status", "")
        role = self.request.GET.get("role", "")

        if search:
            queryset = queryset.filter(
                Q(email__icontains=search) | Q(name__icontains=search)
            )

        if status == "active":
            queryset = queryset.filter(is_active=True)
        elif status == "inactive":
            queryset = queryset.filter(is_active=False)

        if role and role in dict(UserRole.choices):
            queryset = queryset.filter(role=role)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search"] = self.request.GET.get("search", "")
        context["status"] = self.request.GET.get("status", "")
        context["role"] = self.request.GET.get("role", "")
        context["total_count"] = User.objects.count()
        context["active_count"] = User.objects.filter(is_active=True).count()
        context["admin_count"] = User.objects.filter(
            Q(role=UserRole.ADMIN) | Q(is_staff=True) | Q(is_superuser=True)
        ).count()
        context["roles"] = UserRole.choices
        return context


class UserCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    """Create a new user."""

    model = User
    form_class = AdminUserCreateForm
    template_name = "tech-articles/dashboard/pages/users/form.html"
    success_url = reverse_lazy("accounts:users_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Create User")
        context["is_edit"] = False
        return context

    def form_valid(self, form):
        messages.success(self.request, _("User created successfully."))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _("Please correct the errors below."))
        return super().form_invalid(form)


class UserDetailView(LoginRequiredMixin, AdminRequiredMixin, DetailView):
    """View user details."""

    model = User
    template_name = "tech-articles/dashboard/pages/users/detail.html"
    context_object_name = "user_obj"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("User Details")
        return context


class UserUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    """Update an existing user."""

    model = User
    form_class = AdminUserUpdateForm
    template_name = "tech-articles/dashboard/pages/users/form.html"
    success_url = reverse_lazy("accounts:users_list")
    context_object_name = "user_obj"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["current_user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Edit User")
        context["is_edit"] = True
        return context

    def form_valid(self, form):
        messages.success(self.request, _("User updated successfully."))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _("Please correct the errors below."))
        return super().form_invalid(form)


class UserDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    """Delete a user."""

    model = User
    success_url = reverse_lazy("accounts:users_list")

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Prevent deleting own account
        if obj.pk == self.request.user.pk:
            messages.error(self.request, _("You cannot delete your own account."))
            return None
        return obj

    def delete(self, request, *args, **kwargs):
        """Handle both AJAX and regular delete requests."""
        self.object = self.get_object()

        if self.object is None:
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse(
                    {
                        "success": False,
                        "message": str(_("You cannot delete your own account.")),
                    },
                    status=400,
                )
            return redirect(self.success_url)

        user_email = self.object.email

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            self.object.delete()
            return JsonResponse(
                {
                    "success": True,
                    "message": str(
                        _("User '%(email)s' deleted successfully.")
                        % {"email": user_email}
                    ),
                }
            )

        messages.success(
            request, _("User '%(email)s' deleted successfully.") % {"email": user_email}
        )
        return super().delete(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Handle POST request for deletion."""
        return self.delete(request, *args, **kwargs)


class UserPasswordChangeView(LoginRequiredMixin, AdminRequiredMixin, FormView):
    """Change a user's password (admin action)."""

    form_class = AdminUserPasswordChangeForm
    template_name = "tech-articles/dashboard/pages/users/change_password.html"
    success_url = reverse_lazy("accounts:users_list")

    def get_user_object(self):
        """Get the user whose password is being changed."""
        pk = self.kwargs.get("pk")
        return get_object_or_404(User, pk=pk)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.get_user_object()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_obj"] = self.get_user_object()
        context["page_title"] = _("Change Password")
        return context

    def form_valid(self, form):
        user = form.save()
        messages.success(
            self.request,
            _("Password for '%(email)s' changed successfully.") % {"email": user.email},
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _("Please correct the errors below."))
        return super().form_invalid(form)
