"""
اختبار Gemini AI مع عينة من المنتجات المفقودة
لمعرفة إذا يمكنه إيجاد مطابقات إضافية
"""
import pandas as pd
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import normalize_columns, _get_name, _get_price, extract_brand, extract_size
from engine_v2 import run_smart_matching, light_normalize, GEMINI_AVAILABLE, SmartMatcher

DATA_DIR = "test_data"

print(f"🤖 Gemini متاح: {GEMINI_AVAILABLE}")

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

# أولاً: تشغيل بدون Gemini لتحديد المفقودة
print(f"\n📊 تشغيل بدون Gemini...")
# عينة 200 منتج
indices = list(range(0, len(store_df), 37))[:200]
sample_df = store_df.iloc[indices]

results_no_gemini = run_smart_matching(sample_df, comp_df, use_gemini=False)
missing_no_gemini = [r for r in results_no_gemini if r['category'] == 'missing']
matched_no_gemini = [r for r in results_no_gemini if r['category'] != 'missing']

print(f"   بدون Gemini: {len(matched_no_gemini)} مطابقة | {len(missing_no_gemini)} مفقود")

# ثانياً: تشغيل مع Gemini
print(f"\n🤖 تشغيل مع Gemini AI...")
start = time.time()
results_with_gemini = run_smart_matching(sample_df, comp_df, use_gemini=True)
elapsed = time.time() - start

missing_with_gemini = [r for r in results_with_gemini if r['category'] == 'missing']
matched_with_gemini = [r for r in results_with_gemini if r['category'] != 'missing']
gemini_matches = [r for r in results_with_gemini if r.get('match_stage') == 'gemini']

print(f"   مع Gemini: {len(matched_with_gemini)} مطابقة | {len(missing_with_gemini)} مفقود")
print(f"   مطابقات Gemini: {len(gemini_matches)}")
print(f"   الوقت: {elapsed:.1f} ثانية")

# مقارنة
new_matches = len(matched_with_gemini) - len(matched_no_gemini)
print(f"\n📊 المقارنة:")
print(f"   مطابقات جديدة بفضل Gemini: {new_matches}")
print(f"   تحسن: {new_matches / len(missing_no_gemini) * 100:.1f}% من المفقودة")

# عرض مطابقات Gemini
if gemini_matches:
    print(f"\n🤖 مطابقات Gemini:")
    for r in gemini_matches[:10]:
        print(f"  ✅ {r['my_name'][:50]}")
        print(f"     ← {r['comp_name'][:50]}")
        print(f"     ثقة: {r['confidence']:.0f}% | سبب: {r['match_reason'][:50]}")
