#!/usr/bin/env python3
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ironwarehouse.settings')
django.setup()

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

print(f"Testing new corrected Excel file with user: {user.username}")
print("=" * 70)

# Test the new file
try:
    results = import_unified_stock_excel('قالب_یکپارچه_صحیح_با_تاریخ_فارسی.xlsx', user)
    
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
    
    if not results.get('success') and not results.get('errors'):
        print("No results returned")
        
except Exception as e:
    print(f"❌ Import failed with exception: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("Test completed!")
