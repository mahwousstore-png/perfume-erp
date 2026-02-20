"""
تشخيص لماذا المنتجات لا تُطابق
"""
import pandas as pd
import os
import sys
from rapidfuzz import fuzz

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import normalize_columns, _get_name, _get_price, extract_size
from engine_v2 import extract_brand_dynamic, normalize_for_matching

DATA_DIR = "test_data"

# تحميل البيانات
store_df = pd.read_csv(f"{DATA_DIR}/store.csv", encoding="utf-8-sig")
store_df = normalize_columns(store_df)

# تحميل كل ملفات المنافسين
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

print(f"منتجات المتجر: {len(store_df)}")
print(f"منتجات المنافسين: {len(all_comp)}")

# منتج اختبار
test_product = "عطر لطافة أمير العود أو دو برفيوم 100 مل"
test_norm = normalize_for_matching(test_product)
test_brand = extract_brand_dynamic(test_product)
test_size = extract_size(test_product)

print(f"\n🔍 منتج الاختبار: {test_product}")
print(f"   مطبّع: {test_norm}")
print(f"   ماركة: {test_brand}")
print(f"   حجم: {test_size}")

# البحث في المنافسين عن "لطافة" أو "lattafa"
print(f"\n📋 منتجات المنافسين التي تحتوي 'لطافة' أو 'lattafa':")
lattafa_comps = []
for cp in all_comp:
    name = _get_name(cp)
    if not name:
        continue
    lower = name.lower()
    if 'لطافة' in lower or 'lattafa' in lower or 'لتافة' in lower:
        lattafa_comps.append((name, _get_price(cp), cp.get('_competitor', '')))

print(f"   وجدت: {len(lattafa_comps)} منتج")
for name, price, comp in lattafa_comps[:20]:
    norm = normalize_for_matching(name)
    score = fuzz.token_set_ratio(test_norm, norm)
    print(f"   [{score}%] {name[:60]} | {price} | {comp}")

# البحث عن "أمير" في المنافسين
print(f"\n📋 منتجات المنافسين التي تحتوي 'أمير' أو 'ameer' أو 'amir':")
ameer_comps = []
for cp in all_comp:
    name = _get_name(cp)
    if not name:
        continue
    lower = name.lower()
    if 'أمير' in lower or 'ameer' in lower or 'amir' in lower:
        ameer_comps.append((name, _get_price(cp), cp.get('_competitor', '')))

print(f"   وجدت: {len(ameer_comps)} منتج")
for name, price, comp in ameer_comps[:20]:
    norm = normalize_for_matching(name)
    score = fuzz.token_set_ratio(test_norm, norm)
    print(f"   [{score}%] {name[:60]} | {price} | {comp}")

# أعمدة المنافسين
print(f"\n📋 أعمدة ملف المنافس الأول:")
first_comp_file = comp_files[0]
df = pd.read_csv(f"{DATA_DIR}/{first_comp_file}", encoding="utf-8-sig")
print(f"   الأعمدة الأصلية: {list(df.columns)}")
df = normalize_columns(df)
print(f"   بعد التطبيع: {list(df.columns)}")
print(f"   عينة أول 3 صفوف:")
for _, row in df.head(3).iterrows():
    name = _get_name(row.to_dict())
    price = _get_price(row.to_dict())
    print(f"   - {name[:60]} | سعر: {price}")

# أعمدة المتجر
print(f"\n📋 أعمدة ملف المتجر:")
print(f"   {list(store_df.columns)}")
print(f"   عينة أول 3 صفوف:")
for _, row in store_df.head(3).iterrows():
    name = _get_name(row.to_dict())
    price = _get_price(row.to_dict())
    print(f"   - {name[:60]} | سعر: {price}")

# البحث الشامل: أعلى 10 مطابقات لمنتج الاختبار
print(f"\n🔍 أعلى 10 مطابقات لمنتج الاختبار:")
scores = []
for cp in all_comp[:5000]:  # أول 5000 فقط للسرعة
    name = _get_name(cp)
    if not name:
        continue
    norm = normalize_for_matching(name)
    score = fuzz.token_set_ratio(test_norm, norm)
    if score >= 50:
        scores.append((score, name, _get_price(cp), cp.get('_competitor', '')))

scores.sort(key=lambda x: -x[0])
for score, name, price, comp in scores[:10]:
    print(f"   [{score}%] {name[:60]} | {price} | {comp}")
