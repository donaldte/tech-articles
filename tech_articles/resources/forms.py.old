"""Forms for media library management."""
from __future__ import annotations

from django import forms
from django.utils.translation import gettext_lazy as _

from .models import MediaFile, MediaFolder, MediaTag


class MediaFolderForm(forms.ModelForm):
    """Form for creating and editing media folders."""
    
    class Meta:
        model = MediaFolder
        fields = ["name", "parent", "description"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": _("Folder name"),
                }
            ),
            "parent": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-textarea",
                    "rows": 3,
                    "placeholder": _("Folder description (optional)"),
                }
            ),
        }


class MediaFileForm(forms.ModelForm):
    """Form for uploading and editing media files."""
    
    file = forms.FileField(
        label=_("File"),
        required=False,
        widget=forms.FileInput(
            attrs={
                "class": "form-file",
                "accept": "image/*,video/*,application/pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx",
            }
        ),
    )
    
    class Meta:
        model = MediaFile
        fields = ["title", "description", "alt_text", "folder", "tags", "access_level"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": _("File title"),
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-textarea",
                    "rows": 3,
                    "placeholder": _("File description (optional)"),
                }
            ),
            "alt_text": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": _("Alternative text for accessibility"),
                }
            ),
            "folder": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "tags": forms.SelectMultiple(
                attrs={
                    "class": "form-select",
                }
            ),
            "access_level": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
        }


class MediaFileMetadataForm(forms.ModelForm):
    """Form for editing media file metadata only."""
    
    class Meta:
        model = MediaFile
        fields = ["title", "description", "alt_text", "folder", "tags", "access_level"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": _("File title"),
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-textarea",
                    "rows": 3,
                    "placeholder": _("File description (optional)"),
                }
            ),
            "alt_text": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": _("Alternative text for accessibility"),
                }
            ),
            "folder": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "tags": forms.SelectMultiple(
                attrs={
                    "class": "form-select",
                }
            ),
            "access_level": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
        }


class MediaTagForm(forms.ModelForm):
    """Form for creating and editing media tags."""
    
    class Meta:
        model = MediaTag
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": _("Tag name"),
                }
            ),
        }


class BulkMediaUploadForm(forms.Form):
    """Form for bulk file upload."""
    
    files = forms.FileField(
        label=_("Files"),
        widget=forms.ClearableFileInput(
            attrs={
                "class": "form-file",
                "multiple": True,
                "accept": "image/*,video/*,application/pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx",
            }
        ),
    )
    folder = forms.ModelChoiceField(
        label=_("Folder"),
        queryset=MediaFolder.objects.all(),
        required=False,
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )
