"""
Content views module.
Exports all views from feature-specific modules.
"""
from .categories_views import (
    CategoryListView,
    CategoryCreateView,
    CategoryUpdateView,
    CategoryDeleteView,
)
from .tags_views import (
    TagListView,
    TagCreateView,
    TagUpdateView,
    TagDeleteView,
)

__all__ = [
    # Categories
    "CategoryListView",
    "CategoryCreateView",
    "CategoryUpdateView",
    "CategoryDeleteView",
    # Tags
    "TagListView",
    "TagCreateView",
    "TagUpdateView",
    "TagDeleteView",
]
