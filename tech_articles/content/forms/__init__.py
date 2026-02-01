"""
Content forms module.
Exports all forms from the package.
"""
from .categories_forms import CategoryForm
from .tags_forms import TagForm

__all__ = [
    "CategoryForm",
    "TagForm",
]
