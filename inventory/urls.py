from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Material Types
    path('material-types/', views.material_types, name='material_types'),
    
    # Suppliers
    path('suppliers/', views.suppliers, name='suppliers'),
    
    # Customers
    path('customers/', views.customers, name='customers'),
    
    # Warehouses
    path('warehouses/', views.warehouses, name='warehouses'),
    
    # Inventory
    path('inventory/', views.inventory_list, name='inventory_list'),
    
    # Stock In
    path('stock-in/', views.stock_in_list, name='stock_in_list'),
    
    # Stock Out
    path('stock-out/', views.stock_out_list, name='stock_out_list'),
    
    # Excel Upload Page
    path('excel-upload/', views.excel_upload, name='excel_upload'),
    
    # Download Templates
    path('download-stock-in-template/', views.download_stock_in_template, name='download_stock_in_template'),
    path('download-stock-out-template/', views.download_stock_out_template, name='download_stock_out_template'),
    path('download-unified-template/', views.download_unified_template, name='download_unified_template'),
    path('download-stock-transfer-template/', views.download_stock_transfer_template, name='download_stock_transfer_template'),
    
    # Download Reports
    path('download-inventory-report/', views.download_inventory_report, name='download_inventory_report'),
    
    # Upload Excel Files
    path('upload-stock-in-excel/', views.upload_stock_in_excel, name='upload_stock_in_excel'),
    path('upload-stock-out-excel/', views.upload_stock_out_excel, name='upload_stock_out_excel'),
    path('upload-unified-excel/', views.upload_unified_excel, name='upload_unified_excel'),
    path('upload-stock-transfer-excel/', views.upload_stock_transfer_excel, name='upload_stock_transfer_excel'),
    
    # API Endpoints
    path('api/material-types/', views.get_material_types, name='get_material_types'),
    path('api/suppliers/', views.get_suppliers, name='get_suppliers'),
    path('api/customers/', views.get_customers, name='get_customers'),
    path('api/warehouses/', views.get_warehouses, name='get_warehouses'),
    path('api/inventory-quantity/<int:material_id>/', views.get_inventory_quantity, name='get_inventory_quantity'),
    
    # Test Views
    path('test-warehouse/', views.test_warehouse_operations, name='test_warehouse_operations'),
]
