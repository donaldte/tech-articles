"""
Course URL patterns for dashboard CRUD operations.
"""

from django.urls import path
from ..views import (
    CourseDashboardListView,
    CourseCreateAPIView,
    CourseUpdateAPIView,
    CourseDeleteAPIView,
)

urlpatterns = [
    path("dashboard/courses/", CourseDashboardListView.as_view(), name="courses_dashboard_list"),
    path("dashboard/courses/api/create/", CourseCreateAPIView.as_view(), name="courses_api_create"),
    path("dashboard/courses/<uuid:pk>/api/update/", CourseUpdateAPIView.as_view(), name="courses_api_update"),
    path("dashboard/courses/<uuid:pk>/api/delete/", CourseDeleteAPIView.as_view(), name="courses_api_delete"),
]
