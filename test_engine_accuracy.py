"""
المرحلة 2: اختبار محرك المطابقة منتج بمنتج مع التحقق من الدقة
يختبر عينة من المنتجات الفعلية ويتحقق من صحة المطابقة
"""
import pandas as pd
import os
import sys
import time
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import normalize_columns, _get_name, _get_price, extract_brand, extract_size, classify_product
from engine_v2 import SmartMatcher, run_smart_matching

DATA_DIR = "test_data"

print("=" * 70)
print("المرحلة 2: اختبار محرك المطابقة منتج بمنتج")
print("=" * 70)

# تحميل البيانات
store_df = pd.read_csv(f"{DATA_DIR}/store.csv", encoding="utf-8-sig")
store_df = normalize_columns(store_df)

# تحميل جميع المنافسين
comp_files = [f for f in os.listdir(DATA_DIR) if f != "store.csv" and f.endswith(".csv")]
all_comp_records = []
comp_names_map = {}

for comp_file in comp_files:
    filepath = f"{DATA_DIR}/{comp_file}"
    df = pd.read_csv(filepath, encoding="utf-8-sig")
    df = normalize_columns(df)
    comp_name = comp_file.replace("متجر", "").replace("متحر", "").replace(".csv", "")
    records = df.to_dict('records')
    for r in records:
        r['_competitor'] = comp_name
    all_comp_records.extend(records)
    comp_names_map[comp_file] = comp_name

print(f"\n📊 البيانات المحملة:")
print(f"  منتجات المتجر: {len(store_df)}")
print(f"  منتجات المنافسين: {len(all_comp_records)}")
print(f"  المنافسين: {list(comp_names_map.values())}")

# ====== اختبار 1: extract_brand على عينة فعلية ======
print("\n" + "=" * 70)
print("اختبار 1: استخراج الماركات من المنتجات الفعلية")
print("=" * 70)

store_records = store_df.to_dict('records')
brand_counts = {}
no_brand = []
for r in store_records[:500]:  # أول 500 منتج
    name = _get_name(r)
    brand = extract_brand(name)
    if brand:
        brand_counts[brand] = brand_counts.get(brand, 0) + 1
    else:
        no_brand.append(name[:60])

print(f"  ماركات مكتشفة (أول 500 منتج):")
for brand, count in sorted(brand_counts.items(), key=lambda x: -x[1])[:20]:
    print(f"    {brand}: {count}")
print(f"  بدون ماركة: {len(no_brand)}/{500}")
if no_brand[:5]:
    print(f"  أمثلة بدون ماركة:")
    for n in no_brand[:5]:
        print(f"    - {n}")

# ====== اختبار 2: SmartMatcher مع عينة فعلية ======
print("\n" + "=" * 70)
print("اختبار 2: SmartMatcher - مطابقة 20 منتج فعلي")
print("=" * 70)

# اختيار 20 منتج متنوع
test_products = []
brands_seen = set()
for r in store_records:
    name = _get_name(r)
    brand = extract_brand(name)
    price = _get_price(r)
    if price > 0 and name and brand and brand not in brands_seen:
        test_products.append(r)
        brands_seen.add(brand)
        if len(test_products) >= 10:
            break

# إضافة منتجات بدون ماركة
for r in store_records:
    name = _get_name(r)
    brand = extract_brand(name)
    price = _get_price(r)
    if price > 0 and name and not brand:
        test_products.append(r)
        if len(test_products) >= 20:
            break

# إنشاء matcher
matcher = SmartMatcher(all_comp_records)

correct_matches = 0
wrong_matches = 0
no_matches = 0
results_detail = []

for i, product in enumerate(test_products):
    name = _get_name(product)
    price = _get_price(product)
    brand = extract_brand(name)
    size = extract_size(name)
    
    match = matcher.find_best_match(product)
    
    if match:
        comp_name = _get_name(match['match'])
        comp_price = _get_price(match['match'])
        confidence = match['confidence']
        stage = match['stage']
        comp_brand = extract_brand(comp_name)
        comp_size = extract_size(comp_name)
        
        # تحقق يدوي من الصحة
        brand_match = (brand.lower() == comp_brand.lower()) if brand and comp_brand else True
        size_match = (size == comp_size) if size > 0 and comp_size > 0 else True
        
        is_correct = brand_match and size_match
        
        status = "✅" if is_correct else "⚠️"
        if is_correct:
            correct_matches += 1
        else:
            wrong_matches += 1
        
        diff = price - comp_price
        diff_pct = (diff / comp_price * 100) if comp_price > 0 else 0
        
        print(f"\n  {status} [{i+1}] {name[:50]}")
        print(f"      ماركة: {brand} | حجم: {size} | سعر: {price}")
        print(f"      ← {comp_name[:50]}")
        print(f"      ماركة: {comp_brand} | حجم: {comp_size} | سعر: {comp_price}")
        print(f"      الثقة: {confidence}% | المرحلة: {stage} | الفرق: {diff:.1f} ({diff_pct:.1f}%)")
        if not is_correct:
            print(f"      ⚠️ سبب الخطأ: brand_match={brand_match}, size_match={size_match}")
        
        results_detail.append({
            'product': name[:50],
            'match': comp_name[:50],
            'confidence': confidence,
            'stage': stage,
            'correct': is_correct,
            'diff': diff,
            'diff_pct': round(diff_pct, 1)
        })
    else:
        no_matches += 1
        print(f"\n  🔵 [{i+1}] {name[:50]}")
        print(f"      ماركة: {brand} | حجم: {size} | سعر: {price}")
        print(f"      ← لم يُعثر على مطابقة")

print(f"\n📊 ملخص المطابقة (20 منتج):")
print(f"  ✅ صحيحة: {correct_matches}")
print(f"  ⚠️ مشكوك فيها: {wrong_matches}")
print(f"  🔵 بدون مطابقة: {no_matches}")
print(f"  دقة المطابقة: {correct_matches}/{correct_matches + wrong_matches} = {correct_matches/(correct_matches + wrong_matches)*100:.1f}%" if (correct_matches + wrong_matches) > 0 else "  لا توجد مطابقات")

# ====== اختبار 3: run_smart_matching مع عينة صغيرة ======
print("\n" + "=" * 70)
print("اختبار 3: run_smart_matching الكامل (50 منتج)")
print("=" * 70)

# أخذ عينة 50 منتج
sample_store = store_df.head(50)
sample_comp = pd.DataFrame(all_comp_records[:2000])

start_time = time.time()
results = run_smart_matching(sample_store, sample_comp, use_gemini=False)
elapsed = time.time() - start_time

print(f"  الوقت: {elapsed:.1f} ثانية")
print(f"  عدد النتائج: {len(results)}")

# تحليل النتائج
categories = {}
for r in results:
    cat = r.get('category', 'unknown')
    categories[cat] = categories.get(cat, 0) + 1

print(f"  التصنيفات:")
for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
    print(f"    {cat}: {count}")

# التحقق من الحقول المطلوبة
required_fields = ['my_name', 'my_price', 'category']
missing_fields = []
for r in results[:5]:
    for f in required_fields:
        if f not in r:
            missing_fields.append(f)

if missing_fields:
    print(f"  ❌ حقول مفقودة: {set(missing_fields)}")
else:
    print(f"  ✅ جميع الحقول المطلوبة موجودة")

# عينة من النتائج
print(f"\n  عينة من النتائج:")
for r in results[:5]:
    cat = r.get('category', '?')
    my_name = r.get('my_name', '?')[:40]
    comp_name = r.get('comp_name', 'N/A')[:40] if r.get('comp_name') else 'N/A'
    conf = r.get('confidence', 0)
    print(f"    [{cat}] {my_name} ← {comp_name} ({conf}%)")

# ====== اختبار 4: التحقق من تحويل V2 إلى العربية ======
print("\n" + "=" * 70)
print("اختبار 4: تحويل نتائج V2 إلى الشكل العربي")
print("=" * 70)

# محاكاة التحويل كما في main.py
raise_list = []
lower_list = []
approved_list = []
missing_list = []
all_list = []

for r in results:
    cat = r.get('category', '')
    my_name = r.get('my_name', '')
    my_price = r.get('my_price', 0)
    comp_name = r.get('comp_name', '')
    comp_price = r.get('comp_price', 0)
    diff = r.get('diff', 0)
    diff_pct = r.get('diff_pct', 0)
    confidence = r.get('confidence', 0)
    brand = r.get('my_brand', '')
    comp_brand = r.get('comp_brand', '')
    size = r.get('my_size', '')
    comp_size = r.get('comp_size', '')
    conc = r.get('my_conc', '')
    comp_conc = r.get('comp_conc', '')
    competitor = r.get('competitor', '')
    
    risk = 'حرج' if abs(diff_pct) > 30 else 'متوسط' if abs(diff_pct) > 15 else 'عادي'
    recommended = round(comp_price * 0.997, 2) if comp_price > 0 else my_price
    
    row = {
        'المقارنة': f"{my_name[:30]} 🆚 {comp_name[:30]}" if comp_name else my_name[:60],
        'المنتج': my_name,
        'ماركتنا': brand,
        'تركيزنا': conc,
        'حجمنا': size,
        'ماركة المنافس': comp_brand,
        'تركيز المنافس': comp_conc,
        'حجم المنافس': comp_size,
        'اسم المنافس': comp_name,
        'السعر': my_price,
        'أقل سعر منافس': comp_price,
        'سعر المنافس': comp_price,
        'الفرق': round(diff, 2),
        'النسبة %': round(diff_pct, 2),
        'الثقة %': confidence,
        'الخطورة': risk,
        'السعر الموصى': recommended,
        'المنافس': competitor,
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
        missing_row = {
            'المنتج': my_name,
            'النوع': classify_product(my_name),
            'الحجم': size,
            'السعر': my_price,
            'المنافس': 'جميع المنافسين'
        }
        missing_list.append(missing_row)

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
if not df_raise.empty:
    expected_cols = ['المنتج', 'اسم المنافس', 'السعر', 'أقل سعر منافس', 'الفرق', 'النسبة %', 'الثقة %', 'الخطورة', 'السعر الموصى']
    missing_cols = [c for c in expected_cols if c not in df_raise.columns]
    if missing_cols:
        print(f"  ❌ أعمدة مفقودة في df_raise: {missing_cols}")
    else:
        print(f"  ✅ جميع الأعمدة المطلوبة موجودة في df_raise")

if not df_missing.empty:
    expected_cols = ['المنتج', 'النوع', 'الحجم', 'السعر', 'المنافس']
    missing_cols = [c for c in expected_cols if c not in df_missing.columns]
    if missing_cols:
        print(f"  ❌ أعمدة مفقودة في df_missing: {missing_cols}")
    else:
        print(f"  ✅ جميع الأعمدة المطلوبة موجودة في df_missing")

# ====== اختبار 5: التحقق من save_results_to_db ======
print("\n" + "=" * 70)
print("اختبار 5: التحقق من هيكل حفظ النتائج")
print("=" * 70)

results_dict = {
    "raise": df_raise,
    "lower": df_lower,
    "approved": df_approved,
    "missing": df_missing,
    "all": df_all,
}

# محاكاة _safe_df_len
def _safe_df_len(df):
    if df is None:
        return 0
    if isinstance(df, pd.DataFrame):
        return len(df) if not df.empty else 0
    if isinstance(df, list):
        return len(df)
    return 0

stats = {
    'total': _safe_df_len(df_all),
    'raise_count': _safe_df_len(df_raise),
    'lower_count': _safe_df_len(df_lower),
    'approved_count': _safe_df_len(df_approved),
    'missing_count': _safe_df_len(df_missing),
}

print(f"  الإحصائيات: {json.dumps(stats, ensure_ascii=False)}")

# التحقق من JSON serialization
try:
    for key, df in results_dict.items():
        if isinstance(df, pd.DataFrame) and not df.empty:
            records = df.to_dict('records')
            json_str = json.dumps(records[:2], ensure_ascii=False, default=str)
            print(f"  ✅ {key}: JSON serializable ({len(records)} records)")
except Exception as e:
    print(f"  ❌ JSON serialization error: {e}")

print("\n" + "=" * 70)
print("✅ اكتمل اختبار المحرك!")
print("=" * 70)
