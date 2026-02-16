#!/usr/bin/env python3
"""اختبار حالات حدية"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from thefuzz import fuzz
from engine_v2 import SmartMatcher, light_normalize

matcher = SmartMatcher()

# حالة 1: عود بليند vs بلو عود
cases = [
    ("عطر لطافة عود بليند أو دو برفيوم 100 مل", "لطافة بلو عود أو دو برفيوم 100مل"),
    ("عطر لطافة شهرزاد أو دو برفيوم 100 مل", "لطافة اسد او دو برفيوم 100مل"),
    ("عطر لطافة عود سلامة أو دو برفيوم 100 مل", "لطافة مسك سلامة أو دو برفيوم 100 مل"),
    ("عطر لطافة رائد لوكس أو دو برفيوم 100 مل", "لطافة رائد لوكس او دو برفيوم 100مل"),
]

for my_name, comp_name in cases:
    my_light = light_normalize(my_name)
    comp_light = light_normalize(comp_name)
    my_brand = "لطافة"
    comp_brand = "لطافة"
    
    my_product = matcher._remove_brand_from_name(my_light, my_brand)
    comp_product = matcher._remove_brand_from_name(comp_light, comp_brand)
    
    product_score = fuzz.token_sort_ratio(my_product, comp_product)
    name_score = matcher._compare_names(my_light, comp_light)
    
    ok, score, reason = matcher._verify_match(
        my_name, my_light, my_brand, 100, "EDP",
        comp_name, comp_light, comp_brand, 100, "EDP"
    )
    
    print(f"\n{'='*60}")
    print(f"  متجر: {my_name}")
    print(f"  منافس: {comp_name}")
    print(f"  المنتج بعد التنظيف: '{my_product}' vs '{comp_product}'")
    print(f"  product_score: {product_score}%")
    print(f"  name_score: {name_score:.1f}%")
    print(f"  النتيجة: {'✅ مطابق' if ok else '❌ مختلف'} ({score:.1f}%) - {reason}")
