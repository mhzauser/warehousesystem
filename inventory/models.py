from django.db import models
from django.contrib.auth.models import User

# مدل‌های انبار آهن

class Warehouse(models.Model):
    """مدل انبار"""
    name = models.CharField(max_length=100, verbose_name="نام انبار")
    code = models.CharField(max_length=20, unique=True, verbose_name="کد انبار")
    address = models.TextField(blank=True, verbose_name="آدرس انبار")
    manager = models.CharField(max_length=100, blank=True, verbose_name="مدیر انبار")
    phone = models.CharField(max_length=20, blank=True, verbose_name="شماره تماس")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    class Meta:
        verbose_name = "انبار"
        verbose_name_plural = "انبارها"
        ordering = ['name']

class MaterialType(models.Model):
    """نام کالا (مثل میلگرد، ورق، نبشی و غیره)"""
    name = models.CharField(max_length=100, verbose_name="نام کالا")
    description = models.TextField(blank=True, verbose_name="توضیحات")
    unit = models.CharField(max_length=20, default="کیلوگرم", verbose_name="واحد اندازه‌گیری")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "نام کالا"
        verbose_name_plural = "نام‌های کالا"

class Supplier(models.Model):
    """هویت کالا"""
    name = models.CharField(max_length=200, verbose_name="هویت کالا")
    contact_person = models.CharField(max_length=100, blank=True, verbose_name="شخص رابط")
    phone = models.CharField(max_length=20, blank=True, verbose_name="شماره تماس")
    address = models.TextField(blank=True, verbose_name="آدرس")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "هویت کالا"
        verbose_name_plural = "هویت‌های کالا"

class Customer(models.Model):
    """مشتریان"""
    name = models.CharField(max_length=200, verbose_name="نام مشتری")
    contact_person = models.CharField(max_length=100, blank=True, verbose_name="شخص رابط")
    phone = models.CharField(max_length=20, blank=True, verbose_name="شماره تماس")
    address = models.TextField(blank=True, verbose_name="آدرس")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "مشتری"
        verbose_name_plural = "مشتریان"

class Inventory(models.Model):
    """موجودی انبار"""
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, blank=True, null=True, verbose_name="انبار")
    material_type = models.ForeignKey(MaterialType, on_delete=models.CASCADE, verbose_name="نوع ماده")
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, blank=True, null=True, verbose_name="هویت کالا (Supplier)")
    current_quantity = models.IntegerField(default=0, blank=True, null=True, verbose_name="موجودی فعلی")
    last_updated = models.DateTimeField(auto_now=True, verbose_name="آخرین بروزرسانی")
    
    def __str__(self):
        warehouse_name = self.warehouse.name if self.warehouse else "بدون انبار"
        supplier_name = f" - {self.supplier.name}" if self.supplier else ""
        return f"{warehouse_name} - {self.material_type.name}{supplier_name}: {self.current_quantity} {self.material_type.unit}"
    
    class Meta:
        verbose_name = "موجودی انبار"
        verbose_name_plural = "موجودی انبار"
        # unique_together removed to allow multiple records with None warehouse

class StockIn(models.Model):
    """ورودی انبار"""
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, blank=True, null=True, verbose_name="انبار")
    material_type = models.ForeignKey(MaterialType, on_delete=models.CASCADE, verbose_name="نام کالا")
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, verbose_name="هویت کالا")
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True, null=True, verbose_name="مشتری (پیش‌فرض خودتان)")
    quantity = models.IntegerField(blank=True, null=True, verbose_name="مقدار")
    unit_price = models.IntegerField(blank=True, null=True, verbose_name="قیمت واحد")
    total_price = models.IntegerField(blank=True, null=True, verbose_name="قیمت کل")
    invoice_number = models.CharField(max_length=50, blank=True, verbose_name="شماره بارنامه")
    notes = models.TextField(blank=True, verbose_name="یادداشت‌ها")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="ثبت کننده")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ورود")
    manual_date = models.DateField(blank=True, null=True, verbose_name="تاریخ ورود دستی")
    
    def save(self, *args, **kwargs):
        # محاسبه قیمت کل
        if self.quantity and self.unit_price:
            self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        
        # بروزرسانی موجودی انبار - موجودی هر Supplier جداگانه
        if self.warehouse:
            inventory, created = Inventory.objects.get_or_create(
                warehouse=self.warehouse,
                material_type=self.material_type,
                supplier=self.supplier,
                defaults={'current_quantity': 0}
            )
            inventory.current_quantity += self.quantity or 0
            inventory.save()
    
    def __str__(self):
        warehouse_name = self.warehouse.name if self.warehouse else "بدون انبار"
        supplier_name = self.supplier.name if self.supplier else "بدون هویت"
        customer_name = f" - {self.customer.name}" if self.customer else ""
        return f"ورودی {warehouse_name} - {supplier_name} - {self.material_type.name} - {self.quantity} {self.material_type.unit}{customer_name}"
    
    class Meta:
        verbose_name = "ورودی انبار"
        verbose_name_plural = "ورودی‌های انبار"

class StockOut(models.Model):
    """خروجی انبار"""
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, blank=True, null=True, verbose_name="انبار")
    material_type = models.ForeignKey(MaterialType, on_delete=models.CASCADE, verbose_name="نام کالا")
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name="مشتری")
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, blank=True, null=True, verbose_name="هویت کالای خروجی (از کدام Supplier)")
    quantity = models.IntegerField(blank=True, null=True, verbose_name="مقدار")
    unit_price = models.IntegerField(blank=True, null=True, verbose_name="قیمت واحد")
    total_price = models.IntegerField(blank=True, null=True, verbose_name="قیمت کل")
    invoice_number = models.CharField(max_length=50, blank=True, verbose_name="شماره بارنامه")
    notes = models.TextField(blank=True, verbose_name="یادداشت‌ها")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="ثبت کننده")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ خروج")
    manual_date = models.DateField(blank=True, null=True, verbose_name="تاریخ خروج دستی")
    
    def save(self, *args, **kwargs):
        # محاسبه قیمت کل
        if self.quantity and self.unit_price:
            self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        
        # بروزرسانی موجودی انبار - موجودی هر Supplier جداگانه
        if self.warehouse:
            try:
                # اگر Supplier مشخص شده، از موجودی آن کم کن
                if self.supplier:
                    inventory = Inventory.objects.get(
                        warehouse=self.warehouse, 
                        material_type=self.material_type,
                        supplier=self.supplier
                    )
                    inventory.current_quantity -= self.quantity or 0
                    inventory.save()
                else:
                    # اگر Supplier مشخص نشده، از موجودی کلی کم کن
                    inventory = Inventory.objects.get(
                        warehouse=self.warehouse, 
                        material_type=self.material_type
                    )
                    inventory.current_quantity -= self.quantity or 0
                    inventory.save()
            except Inventory.DoesNotExist:
                pass  # اگر موجودی وجود نداشت، کاری نکن
    
    def __str__(self):
        warehouse_name = self.warehouse.name if self.warehouse else "بدون انبار"
        supplier_name = f" - {self.supplier.name}" if self.supplier else ""
        return f"خروجی {warehouse_name} - {self.material_type.name} - {self.quantity} {self.material_type.unit}{supplier_name}"
    
    class Meta:
        verbose_name = "خروجی انبار"
        verbose_name_plural = "خروجی‌های انبار"

class StockTransfer(models.Model):
    """انتقال بین انبارها"""
    TRANSFER_TYPES = [
        ('in', 'انتقال به انبار'),
        ('out', 'انتقال از انبار'),
    ]
    
    source_warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='transfers_out', blank=True, null=True, verbose_name="انبار مبدا")
    destination_warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='transfers_in', blank=True, null=True, verbose_name="انبار مقصد")
    material_type = models.ForeignKey(MaterialType, on_delete=models.CASCADE, verbose_name="نام کالا")
    quantity = models.IntegerField(blank=True, null=True, verbose_name="مقدار")
    notes = models.TextField(blank=True, verbose_name="یادداشت‌ها")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="ثبت کننده")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ انتقال")
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # بروزرسانی موجودی انبار مبدا
        if self.source_warehouse:
            try:
                source_inventory = Inventory.objects.get(warehouse=self.source_warehouse, material_type=self.material_type)
                source_inventory.current_quantity -= self.quantity or 0
                source_inventory.save()
            except Inventory.DoesNotExist:
                pass
        
        # بروزرسانی موجودی انبار مقصد
        if self.destination_warehouse:
            dest_inventory, created = Inventory.objects.get_or_create(
                warehouse=self.destination_warehouse,
                material_type=self.material_type,
                defaults={'current_quantity': 0}
            )
            dest_inventory.current_quantity += self.quantity or 0
            dest_inventory.save()
    
    def __str__(self):
        source_name = self.source_warehouse.name if self.source_warehouse else "بدون انبار"
        dest_name = self.destination_warehouse.name if self.destination_warehouse else "بدون انبار"
        return f"انتقال {self.material_type.name} - {self.quantity} {self.material_type.unit} از {source_name} به {dest_name}"
    
    class Meta:
        verbose_name = "انتقال انبار"
        verbose_name_plural = "انتقالات انبار"
