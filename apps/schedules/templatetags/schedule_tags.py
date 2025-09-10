# apps/schedules/templatetags/schedule_tags.py
from django import template

register = template.Library()

@register.filter
def session_color(session):
    if session.trainer_approved:
        return 'bg-green-500'
    elif not session.trainer_approved:
        return 'bg-yellow-500'
    return 'bg-gray-400'

@register.filter
def session_status(session):
    if session.trainer_approved:
        return 'Approved'
    elif not session.trainer_approved:
        return 'Pending'
    return 'Unknown'

@register.filter
def format_hour_ampm(hour):
    suffix = "AM" if hour < 12 else "PM"
    display = hour % 12 or 12
    return f"{display:02d}:00 {suffix}"

