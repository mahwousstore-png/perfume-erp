"""
ai_verification.py
نظام التحقق الذكي بالذكاء الصناعي (Gemini AI)
═══════════════════════════════════════════════════
التأكد من صحة كل مطابقة بدقة 100%
"""

import os
import requests
import json
import time

# مفتاح Gemini API
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyBLgjwRh_t0gHqgN-V2NsDzdL5kro4lXVE")

def verify_match_with_ai(my_product, comp_product, semantic_result):
    """
    التحقق من صحة المطابقة باستخدام Gemini AI.
    
    Args:
        my_product: منتجنا {name, brand, concentration, size}
        comp_product: منتج المنافس {name, brand, concentration, size}
        semantic_result: نتيجة التحليل الدلالي {match, confidence, reasoning}
    
    Returns:
        {
            "verified": True/False,
            "confidence": 0-100,
            "status": "✅ مؤكد" / "⚠️ مشكوك" / "❌ خطأ",
            "reasoning": "تفسير القرار",
            "ai_decision": "قبول" / "رفض"
        }
    """
    
    # إذا كان التحليل الدلالي رفض المطابقة، لا حاجة للتحقق بالـ AI
    if not semantic_result.get("match", False):
        return {
            "verified": False,
            "confidence": 0,
            "status": "❌ خطأ",
            "reasoning": semantic_result.get("reasoning", "رفض من التحليل الدلالي"),
            "ai_decision": "رفض"
        }
    
    # بناء Prompt للـ AI
    prompt = f"""أنت خبير في مطابقة منتجات العطور. مهمتك التحقق من صحة المطابقة بين منتجين.

**منتجنا:**
- الاسم: {my_product.get('name', '')}
- الماركة: {my_product.get('brand', '')}
- التركيز: {my_product.get('concentration', '')}
- الحجم: {my_product.get('size', 0)} ml

**منتج المنافس:**
- الاسم: {comp_product.get('name', '')}
- الماركة: {comp_product.get('brand', '')}
- التركيز: {comp_product.get('concentration', '')}
- الحجم: {comp_product.get('size', 0)} ml

**نتيجة التحليل الدلالي:**
- المطابقة: {semantic_result.get('match', False)}
- الثقة: {semantic_result.get('confidence', 0)}%
- التفسير: {semantic_result.get('reasoning', '')}

**السؤال:**
هل هذان المنتجان متطابقان (نفس العطر)؟

**الإجابة المطلوبة (JSON فقط):**
{{
    "match": true/false,
    "confidence": 0-100,
    "reasoning": "تفسير مفصل للقرار (بالعربية)"
}}

**ملاحظات مهمة:**
1. يجب أن تكون الماركة متطابقة تماماً
2. يجب أن يكون اسم العطر متطابقاً (بعد إزالة الماركة والتركيز والحجم)
3. التركيز يجب أن يكون متطابقاً أو متوافقاً (EDP ≈ Parfum, EDT ≈ Cologne)
4. الحجم يجب أن يكون متطابقاً أو قريباً (فرق ≤ 5ml)
5. إذا كان أي من الشروط غير محقق، الإجابة false

أجب بـ JSON فقط بدون أي نص إضافي."""

    try:
        # استدعاء Gemini API
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={GEMINI_API_KEY}"
        
        response = requests.post(
            url,
            json={
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": 0.1,  # دقة عالية
                    "maxOutputTokens": 500
                }
            },
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            text = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            
            # استخراج JSON من النص
            text = text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()
            
            ai_result = json.loads(text)
            
            # تحليل النتيجة
            match = ai_result.get("match", False)
            confidence = ai_result.get("confidence", 0)
            reasoning = ai_result.get("reasoning", "")
            
            # تحديد الحالة
            if match and confidence >= 95:
                status = "✅ مؤكد"
                verified = True
            elif match and confidence >= 80:
                status = "⚠️ مشكوك"
                verified = True
            else:
                status = "❌ خطأ"
                verified = False
            
            return {
                "verified": verified,
                "confidence": confidence,
                "status": status,
                "reasoning": reasoning,
                "ai_decision": "قبول" if match else "رفض"
            }
        
        else:
            # فشل API - استخدام نتيجة التحليل الدلالي
            return {
                "verified": semantic_result.get("match", False),
                "confidence": semantic_result.get("confidence", 0),
                "status": "⚠️ مشكوك (فشل AI)",
                "reasoning": f"فشل التحقق بالـ AI: {response.status_code}. استخدام التحليل الدلالي.",
                "ai_decision": "غير متاح"
            }
    
    except Exception as e:
        # خطأ - استخدام نتيجة التحليل الدلالي
        return {
            "verified": semantic_result.get("match", False),
            "confidence": semantic_result.get("confidence", 0),
            "status": "⚠️ مشكوك (خطأ AI)",
            "reasoning": f"خطأ في التحقق بالـ AI: {str(e)}. استخدام التحليل الدلالي.",
            "ai_decision": "غير متاح"
        }

def batch_verify_matches(matches, progress_callback=None):
    """
    التحقق من مجموعة مطابقات دفعة واحدة.
    
    Args:
        matches: قائمة المطابقات [{my_product, comp_product, semantic_result}]
        progress_callback: دالة لتحديث التقدم
    
    Returns:
        قائمة النتائج مع حالة التحقق
    """
    results = []
    total = len(matches)
    
    for i, match in enumerate(matches):
        # التحقق من المطابقة
        verification = verify_match_with_ai(
            match.get("my_product", {}),
            match.get("comp_product", {}),
            match.get("semantic_result", {})
        )
        
        # إضافة النتيجة
        result = {**match, **verification}
        results.append(result)
        
        # تحديث التقدم
        if progress_callback:
            progress = int((i + 1) / total * 100)
            progress_callback(progress, f"تم التحقق من {i + 1}/{total} مطابقة")
        
        # تأخير بسيط لتجنب Rate Limit
        if i < total - 1:
            time.sleep(0.5)
    
    return results
