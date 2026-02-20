"""
نظام التحقق الذكي بالذكاء الصناعي v5.0
==========================================
يوفر قدرات متقدمة للتحقق والمقارنة والبحث عن المنتجات
- نظام مفاتيح متعددة مع تبديل تلقائي (Gemini + OpenRouter)
- توصيات تسعير حقيقية متخصصة لكل قسم
- مطابقة ذكية بين المنتجات (عربي/إنجليزي)
- تحقق مجمع (Batch) لتسريع العمل
- أزرار قرار: تعديل / تأجيل / إزالة
"""

import os
import requests
import json
import time
import pandas as pd
from typing import Dict, List, Optional, Tuple
import streamlit as st

# ══════════════════════════════════════════════════════════════
# نظام المفاتيح المتعددة مع تبديل تلقائي
# ══════════════════════════════════════════════════════════════

class MultiKeyManager:
    """مدير المفاتيح المتعددة - يبدّل تلقائياً عند الفشل"""
    
    def __init__(self):
        self.gemini_keys = []
        self.openrouter_keys = []
        self.current_gemini_idx = 0
        self.current_openrouter_idx = 0
        self.failed_keys = {}  # key -> timestamp of failure
        self.call_counts = {}  # key -> number of calls
        self.total_calls = 0
        self.total_failures = 0
        self.provider_used = "none"  # آخر مزود تم استخدامه
        self._load_keys()
    
    def _load_keys(self):
        """تحميل المفاتيح من Streamlit Secrets أو متغيرات البيئة أو الملف المحلي"""
        # تحميل المفاتيح من ملف محلي أولاً
        self._load_keys_from_file()
        
        # تحميل مفاتيح Gemini
        gemini_sources = [
            "GEMINI_API_KEY", "GEMINI_API_KEY_1", "GEMINI_API_KEY_2", 
            "GEMINI_API_KEY_3", "GEMINI_API_KEY_4", "GEMINI_API_KEY_5"
        ]
        
        for key_name in gemini_sources:
            key_val = self._get_secret(key_name)
            if key_val and key_val.strip() and key_val not in self.gemini_keys:
                self.gemini_keys.append(key_val.strip())
        
        # تحميل مفاتيح OpenRouter
        openrouter_sources = [
            "OPENROUTER_API_KEY", "OPENROUTER_API_KEY_1", "OPENROUTER_API_KEY_2"
        ]
        
        for key_name in openrouter_sources:
            key_val = self._get_secret(key_name)
            if key_val and key_val.strip() and key_val not in self.openrouter_keys:
                self.openrouter_keys.append(key_val.strip())
    def _load_keys_from_file(self):
        """تحميل المفاتيح من ملف محلي"""
        try:
            secrets_file = ".secrets/api_keys.json"
            if os.path.exists(secrets_file):
                with open(secrets_file, "r") as f:
                    data = json.load(f)
                
                # تحميل مفاتيح Gemini من الملف
                gemini_keys = data.get("gemini_keys", [])
                for key in gemini_keys:
                    if key and key.strip() and key not in self.gemini_keys:
                        self.gemini_keys.append(key.strip())
                
                # تحميل مفاتيح OpenRouter من الملف (إذا كانت موجودة)
                openrouter_keys = data.get("openrouter_keys", [])
                for key in openrouter_keys:
                    if key and key.strip() and key not in self.openrouter_keys:
                        self.openrouter_keys.append(key.strip())
                        
        except Exception as e:
            # إذا فشل تحميل الملف، نستمر بدون أخطاء
            pass

    @staticmethod
    def _get_secret(name: str) -> str:
        """قراءة سر من Streamlit Secrets أو متغيرات البيئة"""
        try:
            if hasattr(st, 'secrets') and name in st.secrets:
                return st.secrets[name]
        except:
            pass
        return os.getenv(name, "")

    def _is_key_failed(self, key: str) -> bool:
        """هل المفتاح فاشل مؤخراً (خلال 5 دقائق)"""
        if key in self.failed_keys:
            if time.time() - self.failed_keys[key] < 300:  # 5 دقائق
                return True
            else:
                del self.failed_keys[key]  # انتهت فترة الحظر
        return False

    def mark_failed(self, key: str):
        """تسجيل فشل مفتاح"""
        self.failed_keys[key] = time.time()
        self.total_failures += 1

    def mark_success(self, key: str):
        """تسجيل نجاح مفتاح"""
        self.call_counts[key] = self.call_counts.get(key, 0) + 1
        self.total_calls += 1
        if key in self.failed_keys:
            del self.failed_keys[key]
    
    def get_next_gemini_key(self) -> Optional[str]:
        """الحصول على مفتاح Gemini التالي المتاح"""
        if not self.gemini_keys:
            return None
        
        for _ in range(len(self.gemini_keys)):
            key = self.gemini_keys[self.current_gemini_idx % len(self.gemini_keys)]
            self.current_gemini_idx += 1
            if not self._is_key_failed(key):
                return key
        
        # كل المفاتيح فاشلة - أعد أول واحد كمحاولة أخيرة
        return self.gemini_keys[0]
    
    def get_next_openrouter_key(self) -> Optional[str]:
        """الحصول على مفتاح OpenRouter التالي المتاح"""
        if not self.openrouter_keys:
            return None
        
        for _ in range(len(self.openrouter_keys)):
            key = self.openrouter_keys[self.current_openrouter_idx % len(self.openrouter_keys)]
            self.current_openrouter_idx += 1
            if not self._is_key_failed(key):
                return key
        
        return self.openrouter_keys[0]
    
    def get_status(self) -> Dict:
        """حالة المفاتيح"""
        active_gemini = sum(1 for k in self.gemini_keys if not self._is_key_failed(k))
        active_openrouter = sum(1 for k in self.openrouter_keys if not self._is_key_failed(k))
        return {
            "gemini_total": len(self.gemini_keys),
            "gemini_active": active_gemini,
            "openrouter_total": len(self.openrouter_keys),
            "openrouter_active": active_openrouter,
            "total_calls": self.total_calls,
            "total_failures": self.total_failures,
            "provider_used": self.provider_used,
        }


# إنشاء مدير المفاتيح العالمي
key_manager = MultiKeyManager()


# ══════════════════════════════════════════════════════════════
# أدوات مساعدة
# ══════════════════════════════════════════════════════════════

def _clean_json_response(text: str) -> str:
    """تنظيف استجابة JSON من AI"""
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


def _call_gemini(prompt: str, temperature: float = 0.1, max_tokens: int = 1024, timeout: int = 30) -> Optional[str]:
    """استدعاء Gemini API مع تبديل تلقائي للمفاتيح"""
    
    # محاولة مع كل مفاتيح Gemini المتاحة
    tried_keys = set()
    for _ in range(len(key_manager.gemini_keys) + 1):
        api_key = key_manager.get_next_gemini_key()
        if not api_key or api_key in tried_keys:
            break
        tried_keys.add(api_key)
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
        
        for attempt in range(2):
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
                        key_manager.mark_success(api_key)
                        key_manager.provider_used = "gemini"
                        return candidates[0]["content"]["parts"][0]["text"].strip()
                    return None
                elif response.status_code == 429:
                    # Rate limit - جرب المفتاح التالي
                    key_manager.mark_failed(api_key)
                    break  # اخرج من حلقة المحاولات وجرب مفتاح آخر
                elif response.status_code == 400:
                    try:
                        err = response.json().get("error", {}).get("message", "")
                        if "leaked" in err.lower() or "invalid" in err.lower() or "API_KEY" in err:
                            key_manager.mark_failed(api_key)
                            break
                    except:
                        pass
                    key_manager.mark_failed(api_key)
                    break
                else:
                    key_manager.mark_failed(api_key)
                    break
            except requests.exceptions.Timeout:
                if attempt == 0:
                    continue
                key_manager.mark_failed(api_key)
                break
            except Exception:
                key_manager.mark_failed(api_key)
                break
    
    # Fallback: استخدام OpenRouter
    return _call_openrouter(prompt, temperature, max_tokens, timeout)


def _call_openrouter(prompt: str, temperature: float = 0.1, max_tokens: int = 1024, timeout: int = 30) -> Optional[str]:
    """استدعاء OpenRouter API كبديل"""
    
    tried_keys = set()
    for _ in range(len(key_manager.openrouter_keys) + 1):
        api_key = key_manager.get_next_openrouter_key()
        if not api_key or api_key in tried_keys:
            break
        tried_keys.add(api_key)
        
        url = "https://openrouter.ai/api/v1/chat/completions"
        
        for attempt in range(2):
            try:
                response = requests.post(
                    url,
                    json={
                        "model": "google/gemini-2.0-flash-001",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                    },
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    timeout=timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    choices = result.get("choices", [])
                    if choices and choices[0].get("message", {}).get("content"):
                        key_manager.mark_success(api_key)
                        key_manager.provider_used = "openrouter"
                        return choices[0]["message"]["content"].strip()
                    return None
                elif response.status_code == 429:
                    key_manager.mark_failed(api_key)
                    break
                else:
                    if attempt == 0:
                        time.sleep(1)
                        continue
                    key_manager.mark_failed(api_key)
                    break
            except requests.exceptions.Timeout:
                if attempt == 0:
                    continue
                key_manager.mark_failed(api_key)
                break
            except Exception:
                key_manager.mark_failed(api_key)
                break
    
    return None


def get_ai_status() -> Dict:
    """حالة AI الشاملة"""
    status = key_manager.get_status()
    status["available"] = (status["gemini_active"] > 0 or status["openrouter_active"] > 0)
    return status


def verify_ai_connection() -> Dict:
    """فحص اتصال AI فعلي"""
    result = _call_gemini("أجب بكلمة: مرحبا", temperature=0.1, max_tokens=10, timeout=15)
    status = key_manager.get_status()
    
    if result:
        return {
            "connected": True,
            "provider": key_manager.provider_used,
            "message": f"متصل عبر {key_manager.provider_used}",
            **status
        }
    else:
        return {
            "connected": False,
            "provider": "none",
            "message": "جميع المفاتيح فاشلة",
            **status
        }


# ══════════════════════════════════════════════════════════════
# نظام خبير العطور المحسّن v5.0
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


# ══════════════════════════════════════════════════════════════
# 1. المطابقة الذكية بين منتجين
# ══════════════════════════════════════════════════════════════

def verify_match_with_gemini(product1: str, product2: str) -> bool:
    """التحقق من تطابق منتجين باستخدام AI"""
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
    """تحقق مفصّل من تطابق منتجين مع شرح السبب"""
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
    """تحقق مجمع من عدة أزواج منتجات في طلب واحد"""
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
                "reason": "AI (فردي)"
            })
    
    return all_results


# ══════════════════════════════════════════════════════════════
# 3. تحليل ذكي متخصص لكل قسم (جديد v5.0)
# ══════════════════════════════════════════════════════════════

def analyze_for_section(
    section_type: str,
    our_product: str,
    competitor_product: str = "",
    our_price: float = 0,
    competitor_price: float = 0,
    competitor_name: str = "",
    confidence: float = 0,
    diff_pct: float = 0,
) -> Dict:
    """
    تحليل ذكي متخصص حسب نوع القسم
    
    section_type: "raise" | "lower" | "approved" | "missing"
    
    Returns:
        Dict مع: match_correct, recommendation, action, reason, suggested_price, details
    """
    
    # حساب الفرق إذا لم يُعطى
    if our_price and competitor_price and diff_pct == 0:
        diff_pct = ((our_price - competitor_price) / competitor_price * 100) if competitor_price > 0 else 0
    
    diff_amount = our_price - competitor_price if our_price and competitor_price else 0
    
    # بناء prompt مخصص حسب القسم
    if section_type == "raise":
        section_prompt = f"""أنت خبير تسعير عطور في السوق السعودي. هذا المنتج في قسم "رفع السعر" - يعني سعرنا أعلى من المنافس.

## بيانات المنتج:
- منتجنا: {our_product}
- منتج المنافس: {competitor_product}
- المنافس: {competitor_name}
- سعرنا: {our_price} ريال
- سعر المنافس: {competitor_price} ريال
- الفرق: {diff_amount:.2f} ريال ({diff_pct:.1f}%)
- نسبة ثقة المطابقة: {confidence}%

## مهمتك:
1. تأكد أن المنتجين فعلاً نفس المنتج (نفس الماركة + الاسم + الحجم + التركيز)
2. إذا كانت المطابقة صحيحة: هل يجب فعلاً خفض سعرنا؟ أم أن الفرق مقبول؟
3. اقترح سعراً مناسباً يحقق التنافسية مع الحفاظ على هامش ربح

## أجب بـ JSON فقط:
{{"match_correct": true/false, "match_reason": "هل المنتجان متطابقان فعلاً؟ اشرح بالتفصيل", "recommendation": "نص التوصية التفصيلية (3-4 جمل)", "action": "تعديل السعر/تأجيل/إزالة من القائمة", "suggested_price": السعر_المقترح_رقم, "urgency": "عاجل/متوسط/منخفض", "reason": "سبب التوصية المختصر"}}"""

    elif section_type == "lower":
        section_prompt = f"""أنت خبير تسعير عطور في السوق السعودي. هذا المنتج في قسم "خفض السعر" - يعني سعرنا أقل من المنافس.

## بيانات المنتج:
- منتجنا: {our_product}
- منتج المنافس: {competitor_product}
- المنافس: {competitor_name}
- سعرنا: {our_price} ريال
- سعر المنافس: {competitor_price} ريال
- الفرق: {diff_amount:.2f} ريال ({diff_pct:.1f}%)
- نسبة ثقة المطابقة: {confidence}%

## مهمتك:
1. تأكد أن المنتجين فعلاً نفس المنتج
2. إذا سعرنا أقل: هل نرفع السعر للاستفادة من الفرصة؟ أم نبقيه كميزة تنافسية؟
3. اقترح سعراً يحقق أفضل ربح

## أجب بـ JSON فقط:
{{"match_correct": true/false, "match_reason": "هل المنتجان متطابقان فعلاً؟ اشرح بالتفصيل", "recommendation": "نص التوصية التفصيلية (3-4 جمل)", "action": "رفع السعر/تأجيل/إزالة من القائمة", "suggested_price": السعر_المقترح_رقم, "urgency": "عاجل/متوسط/منخفض", "reason": "سبب التوصية المختصر"}}"""

    elif section_type == "approved":
        section_prompt = f"""أنت خبير تسعير عطور في السوق السعودي. هذا المنتج في قسم "موافق عليها" - يعني السعر متقارب مع المنافس.

## بيانات المنتج:
- منتجنا: {our_product}
- منتج المنافس: {competitor_product}
- المنافس: {competitor_name}
- سعرنا: {our_price} ريال
- سعر المنافس: {competitor_price} ريال
- الفرق: {diff_amount:.2f} ريال ({diff_pct:.1f}%)
- نسبة ثقة المطابقة: {confidence}%

## مهمتك:
1. تأكد أن المطابقة صحيحة
2. هل السعر فعلاً مناسب أم يحتاج تعديل بسيط؟
3. هل هناك فرصة لتحسين الربح؟

## أجب بـ JSON فقط:
{{"match_correct": true/false, "match_reason": "هل المنتجان متطابقان فعلاً؟ اشرح بالتفصيل", "recommendation": "نص التوصية التفصيلية (3-4 جمل)", "action": "تثبيت السعر/تعديل بسيط/إزالة من القائمة", "suggested_price": السعر_المقترح_رقم, "urgency": "منخفض/متوسط", "reason": "سبب التوصية المختصر"}}"""

    elif section_type == "missing":
        section_prompt = f"""أنت خبير عطور في السوق السعودي. هذا المنتج موجود عند المنافس وغير موجود عندنا.

## بيانات المنتج:
- المنتج: {our_product}
- المنافس: {competitor_name}
- سعر المنافس: {competitor_price} ريال

## مهمتك:
1. حدد نوع المنتج (عطر رجالي/نسائي/للجنسين، تركيز، حجم)
2. هل يستحق الإضافة لمتجرنا؟
3. ما السعر المقترح للبيع؟
4. ما هو هامش الربح المتوقع؟

## أجب بـ JSON فقط:
{{"product_type": "نوع المنتج", "brand": "الماركة", "worth_adding": true/false, "recommendation": "نص التوصية التفصيلية (3-4 جمل)", "action": "إضافة للمتجر/تأجيل/تجاهل", "suggested_sell_price": السعر_المقترح_للبيع, "estimated_cost": التكلفة_المتوقعة, "profit_margin": "هامش الربح المتوقع", "reason": "سبب التوصية المختصر"}}"""
    else:
        return {"success": False, "error": "نوع قسم غير معروف"}
    
    # استدعاء AI
    text = _call_gemini(section_prompt, temperature=0.3, max_tokens=800, timeout=30)
    
    if text:
        try:
            data = json.loads(_clean_json_response(text))
            return {
                "success": True,
                "provider": key_manager.provider_used,
                "data": data
            }
        except (json.JSONDecodeError, KeyError):
            # محاولة استخراج المعلومات من النص العادي
            return {
                "success": True,
                "provider": key_manager.provider_used,
                "data": {
                    "match_correct": True,
                    "recommendation": text[:500],
                    "action": "تأجيل",
                    "reason": "تم الحصول على رد نصي",
                    "suggested_price": our_price or competitor_price or 0,
                }
            }
    
    return {"success": False, "error": "فشل الاتصال بالذكاء الاصطناعي"}


# ══════════════════════════════════════════════════════════════
# 4. البحث عن المنتج (محسّن)
# ══════════════════════════════════════════════════════════════

def search_product_online(product_name: str, brand: str = "") -> Dict:
    """البحث عن المنتج باستخدام AI"""
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
# 5. التحقق من ملف المتجر
# ══════════════════════════════════════════════════════════════

def verify_in_store_file(product_name: str, store_file_path: str) -> Dict:
    """التحقق من وجود المنتج في ملف المتجر"""
    try:
        df = pd.read_csv(store_file_path, encoding='utf-8-sig')
        
        products_list = df.iloc[:, 0].tolist()
        prices_list = df.iloc[:, 1].tolist() if len(df.columns) > 1 else []
        
        full_list = []
        for i, product in enumerate(products_list):
            price = prices_list[i] if i < len(prices_list) else "غير متوفر"
            full_list.append(f"{i+1}. {product} - {price} ر.س")
        
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
    """التحقق السريع من وجود المنتج في ملف المتجر (عينة 200)"""
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
# 6. المقارنة الذكية الشاملة (متوافقة مع الإصدار القديم)
# ══════════════════════════════════════════════════════════════

def smart_comparison(
    product_name: str, 
    competitor_price: float = None,
    our_price: float = None, 
    store_file_path: Optional[str] = None
) -> Dict:
    """مقارنة ذكية شاملة للمنتج مع تحليل وتوصيات"""
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
        
        analysis_prompt = f"""أنت محلل أسعار عطور محترف في السوق السعودي والخليجي.

المنتج: {product_name}
{price_info}

حلل هذا المنتج وأعطني توصيات تسعير حقيقية ومفصلة.

أعد JSON فقط:
{{"competitive": true/false, "price_status": "منخفض/متوسط/مرتفع", "in_our_store": true/false, "profitability": "ممتاز/جيد/ضعيف", "recommendations": ["توصية تفصيلية 1", "توصية تفصيلية 2", "توصية تفصيلية 3"], "suggested_price": السعر_المقترح, "notes": "ملاحظات تفصيلية عن المنتج والسوق"}}"""

        text = _call_gemini(analysis_prompt, temperature=0.3, max_tokens=600, timeout=30)
        
        if text:
            try:
                results["analysis"] = json.loads(_clean_json_response(text))
            except (json.JSONDecodeError, KeyError):
                results["analysis"] = {
                    "competitive": False,
                    "price_status": "غير محدد",
                    "recommendations": ["لم يتمكن AI من تحليل المنتج بشكل كامل"],
                    "notes": "فشل التحليل - يرجى المحاولة مرة أخرى"
                }
        
        return {"success": True, "results": results}
        
    except Exception as e:
        return {"success": False, "error": str(e)}


# ══════════════════════════════════════════════════════════════
# 7. التحقق المجمع للمنتجات
# ══════════════════════════════════════════════════════════════

def batch_verification(products: List[Dict], store_file_path: Optional[str] = None, **kwargs) -> Dict:
    """تحقق مجمع لعدة منتجات مع تقرير شامل"""
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
# 8. كشف أخطاء المطابقة
# ══════════════════════════════════════════════════════════════

def detect_matching_errors(matches: List[Dict], batch_size: int = 5) -> List[Dict]:
    """كشف أخطاء المطابقة في نتائج موجودة"""
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
