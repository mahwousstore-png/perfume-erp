"""
دالة ذكية لاستخراج الماركات باستخدام ملف الماركات
"""

import pandas as pd
import re
from fuzzywuzzy import fuzz

# تحميل ملف الماركات (سيتم تحميله مرة واحدة)
_brands_cache = None

def load_brands(brands_file='/home/ubuntu/upload/ماركاتمهووس.csv'):
    """تحميل قائمة الماركات من الملف"""
    global _brands_cache
    
    if _brands_cache is not None:
        return _brands_cache
    
    try:
        df = pd.read_csv(brands_file)
        brands = []
        
        for brand_name in df['اسم الماركة']:
            if pd.isna(brand_name):
                continue
            
            # استخراج الاسم العربي والإنجليزي
            # مثال: "جيفنشي | Givenchy"
            parts = str(brand_name).split('|')
            
            # الاسم العربي
            arabic_name = parts[0].strip()
            brands.append(arabic_name)
            
            # الاسم الإنجليزي (إن وجد)
            if len(parts) > 1:
                english_name = parts[1].strip()
                brands.append(english_name)
        
        _brands_cache = list(set(brands))  # إزالة التكرار
        return _brands_cache
    
    except Exception as e:
        print(f"⚠️ خطأ في تحميل ملف الماركات: {e}")
        return []


def extract_brand_from_list(product_name, brands_list=None):
    """
    استخراج الماركة من اسم المنتج باستخدام قائمة الماركات
    """
    if not product_name or not isinstance(product_name, str):
        return ""
    
    if brands_list is None:
        brands_list = load_brands()
    
    if not brands_list:
        return ""
    
    # تنظيف النص
    text = product_name.strip()
    
    # إزالة البادئات
    prefixes = [r'^عطر\s+', r'^تستر\s+', r'^طقم\s+', r'^مجموعة\s+', r'^كيس\s+', r'^عود\s+']
    for prefix in prefixes:
        text = re.sub(prefix, '', text, flags=re.IGNORECASE)
    
    # البحث عن أفضل تطابق
    best_match = ""
    best_score = 0
    
    for brand in brands_list:
        # تحقق من وجود الماركة في بداية النص
        if text.lower().startswith(brand.lower()):
            score = 100
        else:
            # استخدام fuzz للمطابقة الجزئية
            score = fuzz.partial_ratio(brand.lower(), text.lower()[:len(brand)*2])
        
        if score > best_score and score >= 85:  # حد أدنى 85%
            best_score = score
            best_match = brand
    
    return best_match


def test_brand_matcher():
    """اختبار الدالة"""
    brands = load_brands()
    print(f"📊 تم تحميل {len(brands)} ماركة\n")
    
    test_cases = [
        "عطر لطافة أمير العود أو دو برفيوم 100 مل",
        "عطر جوليت هاز اجن مس تشارمينج او دو بارفيوم 100مل",
        "تستر ارماني سترونجر ويذ يو اونلي الرجالي او دو تواليت 125مل",
        "عطر شانيل بلو دي شانيل او دو بارفيوم 100مل",
        "عطر ديور سوفاج او دو تواليت 100مل",
        "عطر توم فورد بلاك اوركيد او دو بارفيوم 100مل",
        "طقم مونت بلانك ليجند اودي تواليت رجالي 100 مل + عطر صغير 7.5 مل",
        "عطر بولغاري مان ان بلاك او دو بارفيوم 100مل",
        "عطر فيرساتشي ايروس فلام او دو بارفيوم 100مل",
        "عطر جيفنشي جنتلمان او دو تواليت 100مل",
    ]
    
    print("🧪 اختبار استخراج الماركات:\n")
    for i, test in enumerate(test_cases, 1):
        brand = extract_brand_from_list(test, brands)
        print(f"{i}. {test[:60]}...")
        print(f"   → الماركة: '{brand}'\n")


if __name__ == "__main__":
    test_brand_matcher()
