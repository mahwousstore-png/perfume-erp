"""
اختبار مع عينة متنوعة من المنتجات
"""
import pandas as pd
import os
import sys
from rapidfuzz import fuzz

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import normalize_columns, _get_name, extract_brand
from engine_v2 import run_smart_matching, normalize_for_matching

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

# عينة متنوعة: كل 75 منتج نأخذ واحد (100 منتج من 7505)
indices = list(range(0, len(store_df), 75))[:100]
sample_df = store_df.iloc[indices]

print(f"📊 عينة متنوعة: {len(sample_df)} منتج")
print(f"📊 منتجات المنافسين: {len(comp_df)}")

# عرض أسماء المنتجات في العينة
print("\n📋 عينة المنتجات:")
for _, row in sample_df.head(20).iterrows():
    name = _get_name(row.to_dict())
    brand = extract_brand(name)
    print(f"  - {name[:60]} | ماركة: {brand or 'N/A'}")

# تشغيل المطابقة
print("\n🚀 تشغيل المطابقة...")
results = run_smart_matching(sample_df, comp_df, use_gemini=False)

# تحليل النتائج
categories = {}
stages = {}
for r in results:
    cat = r.get('category', 'unknown')
    categories[cat] = categories.get(cat, 0) + 1
    stage = r.get('match_stage', 'none')
    stages[stage] = stages.get(stage, 0) + 1

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

# عرض المطابقات الناجحة
print(f"\n✅ المطابقات الناجحة:")
for r in results:
    if r['category'] != 'missing':
        my = r['my_name'][:40]
        comp = r['comp_name'][:40]
        conf = r['confidence']
        diff = r['diff']
        diff_pct = r['diff_pct']
        cat = r['category']
        emoji = {'raise_price': '🔴', 'lower_price': '🟡', 'keep_price': '🟢'}.get(cat, '❓')
        print(f"  {emoji} {my}")
        print(f"     ← {comp} | ثقة: {conf:.0f}% | فرق: {diff:.0f} ({diff_pct:.1f}%)")

# عرض بعض المفقودة مع أقرب مطابقة
print(f"\n🔵 عينة من المفقودة (مع أقرب مطابقة):")
missing_count = 0
for r in results:
    if r['category'] == 'missing' and missing_count < 10:
        my_name = r['my_name']
        my_norm = normalize_for_matching(my_name)
        
        # البحث عن أقرب مطابقة
        best_score = 0
        best_name = ""
        for cp in all_comp[:5000]:
            cp_name = _get_name(cp)
            if not cp_name:
                continue
            cp_norm = normalize_for_matching(cp_name)
            score = fuzz.token_set_ratio(my_norm, cp_norm)
            if score > best_score:
                best_score = score
                best_name = cp_name
        
        print(f"  🔵 {my_name[:50]}")
        print(f"     أقرب: [{best_score}%] {best_name[:50]}")
        missing_count += 1
