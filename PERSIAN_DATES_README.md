# Persian (Shamsi) Date Implementation

## Overview
This document describes the implementation of Persian (Shamsi) calendar dates in the Iron Warehouse Django application.

## Features Implemented

### 1. Persian Date Utilities (`inventory/utils.py`)
- **`gregorian_to_persian_str()`**: Converts Gregorian dates to Persian date strings
- **`gregorian_to_persian_datetime_str()`**: Converts Gregorian datetimes to Persian datetime strings
- **`get_current_persian_date()`**: Gets current date in Persian calendar
- **`get_current_persian_datetime()`**: Gets current datetime in Persian calendar
- **`format_persian_date()`**: Formats Persian dates with custom format strings
- **`format_persian_datetime()`**: Formats Persian datetimes with custom format strings

### 2. Django Template Filters (`inventory/templatetags/persian_dates.py`)
- **`persian_date`**: Template filter for Persian date formatting
- **`persian_datetime`**: Template filter for Persian datetime formatting
- **`persian_date_only`**: Template filter for date only (without time)
- **`persian_time_only`**: Template filter for time only

### 3. Admin Interface Updates (`inventory/admin.py`)
All admin list displays now show Persian dates:
- **Warehouse**: `persian_created_at` - تاریخ ایجاد (شمسی)
- **Supplier**: `persian_created_at` - تاریخ ایجاد (شمسی)
- **Customer**: `persian_created_at` - تاریخ ایجاد (شمسی)
- **Inventory**: `persian_last_updated` - آخرین بروزرسانی (شمسی)
- **StockIn**: `persian_manual_date` and `persian_created_at` - تاریخ ورود دستی (شمسی) and تاریخ ثبت (شمسی)
- **StockOut**: `persian_manual_date` and `persian_created_at` - تاریخ خروج دستی (شمسی) and تاریخ ثبت (شمسی)
- **StockTransfer**: `persian_created_at` - تاریخ انتقال (شمسی)

### 4. Excel Export Updates (`inventory/excel_utils.py`)
All Excel exports now use Persian dates:
- Inventory reports
- Stock in/out reports
- Stock transfer reports
- All date columns show Persian format (YYYY/MM/DD)

### 5. Template Updates
- **`warehouses.html`**: Updated to use `{% load persian_dates %}` and `{{ warehouse.created_at|persian_date:"%Y/%m/%d" }}`

## Usage Examples

### In Python Code
```python
from inventory.utils import gregorian_to_persian_str, gregorian_to_persian_datetime_str

# Convert date
persian_date = gregorian_to_persian_str(date(2024, 1, 15), "%Y/%m/%d")
# Result: "1402/10/25"

# Convert datetime
persian_datetime = gregorian_to_persian_datetime_str(datetime(2024, 1, 15, 14, 30), "%Y/%m/%d %H:%M")
# Result: "1402/10/25 14:30"
```

### In Django Templates
```html
{% load persian_dates %}

<!-- Basic usage -->
{{ object.created_at|persian_date }}

<!-- Custom format -->
{{ object.created_at|persian_date:"%Y/%m/%d" }}

<!-- DateTime with custom format -->
{{ object.created_at|persian_datetime:"%Y/%m/%d ساعت %H:%M" }}

<!-- Date only -->
{{ object.created_at|persian_date_only }}

<!-- Time only -->
{{ object.created_at|persian_time_only }}
```

### In Admin Interface
All admin list views automatically display Persian dates with appropriate column headers in Persian.

## Dependencies
- **jdatetime**: Python library for Persian calendar support
- Added to `requirements.txt`: `jdatetime>=4.1.1`

## Installation
```bash
pip install jdatetime
```

## Date Format Patterns
- `%Y`: 4-digit Persian year (e.g., 1402)
- `%y`: 2-digit Persian year (e.g., 02)
- `%m`: 2-digit Persian month (e.g., 10)
- `%d`: 2-digit Persian day (e.g., 25)
- `%H`: 24-hour format hour (e.g., 14)
- `%M`: 2-digit minute (e.g., 30)
- `%S`: 2-digit second (e.g., 45)

## Benefits
1. **User-Friendly**: Persian users can see dates in their familiar calendar format
2. **Consistent**: All date displays throughout the application use Persian format
3. **Flexible**: Multiple format options available for different use cases
4. **Maintainable**: Centralized utility functions for easy maintenance
5. **Template-Ready**: Easy-to-use template filters for frontend display

## Testing
The implementation has been tested with:
- Current date/time conversion
- Specific date conversions (2024-01-15 → 1402/10/25)
- Custom format strings
- None value handling
- Template filter functionality

All tests passed successfully, confirming the Persian date functionality works correctly.
