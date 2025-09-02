from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.utils import timezone
from datetime import datetime, date
import json
import os
import tempfile

from .models import (
    Warehouse, MaterialType, Supplier, Customer, Inventory, 
    StockIn, StockOut, StockTransfer
)
from .excel_utils import (
    create_stock_in_template, create_stock_out_template,
    create_unified_stock_template,
    import_stock_in_excel, import_stock_out_excel,
    import_unified_stock_excel,
    export_inventory_to_excel, create_stock_transfer_template,
    import_stock_transfer_excel
)
from .utils import gregorian_to_persian_str, gregorian_to_persian_datetime_str

# صفحه اصلی انبار
@login_required
def dashboard(request):
    """صفحه اصلی انبار"""
    # آمار کلی
    total_warehouses = Warehouse.objects.count()
    total_materials = MaterialType.objects.count()
    total_suppliers = Supplier.objects.count()
    total_customers = Customer.objects.count()
    total_inventory_value = Inventory.objects.aggregate(
        total=Sum('current_quantity')
    )['total'] or 0
    
    # آخرین ورودی‌ها
    recent_stock_ins = StockIn.objects.select_related('material_type', 'supplier').order_by('-created_at')[:5]
    
    # آخرین خروجی‌ها
    recent_stock_outs = StockOut.objects.select_related('material_type', 'customer').order_by('-created_at')[:5]
    
    # موجودی‌های کم
    low_stock = Inventory.objects.filter(current_quantity__lt=100).select_related('material_type')[:5]
    
    context = {
        'total_warehouses': total_warehouses,
        'total_materials': total_materials,
        'total_suppliers': total_suppliers,
        'total_customers': total_customers,
        'total_inventory_value': total_inventory_value,
        'recent_stock_ins': recent_stock_ins,
        'recent_stock_outs': recent_stock_outs,
        'low_stock': low_stock,
    }
    
    return render(request, 'inventory/dashboard.html', context)

# مدیریت نام‌های کالا
@login_required
def material_types(request):
    """مدیریت نام‌های کالا"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        unit = request.POST.get('unit', 'کیلوگرم')
        
        if name:
            MaterialType.objects.create(
                name=name,
                description=description,
                unit=unit
            )
            messages.success(request, 'نام کالا با موفقیت اضافه شد.')
            return redirect('material_types')
    
    materials = MaterialType.objects.all().order_by('name')
    return render(request, 'inventory/material_types.html', {'materials': materials})

# مدیریت هویت‌های کالا
@login_required
def suppliers(request):
    """
    مدیریت هویت‌های کالا (تامین‌کنندگان)
    
    این تابع مسئول نمایش لیست تامین‌کنندگان و اضافه کردن تامین‌کننده جدید است.
    
    Args:
        request: درخواست HTTP که شامل اطلاعات فرم در صورت POST است
        
    Returns:
        صفحه HTML با لیست تامین‌کنندگان یا ریدایرکت در صورت اضافه شدن موفق
    """
    if request.method == 'POST':
        name = request.POST.get('name')
        contact_person = request.POST.get('contact_person', '')
        phone = request.POST.get('phone', '')
        address = request.POST.get('address', '')
        
        if name:
            Supplier.objects.create(
                name=name,
                contact_person=contact_person,
                phone=phone,
                address=address
            )
            messages.success(request, 'هویت کالا با موفقیت اضافه شد.')
            return redirect('suppliers')
    
    suppliers_list = Supplier.objects.all().order_by('name')
    return render(request, 'inventory/suppliers.html', {'suppliers': suppliers_list})

# مدیریت مشتریان
@login_required
def customers(request):
    """مدیریت مشتریان"""
    if request.method == 'POST':
        name = request.POST.get('name')
        contact_person = request.POST.get('contact_person', '')
        phone = request.POST.get('phone', '')
        address = request.POST.get('address', '')
        
        if name:
            Customer.objects.create(
                name=name,
                contact_person=contact_person,
                phone=phone,
                address=address
            )
            messages.success(request, 'مشتری با موفقیت اضافه شد.')
            return redirect('customers')
    
    customers_list = Customer.objects.all().order_by('name')
    return render(request, 'inventory/customers.html', {'customers': customers_list})

# مدیریت انبارها
@login_required
def warehouses(request):
    """مدیریت انبارها"""
    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        address = request.POST.get('address', '')
        manager = request.POST.get('manager', '')
        phone = request.POST.get('phone', '')
        is_active = request.POST.get('is_active') == 'on'
        
        if name and code:
            # بررسی تکراری نبودن کد انبار
            if Warehouse.objects.filter(code=code).exists():
                messages.error(request, 'کد انبار تکراری است.')
            else:
                Warehouse.objects.create(
                    name=name,
                    code=code,
                    address=address,
                    manager=manager,
                    phone=phone,
                    is_active=is_active
                )
                messages.success(request, 'انبار با موفقیت اضافه شد.')
                return redirect('warehouses')
        else:
            messages.error(request, 'نام و کد انبار الزامی است.')
    
    warehouses_list = Warehouse.objects.all().order_by('name')
    return render(request, 'inventory/warehouses.html', {'warehouses': warehouses_list})

# موجودی انبار
@login_required
def inventory_list(request):
    """لیست موجودی انبار"""
    inventories = Inventory.objects.select_related('material_type').all().order_by('material_type__name')
    
    # جستجو
    search = request.GET.get('search', '')
    if search:
        inventories = inventories.filter(
            Q(material_type__name__icontains=search) |
            Q(material_type__description__icontains=search)
        )
    
    # صفحه‌بندی
    paginator = Paginator(inventories, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'inventory/inventory_list.html', {
        'page_obj': page_obj,
        'search': search
    })

# ورودی انبار
@login_required
def stock_in_list(request):
    """لیست ورودی‌های انبار"""
    stock_ins = StockIn.objects.select_related(
        'material_type', 'supplier', 'created_by'
    ).all().order_by('-created_at')
    
    # فیلتر بر اساس تاریخ
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date:
        stock_ins = stock_ins.filter(created_at__date__gte=start_date)
    if end_date:
        stock_ins = stock_ins.filter(created_at__date__lte=end_date)
    
    # جستجو
    search = request.GET.get('search', '')
    if search:
        stock_ins = stock_ins.filter(
            Q(material_type__name__icontains=search) |
            Q(supplier__name__icontains=search) |
            Q(invoice_number__icontains=search)
        )
    
    # صفحه‌بندی
    paginator = Paginator(stock_ins, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'inventory/stock_in_list.html', {
        'page_obj': page_obj,
        'search': search,
        'start_date': start_date,
        'end_date': end_date
    })

# خروجی انبار
@login_required
def stock_out_list(request):
    """لیست خروجی‌های انبار"""
    stock_outs = StockOut.objects.select_related(
        'material_type', 'customer', 'created_by'
    ).all().order_by('-created_at')
    
    # فیلتر بر اساس تاریخ
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date:
        stock_outs = stock_outs.filter(created_at__date__gte=start_date)
    if end_date:
        stock_outs = stock_outs.filter(created_at__date__lte=end_date)
    
    # جستجو
    search = request.GET.get('search', '')
    if search:
        stock_outs = stock_outs.filter(
            Q(material_type__name__icontains=search) |
            Q(customer__name__icontains=search) |
            Q(invoice_number__icontains=search)
        )
    
    # صفحه‌بندی
    paginator = Paginator(stock_outs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'inventory/stock_out_list.html', {
        'page_obj': page_obj,
        'search': search,
        'start_date': start_date,
        'end_date': end_date
    })

# Excel Upload Views
@login_required
def excel_upload(request):
    """صفحه آپلود Excel"""
    return render(request, 'inventory/excel_upload.html')

@login_required
def download_stock_in_template(request):
    """دانلود قالب Excel برای ورودی انبار"""
    try:
        file_path = create_stock_in_template()
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
            return response
    except Exception as e:
        messages.error(request, f'خطا در ایجاد قالب: {str(e)}')
        return redirect('excel_upload')

@login_required
def download_unified_template(request):
    """دانلود قالب Excel یکپارچه برای ورودی و خروجی انبار"""
    try:
        file_path = create_unified_stock_template()
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
            return response
    except Exception as e:
        messages.error(request, f'خطا در ایجاد قالب: {str(e)}')
        return redirect('excel_upload')

@login_required
def download_stock_out_template(request):
    """دانلود قالب Excel برای خروجی انبار"""
    try:
        file_path = create_stock_out_template()
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
            return response
    except Exception as e:
        messages.error(request, f'خطا در ایجاد قالب: {str(e)}')
        return redirect('excel_upload')

@login_required
def download_inventory_report(request):
    """دانلود گزارش موجودی انبار"""
    try:
        file_path = export_inventory_to_excel()
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
            return response
    except Exception as e:
        messages.error(request, f'خطا در ایجاد گزارش: {str(e)}')
        return redirect('inventory_list')

@login_required
@csrf_exempt
def upload_stock_in_excel(request):
    """آپلود فایل Excel برای ورودی انبار"""
    if request.method == 'POST':
        try:
            uploaded_file = request.FILES.get('excel_file')
            if not uploaded_file:
                return JsonResponse({'success': False, 'message': 'فایل انتخاب نشده است.'})
            
            # ذخیره فایل موقت
            temp_path = f'/tmp/stock_in_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
            with open(temp_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            
            # پردازش فایل
            results = import_stock_in_excel(temp_path, request.user)
            
            # حذف فایل موقت
            os.remove(temp_path)
            
            return JsonResponse({
                'success': True,
                'results': results
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'خطا در پردازش فایل: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'متد نامعتبر'})

@login_required
@csrf_exempt
def upload_stock_out_excel(request):
    """آپلود فایل Excel برای خروجی انبار"""
    if request.method == 'POST':
        try:
            uploaded_file = request.FILES.get('excel_file')
            if not uploaded_file:
                return JsonResponse({'success': False, 'message': 'فایل انتخاب نشده است.'})
            
            # ذخیره فایل موقت
            temp_path = f'/tmp/stock_out_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
            with open(temp_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            
            # پردازش فایل
            results = import_stock_out_excel(temp_path, request.user)
            
            # حذف فایل موقت
            os.remove(temp_path)
            
            return JsonResponse({
                'success': True,
                'results': results
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'خطا در پردازش فایل: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'متد نامعتبر'})

@login_required
@csrf_exempt
def upload_unified_excel(request):
    """آپلود فایل Excel یکپارچه برای ورودی و خروجی انبار"""
    if request.method == 'POST':
        try:
            uploaded_file = request.FILES.get('excel_file')
            if not uploaded_file:
                return JsonResponse({'success': False, 'message': 'فایل انتخاب نشده است.'})
            
            # ذخیره فایل موقت
            temp_path = f'/tmp/unified_stock_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
            with open(temp_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            
            # پردازش فایل
            results = import_unified_stock_excel(temp_path, request.user)
            
            # حذف فایل موقت
            os.remove(temp_path)
            
            return JsonResponse({
                'success': True,
                'results': results
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'خطا در پردازش فایل: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'متد نامعتبر'})

@login_required
def download_stock_transfer_template(request):
    """دانلود قالب Excel برای انتقال انبار"""
    try:
        file_path = create_stock_transfer_template()
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="قالب_انتقال_انبار.xlsx"'
            return response
    except Exception as e:
        messages.error(request, f"خطا در ایجاد قالب: {str(e)}")
        return redirect('inventory:excel_upload')

@login_required
def upload_stock_transfer_excel(request):
    """آپلود فایل Excel برای انتقال انبار"""
    if request.method == 'POST':
        if 'excel_file' not in request.FILES:
            messages.error(request, "فایل انتخاب نشده است")
            return redirect('inventory:excel_upload')
        
        excel_file = request.FILES['excel_file']
        
        # بررسی نوع فایل
        if not excel_file.name.endswith('.xlsx'):
            messages.error(request, "فقط فایل‌های Excel (.xlsx) قابل قبول هستند")
            return redirect('inventory:excel_upload')
        
        try:
            # ذخیره فایل موقت
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
                for chunk in excel_file.chunks():
                    temp_file.write(chunk)
                temp_path = temp_file.name
            
            # پردازش فایل
            results = import_stock_transfer_excel(temp_path, request.user)
            
            # حذف فایل موقت
            os.unlink(temp_path)
            
            # نمایش نتایج
            if results['success']:
                for success_msg in results['success']:
                    messages.success(request, success_msg)
            
            if results['errors']:
                for error_msg in results['errors']:
                    messages.error(request, error_msg)
            
        except Exception as e:
            messages.error(request, f"خطا در پردازش فایل: {str(e)}")
        
        return redirect('inventory:excel_upload')
    
    return redirect('inventory:excel_upload')

# API Views for AJAX
@login_required
def get_material_types(request):
    """دریافت لیست نام‌های کالا برای AJAX"""
    materials = MaterialType.objects.all().values('id', 'name')
    return JsonResponse({'materials': list(materials)})

@login_required
def get_suppliers(request):
    """دریافت لیست هویت‌های کالا برای AJAX"""
    suppliers = Supplier.objects.all().values('id', 'name')
    return JsonResponse({'suppliers': list(suppliers)})

@login_required
def get_customers(request):
    """دریافت لیست مشتریان برای AJAX"""
    customers = Customer.objects.all().values('id', 'name')
    return JsonResponse({'customers': list(customers)})

@login_required
def get_warehouses(request):
    """دریافت لیست انبارها برای AJAX"""
    warehouses = Warehouse.objects.filter(is_active=True).values('id', 'name', 'code')
    return JsonResponse({'warehouses': list(warehouses)})

@login_required
def get_inventory_quantity(request, material_id):
    """دریافت موجودی کالا"""
    try:
        inventory = Inventory.objects.get(material_type_id=material_id)
        return JsonResponse({'quantity': inventory.current_quantity or 0})
    except Inventory.DoesNotExist:
        return JsonResponse({'quantity': 0})

# Test Views for Warehouse Operations
@login_required
def test_warehouse_operations(request):
    """صفحه تست عملیات انبار"""
    from datetime import date
    
    if request.method == 'POST':
        operation_type = request.POST.get('operation_type')
        warehouse_id = request.POST.get('warehouse')
        material_id = request.POST.get('material')
        quantity = int(request.POST.get('quantity', 0))
        
        try:
            warehouse = Warehouse.objects.get(id=warehouse_id)
            material = MaterialType.objects.get(id=material_id)
            
            if operation_type == 'stock_in':
                supplier_id = request.POST.get('supplier')
                supplier = Supplier.objects.get(id=supplier_id)
                
                stock_in = StockIn.objects.create(
                    warehouse=warehouse,
                    material_type=material,
                    supplier=supplier,
                    quantity=quantity,
                    unit_price=int(request.POST.get('unit_price', 0)),
                    invoice_number=request.POST.get('invoice_number', ''),
                    notes=request.POST.get('notes', 'تست دستی'),
                    created_by=request.user,
                    manual_date=date.today()
                )
                messages.success(request, f'ورودی {quantity} {material.unit} {material.name} به انبار {warehouse.name} اضافه شد.')
                
            elif operation_type == 'stock_out':
                customer_id = request.POST.get('customer')
                customer = Customer.objects.get(id=customer_id)
                
                stock_out = StockOut.objects.create(
                    warehouse=warehouse,
                    material_type=material,
                    customer=customer,
                    quantity=quantity,
                    unit_price=int(request.POST.get('unit_price', 0)),
                    invoice_number=request.POST.get('invoice_number', ''),
                    notes=request.POST.get('notes', 'تست دستی'),
                    created_by=request.user,
                    manual_date=date.today()
                )
                messages.success(request, f'خروجی {quantity} {material.unit} {material.name} از انبار {warehouse.name} ثبت شد.')
                
        except Exception as e:
            messages.error(request, f'خطا: {str(e)}')
        
        return redirect('test_warehouse_operations')
    
    # Get data for forms
    warehouses = Warehouse.objects.filter(is_active=True)
    materials = MaterialType.objects.all()
    suppliers = Supplier.objects.all()
    customers = Customer.objects.all()
    
    # Get current inventory
    inventory_items = Inventory.objects.select_related('warehouse', 'material_type').all()
    
    context = {
        'warehouses': warehouses,
        'materials': materials,
        'suppliers': suppliers,
        'customers': customers,
        'inventory_items': inventory_items,
    }
    
    return render(request, 'inventory/test_warehouse_operations.html', context)
