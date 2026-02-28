from django.contrib import admin
from .models import (
    AppointmentSettings,
    AppointmentType,
    AvailabilityRule,
    AppointmentSlot,
    Appointment,
)

@admin.register(AppointmentSettings)
class AppointmentSettingsAdmin(admin.ModelAdmin):
    list_display = ("timezone",)


@admin.register(AppointmentType)
class AppointmentTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "base_hourly_rate", "currency", "created_at")
    list_filter = ("is_active", "currency")
    search_fields = ("name", "description")


@admin.register(AvailabilityRule)
class AvailabilityRuleAdmin(admin.ModelAdmin):
    list_display = ("weekday", "start_time", "end_time", "is_active")
    list_filter = ("weekday", "is_active")


@admin.register(AppointmentSlot)
class AppointmentSlotAdmin(admin.ModelAdmin):
    list_display = ("start_at", "end_at", "is_booked", "booked_at")
    list_filter = ("is_booked",)
    search_fields = ("start_at", "end_at")


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("user", "appointment_type", "status", "payment_status", "total_amount", "created_at")
    list_filter = ("status", "payment_status", "provider", "appointment_type")
    search_fields = ("user__email", "user__username", "provider_payment_id")
    raw_id_fields = ("user", "slot", "appointment_type")
