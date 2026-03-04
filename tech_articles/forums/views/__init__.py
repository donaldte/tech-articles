"""
Forums views module.
Exports all views from feature-specific modules.
"""
from .public_views import ForumCategoryPublicListView
from .category_views import (
    ForumCategoryListView,
    ForumCategoryCreateView,
    ForumCategoryUpdateView,
    ForumCategoryDeleteView,
)
from .thread_views import (
    ForumThreadListView,
    ForumThreadDetailView,
    ForumThreadCreateView,
    ForumThreadUpdateView,
    ForumThreadDeleteView,
    ThreadReplyCreateView,
    ThreadReplyUpdateView,
    ThreadReplyDeleteView,
)
from .access_views import (
    ForumGroupAccessListView,
    GroupAccessRequestView,
    ForumGroupAccessApproveView,
    ForumGroupAccessRejectView,
)
from .vote_views import ThreadReplyVoteView

__all__ = [
    # Public
    "ForumCategoryPublicListView",
    # Admin — categories
    "ForumCategoryListView",
    "ForumCategoryCreateView",
    "ForumCategoryUpdateView",
    "ForumCategoryDeleteView",
    # Threads
    "ForumThreadListView",
    "ForumThreadDetailView",
    "ForumThreadCreateView",
    "ForumThreadUpdateView",
    "ForumThreadDeleteView",
    # Replies
    "ThreadReplyCreateView",
    "ThreadReplyUpdateView",
    "ThreadReplyDeleteView",
    # Votes
    "ThreadReplyVoteView",
    # Access
    "ForumGroupAccessListView",
    "GroupAccessRequestView",
    "ForumGroupAccessApproveView",
    "ForumGroupAccessRejectView",
]
