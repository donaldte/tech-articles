"""
Vote views — allow users to up-vote or down-vote thread replies.
"""

import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.views import View

from tech_articles.forums.models import ThreadReply, ThreadVote

logger = logging.getLogger(__name__)


class ThreadReplyVoteView(LoginRequiredMixin, View):
    """
    AJAX endpoint — cast or toggle a vote on a thread reply.

    POST body: { "value": 1 }   (1 = up-vote, -1 = down-vote)

    Behaviour:
    - If the user has not voted yet  → create the vote and update the cache.
    - If the user voted the same way → remove the vote (toggle off).
    - If the user voted the other way → update to the new value.
    """

    http_method_names = ["post"]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        reply = get_object_or_404(
            ThreadReply, pk=kwargs["reply_pk"], deleted_at__isnull=True
        )

        try:
            value = int(request.POST.get("value", 1))
        except (TypeError, ValueError):
            return JsonResponse(
                {"success": False, "message": str(_("Invalid vote value."))}, status=400
            )

        if value not in (ThreadVote.UPVOTE, ThreadVote.DOWNVOTE):
            return JsonResponse(
                {"success": False, "message": str(_("Invalid vote value."))}, status=400
            )

        existing = ThreadVote.objects.filter(
            reply=reply, voter=request.user
        ).first()

        if existing is None:
            ThreadVote.objects.create(reply=reply, voter=request.user, value=value)
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

        # Update cached counter on the reply
        ThreadReply.objects.filter(pk=reply.pk).update(
            votes_count=reply.votes_count + delta
        )
        reply.refresh_from_db(fields=["votes_count"])

        return JsonResponse(
            {
                "success": True,
                "votes_count": reply.votes_count,
            }
        )
