"""
اختبار لتحديد العتبة المثالية - فحص المطابقات بثقة منخفضة
"""
import pandas as pd
import os
import sys
import time
from rapidfuzz import fuzz

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import normalize_columns, _get_name, _get_price, extract_brand, extract_size
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

# عينة 500 منتج
indices = list(range(0, len(store_df), 15))[:500]
sample_df = store_df.iloc[indices]

print(f"📊 عينة: {len(sample_df)} منتج")

# تشغيل المطابقة
results = run_smart_matching(sample_df, comp_df, use_gemini=False)

# تحليل المطابقات حسب مستوى الثقة
print(f"\n📊 توزيع الثقة:")
matched = [r for r in results if r['category'] != 'missing']
print(f"   مطابقات: {len(matched)}")

# فحص المطابقات بثقة 75-80% (المنطقة الرمادية)
print(f"\n🔍 مطابقات بثقة 75-80% (المنطقة الرمادية):")
gray_zone = [r for r in matched if 75 <= r['confidence'] < 80]
print(f"   عدد: {len(gray_zone)}")

wrong_in_gray = 0
for r in gray_zone[:30]:
    my_name = r['my_name']
    comp_name = r['comp_name']
    conf = r['confidence']
    
    # تحقق يدوي: هل الماركة واسم المنتج متطابقان؟
    my_brand = extract_brand(my_name) or ""
    comp_brand = extract_brand(comp_name) or ""
    
    # استخراج اسم المنتج بدون الماركة
    my_clean = my_name.lower().replace(my_brand.lower(), "").strip() if my_brand else my_name.lower()
    comp_clean = comp_name.lower().replace(comp_brand.lower(), "").strip() if comp_brand else comp_name.lower()
    
    # مقارنة الأسماء النظيفة
    clean_score = fuzz.token_sort_ratio(my_clean, comp_clean)
    
    is_same_brand = True
    if my_brand and comp_brand:
        is_same_brand = light_normalize(my_brand) == light_normalize(comp_brand) or fuzz.ratio(my_brand.lower(), comp_brand.lower()) >= 70
    
    is_likely_correct = is_same_brand and clean_score >= 50
    
    emoji = "✅" if is_likely_correct else "❌"
    print(f"  {emoji} [{conf:.0f}%] {my_name[:45]}")
    print(f"     ← {comp_name[:45]}")
    if not is_likely_correct:
        wrong_in_gray += 1
        print(f"     ⚠️ ماركة: {my_brand}→{comp_brand} | اسم: {clean_score}%")

print(f"\n   خاطئة في المنطقة الرمادية: {wrong_in_gray}/{len(gray_zone[:30])}")

# فحص المطابقات بثقة 80-85%
print(f"\n🔍 مطابقات بثقة 80-85%:")
mid_zone = [r for r in matched if 80 <= r['confidence'] < 85]
print(f"   عدد: {len(mid_zone)}")

wrong_in_mid = 0
for r in mid_zone[:20]:
    my_name = r['my_name']
    comp_name = r['comp_name']
    conf = r['confidence']
    
    my_brand = extract_brand(my_name) or ""
    comp_brand = extract_brand(comp_name) or ""
    
    my_clean = my_name.lower().replace(my_brand.lower(), "").strip() if my_brand else my_name.lower()
    comp_clean = comp_name.lower().replace(comp_brand.lower(), "").strip() if comp_brand else comp_name.lower()
    clean_score = fuzz.token_sort_ratio(my_clean, comp_clean)
    
    is_same_brand = True
    if my_brand and comp_brand:
        is_same_brand = light_normalize(my_brand) == light_normalize(comp_brand) or fuzz.ratio(my_brand.lower(), comp_brand.lower()) >= 70
    
    is_likely_correct = is_same_brand and clean_score >= 50
    
    emoji = "✅" if is_likely_correct else "❌"
    print(f"  {emoji} [{conf:.0f}%] {my_name[:45]}")
    print(f"     ← {comp_name[:45]}")
    if not is_likely_correct:
        wrong_in_mid += 1
        print(f"     ⚠️ ماركة: {my_brand}→{comp_brand} | اسم: {clean_score}%")

print(f"\n   خاطئة في 80-85%: {wrong_in_mid}/{len(mid_zone[:20])}")

# فحص المطابقات بثقة 85%+
print(f"\n🔍 مطابقات بثقة 85%+:")
high_zone = [r for r in matched if r['confidence'] >= 85]
print(f"   عدد: {len(high_zone)}")

wrong_in_high = 0
for r in high_zone[:20]:
    my_name = r['my_name']
    comp_name = r['comp_name']
    conf = r['confidence']
    
    my_brand = extract_brand(my_name) or ""
    comp_brand = extract_brand(comp_name) or ""
    
    is_same_brand = True
    if my_brand and comp_brand:
        is_same_brand = light_normalize(my_brand) == light_normalize(comp_brand) or fuzz.ratio(my_brand.lower(), comp_brand.lower()) >= 70
    
    emoji = "✅" if is_same_brand else "❌"
    print(f"  {emoji} [{conf:.0f}%] {my_name[:45]}")
    print(f"     ← {comp_name[:45]}")
    if not is_same_brand:
        wrong_in_high += 1

print(f"\n   خاطئة في 85%+: {wrong_in_high}/{len(high_zone[:20])}")

# الخلاصة
print(f"\n" + "=" * 60)
print(f"📊 الخلاصة:")
print(f"   75-80%: {wrong_in_gray} خاطئة من {len(gray_zone[:30])}")
print(f"   80-85%: {wrong_in_mid} خاطئة من {len(mid_zone[:20])}")
print(f"   85%+: {wrong_in_high} خاطئة من {len(high_zone[:20])}")
