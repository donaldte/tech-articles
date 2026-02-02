# Generated manually

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TimeSlotConfiguration',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('slot_duration_minutes', models.PositiveIntegerField(default=60, help_text='Default duration for each time slot in minutes', verbose_name='slot duration (minutes)')),
                ('max_appointments_per_slot', models.PositiveIntegerField(default=1, help_text='Maximum number of appointments allowed per time slot', verbose_name='max appointments per slot')),
                ('timezone', models.CharField(default='UTC', help_text="Timezone for availability management (e.g., 'America/New_York', 'Europe/Paris')", max_length=50, verbose_name='timezone')),
                ('minimum_booking_hours', models.PositiveIntegerField(default=24, help_text='Minimum hours in advance required for booking', verbose_name='minimum booking delay (hours)')),
                ('is_active', models.BooleanField(default=True, help_text='Whether this configuration is active', verbose_name='is active')),
            ],
            options={
                'verbose_name': 'time slot configuration',
                'verbose_name_plural': 'time slot configurations',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddField(
            model_name='availabilityrule',
            name='is_recurring',
            field=models.BooleanField(default=True, help_text='Whether this rule repeats every week', verbose_name='is recurring'),
        ),
        migrations.CreateModel(
            name='ExceptionDate',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('date', models.DateField(db_index=True, help_text='Date to block', unique=True, verbose_name='date')),
                ('reason', models.CharField(blank=True, default='', help_text='Reason for blocking (e.g., holiday, absence)', max_length=200, verbose_name='reason')),
                ('is_active', models.BooleanField(db_index=True, default=True, help_text='Whether this exception is active', verbose_name='is active')),
            ],
            options={
                'verbose_name': 'exception date',
                'verbose_name_plural': 'exception dates',
                'ordering': ['date'],
            },
        ),
    ]
