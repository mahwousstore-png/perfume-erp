"""
gemini_integration.py - وحدة ربط Gemini AI المحسّنة
═══════════════════════════════════════════════════
ربط احترافي مع Gemini AI مع معالجة أخطاء كاملة
"""

import streamlit as st
import google.generativeai as genai
import time
from typing import Optional, Dict, Any
import json

# تهيئة Gemini API
def init_gemini():
    """تهيئة Gemini API مع معالجة الأخطاء"""
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        return True
    except Exception as e:
        st.error(f"❌ فشل تهيئة Gemini API: {str(e)}")
        return False

# نموذج Gemini
def get_gemini_model(model_name="gemini-2.0-flash-exp"):
    """الحصول على نموذج Gemini"""
    try:
        model = genai.GenerativeModel(model_name)
        return model
    except Exception as e:
        st.error(f"❌ فشل تحميل نموذج Gemini: {str(e)}")
        return None

# مطابقة منتج واحد باستخدام Gemini
def match_product_with_gemini(
    store_product: str,
    competitor_product: str,
    store_price: float,
    competitor_price: float,
    max_retries: int = 3
) -> Optional[Dict[str, Any]]:
    """
    مطابقة منتج واحد باستخدام Gemini AI
    
    Args:
        store_product: اسم منتج المتجر
        competitor_product: اسم منتج المنافس
        store_price: سعر المتجر
        competitor_price: سعر المنافس
        max_retries: عدد المحاولات عند الفشل
    
    Returns:
        Dict مع النتيجة أو None عند الفشل
    """
    
    model = get_gemini_model()
    if not model:
        return None
    
    prompt = f"""
أنت خبير في مطابقة أسماء العطور. قارن بين هذين المنتجين بدقة 100%.

**منتج المتجر:**
- الاسم: {store_product}
- السعر: {store_price} ر.س

**منتج المنافس:**
- الاسم: {competitor_product}
- السعر: {competitor_price} ر.س

**المطلوب:**
1. هل المنتجان متطابقان؟ (نفس الماركة + نفس الاسم + نفس الحجم + نفس التركيز)
2. ما نسبة التطابق من 0 إلى 100؟
3. ما التوصية؟ (رفع السعر / خفض السعر / الإبقاء / غير متطابق)

**أجب بصيغة JSON فقط:**
{{
  "is_match": true/false,
  "confidence": 0-100,
  "recommendation": "raise_price" أو "lower_price" أو "keep_price" أو "not_match",
  "reason": "سبب القرار"
}}
"""
    
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            result_text = response.text.strip()
            
            # استخراج JSON من الاستجابة
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(result_text)
            return result
            
        except json.JSONDecodeError as e:
            if attempt < max_retries - 1:
                time.sleep(1)  # انتظار ثانية قبل المحاولة التالية
                continue
            else:
                st.warning(f"⚠️ فشل تحليل JSON من Gemini: {str(e)}")
                return None
                
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2)  # انتظار ثانيتين عند الخطأ
                continue
            else:
                st.error(f"❌ خطأ في Gemini API: {str(e)}")
                return None
    
    return None

# مطابقة دفعة من المنتجات
def batch_match_with_gemini(
    products_batch: list,
    progress_callback=None
) -> list:
    """
    مطابقة دفعة من المنتجات باستخدام Gemini
    
    Args:
        products_batch: قائمة المنتجات للمطابقة
        progress_callback: دالة لتحديث التقدم
    
    Returns:
        قائمة النتائج
    """
    results = []
    total = len(products_batch)
    
    for idx, product_data in enumerate(products_batch):
        result = match_product_with_gemini(
            store_product=product_data["store_name"],
            competitor_product=product_data["competitor_name"],
            store_price=product_data["store_price"],
            competitor_price=product_data["competitor_price"]
        )
        
        if result:
            results.append({
                **product_data,
                "gemini_result": result
            })
        else:
            # في حالة الفشل، استخدم Fallback
            results.append({
                **product_data,
                "gemini_result": {
                    "is_match": False,
                    "confidence": 0,
                    "recommendation": "not_match",
                    "reason": "فشل الاتصال بـ Gemini"
                }
            })
        
        # تحديث التقدم
        if progress_callback:
            progress_callback(idx + 1, total)
        
        # تجنب Rate Limiting
        if (idx + 1) % 10 == 0:
            time.sleep(1)
    
    return results

# اختبار الاتصال بـ Gemini
def test_gemini_connection() -> bool:
    """اختبار الاتصال بـ Gemini API"""
    try:
        model = get_gemini_model()
        if not model:
            return False
        
        response = model.generate_content("مرحباً")
        return bool(response)
        
    except Exception as e:
        st.error(f"❌ فشل اختبار Gemini: {str(e)}")
        return False
