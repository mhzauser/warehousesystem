import jdatetime
from datetime import datetime, date
from django.utils import timezone
import pandas as pd


def parse_persian_date(date_str):
    """
    Parse Persian date string to Gregorian date
    Supports formats like: 1404-01-26, 1404/01/26, 1404.01.26
    """
    if not date_str or pd.isna(date_str):
        return None
    
    try:
        # Convert to string if it's not already
        date_str = str(date_str).strip()
        
        # Handle different separators
        if '-' in date_str:
            parts = date_str.split('-')
        elif '/' in date_str:
            parts = date_str.split('/')
        elif '.' in date_str:
            parts = date_str.split('.')
        else:
            return None
        
        if len(parts) != 3:
            return None
        
        year, month, day = map(int, parts)
        
        # Check if it's a Persian date (year > 1400 for modern Persian dates)
        if year > 1400:
            # Convert Persian to Gregorian
            persian_date = jdatetime.date(year, month, day)
            return persian_date.togregorian()
        elif 1900 <= year <= 2100:
            # Assume it's already Gregorian
            return date(year, month, day)
        else:
            # Try as Persian date anyway (for older dates)
            try:
                persian_date = jdatetime.date(year, month, day)
                return persian_date.togregorian()
            except:
                return None
            
    except (ValueError, TypeError):
        return None


def to_persian_date(gregorian_date):
    """
    Convert Gregorian date to Persian (Shamsi) date
    """
    if isinstance(gregorian_date, datetime):
        return jdatetime.datetime.fromgregorian(datetime=gregorian_date)
    elif isinstance(gregorian_date, date):
        return jdatetime.date.fromgregorian(date=gregorian_date)
    return gregorian_date


def to_persian_datetime(gregorian_datetime):
    """
    Convert Gregorian datetime to Persian (Shamsi) datetime
    """
    if isinstance(gregorian_datetime, datetime):
        return jdatetime.datetime.fromgregorian(datetime=gregorian_datetime)
    return gregorian_datetime


def format_persian_date(persian_date, format_str="%Y/%m/%d"):
    """
    Format Persian date to string
    """
    if hasattr(persian_date, 'strftime'):
        return persian_date.strftime(format_str)
    return str(persian_date)


def format_persian_datetime(persian_datetime, format_str="%Y/%m/%d %H:%M"):
    """
    Format Persian datetime to string
    """
    if hasattr(persian_datetime, 'strftime'):
        return persian_datetime.strftime(format_str)
    return str(persian_datetime)


def get_current_persian_date():
    """
    Get current date in Persian calendar
    """
    return jdatetime.date.today()


def get_current_persian_datetime():
    """
    Get current datetime in Persian calendar
    """
    return jdatetime.datetime.now()


def gregorian_to_persian_str(gregorian_date, format_str="%Y/%m/%d"):
    """
    Convert Gregorian date to Persian date string
    """
    persian_date = to_persian_date(gregorian_date)
    return format_persian_date(persian_date, format_str)


def gregorian_to_persian_datetime_str(gregorian_datetime, format_str="%Y/%m/%d %H:%M"):
    """
    Convert Gregorian datetime to Persian datetime string
    """
    persian_datetime = to_persian_datetime(gregorian_datetime)
    return format_persian_datetime(persian_datetime, format_str)
