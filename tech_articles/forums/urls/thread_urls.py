"""
Forum thread and reply URL patterns.
"""
from django.urls import path

from tech_articles.forums.views import (
    ForumThreadListView,
    ForumThreadDetailView,
    ForumThreadCreateView,
    ForumThreadUpdateView,
    ForumThreadDeleteView,
    ThreadReplyCreateView,
    ThreadReplyUpdateView,
    ThreadReplyDeleteView,
    ThreadReplyVoteView,
)

urlpatterns = [
    # Threads
    path(
        "<slug:category_slug>/threads/",
        ForumThreadListView.as_view(),
        name="thread_list",
    ),
    path(
        "<slug:category_slug>/threads/create/",
        ForumThreadCreateView.as_view(),
        name="thread_create",
    ),
    path(
        "<slug:category_slug>/threads/<uuid:pk>/",
        ForumThreadDetailView.as_view(),
        name="thread_detail",
    ),
    path(
        "<slug:category_slug>/threads/<uuid:pk>/edit/",
        ForumThreadUpdateView.as_view(),
        name="thread_update",
    ),
    path(
        "<slug:category_slug>/threads/<uuid:pk>/delete/",
        ForumThreadDeleteView.as_view(),
        name="thread_delete",
    ),

    # Replies
    path(
        "threads/<uuid:thread_pk>/replies/create/",
        ThreadReplyCreateView.as_view(),
        name="reply_create",
    ),
    path(
        "threads/replies/<uuid:pk>/edit/",
        ThreadReplyUpdateView.as_view(),
        name="reply_update",
    ),
    path(
        "threads/replies/<uuid:pk>/delete/",
        ThreadReplyDeleteView.as_view(),
        name="reply_delete",
    ),

    # Votes
    path(
        "threads/replies/<uuid:reply_pk>/vote/",
        ThreadReplyVoteView.as_view(),
        name="reply_vote",
    ),
]
