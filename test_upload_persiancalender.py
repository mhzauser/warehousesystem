#!/usr/bin/env python3
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ironwarehouse.settings')
django.setup()

from inventory.excel_utils import import_unified_stock_excel, import_stock_in_excel, import_stock_out_excel
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

print(f"Testing persiancalender.xlsx upload with user: {user.username}")
print("=" * 70)

# First, let's examine the file
import pandas as pd
try:
    df = pd.read_excel('persiancalender.xlsx')
    print("File structure:")
    print(f"Columns: {df.columns.tolist()}")
    print(f"Shape: {df.shape}")
    print(f"Data types: {df.dtypes}")
    
    print("\nFirst few rows:")
    print(df.head())
    
except Exception as e:
    print(f"❌ Error reading file: {e}")
    sys.exit(1)

print("\n" + "=" * 50)
print("Testing different import functions:")
print("=" * 50)

# Test 1: Unified import (should work)
print("\n1. Testing import_unified_stock_excel (CORRECT function):")
try:
    results = import_unified_stock_excel('persiancalender.xlsx', user)
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

# Test 2: Stock In import (should fail - wrong format)
print("\n2. Testing import_stock_in_excel (WRONG function - should fail):")
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

# Test 3: Stock Out import (should fail - wrong format)
print("\n3. Testing import_stock_out_excel (WRONG function - should fail):")
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
