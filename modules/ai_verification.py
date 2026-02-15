"""
نظام التحقق الذكي بالذكاء الصناعي
====================================
يوفر قدرات متقدمة للتحقق والمقارنة والبحث عن المنتجات
"""

import os
import requests
import json
import pandas as pd
from typing import Dict, List, Optional
import streamlit as st

# ══════════════════════════════════════════════════════════════
# إعدادات API
# ══════════════════════════════════════════════════════════════

# قراءة GEMINI_API_KEY من Streamlit Secrets
try:
    if hasattr(st, 'secrets') and "GEMINI_API_KEY" in st.secrets:
        GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
        st.success("✅ Gemini API Key محمّل من Secrets!")
    else:
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
except Exception as e:
    st.warning(f"⚠️ خطأ في قراءة GEMINI_API_KEY: {e}")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Fallback: إذا كان المفتاح فارغاً، استخدم المفتاح الاحتياطي
if not GEMINI_API_KEY or GEMINI_API_KEY.strip() == "":
    GEMINI_API_KEY = "AIzaSyBLgjwRh_t0gHqgN-V2NsDzdL5kro4lXVE"
    st.warning("⚠️ استخدام مفتاح Gemini الاحتياطي")

# ══════════════════════════════════════════════════════════════
# نظام خبير العطور - Expert System Prompt
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
الشرط: سعر المنافس أقل بوضوح (فرق > 5%)
القرار: خفض إلى سعر المنافس

### 2. رفع السعر
الشرط: سعرنا أقل بكثير من السوق (نخسر ربح)
القرار: رفع للحفاظ على التنافسية مع ربح أفضل

### 3. تثبيت السعر
الشرط: سعرنا قريب من المنافس (فرق < 5%)
القرار: تثبيت (الفرق بسيط)

### 4. لا تغيير
الشرط: المطابقة غير مؤكدة أو مرفوضة
القرار: لا تغيير (لا يمكن المقارنة)

**تذكر:** الدقة أهم من السرعة. عند الشك، اختر "غير مؤكد".
"""

# ══════════════════════════════════════════════════════════════
# 1. البحث النصي والمرئي
# ══════════════════════════════════════════════════════════════

def search_product_online(product_name: str, brand: str = "") -> Dict:
    """
    البحث عن المنتج في الإنترنت باستخدام Gemini
    
    Args:
        product_name: اسم المنتج
        brand: العلامة التجارية (اختياري)
    
    Returns:
        Dict: نتائج البحث مع الأسعار والمصادر
    """
    try:
        search_query = f"{brand} {product_name}" if brand else product_name
        
        prompt = f"""ابحث عن المنتج التالي في الإنترنت:
المنتج: {search_query}

المطلوب:
1. العثور على المنتج في مواقع التجارة الإلكترونية
2. استخراج الأسعار من مصادر متعددة
3. التحقق من الأصالة
4. مقارنة الأسعار

أعد النتيجة بصيغة JSON:
{{
  "found": true/false,
  "sources": [
    {{
      "name": "اسم الموقع",
      "price": السعر بالريال,
      "url": "رابط المنتج",
      "verified": true/false
    }}
  ],
  "average_price": السعر المتوسط,
  "lowest_price": أقل سعر,
  "highest_price": أعلى سعر,
  "authenticity": "أصلي/مشكوك فيه/غير معروف",
  "notes": "ملاحظات إضافية"
}}"""

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
        
        response = requests.post(
            url,
            json={"contents": [{"parts": [{"text": prompt}]}]},
            headers={"Content-Type": "application/json"},
            timeout=60
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
            return {"success": True, "data": data}
        else:
            return {"success": False, "error": f"خطأ في API: {response.status_code}"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

# ══════════════════════════════════════════════════════════════
# 2. التحقق من ملف المتجر
# ══════════════════════════════════════════════════════════════

def verify_in_store_file(product_name: str, store_file_path: str) -> Dict:
    """
    التحقق من وجود المنتج في ملف المتجر
    
    Args:
        product_name: اسم المنتج
        store_file_path: مسار ملف CSV للمتجر
    
    Returns:
        Dict: نتائج التحقق
    """
    try:
        # قراءة ملف المتجر
        df = pd.read_csv(store_file_path, encoding='utf-8-sig')
        
        # البحث الذكي باستخدام Gemini في كل المتجر
        products_list = df.iloc[:, 0].tolist()  # أول عمود = أسماء المنتجات
        prices_list = df.iloc[:, 1].tolist() if len(df.columns) > 1 else []  # ثاني عمود = الأسعار
        
        # إنشاء قائمة كاملة (اسم + سعر)
        full_list = []
        for i, product in enumerate(products_list):
            price = prices_list[i] if i < len(prices_list) else "غير متوفر"
            full_list.append(f"{i+1}. {product} - {price} ر.س")
        
        # تقسيم القائمة إلى أجزاء (كل جزء 500 منتج)
        chunk_size = 500
        all_results = []
        
        for chunk_start in range(0, len(full_list), chunk_size):
            chunk_end = min(chunk_start + chunk_size, len(full_list))
            chunk = full_list[chunk_start:chunk_end]
            
            prompt = f"""ابحث عن المنتج التالي في القائمة:
المنتج المطلوب: {product_name}

قائمة المنتجات في المتجر (من {chunk_start+1} إلى {chunk_end}):
{chr(10).join(chunk)}

المطلوب:
1. هل المنتج موجود في هذا الجزء من القائمة؟
2. إذا كان موجوداً، ما هو الاسم الدقيق والسعر؟
3. ما مدى التطابق (%)؟

أعد النتيجة بصيغة JSON:
{{
  "found": true/false,
  "exact_name": "الاسم الدقيق في المتجر",
  "price": "السعر",
  "match_percentage": نسبة التطابق,
  "row_number": رقم الصف,
  "notes": "ملاحظات"
}}"""
            
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
                
                # إذا وجدنا المنتج، نعيد النتيجة فوراً
                if data.get("found", False):
                    return {"success": True, "data": data}
                
                all_results.append(data)
        
        # إذا لم نجد المنتج في أي جزء
        return {"success": True, "data": {"found": False, "notes": "المنتج غير موجود في ملف المتجر"}}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

# ══════════════════════════════════════════════════════════════
# 2b. نسخة مبسطة للبحث السريع
# ══════════════════════════════════════════════════════════════

def verify_in_store_file_simple(product_name: str, store_file_path: str) -> Dict:
    """
    التحقق من وجود المنتج في ملف المتجر (نسخة مبسطة)
    """
    try:
        # قراءة ملف المتجر
        df = pd.read_csv(store_file_path, encoding='utf-8-sig')
        
        # البحث الذكي باستخدام Gemini
        products_list = df.iloc[:, 0].tolist()  # أول عمود = أسماء المنتجات
        prices_list = df.iloc[:, 1].tolist() if len(df.columns) > 1 else []
        
        # أخذ عينة من 200 منتج فقط للسرعة
        sample_size = min(200, len(products_list))
        sample_products = products_list[:sample_size]
        sample_prices = prices_list[:sample_size] if prices_list else []
        
        full_list = []
        for i, product in enumerate(sample_products):
            price = sample_prices[i] if i < len(sample_prices) else "غير متوفر"
            full_list.append(f"{i+1}. {product} - {price} ر.س")
        
        prompt = f"""ابحث عن المنتج التالي في القائمة:
المنتج المطلوب: {product_name}

قائمة المنتجات في المتجر (عينة من {sample_size} منتج):
{chr(10).join(full_list)}

المطلوب:
1. هل المنتج موجود في القائمة؟
2. إذا كان موجوداً، ما هو الاسم الدقيق والسعر؟
3. ما مدى التطابق (%)؟

أعد النتيجة بصيغة JSON:
{{
  "found": true/false,
  "exact_name": "الاسم الدقيق في المتجر",
  "price": "السعر",
  "match_percentage": نسبة التطابق,
  "row_number": رقم الصف,
  "notes": "ملاحظات"
}}"""

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
        
        response = requests.post(
            url,
            json={"contents": [{"parts": [{"text": prompt}]}]},
            headers={"Content-Type": "application/json"},
            timeout=60
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
            
            # إذا وجد المنتج، استخرج السعر
            if data.get("found") and data.get("row_number"):
                row_idx = data["row_number"] - 1
                if row_idx < len(df):
                    price_col = df.columns[1] if len(df.columns) > 1 else None
                    if price_col:
                        data["store_price"] = df.iloc[row_idx][price_col]
            
            return {"success": True, "data": data}
        else:
            return {"success": False, "error": f"خطأ في API: {response.status_code}"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

# ══════════════════════════════════════════════════════════════
# 3. المقارنة الذكية الشاملة
# ══════════════════════════════════════════════════════════════

def smart_comparison(
    product_name: str, 
    competitor_price: float = None,
    our_price: float = None, 
    store_file_path: Optional[str] = None
) -> Dict:
    """
    مقارنة ذكية شاملة للمنتج
    
    Args:
        product_name: اسم المنتج
        competitor_price: سعر المنافس (اختياري)
        our_price: سعرنا الحالي (اختياري)
        store_file_path: مسار ملف المتجر (اختياري)
    
    Returns:
        Dict: نتائج المقارنة الشاملة
    """
    try:
        results = {
            "product_name": product_name,
            "competitor_price": competitor_price,
            "our_price": our_price,
            "online_search": None,
            "store_verification": None,
            "analysis": None
        }
        
        # 1. البحث الإلكتروني
        online_result = search_product_online(product_name)
        if online_result["success"]:
            results["online_search"] = online_result["data"]
        
        # 2. التحقق من ملف المتجر
        if store_file_path:
            store_result = verify_in_store_file(product_name, store_file_path)
            if store_result["success"]:
                results["store_verification"] = store_result["data"]
        
        # 3. التحليل الذكي
        price_info = ""
        if competitor_price:
            price_info += f"سعر المنافس: {competitor_price} ريال\n"
        if our_price:
            price_info += f"سعرنا: {our_price} ريال\n"
        
        analysis_prompt = f"""حلل نتائج المقارنة التالية:

المنتج: {product_name}
{price_info}

نتائج البحث الإلكتروني:
{json.dumps(results["online_search"], ensure_ascii=False, indent=2) if results["online_search"] else "غير متوفر"}

نتائج التحقق من المتجر:
{json.dumps(results["store_verification"], ensure_ascii=False, indent=2) if results["store_verification"] else "غير متوفر"}

المطلوب:
1. هل سعرنا تنافسي؟
2. ما هي التوصيات؟
3. هل المنتج موجود في متجرنا؟
4. ما مدى الربحية؟

أعد النتيجة بصيغة JSON:
{{
  "competitive": true/false,
  "price_status": "منخفض/متوسط/مرتفع",
  "in_our_store": true/false,
  "profitability": "ممتاز/جيد/ضعيف",
  "recommendations": [
    "توصية 1",
    "توصية 2"
  ],
  "suggested_price": السعر المقترح,
  "notes": "ملاحظات"
}}"""

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
        
        response = requests.post(
            url,
            json={"contents": [{"parts": [{"text": analysis_prompt}]}]},
            headers={"Content-Type": "application/json"},
            timeout=60
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
            
            results["analysis"] = json.loads(text)
        
        return {"success": True, "results": results}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

# ══════════════════════════════════════════════════════════════
# 4. التحقق المجمع
# ══════════════════════════════════════════════════════════════

def batch_verification(products: List[Dict], store_file_path: Optional[str] = None) -> Dict:
    """
    تحقق مجمع لعدة منتجات
    
    Args:
        products: قائمة المنتجات [{"name": "...", "price": ...}, ...]
        store_file_path: مسار ملف المتجر (اختياري)
    
    Returns:
        Dict: نتائج التحقق المجمع
    """
    try:
        results = []
        
        for product in products:
            result = smart_comparison(
                product_name=product["name"],
                our_price=product["price"],
                store_file_path=store_file_path
            )
            results.append(result)
        
        # تحليل إجمالي
        summary_prompt = f"""حلل نتائج التحقق المجمع:

عدد المنتجات: {len(products)}
النتائج: {json.dumps(results, ensure_ascii=False, indent=2)}

المطلوب:
1. كم منتج تنافسي؟
2. كم منتج يحتاج تعديل سعر؟
3. ما هي التوصيات العامة؟

أعد النتيجة بصيغة JSON:
{{
  "total_products": العدد الإجمالي,
  "competitive_count": عدد المنتجات التنافسية,
  "needs_adjustment": عدد المنتجات التي تحتاج تعديل,
  "recommendations": ["توصية 1", "توصية 2"],
  "summary": "ملخص عام"
}}"""

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
        
        response = requests.post(
            url,
            json={"contents": [{"parts": [{"text": summary_prompt}]}]},
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        summary = None
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
            
            summary = json.loads(text)
        
        return {
            "success": True,
            "results": results,
            "summary": summary
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}
