import logging
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _, gettext
from django.views import View
from django.views.generic import ListView
from tech_articles.content.forms import CourseForm
from tech_articles.content.models import Course
from tech_articles.utils.mixins import AdminRequiredMixin

logger = logging.getLogger(__name__)

class CourseDashboardListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    """List all courses in the dashboard with search."""
    model = Course
    template_name = "tech-articles/dashboard/pages/content/courses/list.html"
    context_object_name = "courses"
    paginate_by = 10
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get("search", "").strip()
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search"] = self.request.GET.get("search", "")
        context["total_count"] = Course.objects.count()
        context["active_count"] = Course.objects.filter(is_active=True).count()
        context["form"] = CourseForm()
        return context

class CourseCreateAPIView(LoginRequiredMixin, AdminRequiredMixin, View):
    """API view to create a new course via AJAX."""
    def post(self, request):
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save()
            return JsonResponse({
                "success": True,
                "message": gettext('Course "%(name)s" created successfully.') % {"name": course.name}
            })
        errors = {field: errors[0] for field, errors in form.errors.items()}
        return JsonResponse({
            "success": False,
            "message": gettext("Please correct the errors below."),
            "errors": errors
        }, status=400)

class CourseUpdateAPIView(LoginRequiredMixin, AdminRequiredMixin, View):
    """API view to update an existing course via AJAX."""
    def post(self, request, pk):
        course = get_object_or_404(Course, pk=pk)
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            return JsonResponse({
                "success": True,
                "message": gettext('Course "%(name)s" updated successfully.') % {"name": course.name}
            })
        errors = {field: errors[0] for field, errors in form.errors.items()}
        return JsonResponse({
            "success": False,
            "message": gettext("Please correct the errors below."),
            "errors": errors
        }, status=400)

class CourseDeleteAPIView(LoginRequiredMixin, AdminRequiredMixin, View):
    """API view to delete a course via AJAX."""
    def post(self, request, pk):
        course = get_object_or_404(Course, pk=pk)
        name = course.name
        course.delete()
        return JsonResponse({
            "success": True,
            "message": gettext('Course "%(name)s" deleted successfully.') % {"name": name}
        })
