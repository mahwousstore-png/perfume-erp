import os
import json
from typing import Optional

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


def is_configured() -> bool:
    """التحقق من تكوين Gemini API"""
    api_key = os.getenv('GEMINI_API_KEY', '').strip()
    return bool(api_key) and GEMINI_AVAILABLE


def configure_gemini():
    """تكوين Gemini API"""
    if not GEMINI_AVAILABLE:
        return False
    api_key = os.getenv('GEMINI_API_KEY', '').strip()
    if not api_key:
        return False
    genai.configure(api_key=api_key)
    return True


def generate_product_description(product_name: str,
                                 brand: str,
                                 category: str,
                                 size_ml: int) -> Optional[str]:
    """إنشاء وصف منتج بـ Gemini"""
    if not is_configured():
        return None

    prompt = (
        f"أنشئ وصفاً قصيراً واحترافياً لعطر:\n"
        f"الاسم: {product_name}\n"
        f"الماركة: {brand}\n"
        f"الفئة: {category}\n"
        f"الحجم: {size_ml} مل\n"
        f"الوصف يجب أن يكون:\n"
        f"- قصير (50-100 كلمة)\n"
        f"- احترافي وجذاب\n"
        f"- يركز على المميزات\n"
        f"- باللغة العربية\n"
    )

    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        return response.text if response else None
    except Exception as e:
        print(f"خطأ في Gemini: {e}")
        return None


def generate_social_post(product_name: str,
                         brand: str,
                         sell_price: float,
                         platform: str = "instagram") -> Optional[str]:
    """إنشاء منشور سوشيال ميديا"""
    if not is_configured():
        return None

    prompt = (
        f"أنشئ منشور {platform} جذاب وقصير لعطر:\n"
        f"الاسم: {product_name}\n"
        f"الماركة: {brand}\n"
        f"السعر: {sell_price} ريال\n"
        f"المنشور يجب أن يكون:\n"
        f"- قصير وجذاب\n"
        f"- يشجع على الشراء\n"
        f"- يحتوي على emoji مناسبة\n"
        f"- باللغة العربية\n"
    )

    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        return response.text if response else None
    except Exception as e:
        print(f"خطأ في Gemini: {e}")
        return None


def generate_pricing_recommendation(product_name: str,
                                    my_price: float,
                                    competitor_price: float,
                                    profit_margin: float) -> Optional[str]:
    """توصية ذكية لتسعير المنتج"""
    if not is_configured():
        return None

    price_diff = my_price - competitor_price
    percentage_diff = (price_diff / competitor_price * 100) if competitor_price > 0 else 0

    prompt = (
        f"أعطِ توصية ذكية لتسعير عطر:\n"
        f"اسم المنتج: {product_name}\n"
        f"سعري: {my_price} ريال\n"
        f"سعر المنافس: {competitor_price} ريال\n"
        f"الفرق: {price_diff:.2f} ريال ({percentage_diff:.1f}%)\n"
        f"هامش الربح: {profit_margin:.1f}%\n"
        f"التوصية يجب أن تكون:\n"
        f"- قصيرة ومباشرة\n"
        f"- عملية وقابلة للتنفيذ\n"
        f"- تأخذ في الاعتبار الربح والمنافسة\n"
        f"- باللغة العربية\n"
    )

    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        return response.text if response else None
    except Exception as e:
        print(f"خطأ في Gemini: {e}")
        return None


def analyze_competitor_strategy(competitor_name: str,
                                avg_price: float,
                                product_count: int,
                                price_range: tuple) -> Optional[str]:
    """تحليل استراتيجية المنافس"""
    if not is_configured():
        return None

    prompt = (
        f"حلّل استراتيجية تسعير المنافس:\n"
        f"اسم المنافس: {competitor_name}\n"
        f"عدد المنتجات: {product_count}\n"
        f"متوسط السعر: {avg_price:.2f} ريال\n"
        f"نطاق الأسعار: {price_range[0]:.2f} - {price_range[1]:.2f} ريال\n"
        f"التحليل يجب أن يشمل:\n"
        f"- استراتيجية التسعير\n"
        f"- نقاط القوة والضعف\n"
        f"- التوصيات للمنافسة\n"
        f"- باللغة العربية\n"
    )

    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        return response.text if response else None
    except Exception as e:
        print(f"خطأ في Gemini: {e}")
        return None


def batch_generate_descriptions(products: list) -> list:
    """إنشاء أوصاف لعدة منتجات"""
    results = []
    for product in products:
        desc = generate_product_description(
            product.get('name'),
            product.get('brand'),
            product.get('category'),
            product.get('size_ml')
        )
        results.append({
            'product_id': product.get('id'),
            'description': desc
        })
    return results
