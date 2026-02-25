from django import forms
from django.utils.translation import gettext_lazy as _
from tech_articles.content.models import Course

class CourseForm(forms.ModelForm):
    """Form for creating and updating courses in the dashboard."""
    
    class Meta:
        model = Course
        fields = ["name", "url", "description", "thumbnail", "is_active"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "dashboard-input",
                "placeholder": _("Enter course name")
            }),
            "url": forms.URLInput(attrs={
                "class": "dashboard-input",
                "placeholder": _("https://example.com/course")
            }),
            "description": forms.Textarea(attrs={
                "class": "dashboard-input",
                "placeholder": _("Enter course description"),
                "rows": 4
            }),
            "is_active": forms.CheckboxInput(attrs={
                "class": "w-4 h-4 text-primary bg-surface-dark border-border-dark rounded focus:ring-primary"
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["thumbnail"].widget.attrs.update({"class": "dashboard-input"})
