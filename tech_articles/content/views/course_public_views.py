from django.views.generic import ListView
from tech_articles.content.models import Course

class CourseListView(ListView):
    """
    Public view for listing all active courses.
    Reuses the articles listing layout but without dynamic JS loading for simplicity.
    """
    model = Course
    template_name = "tech-articles/home/pages/courses/courses_list.html"
    context_object_name = "courses"
    paginate_by = 12

    def get_queryset(self):
        return Course.objects.filter(is_active=True).order_by("-created_at")
