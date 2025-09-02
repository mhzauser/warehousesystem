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

print(f"Testing Excel import with user: {user.username}")
print("=" * 60)

# Test the import with our test file
try:
    results = import_unified_stock_excel('test_persian_dates.xlsx', user)
    
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

print("\n" + "=" * 60)
print("Test completed!")
