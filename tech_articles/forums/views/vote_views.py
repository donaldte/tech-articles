"""
Vote views — allow users to up-vote or down-vote threads and thread replies.
"""

import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.views import View

from tech_articles.forums.models import ForumThread, ForumVote, ThreadReply
from tech_articles.utils.enums import ForumVoteValue

logger = logging.getLogger(__name__)


class ForumVoteView(LoginRequiredMixin, View):
    """
    AJAX endpoint — cast or toggle a vote on a forum thread or a reply.

    POST body: { "value": 1 }   (1 = up-vote, -1 = down-vote)

    URL kwargs:
        thread_pk   — PK of a ForumThread   (mutually exclusive with reply_pk)
        reply_pk    — PK of a ThreadReply   (mutually exclusive with thread_pk)

    Behaviour:
    - If the user has not voted yet  → create the vote and update the cache.
    - If the user voted the same way → remove the vote (toggle off).
    - If the user voted the other way → update to the new value.
    """

    http_method_names = ["post"]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        thread_pk = kwargs.get("thread_pk")
        reply_pk = kwargs.get("reply_pk")

        if thread_pk:
            target_model = ForumThread
            target = get_object_or_404(ForumThread, pk=thread_pk, deleted_at__isnull=True)
            vote_filter = {"thread": target, "voter": request.user}
            vote_kwargs = {"thread": target, "voter": request.user}
            count_field = "votes_count"
        elif reply_pk:
            target = get_object_or_404(
                ThreadReply,
                pk=reply_pk,
                deleted_at__isnull=True,
                parent__isnull=True,  # only top-level replies are voteable
            )
            target_model = ThreadReply
            vote_filter = {"reply": target, "voter": request.user}
            vote_kwargs = {"reply": target, "voter": request.user}
            count_field = "votes_count"
        else:
            return JsonResponse(
                {"success": False, "message": str(_("No target specified."))}, status=400
            )

        try:
            value = int(request.POST.get("value", 1))
        except (TypeError, ValueError):
            return JsonResponse(
                {"success": False, "message": str(_("Invalid vote value."))}, status=400
            )

        if value not in ForumVoteValue.values:
            return JsonResponse(
                {"success": False, "message": str(_("Invalid vote value."))}, status=400
            )

        existing = ForumVote.objects.filter(**vote_filter).first()

        if existing is None:
            ForumVote.objects.create(value=value, **vote_kwargs)
            delta = value
        elif existing.value == value:
            # Toggle off
            existing.delete()
            delta = -value
        else:
            # Switch direction
            delta = value - existing.value
            existing.value = value
            existing.save(update_fields=["value"])

        # Update cached counter on the target
        target_model.objects.filter(pk=target.pk).update(
            votes_count=target.votes_count + delta
        )
        target.refresh_from_db(fields=[count_field])

        return JsonResponse(
            {
                "success": True,
                "votes_count": target.votes_count,
            }
        )


# Backward-compatible alias for the reply-only vote URL
ThreadReplyVoteView = ForumVoteView
