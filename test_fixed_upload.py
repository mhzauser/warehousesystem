#!/usr/bin/env python3
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ironwarehouse.settings')
django.setup()

from inventory.excel_utils import import_stock_in_excel, import_stock_out_excel
from django.contrib.auth.models import User

# Get a user for testing
try:
    user = User.objects.first()
    if not user:
        print("No users found in database")
        sys.exit(1)
except Exception as e:
    print(f"Error getting user: {e}")
    sys.exit(1)

print(f"Testing fixed upload functions with persiancalender.xlsx")
print("=" * 70)

# Test 1: Stock In import (should now work with unified format)
print("\n1. Testing import_stock_in_excel (FIXED - should work now):")
try:
    results = import_stock_in_excel('persiancalender.xlsx', user)
    print("Results:")
    if results.get('success'):
        print("✅ Success:")
        for msg in results['success']:
            print(f"  {msg}")
    if results.get('errors'):
        print("❌ Errors:")
        for msg in results['errors']:
            print(f"  {msg}")
except Exception as e:
    print(f"❌ Exception: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Stock Out import (should now work with unified format)
print("\n2. Testing import_stock_out_excel (FIXED - should work now):")
try:
    results = import_stock_out_excel('persiancalender.xlsx', user)
    print("Results:")
    if results.get('success'):
        print("✅ Success:")
        for msg in results['success']:
            print(f"  {msg}")
    if results.get('errors'):
        print("❌ Errors:")
        for msg in results['errors']:
            print(f"  {msg}")
except Exception as e:
    print(f"❌ Exception: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("Test completed!")
