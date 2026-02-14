"""
smart_error_detector.py - نظام كشف الأخطاء الذكي
═══════════════════════════════════════════════════════════
نظام ذكي يستخدم Gemini API لاكتشاف الأخطاء في المطابقة:
1. مطابقات خاطئة (منتجات مختلفة تماماً)
2. مطابقات مفقودة (منتجات متطابقة لم تُكتشف)
3. فروقات أسعار غير منطقية
4. أخطاء في استخراج البيانات

المميزات:
- استخدام Gemini 2.0 Flash للتحليل السريع
- تقارير تفصيلية عن الأخطاء
- اقتراحات لتحسين الدقة
- دعم المعالجة الدفعية
"""

import os
from typing import List, Dict, Any, Optional
from google import genai
from google.genai import types

# تهيئة Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
client = None

if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)


class SmartErrorDetector:
    """نظام كشف الأخطاء الذكي."""
    
    def __init__(self, api_key: Optional[str] = None):
        """تهيئة النظام."""
        self.api_key = api_key or GEMINI_API_KEY
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None
        self.model = "gemini-2.0-flash-exp"
    
    def detect_matching_errors(self, matches: List[Dict[str, Any]], 
                               threshold: float = 0.7) -> Dict[str, Any]:
        """
        كشف الأخطاء في المطابقات.
        
        Args:
            matches: قائمة المطابقات
            threshold: حد الثقة (0-1)
        
        Returns:
            تقرير الأخطاء
        """
        if not self.client:
            return {
                "error": "Gemini API غير متاح",
                "suspicious_matches": [],
                "price_anomalies": [],
                "missing_data": []
            }
        
        # تحليل المطابقات
        suspicious_matches = []
        price_anomalies = []
        missing_data = []
        
        for match in matches[:100]:  # تحليل أول 100 مطابقة
            # فحص المطابقات المشبوهة
            if match.get("similarity", 1.0) < threshold:
                suspicious_matches.append({
                    "my_product": match.get("my_product", ""),
                    "competitor_product": match.get("competitor_product", ""),
                    "similarity": match.get("similarity", 0),
                    "reason": "تشابه منخفض"
                })
            
            # فحص فروقات الأسعار الغريبة
            my_price = match.get("my_price", 0)
            comp_price = match.get("competitor_price", 0)
            
            if my_price > 0 and comp_price > 0:
                price_diff_pct = abs(my_price - comp_price) / comp_price * 100
                
                if price_diff_pct > 50:  # فرق أكثر من 50%
                    price_anomalies.append({
                        "my_product": match.get("my_product", ""),
                        "my_price": my_price,
                        "competitor_price": comp_price,
                        "difference_pct": round(price_diff_pct, 2),
                        "reason": "فرق سعر كبير جداً"
                    })
            
            # فحص البيانات المفقودة
            if not match.get("my_product") or not match.get("competitor_product"):
                missing_data.append({
                    "match": match,
                    "reason": "بيانات ناقصة"
                })
        
        return {
            "total_matches": len(matches),
            "analyzed_matches": min(100, len(matches)),
            "suspicious_matches": suspicious_matches,
            "price_anomalies": price_anomalies,
            "missing_data": missing_data,
            "error_rate": round(len(suspicious_matches) / min(100, len(matches)) * 100, 2) if matches else 0
        }
    
    def verify_match_with_ai(self, product1: str, product2: str) -> Dict[str, Any]:
        """
        التحقق من المطابقة باستخدام Gemini AI.
        
        Args:
            product1: اسم المنتج الأول
            product2: اسم المنتج الثاني
        
        Returns:
            نتيجة التحقق
        """
        if not self.client:
            return {
                "is_match": False,
                "confidence": 0.0,
                "reason": "Gemini API غير متاح"
            }
        
        prompt = f"""أنت خبير في مطابقة منتجات العطور. قارن بين هذين المنتجين:

المنتج 1: {product1}
المنتج 2: {product2}

هل هما نفس المنتج؟ أجب بصيغة JSON فقط:
{{
    "is_match": true/false,
    "confidence": 0.0-1.0,
    "reason": "السبب بالعربية",
    "extracted_info": {{
        "brand": "الماركة",
        "size": "الحجم",
        "concentration": "التركيز",
        "gender": "النوع"
    }}
}}"""
        
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    response_mime_type="application/json"
                )
            )
            
            import json
            result = json.loads(response.text)
            return result
            
        except Exception as e:
            return {
                "is_match": False,
                "confidence": 0.0,
                "reason": f"خطأ في التحليل: {str(e)}"
            }
    
    def analyze_batch(self, matches: List[Dict[str, Any]], 
                     sample_size: int = 50) -> Dict[str, Any]:
        """
        تحليل دفعة من المطابقات باستخدام AI.
        
        Args:
            matches: قائمة المطابقات
            sample_size: عدد العينات للتحليل
        
        Returns:
            تقرير التحليل
        """
        if not self.client:
            return {
                "error": "Gemini API غير متاح",
                "verified_matches": []
            }
        
        # اختيار عينة عشوائية
        import random
        sample = random.sample(matches, min(sample_size, len(matches)))
        
        verified_matches = []
        correct_matches = 0
        
        for match in sample:
            product1 = match.get("my_product", "")
            product2 = match.get("competitor_product", "")
            
            verification = self.verify_match_with_ai(product1, product2)
            
            verified_matches.append({
                "my_product": product1,
                "competitor_product": product2,
                "original_similarity": match.get("similarity", 0),
                "ai_verification": verification
            })
            
            if verification.get("is_match"):
                correct_matches += 1
        
        accuracy = round(correct_matches / len(sample) * 100, 2) if sample else 0
        
        return {
            "total_matches": len(matches),
            "sample_size": len(sample),
            "verified_matches": verified_matches,
            "accuracy": accuracy,
            "correct_matches": correct_matches,
            "incorrect_matches": len(sample) - correct_matches
        }
    
    def generate_error_report(self, matches: List[Dict[str, Any]]) -> str:
        """
        إنشاء تقرير شامل عن الأخطاء.
        
        Args:
            matches: قائمة المطابقات
        
        Returns:
            تقرير نصي
        """
        errors = self.detect_matching_errors(matches)
        
        report = f"""
# 📊 تقرير كشف الأخطاء الذكي

## 📈 الإحصائيات العامة
- إجمالي المطابقات: {errors['total_matches']}
- المطابقات المحللة: {errors['analyzed_matches']}
- معدل الأخطاء: {errors['error_rate']}%

## ⚠️ المطابقات المشبوهة ({len(errors['suspicious_matches'])})
"""
        
        for i, match in enumerate(errors['suspicious_matches'][:10], 1):
            report += f"\n{i}. **{match['my_product']}** ↔ **{match['competitor_product']}**\n"
            report += f"   - التشابه: {match['similarity']:.2f}\n"
            report += f"   - السبب: {match['reason']}\n"
        
        report += f"\n## 💰 فروقات الأسعار الغريبة ({len(errors['price_anomalies'])})\n"
        
        for i, anomaly in enumerate(errors['price_anomalies'][:10], 1):
            report += f"\n{i}. **{anomaly['my_product']}**\n"
            report += f"   - سعرنا: {anomaly['my_price']:.2f} ريال\n"
            report += f"   - سعر المنافس: {anomaly['competitor_price']:.2f} ريال\n"
            report += f"   - الفرق: {anomaly['difference_pct']:.2f}%\n"
        
        report += f"\n## 📝 البيانات المفقودة ({len(errors['missing_data'])})\n"
        
        return report


# دوال مساعدة للاستخدام السريع

def detect_errors(matches: List[Dict[str, Any]], 
                 api_key: Optional[str] = None) -> Dict[str, Any]:
    """كشف الأخطاء في المطابقات."""
    detector = SmartErrorDetector(api_key)
    return detector.detect_matching_errors(matches)


def verify_match(product1: str, product2: str, 
                api_key: Optional[str] = None) -> Dict[str, Any]:
    """التحقق من مطابقة منتجين."""
    detector = SmartErrorDetector(api_key)
    return detector.verify_match_with_ai(product1, product2)


def analyze_matches(matches: List[Dict[str, Any]], 
                   sample_size: int = 50,
                   api_key: Optional[str] = None) -> Dict[str, Any]:
    """تحليل دفعة من المطابقات."""
    detector = SmartErrorDetector(api_key)
    return detector.analyze_batch(matches, sample_size)
