#!/usr/bin/env python3
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ironwarehouse.settings')
django.setup()

import pandas as pd
from inventory.excel_utils import import_unified_stock_excel
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

print(f"Debugging persiancalender.xlsx import with user: {user.username}")
print("=" * 70)

# First, let's examine the file structure
try:
    df = pd.read_excel('persiancalender.xlsx')
    print("File structure:")
    print(f"Columns: {df.columns.tolist()}")
    print(f"Shape: {df.shape}")
    print(f"Data types: {df.dtypes}")
    
    print("\nFirst few rows:")
    print(df.head())
    
    print("\nColumn mapping check:")
    column_mapping = {
        'انبار': ['انبار', 'warehouse'],
        'نوع عملیات': ['نوع عملیات', 'نوع عمليات', 'operation_type'],
        'نام کالا': ['نام کالا', 'نام كالا', 'material_name'],
        'هویت کالا/نام مشتری': ['هویت کالا/نام مشتری', 'هویت كالا/نام مشتری', 'هویت کالا', 'هویت كالا', 'supplier_customer'],
        'مقدار': ['مقدار', 'quantity'],
        'قیمت واحد': ['قیمت واحد', 'قيمت واحد', 'unit_price'],
        'شماره بارنامه': ['شماره بارنامه', 'شماره بارنامه', 'invoice_number'],
        'تاریخ (YYYY-MM-DD)': ['تاریخ (YYYY-MM-DD)', 'تاريخ (YYYY-MM-DD)', 'date'],
        'یادداشت‌ها': ['یادداشت‌ها', 'يادداشت‌ها', 'notes']
    }
    
    # Check which columns are found
    found_columns = {}
    missing_columns = []
    
    for required_col, possible_names in column_mapping.items():
        found = False
        for possible_name in possible_names:
            if possible_name in df.columns:
                found_columns[required_col] = possible_name
                found = True
                print(f"✅ Found '{required_col}' -> '{possible_name}'")
                break
        if not found:
            missing_columns.append(required_col)
            print(f"❌ Missing '{required_col}'")
    
    if missing_columns:
        print(f"\n❌ Missing columns: {missing_columns}")
        print(f"Available columns: {df.columns.tolist()}")
    else:
        print("\n✅ All required columns found!")
        
    # Test the actual import
    print("\n" + "=" * 50)
    print("Testing actual import:")
    
    results = import_unified_stock_excel('persiancalender.xlsx', user)
    
    print("\nImport Results:")
    print("-" * 30)
    
    if results.get('success'):
        print("✅ Successful imports:")
        for success_msg in results['success']:
            print(f"  {success_msg}")
    
    if results.get('errors'):
        print("\n❌ Errors:")
        for error_msg in results['errors']:
            print(f"  {error_msg}")
    
except Exception as e:
    print(f"❌ Error during debugging: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("Debug completed!")
