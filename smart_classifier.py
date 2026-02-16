"""
نظام التصنيف الذكي متعدد المستويات
يقسم المنتجات إلى مجموعات صغيرة لتسريع المطابقة وتحسين الدقة
"""

import re
from brand_matcher import load_brands, extract_brand_from_list

# دوال التصنيف

def classify_gender(product_name):
    """تصنيف النوع (رجالي/نسائي/مشترك)"""
    if not product_name or not isinstance(product_name, str):
        return "unknown"
    
    text = product_name.lower()
    
    # كلمات رجالية
    male_keywords = ['رجالي', 'للرجال', 'homme', 'men', 'man', 'masculin', 'uomo', 'hombre']
    # كلمات نسائية
    female_keywords = ['نسائي', 'للنساء', 'femme', 'women', 'woman', 'féminin', 'donna', 'mujer']
    # كلمات مشتركة
    unisex_keywords = ['unisex', 'مشترك', 'للجنسين']
    
    # تحقق من المشترك أولاً
    if any(kw in text for kw in unisex_keywords):
        return "unisex"
    
    # تحقق من الرجالي
    if any(kw in text for kw in male_keywords):
        return "male"
    
    # تحقق من النسائي
    if any(kw in text for kw in female_keywords):
        return "female"
    
    # افتراضي: مشترك
    return "unisex"


def classify_size(product_name):
    """تصنيف الحجم (صغير/متوسط/كبير)"""
    if not product_name or not isinstance(product_name, str):
        return "unknown"
    
    # استخراج الحجم بالـ ml - دعم أشكال متعددة
    # مثال: "100 مل" أو "100مل" أو "100 ml" أو "100ml"
    size_match = re.search(r'(\d+)\s*(?:مل|ml)', product_name, re.IGNORECASE)
    
    if not size_match:
        return "unknown"
    
    size = int(size_match.group(1))
    
    if size < 50:
        return "small"  # صغير
    elif size <= 100:
        return "medium"  # متوسط
    else:
        return "large"  # كبير


def classify_concentration(product_name):
    """تصنيف التركيز (EDP/EDT/Parfum/etc.)"""
    if not product_name or not isinstance(product_name, str):
        return "unknown"
    
    text = product_name.lower()
    
    # تركيزات معروفة - الترتيب مهم (من الأطول للأقصر)
    concentrations = [
        ('edp', ['eau de parfum', 'او دو بارفيوم', 'او دو بارفان', 'اودو بارفيوم', 'اودوبارفيوم', 'edp', 'e.d.p']),
        ('edt', ['eau de toilette', 'او دو تواليت', 'او دي تواليت', 'اودي تواليت', 'اوديتواليت', 'edt', 'e.d.t']),
        ('edc', ['eau de cologne', 'او دو كولون', 'كولون', 'edc', 'e.d.c']),
        ('parfum', ['extrait de parfum', 'parfum', 'بارفيوم', 'بارفان', 'extrait']),
        ('body_mist', ['body mist', 'بودي ميست', 'رذاذ']),
    ]
    
    for conc_type, keywords in concentrations:
        if any(kw in text for kw in keywords):
            return conc_type
    
    return "unknown"


def classify_product_type(product_name):
    """تصنيف نوع المنتج (عطر/تستر/طقم/مجموعة)"""
    if not product_name or not isinstance(product_name, str):
        return "perfume"
    
    text = product_name.lower()
    
    # أنواع المنتجات
    if any(kw in text for kw in ['تستر', 'tester']):
        return "tester"
    elif any(kw in text for kw in ['طقم', 'set', 'gift set', 'كيس']):
        return "set"
    elif any(kw in text for kw in ['مجموعة', 'collection']):
        return "collection"
    else:
        return "perfume"


def create_product_signature(product_name, brands_list=None):
    """
    إنشاء توقيع فريد للمنتج بناءً على التصنيفات
    """
    brand = extract_brand_from_list(product_name, brands_list)
    gender = classify_gender(product_name)
    size = classify_size(product_name)
    concentration = classify_concentration(product_name)
    product_type = classify_product_type(product_name)
    
    return {
        'brand': brand,
        'gender': gender,
        'size': size,
        'concentration': concentration,
        'product_type': product_type,
        'signature': f"{brand}|{gender}|{size}|{concentration}|{product_type}"
    }


def group_products_by_signature(df, product_name_column='اسم المنتج', brands_list=None):
    """
    تجميع المنتجات حسب التوقيع
    """
    groups = {}
    
    for idx, row in df.iterrows():
        product_name = row[product_name_column]
        signature_data = create_product_signature(product_name, brands_list)
        signature = signature_data['signature']
        
        if signature not in groups:
            groups[signature] = []
        
        groups[signature].append({
            'index': idx,
            'product_name': product_name,
            'signature_data': signature_data,
            'row': row
        })
    
    return groups


def test_classifier():
    """اختبار النظام"""
    test_cases = [
        "عطر لطافة أمير العود الرجالي أو دو برفيوم 100 مل",
        "عطر شانيل بلو دي شانيل الرجالي او دو بارفيوم 100مل",
        "عطر ديور سوفاج الرجالي او دو تواليت 60مل",
        "تستر توم فورد بلاك اوركيد النسائي او دو بارفيوم 100مل",
        "طقم مونت بلانك ليجند اودي تواليت رجالي 100 مل + عطر صغير 7.5 مل",
        "عطر بولغاري مان ان بلاك الرجالي او دو بارفيوم 150مل",
        "عطر لانكوم لا في است بيل النسائي او دو بارفيوم 50مل",
    ]
    
    brands = load_brands()
    
    print("🧪 اختبار نظام التصنيف:\n")
    for i, test in enumerate(test_cases, 1):
        sig = create_product_signature(test, brands)
        print(f"{i}. {test[:60]}...")
        print(f"   🏷️  الماركة: {sig['brand']}")
        print(f"   👤 النوع: {sig['gender']}")
        print(f"   📦 الحجم: {sig['size']}")
        print(f"   💧 التركيز: {sig['concentration']}")
        print(f"   🎁 نوع المنتج: {sig['product_type']}")
        print(f"   🔑 التوقيع: {sig['signature']}\n")


if __name__ == "__main__":
    test_classifier()
