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

print(f"Testing import with user: {user.username}")

# Test the import
try:
    results = import_unified_stock_excel('persiancalender.xlsx', user)
    print("\nImport Results:")
    print("Success:", results.get('success', []))
    print("Errors:", results.get('errors', []))
except Exception as e:
    print(f"Import failed with exception: {e}")
    import traceback
    traceback.print_exc()
