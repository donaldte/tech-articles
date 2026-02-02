from django.test import TestCase
from django.utils import timezone
from datetime import time, date, timedelta

from .models import (
    TimeSlotConfiguration,
    AvailabilityRule,
    ExceptionDate,
    AppointmentType,
    AppointmentSlot,
)


class TimeSlotConfigurationModelTest(TestCase):
    """Tests for TimeSlotConfiguration model."""

    def test_create_configuration(self):
        """Test creating a time slot configuration."""
        config = TimeSlotConfiguration.objects.create(
            slot_duration_minutes=60,
            max_appointments_per_slot=2,
            timezone='Europe/Paris',
            minimum_booking_hours=24,
        )
        self.assertEqual(config.slot_duration_minutes, 60)
        self.assertEqual(config.max_appointments_per_slot, 2)
        self.assertEqual(config.timezone, 'Europe/Paris')
        self.assertEqual(config.minimum_booking_hours, 24)
        self.assertTrue(config.is_active)

    def test_configuration_str(self):
        """Test string representation of configuration."""
        config = TimeSlotConfiguration.objects.create(
            slot_duration_minutes=30,
            max_appointments_per_slot=1,
        )
        expected = "Config: 30min slots, max 1 per slot"
        self.assertEqual(str(config), expected)


class AvailabilityRuleModelTest(TestCase):
    """Tests for AvailabilityRule model."""

    def test_create_availability_rule(self):
        """Test creating an availability rule."""
        rule = AvailabilityRule.objects.create(
            weekday='mon',
            start_time=time(9, 0),
            end_time=time(17, 0),
            is_recurring=True,
        )
        self.assertEqual(rule.weekday, 'mon')
        self.assertEqual(rule.start_time, time(9, 0))
        self.assertEqual(rule.end_time, time(17, 0))
        self.assertTrue(rule.is_recurring)
        self.assertTrue(rule.is_active)

    def test_availability_rule_str(self):
        """Test string representation of availability rule."""
        rule = AvailabilityRule.objects.create(
            weekday='tue',
            start_time=time(10, 0),
            end_time=time(18, 0),
        )
        expected = "tue 10:00:00-18:00:00"
        self.assertEqual(str(rule), expected)


class ExceptionDateModelTest(TestCase):
    """Tests for ExceptionDate model."""

    def test_create_exception_date(self):
        """Test creating an exception date."""
        exception = ExceptionDate.objects.create(
            date=date.today() + timedelta(days=7),
            reason='Holiday',
        )
        self.assertEqual(exception.reason, 'Holiday')
        self.assertTrue(exception.is_active)

    def test_exception_date_str(self):
        """Test string representation of exception date."""
        test_date = date(2026, 12, 25)
        exception = ExceptionDate.objects.create(
            date=test_date,
            reason='Christmas',
        )
        expected = f"{test_date} - Christmas"
        self.assertEqual(str(exception), expected)

    def test_exception_date_unique_constraint(self):
        """Test that duplicate dates are not allowed."""
        test_date = date.today()
        ExceptionDate.objects.create(date=test_date, reason='First')
        
        # Attempting to create another exception with the same date should fail
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            ExceptionDate.objects.create(date=test_date, reason='Second')


class AppointmentSlotModelTest(TestCase):
    """Tests for AppointmentSlot model."""

    def test_create_appointment_slot(self):
        """Test creating an appointment slot."""
        start = timezone.now() + timedelta(days=1)
        end = start + timedelta(hours=1)
        
        slot = AppointmentSlot.objects.create(
            start_at=start,
            end_at=end,
        )
        self.assertEqual(slot.start_at, start)
        self.assertEqual(slot.end_at, end)
        self.assertFalse(slot.is_booked)
        self.assertIsNone(slot.booked_at)

