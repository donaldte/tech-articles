"""
Media files forms for dashboard CRUD operations.
"""
from django import forms
from django.utils.translation import gettext_lazy as _

from tech_articles.resources.models import MediaFile


class MediaFileForm(forms.ModelForm):
    """Form for uploading and editing media files."""
    
    file = forms.FileField(
        label=_("File"),
        required=False,
        widget=forms.FileInput(
            attrs={
                "class": "dashboard-input",
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
                    "class": "dashboard-input",
                    "placeholder": _("File title"),
                    "autocomplete": "off",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "dashboard-textarea",
                    "rows": 3,
                    "placeholder": _("File description (optional)"),
                }
            ),
            "alt_text": forms.TextInput(
                attrs={
                    "class": "dashboard-input",
                    "placeholder": _("Alternative text for accessibility"),
                    "autocomplete": "off",
                }
            ),
            "folder": forms.Select(
                attrs={
                    "class": "dashboard-select",
                }
            ),
            "tags": forms.SelectMultiple(
                attrs={
                    "class": "dashboard-select",
                }
            ),
            "access_level": forms.Select(
                attrs={
                    "class": "dashboard-select",
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
                    "class": "dashboard-input",
                    "placeholder": _("File title"),
                    "autocomplete": "off",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "dashboard-textarea",
                    "rows": 3,
                    "placeholder": _("File description (optional)"),
                }
            ),
            "alt_text": forms.TextInput(
                attrs={
                    "class": "dashboard-input",
                    "placeholder": _("Alternative text for accessibility"),
                    "autocomplete": "off",
                }
            ),
            "folder": forms.Select(
                attrs={
                    "class": "dashboard-select",
                }
            ),
            "tags": forms.SelectMultiple(
                attrs={
                    "class": "dashboard-select",
                }
            ),
            "access_level": forms.Select(
                attrs={
                    "class": "dashboard-select",
                }
            ),
        }


class BulkMediaUploadForm(forms.Form):
    """Form for bulk file upload."""
    
    files = forms.FileField(
        label=_("Files"),
        widget=forms.ClearableFileInput(
            attrs={
                "class": "dashboard-input",
                "multiple": True,
                "accept": "image/*,video/*,application/pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx",
            }
        ),
    )
    folder = forms.ModelChoiceField(
        label=_("Folder"),
        queryset=None,  # Will be set in __init__
        required=False,
        widget=forms.Select(
            attrs={
                "class": "dashboard-select",
            }
        ),
    )
    
    def __init__(self, *args, **kwargs):
        from tech_articles.resources.models import MediaFolder
        super().__init__(*args, **kwargs)
        self.fields["folder"].queryset = MediaFolder.objects.all().order_by("name")
