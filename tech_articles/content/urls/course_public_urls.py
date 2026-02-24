from django.urls import path
from tech_articles.content.views.course_public_views import CourseListView

urlpatterns = [
    path("courses/", CourseListView.as_view(), name="home_courses_list"),
]
