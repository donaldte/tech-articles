"""
Course URL patterns for dashboard CRUD operations.
"""

from django.urls import path
from ..views import (
    CourseDashboardListView,
    CourseCreateAPIView,
    CourseUpdateAPIView,
    CourseDeleteAPIView,
    CourseTagDashboardListView,
    CourseTagCreateAPIView,
    CourseTagUpdateAPIView,
    CourseTagDeleteAPIView,
)

urlpatterns = [
    # Courses
    path("dashboard/courses/", CourseDashboardListView.as_view(), name="courses_dashboard_list"),
    path("dashboard/courses/api/create/", CourseCreateAPIView.as_view(), name="courses_api_create"),
    path("dashboard/courses/<uuid:pk>/api/update/", CourseUpdateAPIView.as_view(), name="courses_api_update"),
    path("dashboard/courses/<uuid:pk>/api/delete/", CourseDeleteAPIView.as_view(), name="courses_api_delete"),

    # Course Tags
    path("dashboard/courses/tags/", CourseTagDashboardListView.as_view(), name="course_tags_dashboard_list"),
    path("dashboard/courses/tags/api/create/", CourseTagCreateAPIView.as_view(), name="course_tags_api_create"),
    path("dashboard/courses/tags/<uuid:pk>/api/update/", CourseTagUpdateAPIView.as_view(), name="course_tags_api_update"),
    path("dashboard/courses/tags/<uuid:pk>/api/delete/", CourseTagDeleteAPIView.as_view(), name="course_tags_api_delete"),
]
