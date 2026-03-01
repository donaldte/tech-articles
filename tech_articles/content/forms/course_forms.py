from django import forms
from django.utils.translation import gettext_lazy as _
from tech_articles.content.models import Course, CourseTag

class CourseForm(forms.ModelForm):
    """Form for creating and updating courses in the dashboard."""

    class Meta:
        model = Course
        fields = ["name", "url", "description", "thumbnail", "language", "tags", "is_active"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "dashboard-input w-full",
                "placeholder": _("Enter course name")
            }),
            "url": forms.URLInput(attrs={
                "class": "dashboard-input w-full",
                "placeholder": _("https://example.com/course")
            }),
            "description": forms.Textarea(attrs={
                "class": "dashboard-input w-full",
                "placeholder": _("Enter course description"),
                "rows": 4
            }),
            "language": forms.Select(attrs={
                "class": "dashboard-input w-full"
            }),
            "tags": forms.SelectMultiple(attrs={
                "class": "dashboard-input w-full"
            }),
            "is_active": forms.CheckboxInput(attrs={
                "class": "w-4 h-4 text-primary bg-surface-dark border-border-dark rounded focus:ring-primary w-full"
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["thumbnail"].widget.attrs.update({"class": "dashboard-input w-full"})

class CourseTagForm(forms.ModelForm):
    """Form for creating and updating course tags."""

    class Meta:
        model = CourseTag
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "dashboard-input w-full",
                "placeholder": _("Enter tag name"),
                "autocomplete": "off",
            }),
        }

    def clean_name(self):
        name = self.cleaned_data.get("name", "").strip()
        if not name:
            raise forms.ValidationError(_("Tag name is required."))

        qs = CourseTag.objects.filter(name__iexact=name)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(_("A course tag with this name already exists."))

        return name


