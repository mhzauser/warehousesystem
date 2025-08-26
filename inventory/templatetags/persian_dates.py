from django import template
from django.utils import timezone
from ..utils import gregorian_to_persian_str, gregorian_to_persian_datetime_str

register = template.Library()


@register.filter
def persian_date(value, format_str="%Y/%m/%d"):
    """
    Convert Gregorian date to Persian date string
    Usage: {{ object.created_at|persian_date:"%Y/%m/%d" }}
    """
    if value is None:
        return ""
    return gregorian_to_persian_str(value, format_str)


@register.filter
def persian_datetime(value, format_str="%Y/%m/%d %H:%M"):
    """
    Convert Gregorian datetime to Persian datetime string
    Usage: {{ object.created_at|persian_datetime:"%Y/%m/%d %H:%M" }}
    """
    if value is None:
        return ""
    return gregorian_to_persian_datetime_str(value, format_str)


@register.filter
def persian_date_only(value):
    """
    Convert to Persian date only (without time)
    Usage: {{ object.created_at|persian_date_only }}
    """
    if value is None:
        return ""
    return gregorian_to_persian_str(value, "%Y/%m/%d")


@register.filter
def persian_time_only(value):
    """
    Convert to Persian time only
    Usage: {{ object.created_at|persian_time_only }}
    """
    if value is None:
        return ""
    return gregorian_to_persian_datetime_str(value, "%H:%M")
