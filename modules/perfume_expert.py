"""
🤖 خبير مطابقة العطور الذكي - Perfume Matching Expert
====================================
نظام ذكاء اصطناعي متخصص في مطابقة منتجات العطور بدقة 100%
"""

import os
import requests
import json
from typing import Dict, Optional
import streamlit as st

# ══════════════════════════════════════════════════════════════
# إعدادات Gemini API
# ══════════════════════════════════════════════════════════════

try:
    GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")
except:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

if not GEMINI_API_KEY or GEMINI_API_KEY.strip() == "":
    GEMINI_API_KEY = "AIzaSyBLgjwRh_t0gHqgN-V2NsDzdL5kro4lXVE"

# ══════════════════════════════════════════════════════════════
# نظام الخبير - System Prompt
# ══════════════════════════════════════════════════════════════

EXPERT_SYSTEM_PROMPT = """# 🤖 خبير مطابقة العطور الذكي - Perfume Matching Expert

## الهوية والدور

أنت **خبير عطور محترف** متخصص في:
- مطابقة منتجات العطور بين المتاجر
- تحليل الأسعار والتسعير التنافسي
- اكتشاف الأخطاء في المطابقات
- تقديم توصيات تسعير دقيقة

**خبرتك:** 10+ سنوات في سوق العطور السعودي والخليجي

---

## ⚠️ القواعد الصارمة (يجب اتباعها دائماً)

### 1. لا تخمين أبداً
- إذا كان هناك **أدنى شك** → القرار: "غير مؤكد"
- الثقة يجب أن تكون **90%+** للقبول
- عند الشك، اطلب مراجعة يدوية

### 2. التطابق يجب أن يكون 100%
- **العلامة التجارية** متطابقة
- **اسم العطر** متطابق
- **الحجم** متطابق
- **التركيز** متطابق (EDT, EDP, Parfum)
- **الجنس** متطابق (رجالي, نسائي, للجنسين)

### 3. الاختلاف = رفض
- اختلاف التركيز = **رفض**
- اختلاف الحجم = **رفض**
- اختلاف الجنس = **رفض**
- طقم vs منتج فردي = **رفض**
- تستر vs ريتيل = **رفض** (إلا إذا محدد)

---

## 🔍 قرارات التسعير

### 1. خفض السعر
```
الشرط: سعر المنافس أقل بوضوح (فرق > 5%)
مثال: سعرنا 500 ريال، المنافس 450 ريال
القرار: خفض إلى 450 ريال
```

### 2. رفع السعر
```
الشرط: سعرنا أقل بكثير من السوق (نخسر ربح)
مثال: سعرنا 300 ريال، المنافس 450 ريال
القرار: رفع إلى 400-420 ريال (للحفاظ على التنافسية مع ربح أفضل)
```

### 3. تثبيت السعر
```
الشرط: سعرنا قريب من المنافس (فرق < 5%)
مثال: سعرنا 500 ريال، المنافس 495 ريال
القرار: تثبيت (الفرق بسيط)
```

### 4. لا تغيير
```
الشرط: المطابقة غير مؤكدة أو مرفوضة
مثال: منتجان مختلفان
القرار: لا تغيير (لا يمكن المقارنة)
```

---

## 📊 صيغة الإجابة

عند مراجعة أي مطابقة، أجب بهذه الصيغة:

```json
{
  "verified": "نعم/لا/غير مؤكد",
  "confidence": 95,
  "price_action": "خفض/رفع/تثبيت/لا تغيير",
  "recommended_price": 450.00,
  "reason": "السبب بجملة واحدة واضحة"
}
```

**تذكر:** الدقة أهم من السرعة. عند الشك، اختر "غير مؤكد".
"""

# ══════════════════════════════════════════════════════════════
# دالة المطابقة الذكية
# ══════════════════════════════════════════════════════════════

def expert_match_verification(
    our_product: str,
    competitor_product: str,
    our_price: float,
    competitor_price: float
) -> Dict:
    """
    التحقق من مطابقة منتجين باستخدام خبير العطور الذكي
    
    Args:
        our_product: اسم منتجنا
        competitor_product: اسم منتج المنافس
        our_price: سعرنا
        competitor_price: سعر المنافس
    
    Returns:
        Dict: نتيجة التحقق مع التوصيات
    """
    try:
        prompt = f"""{EXPERT_SYSTEM_PROMPT}

---

## المطابقة المطلوب التحقق منها:

**منتجنا:**
- الاسم: {our_product}
- السعر: {our_price} ريال

**منتج المنافس:**
- الاسم: {competitor_product}
- السعر: {competitor_price} ريال

---

**المطلوب:**
1. حلل المنتجين بدقة
2. قارن العلامة التجارية، الاسم، التركيز، الحجم، الجنس
3. حدد إذا كان هناك أي اختلاف
4. قرر القبول أو الرفض
5. اقترح السعر المناسب
6. اشرح السبب بوضوح

**أجب بصيغة JSON فقط:**
```json
{{
  "verified": "نعم/لا/غير مؤكد",
  "confidence": 95,
  "price_action": "خفض/رفع/تثبيت/لا تغيير",
  "recommended_price": 450.00,
  "reason": "السبب بجملة واحدة واضحة"
}}
```
"""

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
        
        response = requests.post(
            url,
            json={"contents": [{"parts": [{"text": prompt}]}]},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
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
            
            data = json.loads(text)
            
            # إضافة معلومات إضافية
            data["our_product"] = our_product
            data["competitor_product"] = competitor_product
            data["our_price"] = our_price
            data["competitor_price"] = competitor_price
            data["price_difference"] = round(our_price - competitor_price, 2)
            
            return {"success": True, "data": data}
        else:
            return {"success": False, "error": f"خطأ في API: {response.status_code}"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

# ══════════════════════════════════════════════════════════════
# دالة التحقق المجمع
# ══════════════════════════════════════════════════════════════

def expert_batch_verification(matches: list) -> Dict:
    """
    التحقق من عدة مطابقات دفعة واحدة
    
    Args:
        matches: قائمة المطابقات
        كل عنصر: {
            "our_product": str,
            "competitor_product": str,
            "our_price": float,
            "competitor_price": float
        }
    
    Returns:
        Dict: نتائج التحقق المجمع
    """
    try:
        results = []
        verified_count = 0
        rejected_count = 0
        uncertain_count = 0
        
        for match in matches:
            result = expert_match_verification(
                our_product=match["our_product"],
                competitor_product=match["competitor_product"],
                our_price=match["our_price"],
                competitor_price=match["competitor_price"]
            )
            
            if result["success"]:
                data = result["data"]
                results.append(data)
                
                if data["verified"] == "نعم":
                    verified_count += 1
                elif data["verified"] == "لا":
                    rejected_count += 1
                else:
                    uncertain_count += 1
        
        summary = {
            "total": len(matches),
            "verified": verified_count,
            "rejected": rejected_count,
            "uncertain": uncertain_count,
            "details": results
        }
        
        return {"success": True, "data": summary}
        
    except Exception as e:
        return {"success": False, "error": str(e)}
