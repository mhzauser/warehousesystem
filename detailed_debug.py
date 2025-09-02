#!/usr/bin/env python3
import pandas as pd

print("Detailed debugging of persiancalender.xlsx")
print("=" * 50)

# Read the file
df = pd.read_excel('persiancalender.xlsx')

print("Column names with repr():")
for i, col in enumerate(df.columns):
    print(f"{i}: {repr(col)}")

print("\nColumn names with ord():")
for i, col in enumerate(df.columns):
    print(f"{i}: {col} -> {[ord(c) for c in col]}")

print("\nChecking specific problematic column:")
problematic_col = 'هویت کالا/نام مشتری'
print(f"Target column: {repr(problematic_col)}")
print(f"Target column ord: {[ord(c) for c in problematic_col]}")

# Check if the column exists
if problematic_col in df.columns:
    print(f"✅ Column found in DataFrame")
    print(f"Column value: {repr(df.columns[df.columns == problematic_col][0])}")
else:
    print(f"❌ Column NOT found in DataFrame")
    
    # Try to find similar columns
    print("Looking for similar columns:")
    for col in df.columns:
        if 'هویت' in col or 'کالا' in col or 'مشتری' in col:
            print(f"  Similar: {repr(col)}")
            print(f"  Ord: {[ord(c) for c in col]}")

print("\nAll columns with their exact representation:")
for col in df.columns:
    print(f"'{col}' -> {repr(col)}")
