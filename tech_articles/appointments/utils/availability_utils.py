import logging
from datetime import datetime, date, time, timedelta
from typing import List, Dict
from django.db.models import Q
from tech_articles.appointments.models import AvailabilityRule, AppointmentSlot

logger = logging.getLogger(__name__)

def get_available_blocks(start_date: date, end_date: date) -> List[Dict]:
    """
    Calculates available time ranges for a given date range.
    Logic:
    1. Start with potential ranges from VisibilityRules (recurring).
    2. Add manual blocks (AppointmentSlot with is_booked=False).
    3. Subtract actual bookings (AppointmentSlot with is_booked=True).
    4. Fragment/Shrink ranges based on subtractions.
    """
    available_ranges = []
    
    current_date = start_date
    while current_date <= end_date:
        day_ranges = _get_ranges_for_day(current_date)
        available_ranges.extend(day_ranges)
        current_date += timedelta(days=1)
        
    return available_ranges

def _get_ranges_for_day(target_date: date) -> List[Dict]:
    """
    Helper to calculate blocks for a specific day.
    """
    weekday_map = {0: 'mon', 1: 'tue', 2: 'wed', 3: 'thu', 4: 'fri', 5: 'sat', 6: 'sun'}
    day_code = weekday_map[target_date.weekday()]
    
    # 1. Base Potential Blocks (Rules)
    from django.utils import timezone
    potential_blocks = []
    rules = AvailabilityRule.objects.filter(weekday=day_code, is_active=True)
    for rule in rules:
        start_dt = timezone.make_aware(datetime.combine(target_date, rule.start_time))
        end_dt = timezone.make_aware(datetime.combine(target_date, rule.end_time))
        potential_blocks.append([start_dt, end_dt])
        
    # 2. Add Manual Blocks (is_booked=False)
    manual_blocks = AppointmentSlot.objects.filter(
        start_at__date=target_date,
        is_booked=False
    )
    for mb in manual_blocks:
        potential_blocks.append([mb.start_at, mb.end_at])
        
    # Merge overlapping potential blocks (Union) to start with normalized base
    base_blocks = _merge_ranges(potential_blocks)
    
    # 3. Get Bookings to subtract (is_booked=True)
    bookings = AppointmentSlot.objects.filter(
        start_at__date=target_date,
        is_booked=True
    ).order_by('start_at')
    
    # 4. Subtract Bookings from Base Blocks
    final_ranges = []
    for base_start, base_end in base_blocks:
        current_blocks = [[base_start, base_end]]
        
        for booking in bookings:
            new_current_blocks = []
            for b_start, b_end in current_blocks:
                # Check for overlap
                intersect_start = max(b_start, booking.start_at)
                intersect_end = min(b_end, booking.end_at)
                
                if intersect_start < intersect_end:
                    # There is an overlap, split the block
                    if b_start < intersect_start:
                        new_current_blocks.append([b_start, intersect_start])
                    if b_end > intersect_end:
                        new_current_blocks.append([intersect_end, b_end])
                else:
                    # No overlap, keep the block
                    new_current_blocks.append([b_start, b_end])
            current_blocks = new_current_blocks
            
        for fs, fe in current_blocks:
            final_ranges.append({
                'start_at': fs,
                'end_at': fe,
                'date': target_date.isoformat(),
                'startTime': fs.strftime("%H:%M"),
                'endTime': fe.strftime("%H:%M"),
                # We can't use a single Slot ID anymore for virtual blocks
                'id': f"range_{fs.isoformat()}_{fe.isoformat()}" 
            })
            
    return final_ranges

def _merge_ranges(ranges: List[List[datetime]]) -> List[List[datetime]]:
    """
    Standard range merging algorithm.
    """
    if not ranges:
        return []
    
    # Sort by start time
    sorted_ranges = sorted(ranges, key=lambda x: x[0])
    
    merged = [sorted_ranges[0]]
    for current in sorted_ranges[1:]:
        prev = merged[-1]
        
        if current[0] <= prev[1]:
            # Overlap, merge
            prev[1] = max(prev[1], current[1])
        else:
            merged.append(current)
            
    return merged
