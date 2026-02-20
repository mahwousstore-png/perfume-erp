"""
اختبار شامل لمحرك V3 مع البيانات الفعلية
"""
import pandas as pd
import os
import sys
import time
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import normalize_columns, _get_name, extract_brand
from engine_v2 import run_smart_matching, extract_brand_dynamic

DATA_DIR = "test_data"

print("=" * 70)
print("اختبار شامل لمحرك V3 مع البيانات الفعلية")
print("=" * 70)

# ====== 1. اختبار extract_brand_dynamic ======
print("\n1️⃣ اختبار extract_brand_dynamic:")
test_names = [
    ("عطر ميسوني ويف الرجالي او دو تواليت 100مل", "ميسوني ويف"),
    ("تستر بوشرون كواتر بور فيم او دو بارفيوم 100مل", "بوشرون كواتر"),
    ("عطر لانكم عود بوكيه أو دو برفان 100مل", "لانكم عود"),
    ("عطر لطافة أمير العود أو دو برفيوم 100 مل", "لطافة"),  # معروف
    ("عطر ديور سوفاج او دو بارفيوم 100مل", "ديور"),  # معروف
    ("عطر ريممبر مي برفيوم 75 مل", "ريممبر مي"),
    ("عطر قوتشي قلتي بور فيم او دو بارفيوم 90 مل", "قوتشي قلتي"),
]

for name, expected_contains in test_names:
    brand = extract_brand_dynamic(name)
    status = "✅" if expected_contains.split()[0].lower() in brand.lower() else "⚠️"
    print(f"  {status} '{name[:50]}' → '{brand}' (متوقع يحتوي: {expected_contains})")

# ====== 2. تحميل البيانات ======
print("\n2️⃣ تحميل البيانات:")
store_df = pd.read_csv(f"{DATA_DIR}/store.csv", encoding="utf-8-sig")
store_df = normalize_columns(store_df)
print(f"  منتجات المتجر: {len(store_df)}")

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
print(f"  منتجات المنافسين: {len(comp_df)}")

# ====== 3. اختبار extract_brand_dynamic على كل المنتجات ======
print("\n3️⃣ نسبة استخراج الماركات:")
store_records = store_df.to_dict('records')

old_brand_count = sum(1 for r in store_records if extract_brand(_get_name(r)))
new_brand_count = sum(1 for r in store_records if extract_brand_dynamic(_get_name(r)))

print(f"  extract_brand القديم: {old_brand_count}/{len(store_records)} ({old_brand_count/len(store_records)*100:.1f}%)")
print(f"  extract_brand_dynamic الجديد: {new_brand_count}/{len(store_records)} ({new_brand_count/len(store_records)*100:.1f}%)")

# ====== 4. اختبار run_smart_matching مع 100 منتج ======
print("\n4️⃣ اختبار run_smart_matching (100 منتج، بدون Gemini):")
sample_store = store_df.head(100)

start_time = time.time()
results = run_smart_matching(sample_store, comp_df, use_gemini=False)
elapsed = time.time() - start_time

print(f"  الوقت: {elapsed:.1f} ثانية")
print(f"  عدد النتائج: {len(results)}")

# تحليل التصنيفات
categories = {}
for r in results:
    cat = r.get('category', 'unknown')
    categories[cat] = categories.get(cat, 0) + 1

print(f"  التصنيفات:")
for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
    pct = count / len(results) * 100
    print(f"    {cat}: {count} ({pct:.1f}%)")

# نسبة المطابقة
matched = sum(1 for r in results if r['category'] != 'missing')
print(f"  نسبة المطابقة: {matched}/{len(results)} ({matched/len(results)*100:.1f}%)")

# تحليل المراحل
stages = {}
for r in results:
    stage = r.get('match_stage', 'none')
    stages[stage] = stages.get(stage, 0) + 1

print(f"  المراحل:")
for stage, count in sorted(stages.items(), key=lambda x: -x[1]):
    print(f"    {stage}: {count}")

# ====== 5. التحقق من الحقول المطلوبة ======
print("\n5️⃣ التحقق من الحقول:")
required_fields = [
    'my_name', 'my_price', 'my_brand', 'my_size', 'my_conc', 'my_type',
    'comp_name', 'comp_price', 'comp_brand', 'comp_size', 'comp_conc',
    'competitor', 'diff', 'diff_pct', 'category', 'confidence', 'match_reason', 'match_stage'
]

missing_fields = set()
for r in results:
    for f in required_fields:
        if f not in r:
            missing_fields.add(f)

if missing_fields:
    print(f"  ❌ حقول مفقودة: {missing_fields}")
else:
    print(f"  ✅ جميع {len(required_fields)} حقل موجودة")

# ====== 6. عينة من النتائج ======
print("\n6️⃣ عينة من النتائج:")
for r in results[:10]:
    cat = r['category']
    my_name = r['my_name'][:40]
    comp_name = (r['comp_name'] or 'N/A')[:40]
    conf = r['confidence']
    stage = r['match_stage']
    diff = r['diff']
    diff_pct = r['diff_pct']
    
    emoji = {'raise_price': '🔴', 'lower_price': '🟡', 'keep_price': '🟢', 'missing': '🔵'}.get(cat, '❓')
    print(f"  {emoji} {my_name}")
    print(f"     ← {comp_name} | ثقة: {conf}% | مرحلة: {stage} | فرق: {diff:.0f} ({diff_pct:.1f}%)")

# ====== 7. التحقق من دقة المطابقة ======
print("\n7️⃣ التحقق من دقة المطابقة (عينة 20):")
correct = 0
wrong = 0
for r in results[:20]:
    if r['category'] == 'missing':
        continue
    
    my_name = r['my_name']
    comp_name = r['comp_name']
    my_size = r['my_size']
    comp_size = r['comp_size']
    my_brand_d = extract_brand_dynamic(my_name)
    comp_brand_d = extract_brand_dynamic(comp_name)
    
    # تحقق: الحجم يجب أن يكون قريب
    size_ok = True
    if my_size > 0 and comp_size > 0:
        size_ok = abs(my_size - comp_size) <= 15
    
    # تحقق: الماركة الديناميكية يجب أن تكون متشابهة
    brand_ok = True
    if my_brand_d and comp_brand_d:
        from rapidfuzz import fuzz
        brand_ok = fuzz.ratio(my_brand_d, comp_brand_d) >= 50
    
    is_correct = size_ok and brand_ok
    if is_correct:
        correct += 1
    else:
        wrong += 1
        print(f"  ⚠️ خطأ محتمل:")
        print(f"     متجر: {my_name[:50]} (ماركة: {my_brand_d}, حجم: {my_size})")
        print(f"     منافس: {comp_name[:50]} (ماركة: {comp_brand_d}, حجم: {comp_size})")

total_checked = correct + wrong
if total_checked > 0:
    print(f"\n  دقة المطابقة: {correct}/{total_checked} ({correct/total_checked*100:.1f}%)")

# ====== 8. اختبار التحويل العربي ======
print("\n8️⃣ اختبار التحويل العربي:")
raise_list = []
lower_list = []
approved_list = []
missing_list = []
all_list = []

for r in results:
    cat = r['category']
    risk = 'حرج' if abs(r['diff_pct']) > 30 else 'متوسط' if abs(r['diff_pct']) > 15 else 'عادي'
    recommended = round(r['comp_price'] * 0.997, 2) if r['comp_price'] > 0 else r['my_price']
    
    row = {
        'المقارنة': f"{r['my_name'][:30]} 🆚 {(r['comp_name'] or '')[:30]}",
        'المنتج': r['my_name'],
        'ماركتنا': r['my_brand'],
        'تركيزنا': r['my_conc'],
        'حجمنا': r['my_size'],
        'ماركة المنافس': r['comp_brand'],
        'تركيز المنافس': r['comp_conc'],
        'حجم المنافس': r['comp_size'],
        'اسم المنافس': r['comp_name'] or '',
        'السعر': r['my_price'],
        'أقل سعر منافس': r['comp_price'],
        'سعر المنافس': r['comp_price'],
        'الفرق': r['diff'],
        'النسبة %': r['diff_pct'],
        'الثقة %': r['confidence'],
        'الخطورة': risk,
        'السعر الموصى': recommended,
        'المنافس': r['competitor'],
        'التصنيف': cat,
    }
    
    all_list.append(row)
    if cat == 'raise_price':
        raise_list.append(row)
    elif cat == 'lower_price':
        lower_list.append(row)
    elif cat == 'keep_price':
        approved_list.append(row)
    elif cat == 'missing':
        missing_list.append({
            'المنتج': r['my_name'],
            'النوع': r['my_type'],
            'الحجم': r['my_size'],
            'السعر': r['my_price'],
            'المنافس': 'جميع المنافسين'
        })

df_raise = pd.DataFrame(raise_list) if raise_list else pd.DataFrame()
df_lower = pd.DataFrame(lower_list) if lower_list else pd.DataFrame()
df_approved = pd.DataFrame(approved_list) if approved_list else pd.DataFrame()
df_missing = pd.DataFrame(missing_list) if missing_list else pd.DataFrame()
df_all = pd.DataFrame(all_list) if all_list else pd.DataFrame()

print(f"  رفع سعر: {len(df_raise)}")
print(f"  خفض سعر: {len(df_lower)}")
print(f"  موافق: {len(df_approved)}")
print(f"  مفقود: {len(df_missing)}")
print(f"  الكل: {len(df_all)}")

# التحقق من الأعمدة
expected = ['المنتج', 'اسم المنافس', 'السعر', 'أقل سعر منافس', 'الفرق', 'النسبة %', 'الثقة %', 'الخطورة', 'السعر الموصى']
if not df_raise.empty:
    missing = [c for c in expected if c not in df_raise.columns]
    print(f"  {'❌ أعمدة مفقودة: ' + str(missing) if missing else '✅ جميع الأعمدة موجودة في df_raise'}")

if not df_missing.empty:
    expected_m = ['المنتج', 'النوع', 'الحجم', 'السعر', 'المنافس']
    missing = [c for c in expected_m if c not in df_missing.columns]
    print(f"  {'❌ أعمدة مفقودة: ' + str(missing) if missing else '✅ جميع الأعمدة موجودة في df_missing'}")

# JSON serialization
try:
    for key, df in [('raise', df_raise), ('lower', df_lower), ('approved', df_approved), ('missing', df_missing), ('all', df_all)]:
        if isinstance(df, pd.DataFrame) and not df.empty:
            json.dumps(df.head(2).to_dict('records'), ensure_ascii=False, default=str)
    print(f"  ✅ JSON serialization OK")
except Exception as e:
    print(f"  ❌ JSON error: {e}")

print("\n" + "=" * 70)
print("✅ اكتمل الاختبار الشامل!")
print("=" * 70)
