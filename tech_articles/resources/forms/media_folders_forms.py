"""
Media folders forms for dashboard CRUD operations.
"""
from django import forms
from django.utils.translation import gettext_lazy as _

from tech_articles.resources.models import MediaFolder


class MediaFolderForm(forms.ModelForm):
    """Form for creating and editing media folders."""
    
    class Meta:
        model = MediaFolder
        fields = ["name", "parent", "description"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "dashboard-input",
                    "placeholder": _("Folder name"),
                    "autocomplete": "off",
                }
            ),
            "parent": forms.Select(
                attrs={
                    "class": "dashboard-select",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "dashboard-textarea",
                    "rows": 3,
                    "placeholder": _("Optional description for this folder"),
                }
            ),
        }
    
    def clean_name(self):
        name = self.cleaned_data.get("name", "").strip()
        if not name:
            raise forms.ValidationError(_("Folder name is required."))
        
        # Check for duplicates excluding current instance
        parent = self.cleaned_data.get("parent")
        qs = MediaFolder.objects.filter(name__iexact=name, parent=parent)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(_("A folder with this name already exists in this location."))
        
        return name
