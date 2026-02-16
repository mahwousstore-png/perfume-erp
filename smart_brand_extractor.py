"""
دالة ذكية لاستخراج جميع الماركات من أسماء المنتجات
"""

import re

def extract_brand_smart(product_name):
    """
    استخراج الماركة من اسم المنتج بذكاء
    
    النمط:
    - "عطر [ماركة] ..." → الماركة
    - "تستر [ماركة] ..." → الماركة
    - "طقم [ماركة] ..." → الماركة
    """
    if not product_name or not isinstance(product_name, str):
        return ""
    
    # تنظيف النص
    text = product_name.strip()
    
    # الكلمات المفتاحية التي تسبق الماركة
    prefixes = [
        r'^عطر\s+',
        r'^تستر\s+',
        r'^طقم\s+',
        r'^مجموعة\s+',
        r'^كيس\s+',
        r'^عود\s+',
    ]
    
    # إزالة البادئة
    for prefix in prefixes:
        text = re.sub(prefix, '', text, flags=re.IGNORECASE)
    
    # الكلمات التي تنتهي عندها الماركة
    stop_words = [
        'او دو', 'أو دو', 'او دي', 'أو دي',
        'عالي التركيز', 'تواليت', 'برفيوم', 'بارفيوم', 'كولونيا',
        'للرجال', 'للنساء', 'النسائي', 'الرجالي', 'رجالي', 'نسائي',
        'حجم', 'مل', 'ملل',
        'اودي', 'اودو', 'ايو', 'دي', 'دو',
        'edp', 'edt', 'parfum', 'perfume', 'cologne',
        'men', 'women', 'homme', 'femme',
        'ml', 'oz',
        'بديل', 'متقن', 'لعطر',
        'عطر', 'تستر', 'طقم',
    ]
    
    # البحث عن أول كلمة توقف
    words = text.split()
    brand_words = []
    
    for word in words:
        # تحقق من كلمات التوقف
        is_stop = False
        word_lower = word.lower().strip('()')
        
        for stop in stop_words:
            if stop in word_lower:
                is_stop = True
                break
        
        if is_stop:
            break
        
        # تحقق من الأرقام (الحجم)
        if re.search(r'\d+\s*م[لل]', word):
            break
        
        if re.search(r'^\d+$', word):
            break
            
        brand_words.append(word)
    
    # دمج كلمات الماركة
    brand = ' '.join(brand_words).strip()
    
    # تنظيف نهائي
    brand = re.sub(r'[:\-\|]+$', '', brand).strip()
    
    # إذا كانت الماركة طويلة جداً (أكثر من 5 كلمات)، خذ أول 3 كلمات فقط
    if len(brand.split()) > 5:
        brand = ' '.join(brand.split()[:3])
    
    return brand if brand else ""


def test_brand_extractor():
    """اختبار الدالة"""
    test_cases = [
        "عطر لطافة أمير العود أو دو برفيوم 100 مل",
        "عطر جوليت هاز اجن مس تشارمينج او دو بارفيوم 100مل",
        "تستر ارماني سترونجر ويذ يو اونلي الرجالي او دو تواليت 125مل",
        "عطر شانيل بلو دي شانيل او دو بارفيوم 100مل",
        "عطر ديور سوفاج او دو تواليت 100مل",
        "عطر توم فورد بلاك اوركيد او دو بارفيوم 100مل",
        "طقم مونت بلانك ليجند اودي تواليت رجالي 100 مل + عطر صغير 7.5 مل",
        "عطر ماجك بلاك عالي التركيز 80 مل بديل متقن لعطر فيكتور اند رولف سبايس بومب",
        "كيس جورجيوا أرمني حجم وسط",
        "عود فيتنامي زوايا طبيعي ثمن كيلو 125 جرام",
    ]
    
    print("🧪 اختبار استخراج الماركات:\n")
    for i, test in enumerate(test_cases, 1):
        brand = extract_brand_smart(test)
        print(f"{i}. {test[:60]}...")
        print(f"   → الماركة: '{brand}'\n")


if __name__ == "__main__":
    test_brand_extractor()
