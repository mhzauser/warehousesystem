#!/usr/bin/env python3
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ironwarehouse.settings')
django.setup()

from inventory.excel_utils import create_unified_stock_template

print("Creating unified template with Persian dates...")
print("=" * 50)

try:
    # Create the unified template
    file_path = create_unified_stock_template()
    print(f"✅ Template created successfully!")
    print(f"📁 File path: {file_path}")
    print(f"📄 File name: {os.path.basename(file_path)}")
    
    # Check if file exists
    if os.path.exists(file_path):
        print(f"✅ File exists on disk")
        file_size = os.path.getsize(file_path)
        print(f"📊 File size: {file_size} bytes")
    else:
        print(f"❌ File not found on disk")
        
except Exception as e:
    print(f"❌ Error creating template: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("Template creation completed!")
