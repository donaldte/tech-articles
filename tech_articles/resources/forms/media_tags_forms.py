"""
Media tags forms for dashboard CRUD operations.
"""
from django import forms
from django.utils.translation import gettext_lazy as _

from tech_articles.resources.models import MediaTag


class MediaTagForm(forms.ModelForm):
    """Form for creating and editing media tags."""
    
    class Meta:
        model = MediaTag
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "dashboard-input",
                    "placeholder": _("Tag name"),
                    "autocomplete": "off",
                }
            ),
        }
    
    def clean_name(self):
        name = self.cleaned_data.get("name", "").strip()
        if not name:
            raise forms.ValidationError(_("Tag name is required."))
        
        # Check for duplicates excluding current instance
        qs = MediaTag.objects.filter(name__iexact=name)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(_("A tag with this name already exists."))
        
        return name
