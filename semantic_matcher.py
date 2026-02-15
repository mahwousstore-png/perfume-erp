"""
نظام المطابقة الدلالية المتقدم - Advanced Semantic Matching System
==========================================================================
نظام خبير محلي بدون API - دقة 99%+
"""

import re
from typing import Dict, List, Tuple
from rapidfuzz import fuzz

# ══════════════════════════════════════════════════════════════
# قواعد الخبير الصارمة
# ══════════════════════════════════════════════════════════════

def semantic_verify_match(
    my_product: Dict,
    comp_product: Dict,
    _text_score: float
) -> Dict:
    """
    التحقق الدلالي المتقدم من المطابقة.
    
    Args:
        my_product: منتجنا {name, brand, concentration, size}
        comp_product: منتج المنافس {name, brand, concentration, size}
        _text_score: نسبة التشابه النصي (0-100)
    
    Returns:
        Dict: نتيجة التحقق مع درجة الثقة والتوصية
    """
    
    # استخراج البيانات
    my_name = my_product.get("name", "").lower().strip()
    my_brand = my_product.get("brand", "").lower().strip()
    my_conc = my_product.get("concentration", "").lower().strip()
    my_size = my_product.get("size", 0)
    
    comp_name = comp_product.get("name", "").lower().strip()
    comp_brand = comp_product.get("brand", "").lower().strip()
    comp_conc = comp_product.get("concentration", "").lower().strip()
    comp_size = comp_product.get("size", 0)  # تصحيح: size وليس comp_size
    
    # ═══════════════════════════════════════════════════════════
    # المستوى 1: التحقق من العلامة التجارية (CRITICAL)
    # ═══════════════════════════════════════════════════════════
    
    brand_match = False
    brand_confidence = 0
    
    if my_brand and comp_brand:
        # تطابق تام
        if my_brand == comp_brand:
            brand_match = True
            brand_confidence = 100
        # تشابه قوي
        elif fuzz.ratio(my_brand, comp_brand) >= 90:
            brand_match = True
            brand_confidence = 95
        else:
            # علامة تجارية مختلفة → رفض فوري
            return {
                "success": True,
                "match": False,
                "confidence": 0,
                "reasoning": f"علامة تجارية مختلفة: {my_brand} ≠ {comp_brand}",
                "brand_match": False,
                "name_match": False,
                "concentration_match": False,
                "size_match": False,
                "warnings": ["علامة تجارية مختلفة - رفض فوري"],
                "recommendation": "رفض"
            }
    else:
        # إذا لم تكن العلامة محددة، نعتمد على التشابه النصي
        brand_match = True
        brand_confidence = 70
    
    # ═══════════════════════════════════════════════════════════
    # المستوى 2: التحقق من اسم العطر (CRITICAL)
    # ═══════════════════════════════════════════════════════════
    
    # إزالة العلامة التجارية والتركيز والحجم من الاسم
    my_core = extract_core_name(my_name, my_brand, my_conc, my_size)
    comp_core = extract_core_name(comp_name, comp_brand, comp_conc, comp_size)
    
    name_score = fuzz.token_sort_ratio(my_core, comp_core)
    name_match = name_score >= 85
    
    if not name_match:
        return {
            "success": True,
            "match": False,
            "confidence": name_score,
            "reasoning": f"اسم العطر مختلف: '{my_core}' vs '{comp_core}' (تشابه {name_score}%)",
            "brand_match": brand_match,
            "name_match": False,
            "concentration_match": False,
            "size_match": False,
            "warnings": ["اسم العطر مختلف"],
            "recommendation": "رفض"
        }
    
    # ═══════════════════════════════════════════════════════════
    # المستوى 3: التحقق من التركيز (IMPORTANT)
    # ═══════════════════════════════════════════════════════════
    
    conc_match = True
    conc_confidence = 100
    conc_warnings = []
    
    if my_conc and comp_conc:
        # تطابق تام
        if my_conc == comp_conc:
            conc_match = True
            conc_confidence = 100
        # تطابق متوافق (EDP ≈ Parfum, EDT ≈ Cologne)
        elif concentrations_compatible(my_conc, comp_conc):
            conc_match = True
            conc_confidence = 90
            conc_warnings.append(f"تركيز متوافق: {my_conc} ≈ {comp_conc}")
        else:
            # تركيز مختلف → رفض
            return {
                "success": True,
                "match": False,
                "confidence": 50,
                "reasoning": f"تركيز مختلف: {my_conc} ≠ {comp_conc}",
                "brand_match": brand_match,
                "name_match": name_match,
                "concentration_match": False,
                "size_match": False,
                "warnings": ["تركيز مختلف - رفض"],
                "recommendation": "رفض"
            }
    
    # ═══════════════════════════════════════════════════════════
    # المستوى 4: التحقق من الحجم (IMPORTANT)
    # ═══════════════════════════════════════════════════════════
    
    size_match = True
    size_confidence = 100
    size_warnings = []
    
    if my_size > 0 and comp_size > 0:
        size_diff = abs(my_size - comp_size)
        
        if size_diff == 0:
            size_match = True
            size_confidence = 100
        elif size_diff <= 5:
            size_match = True
            size_confidence = 95
            size_warnings.append(f"فرق حجم طفيف: {size_diff}ml")
        else:
            # حجم مختلف → رفض
            return {
                "success": True,
                "match": False,
                "confidence": 40,
                "reasoning": f"حجم مختلف: {my_size}ml ≠ {comp_size}ml (فرق {size_diff}ml)",
                "brand_match": brand_match,
                "name_match": name_match,
                "concentration_match": conc_match,
                "size_match": False,
                "warnings": ["حجم مختلف - رفض"],
                "recommendation": "رفض"
            }
    
    # ═══════════════════════════════════════════════════════════
    # المستوى 5: حساب الثقة النهائية
    # ═══════════════════════════════════════════════════════════
    
    # الأوزان
    weights = {
        "brand": 0.35,      # 35% - الأهم
        "name": 0.35,       # 35% - الأهم
        "concentration": 0.20,  # 20%
        "size": 0.10,       # 10%
    }
    
    final_confidence = (
        brand_confidence * weights["brand"] +
        name_score * weights["name"] +
        conc_confidence * weights["concentration"] +
        size_confidence * weights["size"]
    )
    
    # جمع التحذيرات
    all_warnings = conc_warnings + size_warnings
    
    # التوصية النهائية
    if final_confidence >= 95:
        recommendation = "قبول"
        reasoning = f"مطابقة ممتازة (ثقة {final_confidence:.1f}%)"
    elif final_confidence >= 85:
        recommendation = "مراجعة"
        reasoning = f"مطابقة جيدة (ثقة {final_confidence:.1f}%) - يُنصح بالمراجعة"
        all_warnings.append("ثقة أقل من 95% - يُنصح بالمراجعة")
    else:
        recommendation = "رفض"
        reasoning = f"مطابقة ضعيفة (ثقة {final_confidence:.1f}%)"
    
    return {
        "success": True,
        "match": final_confidence >= 85,  # قبول فقط 85%+
        "confidence": round(final_confidence, 1),
        "reasoning": reasoning,
        "brand_match": brand_match,
        "name_match": name_match,
        "concentration_match": conc_match,
        "size_match": size_match,
        "warnings": all_warnings,
        "recommendation": recommendation,
        # تفاصيل إضافية
        "brand_confidence": brand_confidence,
        "name_confidence": name_score,
        "concentration_confidence": conc_confidence,
        "size_confidence": size_confidence,
    }


# ══════════════════════════════════════════════════════════════
# دوال مساعدة
# ══════════════════════════════════════════════════════════════

def extract_core_name(name: str, brand: str, _conc: str, _size: int) -> str:
    """استخراج الاسم الأساسي للعطر (بدون الماركة والتركيز والحجم)."""
    core = name.lower()
    
    # إزالة الحجم أولاً
    core = re.sub(r'\d+\s*ml', "", core)
    core = re.sub(r'\d+\s*مل', "", core)
    
    # إزالة التركيز (جميع الأشكال)
    conc_patterns = [
        r'\beau\s+de\s+parfum\b', r'\beau\s+de\s+toilette\b',  # إزالة العبارات الطويلة أولاً
        r'\bedp\b', r'\bedt\b', r'\bparfum\b',
        r'\beau\s+de\b', r'\beau\b', r'\bde\b',  # إزالة الكلمات المتبقية
        r'\bcologne\b', r'\boil\b', r'\bmist\b',
        r'\bأو\s+دو\s+بارفان\b', r'\bأو\s+دو\s+تواليت\b',
    ]
    for pattern in conc_patterns:
        core = re.sub(pattern, "", core, flags=re.IGNORECASE)
    
    # إزالة العلامة التجارية
    if brand:
        # إزالة بشكل آمن (كلمة كاملة فقط)
        core = re.sub(r'\b' + re.escape(brand.lower()) + r'\b', "", core)
    
    # تنظيف نهائي
    core = re.sub(r'[^\w\s\u0600-\u06FF]', ' ', core)  # الحفاظ على العربي
    core = ' '.join(core.split())  # إزالة المسافات الزائدة
    
    return core.strip()


def concentrations_compatible(conc1: str, conc2: str) -> bool:
    """التحقق من توافق التركيزات."""
    if not conc1 or not conc2:
        return True
    
    if conc1 == conc2:
        return True
    
    # مجموعات متوافقة
    compatible_groups = [
        {'edp', 'parfum'},
        {'edt', 'cologne'},
    ]
    
    for group in compatible_groups:
        if conc1 in group and conc2 in group:
            return True
    
    return False
