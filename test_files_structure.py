"""
فحص هيكل الملفات الفعلية - المرحلة 1
"""
import pandas as pd
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import normalize_columns, _get_name, _get_price, extract_brand, extract_size, extract_concentration

DATA_DIR = "test_data"

print("=" * 70)
print("المرحلة 1: فحص هيكل الملفات")
print("=" * 70)

# 1. فحص ملف المتجر
print("\n📦 ملف المتجر (store.csv):")
print("-" * 50)
try:
    store_df = pd.read_csv(f"{DATA_DIR}/store.csv", encoding="utf-8-sig")
    print(f"  عدد الصفوف: {len(store_df)}")
    print(f"  الأعمدة: {list(store_df.columns)}")
    print(f"  أول 3 صفوف:")
    for i, row in store_df.head(3).iterrows():
        print(f"    {dict(row)}")
    
    # تطبيع الأعمدة
    store_norm = normalize_columns(store_df)
    print(f"\n  بعد التطبيع:")
    print(f"  الأعمدة: {list(store_norm.columns)}")
    
    # اختبار _get_name و _get_price
    store_records = store_norm.to_dict('records')
    sample = store_records[0]
    name = _get_name(sample)
    price = _get_price(sample)
    brand = extract_brand(name)
    size = extract_size(name)
    conc = extract_concentration(name)
    print(f"\n  عينة أول منتج:")
    print(f"    الاسم: {name}")
    print(f"    السعر: {price}")
    print(f"    الماركة: {brand}")
    print(f"    الحجم: {size}")
    print(f"    التركيز: {conc}")
    
    # إحصائيات
    valid_names = sum(1 for r in store_records if _get_name(r))
    valid_prices = sum(1 for r in store_records if _get_price(r) > 0)
    brands = set(extract_brand(_get_name(r)) for r in store_records if _get_name(r))
    brands.discard("")
    print(f"\n  إحصائيات:")
    print(f"    منتجات بأسماء صالحة: {valid_names}/{len(store_records)}")
    print(f"    منتجات بأسعار صالحة: {valid_prices}/{len(store_records)}")
    print(f"    عدد الماركات المكتشفة: {len(brands)}")
    print(f"    أمثلة ماركات: {list(brands)[:15]}")
    
except Exception as e:
    print(f"  ❌ خطأ: {e}")
    import traceback
    traceback.print_exc()

# 2. فحص ملفات المنافسين
print("\n" + "=" * 70)
print("🏪 ملفات المنافسين:")
print("=" * 70)

comp_files = [f for f in os.listdir(DATA_DIR) if f != "store.csv" and f.endswith(".csv")]
total_comp_products = 0

for comp_file in sorted(comp_files):
    filepath = f"{DATA_DIR}/{comp_file}"
    try:
        df = pd.read_csv(filepath, encoding="utf-8-sig")
        df_norm = normalize_columns(df)
        records = df_norm.to_dict('records')
        
        valid = sum(1 for r in records if _get_name(r) and _get_price(r) > 0)
        total_comp_products += len(records)
        
        # عينة
        if records:
            sample_name = _get_name(records[0])
            sample_price = _get_price(records[0])
        else:
            sample_name = "N/A"
            sample_price = 0
        
        print(f"\n  📁 {comp_file}:")
        print(f"    الأعمدة: {list(df.columns)[:5]}...")
        print(f"    عدد المنتجات: {len(records)} (صالحة: {valid})")
        print(f"    عينة: {sample_name[:50]} | {sample_price} ر.س")
        
    except Exception as e:
        print(f"\n  ❌ {comp_file}: {e}")

print(f"\n📊 الملخص:")
print(f"  إجمالي منتجات المتجر: {len(store_records)}")
print(f"  إجمالي منتجات المنافسين: {total_comp_products}")
print(f"  عدد ملفات المنافسين: {len(comp_files)}")
