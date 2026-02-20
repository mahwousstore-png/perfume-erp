"""
اختبار دقة المحرك v3.1 مع عينة متنوعة
"""
import pandas as pd
import os
import sys
import time
from rapidfuzz import fuzz

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import normalize_columns, extract_brand
from engine_v2 import run_smart_matching, light_normalize

DATA_DIR = "test_data"

# تحميل البيانات
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

# عينة متنوعة
indices = list(range(0, len(store_df), 75))[:100]
sample_df = store_df.iloc[indices]

print(f"📊 عينة: {len(sample_df)} منتج | منافسين: {len(comp_df)}")

# تشغيل المطابقة
start = time.time()
results = run_smart_matching(sample_df, comp_df, use_gemini=False)
elapsed = time.time() - start

print(f"⏱️ الوقت: {elapsed:.1f} ثانية")

# تحليل
categories = {}
stages = {}
for r in results:
    categories[r['category']] = categories.get(r['category'], 0) + 1
    stages[r['match_stage']] = stages.get(r['match_stage'], 0) + 1

print(f"\n📊 التصنيفات:")
for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
    pct = count / len(results) * 100
    emoji = {'raise_price': '🔴', 'lower_price': '🟡', 'keep_price': '🟢', 'missing': '🔵'}.get(cat, '❓')
    print(f"  {emoji} {cat}: {count} ({pct:.1f}%)")

matched = sum(1 for r in results if r['category'] != 'missing')
print(f"\n  نسبة المطابقة: {matched}/{len(results)} ({matched/len(results)*100:.1f}%)")

# التحقق من الدقة
print(f"\n🔍 التحقق من دقة المطابقات:")
correct = 0
wrong = 0
uncertain = 0

for r in results:
    if r['category'] == 'missing':
        continue
    
    my_name = r['my_name']
    comp_name = r['comp_name']
    my_brand = extract_brand(my_name)
    comp_brand = extract_brand(comp_name)
    my_size = r['my_size']
    comp_size = r['comp_size']
    conf = r['confidence']
    
    # تحقق الماركة
    brand_ok = True
    if my_brand and comp_brand:
        my_b = light_normalize(my_brand)
        comp_b = light_normalize(comp_brand)
        brand_ok = my_b == comp_b or fuzz.ratio(my_b, comp_b) >= 80
    
    # تحقق الحجم
    size_ok = True
    if my_size > 0 and comp_size > 0:
        size_ok = abs(my_size - comp_size) <= 10
    
    # تحقق الاسم (يجب أن يكون المنتج نفسه وليس منتج آخر من نفس الماركة)
    my_light = light_normalize(my_name)
    comp_light = light_normalize(comp_name)
    name_score = fuzz.token_sort_ratio(my_light, comp_light)
    name_ok = name_score >= 65
    
    is_correct = brand_ok and size_ok and name_ok
    
    if is_correct:
        correct += 1
        print(f"  ✅ [{conf:.0f}%] {my_name[:45]}")
        print(f"     ← {comp_name[:45]}")
    else:
        wrong += 1
        issues = []
        if not brand_ok:
            issues.append(f"ماركة: {my_brand}≠{comp_brand}")
        if not size_ok:
            issues.append(f"حجم: {my_size}≠{comp_size}")
        if not name_ok:
            issues.append(f"اسم: {name_score}%")
        print(f"  ❌ [{conf:.0f}%] {my_name[:45]}")
        print(f"     ← {comp_name[:45]}")
        print(f"     مشاكل: {', '.join(issues)}")

total_checked = correct + wrong
if total_checked > 0:
    accuracy = correct / total_checked * 100
    print(f"\n📊 الدقة: {correct}/{total_checked} ({accuracy:.1f}%)")
    print(f"   صحيح: {correct} | خطأ: {wrong}")
else:
    print("\n⚠️ لا توجد مطابقات للتحقق!")

# عينة من المفقودة
print(f"\n🔵 عينة من المفقودة:")
missing_count = 0
for r in results:
    if r['category'] == 'missing' and missing_count < 5:
        print(f"  - {r['my_name'][:60]}")
        missing_count += 1
