#!/usr/bin/env python3
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ironwarehouse.settings')
django.setup()

from inventory.models import MaterialType, Supplier, Customer, Warehouse, StockIn, StockOut
from django.contrib.auth.models import User

print("Testing database constraints and model creation")
print("=" * 50)

try:
    # Get user
    user = User.objects.first()
    print(f"Using user: {user.username}")
    
    # Test creating basic objects
    print("\n1. Testing basic object creation:")
    
    # Test warehouse creation
    warehouse, created = Warehouse.objects.get_or_create(
        name="انبار اصلی",
        defaults={'code': 'ANBAR1', 'is_active': True}
    )
    print(f"   Warehouse: {warehouse.name} (created: {created})")
    
    # Test material type creation
    material, created = MaterialType.objects.get_or_create(
        name="میلگرد 16",
        defaults={'unit': 'کیلوگرم'}
    )
    print(f"   Material: {material.name} (created: {created})")
    
    # Test supplier creation
    supplier, created = Supplier.objects.get_or_create(
        name="شرکت آهن آلات تهران"
    )
    print(f"   Supplier: {supplier.name} (created: {created})")
    
    # Test customer creation
    customer, created = Customer.objects.get_or_create(
        name="شرکت ساختمانی آسمان"
    )
    print(f"   Customer: {customer.name} (created: {created})")
    
    print("\n2. Testing StockIn creation:")
    try:
        stock_in = StockIn.objects.create(
            warehouse=warehouse,
            material_type=material,
            supplier=supplier,
            quantity=100,
            unit_price=15000,
            invoice_number="TEST001",
            notes="تست",
            created_by=user
        )
        print(f"   ✅ StockIn created successfully: {stock_in.id}")
        
        # Clean up
        stock_in.delete()
        print(f"   ✅ StockIn deleted successfully")
        
    except Exception as e:
        print(f"   ❌ StockIn creation failed: {e}")
    
    print("\n3. Testing StockOut creation:")
    try:
        stock_out = StockOut.objects.create(
            warehouse=warehouse,
            material_type=material,
            customer=customer,
            quantity=50,
            unit_price=18000,
            invoice_number="TEST002",
            notes="تست",
            created_by=user
        )
        print(f"   ✅ StockOut created successfully: {stock_out.id}")
        
        # Clean up
        stock_out.delete()
        print(f"   ✅ StockOut deleted successfully")
        
    except Exception as e:
        print(f"   ❌ StockOut creation failed: {e}")
    
    print("\n4. Testing with actual data from Excel:")
    try:
        # Test with the actual data from row 1
        stock_in = StockIn.objects.create(
            warehouse=warehouse,
            material_type=material,
            supplier=supplier,
            quantity=1000,
            unit_price=15000,
            invoice_number="BR001",
            notes="ورودی اولیه",
            created_by=user
        )
        print(f"   ✅ StockIn with Excel data created successfully: {stock_in.id}")
        
        # Clean up
        stock_in.delete()
        print(f"   ✅ StockIn with Excel data deleted successfully")
        
    except Exception as e:
        print(f"   ❌ StockIn with Excel data failed: {e}")
        import traceback
        traceback.print_exc()
    
except Exception as e:
    print(f"❌ General error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("Database test completed!")
