"""
نظام المطابقة الذكي متعدد المستويات
Multi-Layer AI Matching System
====================================
يستخدم Gemini AI للتحقق الدلالي العميق من المطابقات
"""

import os
import requests
import json
from typing import Dict, List, Optional, Tuple

# ══════════════════════════════════════════════════════════════
# إعدادات API
# ══════════════════════════════════════════════════════════════

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyBLgjwRh_t0gHqgN-V2NsDzdL5kro4lXVE")
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

# ══════════════════════════════════════════════════════════════
# نظام خبير المطابقة - Expert Matching Prompt
# ══════════════════════════════════════════════════════════════

EXPERT_MATCHING_PROMPT = """# 🤖 خبير مطابقة العطور الذكي - Perfume Matching Expert

## الهوية والدور

أنت **خبير عطور محترف** متخصص في مطابقة المنتجات بدقة 100%.

**خبرتك:** 15+ سنة في سوق العطور العالمي والخليجي

---

## ⚠️ القواعد الصارمة (MUST FOLLOW)

### 1. التطابق التام فقط
- **العلامة التجارية** يجب أن تكون متطابقة 100%
- **اسم العطر** يجب أن يكون متطابقاً 100%
- **الحجم** يجب أن يكون متطابقاً (±5ml مقبول)
- **التركيز** يجب أن يكون متطابقاً أو متوافقاً:
  - EDP = Eau de Parfum ≈ Parfum (متوافقان)
  - EDT = Eau de Toilette ≈ Cologne (متوافقان)
  - EDP ≠ EDT (غير متوافقان)
- **الجنس** يجب أن يكون متطابقاً (رجالي = رجالي، نسائي = نسائي)

### 2. الاختلاف = رفض
- اختلاف العلامة التجارية = **رفض فوري**
- اختلاف اسم العطر = **رفض فوري**
- اختلاف التركيز (EDP vs EDT) = **رفض فوري**
- اختلاف الجنس = **رفض فوري**
- طقم vs منتج فردي = **رفض فوري**
- تستر vs ريتيل = **رفض** (إلا إذا محدد في كلاهما)

### 3. لا تخمين أبداً
- إذا كان هناك **أدنى شك** → القرار: "غير مؤكد"
- الثقة يجب أن تكون **95%+** للقبول
- عند الشك، اختر "رفض"

---

## 📊 درجات الثقة

- **100%**: تطابق تام (نفس العلامة، نفس الاسم، نفس الحجم، نفس التركيز)
- **95-99%**: تطابق ممتاز (اختلافات طفيفة في الكتابة فقط)
- **85-94%**: تطابق جيد (يحتاج مراجعة يدوية)
- **< 85%**: تطابق ضعيف (رفض)

---

## 🎯 أمثلة

### ✅ مقبول (100%)
- منتجنا: "Dior Sauvage EDP 100ml"
- المنافس: "Dior Sauvage Eau de Parfum 100ml"
- القرار: **مطابقة تامة** (نفس العلامة، نفس الاسم، نفس التركيز، نفس الحجم)

### ✅ مقبول (98%)
- منتجنا: "Chanel Bleu de Chanel EDP 100ml"
- المنافس: "Bleu de Chanel by Chanel Eau de Parfum 100ml"
- القرار: **مطابقة ممتازة** (نفس المنتج، ترتيب مختلف فقط)

### ⚠️ يحتاج مراجعة (90%)
- منتجنا: "Tom Ford Oud Wood 100ml"
- المنافس: "Tom Ford Oud Wood EDP 100ml"
- القرار: **مطابقة جيدة** (التركيز غير محدد في منتجنا، يحتاج تأكيد)

### ❌ مرفوض (50%)
- منتجنا: "Dior Sauvage EDP 100ml"
- المنافس: "Dior Sauvage EDT 100ml"
- القرار: **رفض** (تركيز مختلف: EDP ≠ EDT)

### ❌ مرفوض (30%)
- منتجنا: "Versace Eros 100ml"
- المنافس: "Versace Eros Flame 100ml"
- القرار: **رفض** (عطر مختلف: Eros ≠ Eros Flame)

---

## 📝 تعليمات الإخراج

أعد النتيجة بصيغة JSON فقط (بدون markdown):

```json
{
  "match": true/false,
  "confidence": 0-100,
  "reasoning": "شرح مفصل للقرار",
  "brand_match": true/false,
  "name_match": true/false,
  "concentration_match": true/false,
  "size_match": true/false,
  "warnings": ["تحذير 1", "تحذير 2"],
  "recommendation": "قبول/رفض/مراجعة"
}
```

**تذكر:** الدقة أهم من السرعة. عند الشك، اختر "رفض".
"""

# ══════════════════════════════════════════════════════════════
# دوال المطابقة الذكية
# ══════════════════════════════════════════════════════════════

def ai_verify_match(
    my_product: Dict,
    comp_product: Dict,
    text_score: float
) -> Dict:
    """
    التحقق الذكي من المطابقة باستخدام Gemini AI.
    
    Args:
        my_product: منتجنا {name, brand, concentration, size}
        comp_product: منتج المنافس {name, brand, concentration, size}
        text_score: نسبة التشابه النصي (0-100)
    
    Returns:
        Dict: نتيجة التحقق مع درجة الثقة والتوصية
    """
    try:
        # بناء الطلب
        prompt = f"""{EXPERT_MATCHING_PROMPT}

---

## المطابقة المطلوب التحقق منها:

**منتجنا:**
- الاسم الكامل: {my_product.get('name', '')}
- الماركة: {my_product.get('brand', 'غير محدد')}
- التركيز: {my_product.get('concentration', 'غير محدد')}
- الحجم: {my_product.get('size', 0)} ml

**منتج المنافس:**
- الاسم الكامل: {comp_product.get('name', '')}
- الماركة: {comp_product.get('brand', 'غير محدد')}
- التركيز: {comp_product.get('concentration', 'غير محدد')}
- الحجم: {comp_product.get('size', 0)} ml

**نسبة التشابه النصي:** {text_score}%

---

**المطلوب:** حلل المطابقة وأعد النتيجة بصيغة JSON فقط (بدون markdown).
"""

        # استدعاء Gemini API
        response = requests.post(
            GEMINI_API_URL,
            json={
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": 0.1,  # دقة عالية
                    "topK": 1,
                    "topP": 0.8,
                }
            },
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code != 200:
            return {
                "success": False,
                "error": f"API Error: {response.status_code}",
                "match": False,
                "confidence": 0,
            }
        
        result = response.json()
        text = result["candidates"][0]["content"]["parts"][0]["text"]
        
        # تنظيف JSON
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        
        # تحليل JSON
        ai_result = json.loads(text)
        ai_result["success"] = True
        
        return ai_result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "match": False,
            "confidence": 0,
        }


def batch_ai_verify(
    matches: List[Tuple[Dict, Dict, float]],
    min_confidence: float = 95.0
) -> List[Dict]:
    """
    التحقق الدفعي من المطابقات باستخدام AI.
    
    Args:
        matches: قائمة من (my_product, comp_product, text_score)
        min_confidence: الحد الأدنى للثقة (0-100)
    
    Returns:
        List[Dict]: قائمة النتائج المعتمدة
    """
    verified_matches = []
    
    for my_p, comp_p, score in matches:
        # التحقق بالذكاء الصناعي
        ai_result = ai_verify_match(my_p, comp_p, score)
        
        if ai_result.get("success") and ai_result.get("match"):
            confidence = ai_result.get("confidence", 0)
            
            # قبول فقط المطابقات عالية الثقة
            if confidence >= min_confidence:
                verified_matches.append({
                    "my_product": my_p,
                    "comp_product": comp_p,
                    "text_score": score,
                    "ai_confidence": confidence,
                    "ai_reasoning": ai_result.get("reasoning", ""),
                    "warnings": ai_result.get("warnings", []),
                    "recommendation": ai_result.get("recommendation", "قبول"),
                })
    
    return verified_matches


# ══════════════════════════════════════════════════════════════
# دوال مساعدة
# ══════════════════════════════════════════════════════════════

def format_product_details(product: Dict) -> str:
    """تنسيق تفاصيل المنتج للعرض."""
    return f"""
📦 **الاسم الكامل:** {product.get('name', 'غير محدد')}
🏷️ **الماركة:** {product.get('brand', 'غير محدد')}
💧 **التركيز:** {product.get('concentration', 'غير محدد')}
📏 **الحجم:** {product.get('size', 0)} ml
"""
