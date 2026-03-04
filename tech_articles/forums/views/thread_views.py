"""
Forum thread and reply views.
"""

import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from tech_articles.forums.forms import ForumThreadForm, ThreadReplyForm
from tech_articles.forums.models import ForumCategory, ForumThread, ThreadReply

logger = logging.getLogger(__name__)


class ForumThreadListView(LoginRequiredMixin, ListView):
    """List threads in a specific forum category."""

    model = ForumThread
    template_name = "tech-articles/forums/threads/list.html"
    context_object_name = "threads"
    paginate_by = 20

    def get_queryset(self):
        self.category = get_object_or_404(
            ForumCategory, slug=self.kwargs["category_slug"], is_active=True
        )
        return (
            ForumThread.objects.filter(
                category=self.category,
                deleted_at__isnull=True,
            )
            .select_related("author")
            .order_by("-is_pinned", "-created_at")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.category
        return context


class ForumThreadDetailView(LoginRequiredMixin, DetailView):
    """Display a forum thread with all its replies."""

    model = ForumThread
    template_name = "tech-articles/forums/threads/detail.html"
    context_object_name = "thread"

    def get_object(self, queryset=None):
        thread = get_object_or_404(
            ForumThread,
            pk=self.kwargs["pk"],
            deleted_at__isnull=True,
        )
        # Increment view counter
        ForumThread.objects.filter(pk=thread.pk).update(
            views_count=thread.views_count + 1
        )
        return thread

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["replies"] = (
            self.object.replies.filter(deleted_at__isnull=True)
            .select_related("author")
            .order_by("-is_best_answer", "-votes_count", "created_at")
        )
        context["reply_form"] = ThreadReplyForm()
        return context


class ForumThreadCreateView(LoginRequiredMixin, CreateView):
    """Create a new forum thread inside a category."""

    model = ForumThread
    form_class = ForumThreadForm
    template_name = "tech-articles/forums/threads/create.html"

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
        form.instance.author = self.request.user
        form.instance.category = self.get_category()
        messages.success(self.request, _("Thread created successfully."))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _("Please correct the errors below."))
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy(
            "forums:thread_detail",
            kwargs={
                "category_slug": self.kwargs["category_slug"],
                "pk": self.object.pk,
            },
        )


class ForumThreadUpdateView(LoginRequiredMixin, UpdateView):
    """Update an existing forum thread (author or admin only)."""

    model = ForumThread
    form_class = ForumThreadForm
    template_name = "tech-articles/forums/threads/edit.html"
    context_object_name = "thread"

    def get_queryset(self):
        qs = super().get_queryset().filter(deleted_at__isnull=True)
        if not self.request.user.is_staff:
            qs = qs.filter(author=self.request.user)
        return qs

    def form_valid(self, form):
        messages.success(self.request, _("Thread updated successfully."))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "forums:thread_detail",
            kwargs={
                "category_slug": self.object.category.slug,
                "pk": self.object.pk,
            },
        )


class ForumThreadDeleteView(LoginRequiredMixin, DeleteView):
    """Soft-delete a forum thread (author or admin only)."""

    model = ForumThread

    def get_queryset(self):
        qs = super().get_queryset().filter(deleted_at__isnull=True)
        if not self.request.user.is_staff:
            qs = qs.filter(author=self.request.user)
        return qs

    def post(self, request, *args, **kwargs):
        from django.utils import timezone

        self.object = self.get_object()
        self.object.deleted_at = timezone.now()
        self.object.save(update_fields=["deleted_at"])

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"success": True, "message": str(_("Thread deleted."))})

        messages.success(request, _("Thread deleted successfully."))
        from django.http import HttpResponseRedirect
        return HttpResponseRedirect(
            reverse_lazy(
                "forums:thread_list",
                kwargs={"category_slug": self.object.category.slug},
            )
        )


# ============================================================================
# REPLY VIEWS
# ============================================================================


class ThreadReplyCreateView(LoginRequiredMixin, CreateView):
    """Post a reply to a forum thread."""

    model = ThreadReply
    form_class = ThreadReplyForm
    template_name = "tech-articles/forums/replies/create.html"

    def get_thread(self):
        if not hasattr(self, "_thread"):
            self._thread = get_object_or_404(
                ForumThread,
                pk=self.kwargs["thread_pk"],
                deleted_at__isnull=True,
                is_closed=False,
            )
        return self._thread

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.thread = self.get_thread()
        messages.success(self.request, _("Reply posted successfully."))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _("Please correct the errors below."))
        return super().form_invalid(form)

    def get_success_url(self):
        thread = self.get_thread()
        return reverse_lazy(
            "forums:thread_detail",
            kwargs={
                "category_slug": thread.category.slug,
                "pk": thread.pk,
            },
        )


class ThreadReplyUpdateView(LoginRequiredMixin, UpdateView):
    """Edit a reply (author or admin only)."""

    model = ThreadReply
    form_class = ThreadReplyForm
    template_name = "tech-articles/forums/replies/edit.html"
    context_object_name = "reply"

    def get_queryset(self):
        qs = super().get_queryset().filter(deleted_at__isnull=True)
        if not self.request.user.is_staff:
            qs = qs.filter(author=self.request.user)
        return qs

    def form_valid(self, form):
        messages.success(self.request, _("Reply updated successfully."))
        return super().form_valid(form)

    def get_success_url(self):
        thread = self.object.thread
        return reverse_lazy(
            "forums:thread_detail",
            kwargs={
                "category_slug": thread.category.slug,
                "pk": thread.pk,
            },
        )


class ThreadReplyDeleteView(LoginRequiredMixin, DeleteView):
    """Soft-delete a reply (author or admin only)."""

    model = ThreadReply

    def get_queryset(self):
        qs = super().get_queryset().filter(deleted_at__isnull=True)
        if not self.request.user.is_staff:
            qs = qs.filter(author=self.request.user)
        return qs

    def post(self, request, *args, **kwargs):
        from django.utils import timezone

        self.object = self.get_object()
        thread = self.object.thread
        self.object.deleted_at = timezone.now()
        self.object.save(update_fields=["deleted_at"])

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"success": True, "message": str(_("Reply deleted."))})

        messages.success(request, _("Reply deleted successfully."))
        from django.http import HttpResponseRedirect
        return HttpResponseRedirect(
            reverse_lazy(
                "forums:thread_detail",
                kwargs={
                    "category_slug": thread.category.slug,
                    "pk": thread.pk,
                },
            )
        )
