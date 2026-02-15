#!/usr/bin/env python3
"""اختبار الحالات المشكوك فيها من الاختبار السابق"""
import sys
sys.path.insert(0, '.')
from engine_v2 import SmartMatcher, light_normalize, extract_brand, extract_size, extract_concentration
from fuzzywuzzy import fuzz

matcher = SmartMatcher()

suspicious_cases = [
    ("عطر أرماف كلوب دي نويت عود أو دو برفيوم 100مل", "عطر ارماف كلوب دي نوي عود بارفيوم 105مل"),
    ("عطر روبرتو كافالي جولد نوبل وودز أو دو برفيوم 100مل", "عطر روبرتو كفالي اومو بارفيوم 100مل"),
    ("عطر جان بول غوتييه ديفاين إلكسير أو دو بارفيوم 100 مل للنساء", "عطر جان بول غولتير غولتير ديفين النسائي او دو بارفيوم 100مل"),
    ("عطر مونتال دايموند فلاورز أو دو برفيوم 100 مل", "عطر مونتال عود فلاور او دو بارفيوم 100مل"),
    ("عطر زودياك هنتر او دو بارفيوم 100 مل", "عطر زودياك ويفز او دو بارفيوم 100مل"),
    ("طقم جيس باي مرسيانو اودي برفيوم نسائي 100 مل + عطر بخ 15 مل", "طقم قيس باي مارسيانو النسائي او دو بارفيوم (عطر 100مل+بودي لوشن)"),
    ("عطر اجنر ليديز داي النسائي او دو تواليت 100مل", "عطر اجنر انيشيال الرجالي او دو تواليت 100مل"),
    ("عطر لانكوم آيدول أو دو تواليت 100 مل للنساء", "عطر لانكوم ايدول نكتار او دو بارفيوم النسائي 100مل"),
    ("عطر ليكويد اماجينيرز سانكتي أو دو برفيوم 100مل", "عطر ليكويد ايماجيناير بلانش بيت او دو بارفيوم 100مل"),
    ("تستر جيرلان لوم ايديال او دو تواليت 100 مل", "تستر غيرلان لي هوم ايديل او دو تواليت 100مل"),
    ("عطر بريتني سبيرز فانتازي أو دو بارفيوم 100 مل للنساء", "عطر بريتني سبيرز فانتاسي انتنس او دو بارفيوم 100مل"),
]

# Expected: which should match and which shouldn't
# 1. ارماف كلوب دي نويت عود = ارماف كلوب دي نوي عود → ✅ نفس المنتج (تهجئة مختلفة)
# 2. روبرتو كافالي جولد نوبل وودز ≠ روبرتو كفالي اومو → ❌ منتج مختلف
# 3. جان بول غوتييه ديفاين إلكسير ≈ جان بول غولتير ديفين → ✅ نفس المنتج تقريباً
# 4. مونتال دايموند فلاورز ≠ مونتال عود فلاور → ❌ منتج مختلف
# 5. زودياك هنتر ≠ زودياك ويفز → ❌ منتج مختلف
# 6. جيس باي مرسيانو ≈ قيس باي مارسيانو → ✅ نفس المنتج (تهجئة)
# 7. اجنر ليديز داي ≠ اجنر انيشيال → ❌ منتج مختلف
# 8. لانكوم آيدول تواليت ≠ لانكوم ايدول نكتار → ❌ منتج مختلف
# 9. ليكويد اماجينيرز سانكتي ≠ ليكويد ايماجيناير بلانش بيت → ❌ منتج مختلف
# 10. جيرلان لوم ايديال ≈ غيرلان لي هوم ايديل → ✅ نفس المنتج (تهجئة)
# 11. بريتني سبيرز فانتازي ≠ بريتني سبيرز فانتاسي انتنس → ❌ منتج مختلف (نسخة مختلفة)

expected = [True, False, True, False, False, True, False, False, False, True, False]

print("=" * 80)
print("اختبار الحالات المشكوك فيها")
print("=" * 80)

correct = 0
for i, (my, comp) in enumerate(suspicious_cases):
    my_light = light_normalize(my)
    comp_light = light_normalize(comp)
    my_brand = extract_brand(my)
    comp_brand = extract_brand(comp)
    my_size = extract_size(my)
    comp_size = extract_size(comp)
    my_conc = extract_concentration(my)
    comp_conc = extract_concentration(comp)
    
    passed, score, reason = matcher._verify_match(
        my, my_light, my_brand, my_size, my_conc,
        comp, comp_light, comp_brand, comp_size, comp_conc
    )
    
    exp = expected[i]
    status = "✅" if passed == exp else "❌ خطأ!"
    match_str = "مطابق" if passed else "مختلف"
    exp_str = "مطابق" if exp else "مختلف"
    
    print(f"\n{i+1}. {status}")
    print(f"   متجر: {my[:60]}")
    print(f"   منافس: {comp[:60]}")
    print(f"   brand: '{my_brand}' vs '{comp_brand}'")
    print(f"   النتيجة: {match_str} ({score:.0f}%) | المتوقع: {exp_str}")
    print(f"   السبب: {reason}")
    
    if passed == exp:
        correct += 1

print(f"\n{'=' * 80}")
print(f"النتيجة: {correct}/{len(suspicious_cases)} صحيحة ({correct/len(suspicious_cases)*100:.0f}%)")
print(f"{'=' * 80}")
