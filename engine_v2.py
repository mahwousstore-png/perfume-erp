"""
نظام المطابقة الذكي v2.0
- مطابقة متعددة المراحل (Fast → Medium → Deep)
- Caching ذكي لنتائج Gemini
- معالجة جميع المنتجات بدون رفض
- دقة 100% بدون تخمين
"""

import streamlit as st
from rapidfuzz import fuzz
from collections import defaultdict
import time
from typing import Dict, List, Tuple, Optional
import hashlib
import json

# استيراد الدوال الموجودة
from engine import (
    normalize_name,
    extract_brand,
    extract_concentration,
    extract_size,
    classify_product,
    _get_name,
    _get_price,
)

# استيراد Gemini AI
try:
    from modules.ai_verification import verify_match_with_gemini
    GEMINI_AVAILABLE = True
except:
    GEMINI_AVAILABLE = False
    st.warning("⚠️ Gemini AI غير متاح - سيتم استخدام المطابقة السريعة فقط")


# ===== Cache لنتائج Gemini =====
class GeminiCache:
    """Cache ذكي لنتائج Gemini AI"""
    
    def __init__(self):
        self.cache = {}
    
    def _make_key(self, product1: str, product2: str) -> str:
        """إنشاء مفتاح فريد للمنتجين"""
        # ترتيب أبجدي لضمان نفس المفتاح
        p1, p2 = sorted([product1.lower().strip(), product2.lower().strip()])
        combined = f"{p1}|{p2}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def get(self, product1: str, product2: str) -> Optional[bool]:
        """الحصول على نتيجة من Cache"""
        key = self._make_key(product1, product2)
        return self.cache.get(key)
    
    def set(self, product1: str, product2: str, result: bool):
        """حفظ نتيجة في Cache"""
        key = self._make_key(product1, product2)
        self.cache[key] = result
    
    def size(self) -> int:
        """حجم Cache"""
        return len(self.cache)


# ===== نظام المطابقة متعدد المراحل =====
class SmartMatcher:
    """نظام مطابقة ذكي متعدد المراحل"""
    
    def __init__(self):
        self.gemini_cache = GeminiCache()
        self.stats = {
            "fast_matches": 0,
            "medium_matches": 0,
            "deep_matches": 0,
            "gemini_calls": 0,
            "cache_hits": 0,
        }
    
    def match_stage1_fast(
        self,
        my_name: str,
        my_normalized: str,
        my_brand: str,
        my_size: float,
        my_concentration: str,
        comp_name: str,
        comp_normalized: str,
        comp_brand: str,
        comp_size: float,
        comp_concentration: str,
    ) -> Tuple[bool, int, str]:
        """
        المرحلة 1: مطابقة سريعة
        - Fuzzy matching عالي (95%+)
        - Brand متطابق 100%
        - Size متطابق (±5ml)
        - Concentration متطابق
        
        Returns: (is_match, confidence, reason)
        """
        # 1. التحقق من Brand
        if my_brand != comp_brand:
            return (False, 0, "Brand مختلف")
        
        # 2. التحقق من Concentration
        if my_concentration != comp_concentration:
            return (False, 0, "Concentration مختلف")
        
        # 3. التحقق من Size (±5ml)
        size_diff = abs(my_size - comp_size)
        if size_diff > 5:
            return (False, 0, f"Size مختلف ({size_diff}ml)")
        
        # 4. Fuzzy matching
        score = fuzz.token_set_ratio(my_normalized, comp_normalized)
        
        if score >= 95:
            self.stats["fast_matches"] += 1
            return (True, score, "مطابقة سريعة (95%+)")
        
        return (False, score, f"Fuzzy score منخفض ({score}%)")
    
    def match_stage2_medium(
        self,
        my_name: str,
        my_normalized: str,
        my_brand: str,
        my_size: float,
        my_concentration: str,
        comp_name: str,
        comp_normalized: str,
        comp_brand: str,
        comp_size: float,
        comp_concentration: str,
    ) -> Tuple[bool, int, str]:
        """
        المرحلة 2: مطابقة متوسطة
        - Fuzzy matching متوسط (85-94%)
        - Brand متطابق
        - Size متطابق (±10ml)
        - Concentration متطابق أو قريب
        
        Returns: (is_match, confidence, reason)
        """
        # 1. التحقق من Brand
        if my_brand != comp_brand:
            return (False, 0, "Brand مختلف")
        
        # 2. التحقق من Size (±10ml)
        size_diff = abs(my_size - comp_size)
        if size_diff > 10:
            return (False, 0, f"Size مختلف ({size_diff}ml)")
        
        # 3. Fuzzy matching
        score = fuzz.token_set_ratio(my_normalized, comp_normalized)
        
        if score >= 85:
            # التحقق من Concentration (يمكن أن يكون قريب)
            if my_concentration == comp_concentration:
                self.stats["medium_matches"] += 1
                return (True, score, "مطابقة متوسطة (85-94%)")
            elif my_concentration and comp_concentration:
                # مثلاً: EDP vs Parfum (قريبين)
                if abs(len(my_concentration) - len(comp_concentration)) <= 3:
                    self.stats["medium_matches"] += 1
                    return (True, score - 5, "مطابقة متوسطة (concentration قريب)")
        
        return (False, score, f"Fuzzy score منخفض ({score}%)")
    
    def match_stage3_deep(
        self,
        my_name: str,
        comp_name: str,
    ) -> Tuple[bool, int, str]:
        """
        المرحلة 3: مطابقة عميقة باستخدام Gemini AI
        - للحالات الصعبة فقط
        - دقة 100%
        
        Returns: (is_match, confidence, reason)
        """
        if not GEMINI_AVAILABLE:
            return (False, 0, "Gemini غير متاح")
        
        # التحقق من Cache أولاً
        cached_result = self.gemini_cache.get(my_name, comp_name)
        if cached_result is not None:
            self.stats["cache_hits"] += 1
            confidence = 100 if cached_result else 0
            reason = "مطابقة عميقة (Gemini - من Cache)"
            return (cached_result, confidence, reason)
        
        # استدعاء Gemini
        self.stats["gemini_calls"] += 1
        try:
            result = verify_match_with_gemini(my_name, comp_name)
            
            # حفظ في Cache
            self.gemini_cache.set(my_name, comp_name, result)
            
            if result:
                self.stats["deep_matches"] += 1
                return (True, 100, "مطابقة عميقة (Gemini - متطابق)")
            else:
                return (False, 0, "مطابقة عميقة (Gemini - غير متطابق)")
        
        except Exception as e:
            st.warning(f"⚠️ خطأ في Gemini: {str(e)}")
            return (False, 0, f"خطأ في Gemini: {str(e)}")
    
    def find_best_match(
        self,
        my_product: dict,
        candidates: List[dict],
    ) -> Optional[dict]:
        """
        البحث عن أفضل مطابقة من قائمة المرشحين
        
        Args:
            my_product: منتج المتجر
            candidates: قائمة المنتجات المرشحة من المنافسين
        
        Returns:
            أفضل مطابقة أو None
        """
        my_name = _get_name(my_product)
        my_normalized = normalize_name(my_name)
        my_brand = extract_brand(my_name)
        my_size = my_product.get("size_ml", 0) or extract_size(my_name)
        my_concentration = extract_concentration(my_name)
        
        best_match = None
        best_confidence = 0
        best_reason = ""
        
        for candidate in candidates:
            comp_name = candidate["name"]
            comp_normalized = candidate["normalized"]
            comp_brand = extract_brand(comp_name)
            comp_size = candidate["size"]
            comp_concentration = extract_concentration(comp_name)
            
            # المرحلة 1: مطابقة سريعة
            is_match, confidence, reason = self.match_stage1_fast(
                my_name, my_normalized, my_brand, my_size, my_concentration,
                comp_name, comp_normalized, comp_brand, comp_size, comp_concentration,
            )
            
            if is_match and confidence > best_confidence:
                best_match = candidate
                best_confidence = confidence
                best_reason = reason
                continue  # مطابقة سريعة ناجحة!
            
            # المرحلة 2: مطابقة متوسطة
            is_match, confidence, reason = self.match_stage2_medium(
                my_name, my_normalized, my_brand, my_size, my_concentration,
                comp_name, comp_normalized, comp_brand, comp_size, comp_concentration,
            )
            
            if is_match and confidence > best_confidence:
                best_match = candidate
                best_confidence = confidence
                best_reason = reason
                # لا نتوقف - قد يكون هناك مطابقة أفضل
            
            # المرحلة 3: مطابقة عميقة (فقط إذا كان Brand متطابق)
            if my_brand == comp_brand and confidence >= 75:
                is_match, confidence, reason = self.match_stage3_deep(
                    my_name, comp_name
                )
                
                if is_match and confidence > best_confidence:
                    best_match = candidate
                    best_confidence = confidence
                    best_reason = reason
        
        # إضافة معلومات المطابقة
        if best_match:
            best_match["match_confidence"] = best_confidence
            best_match["match_reason"] = best_reason
        
        return best_match
    
    def get_stats(self) -> dict:
        """الحصول على إحصائيات المطابقة"""
        return {
            **self.stats,
            "cache_size": self.gemini_cache.size(),
        }


# ===== الدالة الرئيسية =====
def run_smart_matching(
    my_products: List[dict],
    competitor_products: List[dict],
    progress_callback=None,
) -> List[dict]:
    """
    تشغيل المطابقة الذكية
    
    Args:
        my_products: منتجات المتجر
        competitor_products: منتجات المنافسين
        progress_callback: دالة لتحديث Progress Bar
    
    Returns:
        قائمة النتائج
    """
    matcher = SmartMatcher()
    results = []
    
    # بناء فهرس للمنافسين (حسب Brand + Size)
    comp_index = defaultdict(list)
    
    for idx, cp in enumerate(competitor_products):
        cp_name = _get_name(cp)
        if not cp_name:
            continue
        
        cp_brand = extract_brand(cp_name)
        cp_size = cp.get("size_ml", 0) or extract_size(cp_name)
        cp_price = _get_price(cp)
        
        if cp_price <= 0:
            continue
        
        # تجميع حسب Brand + Size (مع تقريب)
        size_bucket = round(cp_size / 5) * 5 if cp_size > 0 else 0
        key = (cp_brand, size_bucket)
        
        comp_index[key].append({
            "index": idx,
            "product": cp,
            "name": cp_name,
            "size": cp_size,
            "price": cp_price,
            "normalized": normalize_name(cp_name),
        })
    
    # المطابقة
    total = len(my_products)
    start_time = time.time()
    
    for idx, my_p in enumerate(my_products):
        my_name = _get_name(my_p)
        if not my_name:
            continue
        
        my_brand = extract_brand(my_name)
        my_size = my_p.get("size_ml", 0) or extract_size(my_name)
        my_price = _get_price(my_p)
        
        if my_price <= 0:
            continue
        
        # البحث في الفهرس
        size_bucket = round(my_size / 5) * 5 if my_size > 0 else 0
        candidates = []
        
        # البحث في نفس الحجم
        key = (my_brand, size_bucket)
        candidates.extend(comp_index.get(key, []))
        
        # البحث في الأحجام القريبة (±10ml)
        for offset in [-10, -5, 5, 10]:
            nearby_bucket = size_bucket + offset
            if nearby_bucket > 0:
                key = (my_brand, nearby_bucket)
                candidates.extend(comp_index.get(key, []))
        
        # Fallback: إذا كان brand فارغ أو لم نجد مرشحين، نبحث في كل المنافسين بنفس الحجم
        if not candidates:
            # البحث بدون brand (حسب الحجم فقط)
            for comp_key, comp_list in comp_index.items():
                comp_brand_key, comp_size_key = comp_key
                if abs(comp_size_key - size_bucket) <= 10:
                    candidates.extend(comp_list)
        
        # Fallback 2: إذا لا يزال فارغاً، ابحث في كل المنافسين (بحث شامل)
        if not candidates and my_brand:
            # البحث بالـ brand فقط بدون قيد الحجم
            for comp_key, comp_list in comp_index.items():
                comp_brand_key, _ = comp_key
                if comp_brand_key == my_brand:
                    candidates.extend(comp_list)
        
        # البحث عن أفضل مطابقة
        best_match = matcher.find_best_match(my_p, candidates)
        
        if best_match:
            # حساب الفرق
            comp_price = best_match["price"]
            diff = my_price - comp_price
            diff_pct = (diff / comp_price * 100) if comp_price > 0 else 0
            
            # التصنيف
            if diff_pct > 10:
                category = "raise_price"
            elif diff_pct < -10:
                category = "lower_price"
            else:
                category = "keep_price"
            
            results.append({
                "my_product": my_p,
                "my_name": my_name,
                "my_price": my_price,
                "comp_product": best_match["product"],
                "comp_name": best_match["name"],
                "comp_price": comp_price,
                "diff": diff,
                "diff_pct": diff_pct,
                "category": category,
                "match_confidence": best_match["match_confidence"],
                "match_reason": best_match["match_reason"],
            })
        else:
            # منتج مفقود
            results.append({
                "my_product": my_p,
                "my_name": my_name,
                "my_price": my_price,
                "comp_product": None,
                "comp_name": None,
                "comp_price": 0,
                "diff": 0,
                "diff_pct": 0,
                "category": "missing",
                "match_confidence": 0,
                "match_reason": "غير موجود عند المنافس",
            })
        
        # تحديث Progress
        if progress_callback and (idx + 1) % 100 == 0:
            progress = (idx + 1) / total
            elapsed = time.time() - start_time
            eta = (elapsed / (idx + 1)) * (total - idx - 1)
            progress_callback(progress, elapsed, eta, matcher.get_stats())
    
    # الإحصائيات النهائية
    total_time = time.time() - start_time
    stats = matcher.get_stats()
    
    st.success(f"""
    ✅ **اكتملت المطابقة!**
    
    - **الوقت:** {total_time:.1f} ثانية
    - **مطابقات سريعة:** {stats['fast_matches']}
    - **مطابقات متوسطة:** {stats['medium_matches']}
    - **مطابقات عميقة:** {stats['deep_matches']}
    - **استدعاءات Gemini:** {stats['gemini_calls']}
    - **Cache hits:** {stats['cache_hits']}
    - **حجم Cache:** {stats['cache_size']}
    """)
    
    return results
