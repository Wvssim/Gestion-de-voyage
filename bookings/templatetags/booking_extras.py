from django import template
from django.utils import timezone

register = template.Library()

@register.filter
def days_until(value):
    """Returns the number of days until the given date"""
    if not value:
        return ""
    
    today = timezone.now().date()
    delta = value - today
    
    if delta.days < 0:
        return "Past"
    elif delta.days == 0:
        return "Today"
    elif delta.days == 1:
        return "Tomorrow"
    else:
        return f"{delta.days} days"

@register.filter
def format_price(value):
    """Format price with two decimal places and currency symbol"""
    if value is None:
        return ""
    return f"${value:.2f}"

@register.filter
def status_badge(value):
    """Return Bootstrap badge class based on booking status"""
    badges = {
        'confirmed': 'bg-success',
        'pending': 'bg-warning',
        'cancelled': 'bg-danger',
    }
    return badges.get(value, 'bg-secondary')
