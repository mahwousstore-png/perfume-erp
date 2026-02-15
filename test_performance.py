#!/usr/bin/env python3
"""اختبار أداء المحرك مع البيانات الكاملة"""
import time
import pandas as pd
import sys
import os

# إضافة مسار المشروع
sys.path.insert(0, os.path.dirname(__file__))

from engine import normalize_columns
from engine_v2 import run_smart_matching

# تحميل الملفات
print("📂 تحميل الملفات...")
my_df = pd.read_csv("test_data/منتجاتمهووستنسيقتحيثالاسعار.csv", encoding='utf-8-sig')
my_df = normalize_columns(my_df)
my_products = my_df.to_dict('records')

comp_products = []
comp_files = [f for f in os.listdir("test_data") if f != "منتجاتمهووستنسيقتحيثالاسعار.csv" and f.endswith('.csv')]
for cf in comp_files:
    try:
        df = pd.read_csv(f"test_data/{cf}", encoding='utf-8-sig')
        df = normalize_columns(df)
        records = df.to_dict('records')
        name = cf.replace('.csv', '').replace('متجر', '').replace('متحر', '').strip()
        for r in records:
            r['_competitor'] = name
        comp_products.extend(records)
    except:
        pass

print(f"📊 المتجر: {len(my_products)} | المنافسين: {len(comp_products)}")

# اختبار أداء - أول 500 منتج فقط
print("\n🚀 اختبار أداء (أول 500 منتج)...")
start = time.time()

def progress(p, elapsed, eta, stats):
    print(f"  📊 {p*100:.0f}% | {elapsed:.1f}s | ETA: {eta:.0f}s | fast:{stats['fast_matches']} med:{stats['medium_matches']} deep:{stats['deep_matches']}")

results = run_smart_matching(
    my_products[:500],
    comp_products,
    use_gemini=False,
    progress_callback=progress
)

elapsed = time.time() - start
print(f"\n⏱️ الوقت: {elapsed:.1f} ثانية لـ 500 منتج")
print(f"📈 المتوقع لـ {len(my_products)} منتج: {elapsed / 500 * len(my_products):.0f} ثانية")

# إحصائيات
matched = [r for r in results if r["category"] != "missing"]
missing = [r for r in results if r["category"] == "missing"]
raise_p = [r for r in results if r["category"] == "raise_price"]
lower_p = [r for r in results if r["category"] == "lower_price"]
keep_p = [r for r in results if r["category"] == "keep_price"]

print(f"\n📊 النتائج:")
print(f"  ✅ مطابقات: {len(matched)} ({len(matched)/500*100:.1f}%)")
print(f"  🔴 رفع: {len(raise_p)}")
print(f"  🟡 خفض: {len(lower_p)}")
print(f"  🟢 موافق: {len(keep_p)}")
print(f"  🔵 مفقود: {len(missing)}")

# فحص عينة من المطابقات
print(f"\n🔍 عينة من المطابقات:")
for r in matched[:5]:
    print(f"  {r['my_name'][:40]} → {r['comp_name'][:40]} | ثقة: {r['confidence']}% | {r['match_stage']}")

print("\n✅ اكتمل الاختبار!")
