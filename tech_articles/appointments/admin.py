from django.contrib import admin
from .models import (
    AppointmentType,
    AvailabilityRule,
    AppointmentSlot,
    Appointment,
    TimeSlotConfiguration,
    ExceptionDate,
)


@admin.register(TimeSlotConfiguration)
class TimeSlotConfigurationAdmin(admin.ModelAdmin):
    list_display = ['slot_duration_minutes', 'max_appointments_per_slot', 'timezone', 'minimum_booking_hours', 'is_active', 'created_at']
    list_filter = ['is_active', 'timezone']
    search_fields = ['timezone']


@admin.register(AvailabilityRule)
class AvailabilityRuleAdmin(admin.ModelAdmin):
    list_display = ['weekday', 'start_time', 'end_time', 'is_recurring', 'is_active', 'created_at']
    list_filter = ['weekday', 'is_recurring', 'is_active']
    ordering = ['weekday', 'start_time']


@admin.register(ExceptionDate)
class ExceptionDateAdmin(admin.ModelAdmin):
    list_display = ['date', 'reason', 'is_active', 'created_at']
    list_filter = ['is_active', 'date']
    search_fields = ['reason']
    ordering = ['-date']


@admin.register(AppointmentType)
class AppointmentTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'base_hourly_rate', 'currency', 'is_active', 'created_at']
    list_filter = ['is_active', 'currency']
    search_fields = ['name', 'description']


@admin.register(AppointmentSlot)
class AppointmentSlotAdmin(admin.ModelAdmin):
    list_display = ['start_at', 'end_at', 'is_booked', 'booked_at']
    list_filter = ['is_booked']
    ordering = ['-start_at']


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'appointment_type', 'status', 'payment_status', 'created_at']
    list_filter = ['status', 'payment_status', 'created_at']
    search_fields = ['user__email', 'notes']
    ordering = ['-created_at']
