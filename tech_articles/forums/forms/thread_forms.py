"""
Forum thread and reply forms.
"""

from django import forms
from django.utils.translation import gettext_lazy as _

from tech_articles.forums.models import ForumThread, ThreadReply, ThreadAttachment


class ForumThreadForm(forms.ModelForm):
    """Form for creating and editing forum threads."""

    class Meta:
        model = ForumThread
        fields = ["title", "content"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "dashboard-input",
                    "placeholder": _("Thread title"),
                }
            ),
            "content": forms.Textarea(
                attrs={
                    "class": "dashboard-textarea",
                    "rows": 10,
                    "placeholder": _("Describe your issue or question (Markdown supported)"),
                }
            ),
        }


class ThreadReplyForm(forms.ModelForm):
    """Form for writing a reply to a thread."""

    class Meta:
        model = ThreadReply
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(
                attrs={
                    "class": "dashboard-textarea",
                    "rows": 6,
                    "placeholder": _("Write your reply (Markdown supported)"),
                }
            ),
        }


class ThreadAttachmentForm(forms.ModelForm):
    """Form for uploading an attachment to a thread or reply."""

    class Meta:
        model = ThreadAttachment
        fields = ["file"]
        widgets = {
            "file": forms.ClearableFileInput(attrs={"class": "dashboard-file-input"}),
        }
