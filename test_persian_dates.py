#!/usr/bin/env python3
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ironwarehouse.settings')
django.setup()

from inventory.utils import parse_persian_date

# Test Persian date parsing
test_dates = [
    "1404-01-26",  # Persian date with dash
    "1404/01/27",  # Persian date with slash
    "1404.01.28",  # Persian date with dot
    "2024-01-15",  # Gregorian date
    "1404-02-30",  # Invalid Persian date
    "invalid",      # Invalid format
    "",            # Empty string
    None           # None value
]

print("Testing Persian date parsing:")
print("=" * 50)

for date_str in test_dates:
    result = parse_persian_date(date_str)
    print(f"Input: {repr(date_str)} -> Result: {result}")

print("\n" + "=" * 50)
print("Test completed!")
