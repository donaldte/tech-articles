from django.urls import path
from . import views

app_name = "appointments"

urlpatterns = [
    path('availability/', views.AvailabilitySettingsView.as_view(), name='availability_settings'),
    path('api/config/', views.SaveConfigurationView.as_view(), name='save_config'),
    path('api/rules/', views.AvailabilityRuleAPIView.as_view(), name='availability_rules'),
    path('api/exceptions/', views.ExceptionDateAPIView.as_view(), name='exception_dates'),
]
