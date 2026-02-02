# Time Slot Configuration System

## Overview
The time slot configuration system provides a comprehensive interface for managing appointment availability with a visual weekly calendar, exception handling, and flexible scheduling options.

## Features

### 1. Global Configuration
Configure system-wide settings for appointment scheduling:
- **Slot Duration**: Define the duration of each time slot in minutes (e.g., 15, 30, 60 minutes)
- **Max Appointments per Slot**: Set the maximum number of appointments allowed in a single time slot
- **Timezone**: Select the timezone for availability management (supports UTC, America/New_York, Europe/Paris, etc.)
- **Minimum Booking Delay**: Set how many hours in advance appointments must be booked

### 2. Weekly Calendar Interface
An interactive calendar view displaying a full week:
- Visual 24-hour grid for all 7 days
- Color-coded availability display (green for available slots)
- Horizontal scrolling for mobile responsiveness
- Real-time updates when adding/removing availability rules

### 3. Availability Rules
Define when appointments can be scheduled:
- **Day-specific schedules**: Set different hours for each day of the week
- **Time ranges**: Define start and end times for each availability period
- **Recurring patterns**: Mark rules as recurring for weekly repetition
- **Active/Inactive toggle**: Temporarily disable rules without deleting them

### 4. Exception Management
Block specific dates when appointments should not be available:
- Add blocked dates with reasons (holidays, vacations, etc.)
- Date picker interface for easy selection
- Unique date constraint (prevents duplicate exceptions)
- Easy deletion of exceptions

### 5. Real-time AJAX Operations
All changes are saved immediately without page refresh:
- Configuration updates
- Adding/removing availability rules
- Managing exception dates
- Visual feedback with success/error notifications

## Usage

### Accessing the Page
Navigate to: **Dashboard → Appointments → Availability Settings**

### Setting Up Weekly Schedule
1. Click "Add Time Slot" button
2. Select day of week (Monday-Sunday)
3. Enter start and end times
4. Check "Recurring weekly" for rules that repeat
5. Click "Add" to save

### Adding Exception Dates
1. Click "Add Exception" button
2. Select a date from the date picker
3. Enter a reason (optional)
4. Click "Add" to save

### Modifying Configuration
1. Update any field in the Global Configuration section
2. Click "Save Configuration"
3. Changes apply immediately

## Technical Details

### Models
- **TimeSlotConfiguration**: Global settings (singleton pattern)
- **AvailabilityRule**: Weekly recurring availability patterns
- **ExceptionDate**: Blocked dates with reasons

### API Endpoints
- `POST /dashboard/appointments/api/config/` - Save configuration
- `GET/POST/DELETE /dashboard/appointments/api/rules/` - Manage availability rules
- `GET/POST/DELETE /dashboard/appointments/api/exceptions/` - Manage exception dates

### Internationalization
The system fully supports multiple languages:
- All UI text uses Django's `gettext_lazy`
- JavaScript messages are translated via template-embedded i18n object
- Compatible with French, English, and other languages

### Security
- All endpoints require authentication and admin privileges
- CSRF protection on all POST/DELETE requests
- Input validation through Django forms
- Specific exception handling to prevent information leakage

## Future Enhancements
Possible improvements for future versions:
- Drag-and-drop time slot creation on calendar
- Bulk import/export of availability rules
- Copy availability from one day to another
- Time slot templates for quick setup
- Visual indicators for overlapping rules
