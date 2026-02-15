"""
نظام التحقق الذكي بالذكاء الصناعي v3.0
==========================================
يوفر قدرات متقدمة للتحقق والمقارنة والبحث عن المنتجات
- مطابقة ذكية بين المنتجات (عربي/إنجليزي)
- تحقق مجمع (Batch) لتسريع العمل
- تحليل أسعار وتوصيات تسعير
- كشف أخطاء المطابقة
"""

import os
import requests
import json
import re
import time
import pandas as pd
from typing import Dict, List, Optional, Tuple
import streamlit as st

# ══════════════════════════════════════════════════════════════
# إعدادات API
# ══════════════════════════════════════════════════════════════

# قراءة GEMINI_API_KEY من Streamlit Secrets
try:
    if hasattr(st, 'secrets') and "GEMINI_API_KEY" in st.secrets:
        GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    else:
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
except Exception as e:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Fallback: إذا كان المفتاح فارغاً، استخدم المفتاح الاحتياطي
if not GEMINI_API_KEY or GEMINI_API_KEY.strip() == "":
    GEMINI_API_KEY = ""

# ══════════════════════════════════════════════════════════════
# أدوات مساعدة
# ══════════════════════════════════════════════════════════════

def _clean_json_response(text: str) -> str:
    """تنظيف استجابة JSON من Gemini"""
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


def _call_gemini(prompt: str, temperature: float = 0.1, max_tokens: int = 1024, timeout: int = 30) -> Optional[str]:
    """استدعاء Gemini API مع إعادة المحاولة"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    for attempt in range(3):
        try:
            response = requests.post(
                url,
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": temperature,
                        "maxOutputTokens": max_tokens,
                    }
                },
                headers={"Content-Type": "application/json"},
                timeout=timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                candidates = result.get("candidates", [])
                if candidates and candidates[0].get("content", {}).get("parts"):
                    return candidates[0]["content"]["parts"][0]["text"].strip()
                return None
            elif response.status_code == 429:
                # Rate limit - انتظر وأعد المحاولة
                wait_time = min(5 * (attempt + 1), 30)
                time.sleep(wait_time)
                continue
            else:
                return None
        except requests.exceptions.Timeout:
            if attempt < 2:
                time.sleep(2)
                continue
            return None
        except Exception:
            return None
    return None


# ══════════════════════════════════════════════════════════════
# نظام خبير العطور المحسّن v3.0
# ══════════════════════════════════════════════════════════════

MATCH_SYSTEM_PROMPT = """أنت خبير مطابقة عطور محترف. مهمتك تحديد هل منتجان هما نفس المنتج أم لا.

## القواعد الصارمة:
1. **متطابق** فقط إذا كل ما يلي صحيح:
   - نفس العلامة التجارية (بأي لغة: ديور=Dior، فرزاتشي=Versace، لطافة=Lattafa)
   - نفس اسم العطر (بأي لغة: سوفاج=Sauvage، كريستال نوار=Crystal Noir)
   - نفس الحجم (±5ml مقبول)
   - نفس التركيز (EDT=او دو تواليت، EDP=او دو بارفيوم، Parfum=بارفيوم)

2. **غير متطابق** إذا أي مما يلي:
   - اختلاف التركيز (EDT ≠ EDP)
   - اختلاف الحجم (أكثر من 5ml)
   - أحدهما تستر والآخر ريتيل
   - أحدهما طقم والآخر فردي
   - منتجات مختلفة من نفس الماركة

3. **تعامل مع الأسماء العربية بذكاء:**
   - "او دو بارفان" = "او دو بارفيوم" = EDP
   - "او دو تواليت" = EDT
   - "بارفيوم" = Parfum (أقوى من EDP)
   - الأرقام العربية = الأرقام اللاتينية (١٠٠ = 100)
"""

ANALYSIS_SYSTEM_PROMPT = """أنت محلل أسعار عطور محترف في السوق السعودي والخليجي.

## قواعد التسعير:
- إذا سعر المنافس أقل بأكثر من 5%: نوصي بخفض السعر
- إذا سعرنا أقل من المنافس بأكثر من 10%: نوصي برفع السعر
- إذا الفرق أقل من 5%: السعر مناسب (تثبيت)
- الربحية: ممتاز (هامش >30%)، جيد (15-30%)، ضعيف (<15%)
"""


# ══════════════════════════════════════════════════════════════
# 1. المطابقة الذكية بين منتجين (محسّنة)
# ══════════════════════════════════════════════════════════════

def verify_match_with_gemini(product1: str, product2: str) -> bool:
    """
    التحقق من تطابق منتجين باستخدام Gemini AI
    
    Returns:
        bool: True إذا كان المنتجان متطابقان
    """
    prompt = f"""{MATCH_SYSTEM_PROMPT}

## المهمة:
المنتج 1: {product1}
المنتج 2: {product2}

هل هما نفس المنتج بالضبط؟
أجب بكلمة واحدة فقط: YES أو NO"""

    text = _call_gemini(prompt, temperature=0.05, max_tokens=5, timeout=15)
    
    if text:
        text = text.upper().strip()
        if "YES" in text:
            return True
    return False


def verify_match_detailed(product1: str, product2: str) -> Dict:
    """
    تحقق مفصّل من تطابق منتجين مع شرح السبب
    
    Returns:
        Dict: {"match": bool, "confidence": int, "reason": str, "details": dict}
    """
    prompt = f"""{MATCH_SYSTEM_PROMPT}

## المهمة: تحقق مفصّل
المنتج 1: {product1}
المنتج 2: {product2}

حلل التطابق وأعد JSON فقط:
{{"match": true/false, "confidence": 0-100, "reason": "سبب مختصر", "brand_match": true/false, "name_match": true/false, "size_match": true/false, "conc_match": true/false}}"""

    text = _call_gemini(prompt, temperature=0.1, max_tokens=200, timeout=20)
    
    if text:
        try:
            data = json.loads(_clean_json_response(text))
            return {
                "match": data.get("match", False),
                "confidence": data.get("confidence", 0),
                "reason": data.get("reason", ""),
                "details": {
                    "brand_match": data.get("brand_match", False),
                    "name_match": data.get("name_match", False),
                    "size_match": data.get("size_match", False),
                    "conc_match": data.get("conc_match", False),
                }
            }
        except (json.JSONDecodeError, KeyError):
            pass
    
    return {"match": False, "confidence": 0, "reason": "فشل التحقق", "details": {}}


# ══════════════════════════════════════════════════════════════
# 2. التحقق المجمع (Batch) - أسرع 5x
# ══════════════════════════════════════════════════════════════

def batch_verify_matches(pairs: List[Tuple[str, str]], batch_size: int = 10) -> List[Dict]:
    """
    تحقق مجمع من عدة أزواج منتجات في طلب واحد
    
    Args:
        pairs: قائمة أزواج [(product1, product2), ...]
        batch_size: عدد الأزواج في كل طلب
    
    Returns:
        List[Dict]: نتائج التحقق لكل زوج
    """
    all_results = []
    
    for i in range(0, len(pairs), batch_size):
        batch = pairs[i:i + batch_size]
        
        pairs_text = ""
        for idx, (p1, p2) in enumerate(batch, 1):
            pairs_text += f"{idx}. [{p1}] vs [{p2}]\n"
        
        prompt = f"""{MATCH_SYSTEM_PROMPT}

## المهمة: تحقق مجمع من {len(batch)} زوج

{pairs_text}

لكل زوج، حدد هل هما نفس المنتج.
أعد JSON array فقط (بدون شرح):
[{{"id": 1, "match": true/false, "confidence": 0-100, "reason": "سبب مختصر"}}, ...]"""

        text = _call_gemini(prompt, temperature=0.1, max_tokens=2000, timeout=45)
        
        if text:
            try:
                data = json.loads(_clean_json_response(text))
                if isinstance(data, list):
                    all_results.extend(data)
                    continue
            except (json.JSONDecodeError, KeyError):
                pass
        
        # Fallback: إذا فشل الـbatch، نحقق واحد واحد
        for p1, p2 in batch:
            result = verify_match_with_gemini(p1, p2)
            all_results.append({
                "match": result,
                "confidence": 95 if result else 10,
                "reason": "Gemini (فردي)"
            })
    
    return all_results


# ══════════════════════════════════════════════════════════════
# 3. البحث النصي والمرئي (محسّن)
# ══════════════════════════════════════════════════════════════

def search_product_online(product_name: str, brand: str = "") -> Dict:
    """
    البحث عن المنتج في الإنترنت باستخدام Gemini
    """
    try:
        search_query = f"{brand} {product_name}" if brand else product_name
        
        prompt = f"""ابحث عن العطر التالي وأعطني معلومات عنه:
المنتج: {search_query}

أعد JSON فقط:
{{"found": true/false, "brand": "الماركة", "name": "اسم العطر", "concentration": "التركيز", "size_ml": الحجم, "average_price_sar": السعر_المتوسط_بالريال, "price_range": {{"min": أقل, "max": أعلى}}, "gender": "رجالي/نسائي/للجنسين", "notes": "ملاحظات مختصرة"}}"""

        text = _call_gemini(prompt, temperature=0.2, max_tokens=500, timeout=30)
        
        if text:
            data = json.loads(_clean_json_response(text))
            return {"success": True, "data": data}
        
        return {"success": False, "error": "لا توجد استجابة"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}


# ══════════════════════════════════════════════════════════════
# 4. التحقق من ملف المتجر (محسّن)
# ══════════════════════════════════════════════════════════════

def verify_in_store_file(product_name: str, store_file_path: str) -> Dict:
    """
    التحقق من وجود المنتج في ملف المتجر
    """
    try:
        df = pd.read_csv(store_file_path, encoding='utf-8-sig')
        
        products_list = df.iloc[:, 0].tolist()
        prices_list = df.iloc[:, 1].tolist() if len(df.columns) > 1 else []
        
        full_list = []
        for i, product in enumerate(products_list):
            price = prices_list[i] if i < len(prices_list) else "غير متوفر"
            full_list.append(f"{i+1}. {product} - {price} ر.س")
        
        # تقسيم القائمة إلى أجزاء
        chunk_size = 500
        
        for chunk_start in range(0, len(full_list), chunk_size):
            chunk_end = min(chunk_start + chunk_size, len(full_list))
            chunk = full_list[chunk_start:chunk_end]
            
            prompt = f"""ابحث عن المنتج التالي في القائمة:
المنتج المطلوب: {product_name}

قائمة المنتجات ({chunk_start+1} إلى {chunk_end}):
{chr(10).join(chunk)}

أعد JSON فقط:
{{"found": true/false, "exact_name": "الاسم الدقيق", "price": السعر, "match_percentage": نسبة_التطابق, "row_number": رقم_الصف, "notes": "ملاحظات"}}"""
            
            text = _call_gemini(prompt, temperature=0.1, max_tokens=200, timeout=30)
            
            if text:
                try:
                    data = json.loads(_clean_json_response(text))
                    if data.get("found", False):
                        return {"success": True, "data": data}
                except (json.JSONDecodeError, KeyError):
                    continue
        
        return {"success": True, "data": {"found": False, "notes": "المنتج غير موجود في ملف المتجر"}}
        
    except Exception as e:
        return {"success": False, "error": str(e)}


def verify_in_store_file_simple(product_name: str, store_file_path: str) -> Dict:
    """
    التحقق السريع من وجود المنتج في ملف المتجر (عينة 200)
    """
    try:
        df = pd.read_csv(store_file_path, encoding='utf-8-sig')
        
        products_list = df.iloc[:, 0].tolist()
        prices_list = df.iloc[:, 1].tolist() if len(df.columns) > 1 else []
        
        sample_size = min(200, len(products_list))
        sample_products = products_list[:sample_size]
        sample_prices = prices_list[:sample_size] if prices_list else []
        
        full_list = []
        for i, product in enumerate(sample_products):
            price = sample_prices[i] if i < len(sample_prices) else "غير متوفر"
            full_list.append(f"{i+1}. {product} - {price} ر.س")
        
        prompt = f"""ابحث عن المنتج التالي في القائمة:
المنتج المطلوب: {product_name}

قائمة المنتجات (عينة من {sample_size} منتج):
{chr(10).join(full_list)}

أعد JSON فقط:
{{"found": true/false, "exact_name": "الاسم الدقيق", "price": السعر, "match_percentage": نسبة_التطابق, "row_number": رقم_الصف, "notes": "ملاحظات"}}"""

        text = _call_gemini(prompt, temperature=0.1, max_tokens=200, timeout=30)
        
        if text:
            data = json.loads(_clean_json_response(text))
            
            if data.get("found") and data.get("row_number"):
                row_idx = data["row_number"] - 1
                if row_idx < len(df):
                    price_col = df.columns[1] if len(df.columns) > 1 else None
                    if price_col:
                        data["store_price"] = df.iloc[row_idx][price_col]
            
            return {"success": True, "data": data}
        
        return {"success": False, "error": "لا توجد استجابة"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}


# ══════════════════════════════════════════════════════════════
# 5. المقارنة الذكية الشاملة (محسّنة)
# ══════════════════════════════════════════════════════════════

def smart_comparison(
    product_name: str, 
    competitor_price: float = None,
    our_price: float = None, 
    store_file_path: Optional[str] = None
) -> Dict:
    """
    مقارنة ذكية شاملة للمنتج مع تحليل وتوصيات
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
            store_result = verify_in_store_file_simple(product_name, store_file_path)
            if store_result["success"]:
                results["store_verification"] = store_result["data"]
        
        # 3. التحليل الذكي
        price_info = ""
        if competitor_price:
            price_info += f"سعر المنافس: {competitor_price} ريال\n"
        if our_price:
            price_info += f"سعرنا: {our_price} ريال\n"
        if competitor_price and our_price:
            diff = our_price - competitor_price
            diff_pct = (diff / competitor_price * 100) if competitor_price > 0 else 0
            price_info += f"الفرق: {diff:.2f} ريال ({diff_pct:.1f}%)\n"
        
        analysis_prompt = f"""{ANALYSIS_SYSTEM_PROMPT}

المنتج: {product_name}
{price_info}

أعد JSON فقط:
{{"competitive": true/false, "price_status": "منخفض/متوسط/مرتفع", "in_our_store": true/false, "profitability": "ممتاز/جيد/ضعيف", "recommendations": ["توصية 1", "توصية 2"], "suggested_price": السعر_المقترح, "notes": "ملاحظات"}}"""

        text = _call_gemini(analysis_prompt, temperature=0.2, max_tokens=500, timeout=30)
        
        if text:
            try:
                results["analysis"] = json.loads(_clean_json_response(text))
            except (json.JSONDecodeError, KeyError):
                results["analysis"] = {
                    "competitive": False,
                    "price_status": "غير محدد",
                    "notes": "فشل التحليل"
                }
        
        return {"success": True, "results": results}
        
    except Exception as e:
        return {"success": False, "error": str(e)}


# ══════════════════════════════════════════════════════════════
# 6. التحقق المجمع للمنتجات (محسّن)
# ══════════════════════════════════════════════════════════════

def batch_verification(products: List[Dict], store_file_path: Optional[str] = None) -> Dict:
    """
    تحقق مجمع لعدة منتجات مع تقرير شامل
    """
    try:
        results = []
        
        for product in products:
            result = smart_comparison(
                product_name=product["name"],
                our_price=product.get("price"),
                competitor_price=product.get("competitor_price"),
                store_file_path=store_file_path
            )
            results.append(result)
        
        # تحليل إجمالي
        summary_prompt = f"""حلل نتائج التحقق المجمع:

عدد المنتجات: {len(products)}
النتائج: {json.dumps(results, ensure_ascii=False, indent=2)[:3000]}

أعد JSON فقط:
{{"total_products": {len(products)}, "competitive_count": عدد_التنافسية, "needs_adjustment": عدد_التعديل, "recommendations": ["توصية 1", "توصية 2"], "summary": "ملخص عام"}}"""

        text = _call_gemini(summary_prompt, temperature=0.2, max_tokens=500, timeout=30)
        
        summary = None
        if text:
            try:
                summary = json.loads(_clean_json_response(text))
            except (json.JSONDecodeError, KeyError):
                pass
        
        return {
            "success": True,
            "results": results,
            "summary": summary
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


# ══════════════════════════════════════════════════════════════
# 7. كشف أخطاء المطابقة (جديد)
# ══════════════════════════════════════════════════════════════

def detect_matching_errors(matches: List[Dict], batch_size: int = 5) -> List[Dict]:
    """
    كشف أخطاء المطابقة في نتائج موجودة
    
    Args:
        matches: قائمة المطابقات [{"our_product": "...", "competitor_product": "...", "confidence": ...}, ...]
        batch_size: عدد المطابقات في كل طلب
    
    Returns:
        List[Dict]: المطابقات المشبوهة مع السبب
    """
    suspicious = []
    
    for i in range(0, len(matches), batch_size):
        batch = matches[i:i + batch_size]
        
        pairs_text = ""
        for idx, m in enumerate(batch, 1):
            pairs_text += f"{idx}. [{m.get('our_product', '')}] ↔ [{m.get('competitor_product', '')}] (ثقة: {m.get('confidence', 0)}%)\n"
        
        prompt = f"""{MATCH_SYSTEM_PROMPT}

## المهمة: كشف أخطاء المطابقة
راجع المطابقات التالية وحدد أي منها خاطئ:

{pairs_text}

لكل مطابقة مشبوهة، أعد JSON array:
[{{"id": رقم, "error": true/false, "reason": "سبب الخطأ", "severity": "حرج/متوسط/بسيط"}}]
إذا كلها صحيحة أعد: []"""

        text = _call_gemini(prompt, temperature=0.1, max_tokens=1000, timeout=30)
        
        if text:
            try:
                data = json.loads(_clean_json_response(text))
                if isinstance(data, list):
                    for item in data:
                        if item.get("error"):
                            idx = item.get("id", 1) - 1
                            if 0 <= idx < len(batch):
                                suspicious.append({
                                    **batch[idx],
                                    "error_reason": item.get("reason", ""),
                                    "severity": item.get("severity", "متوسط"),
                                })
            except (json.JSONDecodeError, KeyError):
                pass
    
    return suspicious
