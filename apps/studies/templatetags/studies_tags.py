"""Template tags for studies app."""
from django import template

register = template.Library()


@register.filter
def submission_number_display(value):
    """Return submission number or 'Pending' (never None or 'None')."""
    if value is None:
        return 'Pending'
    s = str(value).strip()
    if not s or s.lower() == 'none':
        return 'Pending'
    return value
