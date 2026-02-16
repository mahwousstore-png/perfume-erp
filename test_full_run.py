"""
اختبار شامل مع كل البيانات (7505 منتج)
"""
import pandas as pd
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import normalize_columns, _get_name, _get_price, extract_brand, extract_size
from engine_v2 import run_smart_matching, light_normalize, GEMINI_AVAILABLE

DATA_DIR = "test_data"

# تحميل البيانات
print("📂 تحميل البيانات...")
store_df = pd.read_csv(f"{DATA_DIR}/store.csv", encoding="utf-8-sig")
store_df = normalize_columns(store_df)

comp_files = [f for f in os.listdir(DATA_DIR) if f != "store.csv" and f.endswith(".csv")]
all_comp = []
for comp_file in comp_files:
    df = pd.read_csv(f"{DATA_DIR}/{comp_file}", encoding="utf-8-sig")
    df = normalize_columns(df)
    comp_name = comp_file.replace("متجر", "").replace("متحر", "").replace(".csv", "")
    for _, row in df.iterrows():
        r = row.to_dict()
        r['_competitor'] = comp_name
        all_comp.append(r)

comp_df = pd.DataFrame(all_comp)

print(f"📊 المتجر: {len(store_df)} | المنافسين: {len(comp_df)} | Gemini: {'✅' if GEMINI_AVAILABLE else '❌'}")

# تشغيل المطابقة الكاملة (بدون Gemini أولاً)
print(f"\n🚀 تشغيل المطابقة الكاملة (بدون Gemini)...")
start = time.time()
results = run_smart_matching(store_df, comp_df, use_gemini=False)
elapsed = time.time() - start

print(f"⏱️ الوقت: {elapsed:.1f} ثانية")

# تحليل
categories = {}
stages = {}
for r in results:
    categories[r['category']] = categories.get(r['category'], 0) + 1
    stages[r['match_stage']] = stages.get(r['match_stage'], 0) + 1

print(f"\n📊 النتائج:")
for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
    pct = count / len(results) * 100
    emoji = {'raise_price': '🔴', 'lower_price': '🟡', 'keep_price': '🟢', 'missing': '🔵'}.get(cat, '❓')
    print(f"  {emoji} {cat}: {count} ({pct:.1f}%)")

matched = sum(1 for r in results if r['category'] != 'missing')
print(f"\n  نسبة المطابقة: {matched}/{len(results)} ({matched/len(results)*100:.1f}%)")

print(f"\n📊 المراحل:")
for stage, count in sorted(stages.items(), key=lambda x: -x[1]):
    print(f"  {stage}: {count}")

# التحقق من الحقول المطلوبة
print(f"\n🔍 التحقق من الحقول:")
required_fields = [
    'my_name', 'my_price', 'my_brand', 'my_size', 'my_conc', 'my_type',
    'comp_name', 'comp_price', 'comp_brand', 'comp_size', 'comp_conc',
    'competitor', 'diff', 'diff_pct', 'category', 'confidence',
    'match_reason', 'match_stage'
]
sample = results[0]
for f in required_fields:
    exists = f in sample
    print(f"  {'✅' if exists else '❌'} {f}: {str(sample.get(f, 'MISSING'))[:50]}")

# التحقق من الدقة على عينة عشوائية
import random
random.seed(42)
matched_results = [r for r in results if r['category'] != 'missing']
sample_check = random.sample(matched_results, min(50, len(matched_results)))

print(f"\n🔍 التحقق من دقة {len(sample_check)} مطابقة عشوائية:")
correct = 0
wrong = 0
suspicious = []

for r in sample_check:
    my_name = r['my_name']
    comp_name = r['comp_name']
    my_brand = extract_brand(my_name)
    comp_brand = extract_brand(comp_name)
    
    # تحقق الماركة
    brand_ok = True
    if my_brand and comp_brand:
        my_b = light_normalize(my_brand)
        comp_b = light_normalize(comp_brand)
        brand_ok = my_b == comp_b or fuzz.ratio(my_b, comp_b) >= 80
    
    # تحقق الحجم
    size_ok = True
    my_size = r['my_size']
    comp_size = r['comp_size']
    if my_size > 0 and comp_size > 0:
        size_ok = abs(my_size - comp_size) <= 10
    
    if brand_ok and size_ok:
        correct += 1
    else:
        wrong += 1
        suspicious.append(r)

from rapidfuzz import fuzz

accuracy = correct / len(sample_check) * 100 if sample_check else 0
print(f"  ✅ صحيح: {correct} | ❌ مشكوك: {wrong} | دقة: {accuracy:.1f}%")

if suspicious:
    print(f"\n⚠️ مطابقات مشكوك فيها:")
    for r in suspicious[:10]:
        print(f"  ❌ {r['my_name'][:45]}")
        print(f"     ← {r['comp_name'][:45]}")
        print(f"     ماركة: {r['my_brand']} vs {r['comp_brand']} | حجم: {r['my_size']} vs {r['comp_size']}")

# اختبار تحويل النتائج إلى الشكل العربي (كما في main.py)
print(f"\n🔍 اختبار تحويل النتائج إلى الشكل العربي:")
raise_list = []
lower_list = []
keep_list = []
missing_list = []
all_list = []

for r in results:
    row = {
        'المنتج': r['my_name'],
        'السعر': r['my_price'],
        'الماركة': r.get('my_brand', ''),
        'الحجم': r.get('my_size', ''),
        'التركيز': r.get('my_conc', ''),
        'النوع': r.get('my_type', ''),
        'اسم المنافس': r.get('comp_name', ''),
        'سعر المنافس': r.get('comp_price', 0),
        'أقل سعر منافس': r.get('comp_price', 0),
        'ماركة المنافس': r.get('comp_brand', ''),
        'حجم المنافس': r.get('comp_size', ''),
        'تركيز المنافس': r.get('comp_conc', ''),
        'المنافس': r.get('competitor', ''),
        'الفرق': r.get('diff', 0),
        'النسبة %': r.get('diff_pct', 0),
        'الثقة %': r.get('confidence', 0),
        'مرحلة المطابقة': r.get('match_stage', ''),
        'سبب المطابقة': r.get('match_reason', ''),
    }
    
    # تحديد الخطورة
    diff_pct = abs(r.get('diff_pct', 0))
    if diff_pct > 30:
        row['الخطورة'] = 'عالية'
    elif diff_pct > 15:
        row['الخطورة'] = 'متوسطة'
    else:
        row['الخطورة'] = 'منخفضة'
    
    # السعر الموصى
    comp_price = r.get('comp_price', 0)
    if comp_price > 0:
        row['السعر الموصى'] = round(comp_price * 0.95, 2)
    else:
        row['السعر الموصى'] = r['my_price']
    
    all_list.append(row)
    
    if r['category'] == 'raise_price':
        raise_list.append(row)
    elif r['category'] == 'lower_price':
        lower_list.append(row)
    elif r['category'] == 'keep_price':
        keep_list.append(row)
    elif r['category'] == 'missing':
        missing_list.append(row)

raise_df = pd.DataFrame(raise_list) if raise_list else pd.DataFrame()
lower_df = pd.DataFrame(lower_list) if lower_list else pd.DataFrame()
keep_df = pd.DataFrame(keep_list) if keep_list else pd.DataFrame()
missing_df = pd.DataFrame(missing_list) if missing_list else pd.DataFrame()
all_df = pd.DataFrame(all_list) if all_list else pd.DataFrame()

print(f"  رفع: {len(raise_df)} | خفض: {len(lower_df)} | موافق: {len(keep_df)} | مفقود: {len(missing_df)} | الكل: {len(all_df)}")

# التحقق من الأعمدة
expected_cols = ['المنتج', 'السعر', 'اسم المنافس', 'سعر المنافس', 'الفرق', 'النسبة %', 'الثقة %', 'الخطورة', 'السعر الموصى']
if not raise_df.empty:
    for col in expected_cols:
        exists = col in raise_df.columns
        print(f"  {'✅' if exists else '❌'} {col}")

print(f"\n✅ الاختبار الشامل اكتمل!")
print(f"   المنتجات: {len(results)}")
print(f"   المطابقات: {matched} ({matched/len(results)*100:.1f}%)")
print(f"   الدقة: {accuracy:.1f}%")
print(f"   الوقت: {elapsed:.1f} ثانية")
