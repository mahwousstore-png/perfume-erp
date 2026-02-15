"""اختبار المطابقات الخاطئة المكتشفة"""
import sys
sys.path.insert(0, '/home/ubuntu/perfume-erp')
from rapidfuzz import fuzz
from engine_v2 import light_normalize, SmartMatcher
from engine import extract_brand, extract_size, extract_concentration

matcher = SmartMatcher()

# الحالات الخاطئة المكتشفة
false_matches = [
    ("عطر لطافة حكاية العود أو دو برفيوم 100 مل", "لطافة روعة العود أو دو برفيوم 100 مل"),
    ("عطر لطافة سر الخلود أو دو برفيوم 100 مل", "لطافة روعة العود أو دو برفيوم 100 مل"),
    ("عطر لطافة رئيس أو دو برفيوم 100 مل", "لطافة خرافي أو دو برفيوم 100 مل"),
    ("عطر لطافة 24 قيراط وايت جولد أو دو برفيوم", "لطافة 24 قيراط بيور جولد أو دو برفيوم"),
]

# الحالات الصحيحة
true_matches = [
    ("عطر لطافة منقوع العود أو دو برفيوم 100 مل", "لطافة منقوع العود أو دو 100 مل"),
    ("عطر صمام اوي بيور بارفيوم 100 مل", "صمام اوي بيور بارفيوم 100 مل"),
    ("عطر نرسيسو فور هير فور إيفر 100 مل", "نرسيسو فور هير فور ايفر 100 مل"),
]

print("=" * 80)
print("❌ حالات يجب أن تكون خاطئة (يجب أن تُرفض):")
print("=" * 80)
for my, comp in false_matches:
    my_light = light_normalize(my)
    comp_light = light_normalize(comp)
    my_brand = extract_brand(my)
    comp_brand = extract_brand(comp)
    my_size = extract_size(my)
    comp_size = extract_size(comp)
    my_conc = extract_concentration(my)
    comp_conc = extract_concentration(comp)
    
    # اسم المنتج بدون الماركة
    my_prod = matcher._remove_brand_from_name(my_light, my_brand)
    comp_prod = matcher._remove_brand_from_name(comp_light, comp_brand)
    
    is_match, score, reason = matcher._verify_match(
        my, my_light, my_brand, my_size, my_conc,
        comp, comp_light, comp_brand, comp_size, comp_conc,
    )
    
    print(f"\n  المنتج: {my}")
    print(f"  المنافس: {comp}")
    print(f"  الماركة: {my_brand} vs {comp_brand}")
    print(f"  light: '{my_light}' vs '{comp_light}'")
    print(f"  product: '{my_prod}' vs '{comp_prod}'")
    print(f"  token_sort_ratio(product): {fuzz.token_sort_ratio(my_prod, comp_prod)}")
    print(f"  ratio(product): {fuzz.ratio(my_prod, comp_prod)}")
    print(f"  token_set_ratio(product): {fuzz.token_set_ratio(my_prod, comp_prod)}")
    
    my_words = {w for w in my_prod.split() if len(w) >= 3}
    comp_words = {w for w in comp_prod.split() if len(w) >= 3}
    common = my_words & comp_words
    all_w = my_words | comp_words
    overlap = len(common) / max(len(all_w), 1)
    print(f"  my_words: {my_words}")
    print(f"  comp_words: {comp_words}")
    print(f"  common: {common}")
    print(f"  word_overlap: {overlap:.0%}")
    print(f"  ➡️ is_match={is_match}, score={score:.1f}, reason={reason}")
    if is_match:
        print(f"  ⚠️ خطأ! يجب أن تكون False!")

print("\n" + "=" * 80)
print("✅ حالات يجب أن تكون صحيحة (يجب أن تُقبل):")
print("=" * 80)
for my, comp in true_matches:
    my_light = light_normalize(my)
    comp_light = light_normalize(comp)
    my_brand = extract_brand(my)
    comp_brand = extract_brand(comp)
    my_size = extract_size(my)
    comp_size = extract_size(comp)
    my_conc = extract_concentration(my)
    comp_conc = extract_concentration(comp)
    
    my_prod = matcher._remove_brand_from_name(my_light, my_brand)
    comp_prod = matcher._remove_brand_from_name(comp_light, comp_brand)
    
    is_match, score, reason = matcher._verify_match(
        my, my_light, my_brand, my_size, my_conc,
        comp, comp_light, comp_brand, comp_size, comp_conc,
    )
    
    print(f"\n  المنتج: {my}")
    print(f"  المنافس: {comp}")
    print(f"  product: '{my_prod}' vs '{comp_prod}'")
    print(f"  token_sort_ratio(product): {fuzz.token_sort_ratio(my_prod, comp_prod)}")
    print(f"  ratio(product): {fuzz.ratio(my_prod, comp_prod)}")
    print(f"  word_overlap: ", end="")
    my_words = {w for w in my_prod.split() if len(w) >= 3}
    comp_words = {w for w in comp_prod.split() if len(w) >= 3}
    common = my_words & comp_words
    all_w = my_words | comp_words
    overlap = len(common) / max(len(all_w), 1)
    print(f"{overlap:.0%}")
    print(f"  ➡️ is_match={is_match}, score={score:.1f}, reason={reason}")
    if not is_match:
        print(f"  ⚠️ خطأ! يجب أن تكون True!")
