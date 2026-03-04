"""
Forum group access forms (subscription-based request + one-time purchase).
"""

from django import forms
from django.utils.translation import gettext_lazy as _

from tech_articles.forums.models import ForumGroupAccess


class GroupAccessRequestForm(forms.ModelForm):
    """
    Form used when a premium subscriber requests access to a group.
    The category is injected from the view; only a confirmation is needed.
    """

    class Meta:
        model = ForumGroupAccess
        fields = []  # category and user are set in the view

    confirm = forms.BooleanField(
        label=_("I confirm I want to request access to this group"),
        required=True,
        widget=forms.CheckboxInput(attrs={"class": "dashboard-checkbox"}),
    )
