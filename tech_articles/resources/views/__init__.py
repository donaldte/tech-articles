"""
Resources views module.
"""
from .resource_views import (
    ResourceListView,
    ResourceCreateView,
    ResourceUpdateView,
    ResourceDeleteView,
    ResourceReadView,
    ResourceReadUrlApiView,
)

__all__ = [
    "ResourceListView",
    "ResourceCreateView",
    "ResourceUpdateView",
    "ResourceDeleteView",
    "ResourceReadView",
    "ResourceReadUrlApiView",
]
