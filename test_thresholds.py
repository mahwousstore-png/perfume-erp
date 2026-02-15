#!/usr/bin/env python3
"""اختبار عتبات مختلفة لإيجاد التوازن الأمثل بين الدقة والتغطية"""
import sys, os, io, time
sys.path.insert(0, '.')
os.environ['GEMINI_API_KEY'] = os.environ.get('GEMINI_API_KEY', 'test')

import pandas as pd
from engine import normalize_columns

# تحميل البيانات
my_df = pd.read_csv("test_data/منتجاتمهووستنسيقتحيثالاسعار.csv")
my_df = normalize_columns(my_df)

comp_dfs = []
for f in sorted(os.listdir("test_data/")):
    if f.startswith("متج") or f.startswith("متح"):
        df = pd.read_csv(f"test_data/{f}")
        df = normalize_columns(df)
        name = f.replace('.csv', '')
        df['_competitor'] = name
        comp_dfs.append(df)

comp_df = pd.concat(comp_dfs, ignore_index=True)

# عينة 200 منتج متنوعة
import random
random.seed(42)
sample_indices = random.sample(range(len(my_df)), min(200, len(my_df)))
sample_df = my_df.iloc[sample_indices].copy()

# اختبار عتبات مختلفة
from engine_v2 import SmartMatcher, _get_name, _get_price, light_normalize, extract_brand, extract_size, extract_concentration, normalize_columns
from fuzzywuzzy import fuzz

# بناء المرشحين مرة واحدة
from collections import defaultdict
all_candidates = []
brand_index = defaultdict(list)
size_index = defaultdict(list)

comp_products = comp_df.to_dict('records')
for idx, cp in enumerate(comp_products):
    cp_name = _get_name(cp)
    if not cp_name: continue
    cp_price = _get_price(cp)
    if cp_price <= 0: continue
    cp_size = extract_size(cp_name)
    cp_brand = extract_brand(cp_name)
    cp_light = light_normalize(cp_name)
    entry = {"index": idx, "product": cp, "name": cp_name, "size": cp_size, "price": cp_price, "brand": cp_brand, "light": cp_light, "competitor": cp.get('_competitor', '')}
    all_candidates.append(entry)
    size_bucket = round(cp_size / 5) * 5 if cp_size > 0 else 0
    size_index[size_bucket].append(entry)
    if cp_brand:
        brand_index[cp_brand.lower()].append(entry)

print(f"المنافسين: {len(all_candidates)}")

# اختبار كل منتج مع عتبات مختلفة
# نجمع المرشحين لكل منتج أولاً
def get_candidates(my_name, my_brand, my_size):
    seen = set()
    candidates = []
    
    def add(entries):
        for e in entries:
            if e["index"] not in seen:
                seen.add(e["index"])
                candidates.append(e)
    
    if my_brand:
        add(brand_index.get(my_brand.lower(), []))
    
    size_bucket = round(my_size / 5) * 5 if my_size > 0 else 0
    if size_bucket > 0:
        for offset in [0, -5, 5, -10, 10]:
            b = size_bucket + offset
            if b > 0:
                add(size_index.get(b, []))
    
    if len(candidates) < 10:
        my_light = light_normalize(my_name)
        noise = {'عطر', 'او', 'دو', 'برفيوم', 'بارفيوم', 'تواليت', 'مل', 'للرجال', 'للنساء', 'النسائي', 'الرجالي', 'تستر'}
        my_words = set(my_light.split()) - noise
        for entry in all_candidates:
            if entry["index"] not in seen:
                entry_words = set(entry["light"].split()) - noise
                common = my_words & entry_words
                if len(common) >= 1:
                    quick = fuzz.token_set_ratio(my_light, entry["light"])
                    if quick >= 55:
                        seen.add(entry["index"])
                        candidates.append(entry)
                        if len(candidates) >= 50:
                            break
    return candidates

# جمع كل المرشحين
print("جمع المرشحين...")
product_candidates = []
for _, my_p in sample_df.iterrows():
    my_name = _get_name(my_p.to_dict())
    if not my_name: continue
    my_price = _get_price(my_p.to_dict())
    if my_price <= 0: continue
    my_brand = extract_brand(my_name)
    my_size = extract_size(my_name)
    candidates = get_candidates(my_name, my_brand, my_size)
    product_candidates.append((my_p.to_dict(), my_name, my_price, my_brand, my_size, candidates))

print(f"منتجات للاختبار: {len(product_candidates)}")

# اختبار عتبات مختلفة
thresholds = [
    {"name": "صارم جداً", "min_prod": 70, "min_word": 0.5, "min_adj": 82, "min_char": 65},
    {"name": "صارم", "min_prod": 65, "min_word": 0.4, "min_adj": 80, "min_char": 60},
    {"name": "متوسط", "min_prod": 60, "min_word": 0.35, "min_adj": 78, "min_char": 55},
    {"name": "مرن", "min_prod": 55, "min_word": 0.3, "min_adj": 75, "min_char": 50},
    {"name": "مرن جداً", "min_prod": 50, "min_word": 0.25, "min_adj": 72, "min_char": 45},
]

for thresh in thresholds:
    matcher = SmartMatcher()
    # تعديل العتبات
    matched = 0
    total = len(product_candidates)
    
    for my_p, my_name, my_price, my_brand, my_size, candidates in product_candidates:
        my_light = light_normalize(my_name)
        my_conc = extract_concentration(my_name)
        
        best_score = 0
        best_match = None
        
        scored = []
        for c in candidates:
            quick = fuzz.token_set_ratio(my_light, c["light"])
            if quick >= 55:
                scored.append((quick, c))
        scored.sort(key=lambda x: -x[0])
        
        for _, candidate in scored[:30]:
            comp_name = candidate["name"]
            comp_light = candidate["light"]
            comp_brand = extract_brand(comp_name)
            comp_size = candidate["size"]
            comp_conc = extract_concentration(comp_name)
            
            # تطبيق _verify_match مع العتبات المخصصة
            name_score = fuzz.token_sort_ratio(my_light, comp_light)
            if name_score < 75:
                continue
            
            my_product_name = matcher._remove_brand_from_name(my_name, my_brand or comp_brand or "")
            comp_product_name = matcher._remove_brand_from_name(comp_name, comp_brand or my_brand or "")
            
            if not my_product_name or not comp_product_name:
                if name_score >= 85:
                    if name_score > best_score:
                        best_score = name_score
                        best_match = candidate
                continue
            
            product_score = fuzz.token_sort_ratio(my_product_name, comp_product_name)
            my_words = set(my_product_name.split())
            comp_words = set(comp_product_name.split())
            common_words = my_words & comp_words
            all_words = my_words | comp_words
            word_overlap = len(common_words) / max(len(all_words), 1)
            
            if product_score < thresh["min_prod"]:
                continue
            if product_score < 75 and word_overlap < thresh["min_word"]:
                continue
            if product_score >= 75 and word_overlap < 0.3:
                char_ratio = fuzz.ratio(my_product_name, comp_product_name)
                if char_ratio < thresh["min_char"]:
                    continue
            
            adjusted_score = (name_score * 0.4) + (product_score * 0.4) + (word_overlap * 100 * 0.2)
            if adjusted_score >= thresh["min_adj"] and adjusted_score > best_score:
                best_score = adjusted_score
                best_match = candidate
        
        if best_match:
            matched += 1
    
    pct = matched / total * 100
    print(f"  {thresh['name']:15s} | مطابق: {matched:4d}/{total} ({pct:5.1f}%) | min_prod={thresh['min_prod']} min_word={thresh['min_word']} min_adj={thresh['min_adj']}")

print("\nملاحظة: نسبة المطابقة تعتمد على العينة (200 منتج)")
