"""
استديو مهووس الذكي v9.0
═══════════════════════════════
نظام متكامل لتوليد المحتوى التسويقي للعطور
"""

import streamlit as st
import requests
import json
import base64
import time
from io import BytesIO
from PIL import Image
import os

# ══════════════════════════════════════════════════════════════
# إعدادات API
# ══════════════════════════════════════════════════════════════

try:
    GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")
    LUMA_API_KEY = st.secrets.get("LUMA_API_KEY", "mahwous_oybcg")
except:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    LUMA_API_KEY = "mahwous_oybcg"

# ══════════════════════════════════════════════════════════════
# دوال Gemini Vision
# ══════════════════════════════════════════════════════════════

def analyze_perfume_image(image_bytes):
    """تحليل صورة العطر باستخدام Gemini Vision"""
    try:
        # تحويل الصورة إلى base64
        image_b64 = base64.b64encode(image_bytes).decode('utf-8')
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
        
        payload = {
            "contents": [{
                "parts": [
                    {
                        "text": """حلل هذه الصورة للعطر واستخرج المعلومات التالية بدقة:

1. اسم العطر (إن كان مقروءاً)
2. العلامة التجارية
3. نوع العطر (Eau de Parfum, Eau de Toilette, إلخ)
4. الحجم (مل)
5. الألوان السائدة في الزجاجة
6. شكل الزجاجة (مربع، دائري، مستطيل، إلخ)
7. الطابع العام (فاخر، رياضي، كلاسيكي، عصري، إلخ)
8. الجنس المستهدف (رجالي، نسائي، للجنسين)

أعد النتيجة بصيغة JSON فقط بدون أي نص إضافي:
{
  "name": "",
  "brand": "",
  "type": "",
  "size": "",
  "colors": [],
  "bottle_shape": "",
  "style": "",
  "gender": ""
}"""
                    },
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": image_b64
                        }
                    }
                ]
            }],
            "generationConfig": {
                "temperature": 0.4,
                "topP": 0.95,
                "topK": 40,
                "maxOutputTokens": 1024,
            }
        }
        
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            text = result["candidates"][0]["content"]["parts"][0]["text"]
            
            # استخراج JSON من النص
            text = text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()
            
            analysis = json.loads(text)
            return {"success": True, "analysis": analysis}
        else:
            return {"success": False, "error": f"خطأ في API: {response.status_code}"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

# ══════════════════════════════════════════════════════════════
# دوال Gemini Imagen
# ══════════════════════════════════════════════════════════════

def generate_product_images(analysis, original_image_bytes):
    """توليد 3 صور احترافية بأحجام مختلفة"""
    
    # استخراج المعلومات
    product_name = analysis.get("name", "عطر فاخر")
    brand = analysis.get("brand", "")
    colors = ", ".join(analysis.get("colors", ["ذهبي", "أسود"]))
    style = analysis.get("style", "فاخر")
    bottle_shape = analysis.get("bottle_shape", "أنيق")
    
    # قوالب الصور الثلاثة
    templates = {
        "story": {
            "size": "1080x1920",
            "prompt": f"""صورة احترافية لعطر {product_name} من {brand}، تصوير استديو فاخر:

- الزجاجة: {bottle_shape}، ألوان {colors}
- الخلفية: خلفية {style} مع إضاءة ناعمة وظلال جمالية
- الإضاءة: إضاءة استديو احترافية مع انعكاسات طبيعية
- التكوين: الزجاجة في المنتصف، تأخذ 70% من الإطار
- الأسلوب: تصوير منتجات فاخر، واقعي 100%، بدون تعديلات مبالغ فيها
- الدقة: عالية الجودة، تفاصيل واضحة

IMPORTANT: The perfume bottle must look 100% real and photorealistic, no artistic stylization."""
        },
        "post": {
            "size": "1080x1080",
            "prompt": f"""صورة مربعة احترافية لعطر {product_name}:

- الزجاجة: {bottle_shape}، ألوان {colors}
- المشهد: تصوير من الأعلى (flat lay) مع عناصر ديكور فاخرة
- العناصر: أوراق ذهبية، قماش حريري، أحجار كريمة
- الإضاءة: طبيعية ناعمة من الجانب
- الأسلوب: تصوير منتجات فاخر، واقعي 100%
- التكوين: متوازن، الزجاجة في المركز

IMPORTANT: 100% photorealistic product photography, no AI artifacts."""
        },
        "twitter": {
            "size": "1200x675",
            "prompt": f"""صورة أفقية احترافية لعطر {product_name}:

- الزجاجة: {bottle_shape}، ألوان {colors}
- المشهد: خلفية {style} مع عمق مجال ضحل
- الإضاءة: دراماتيكية مع تباين عالي
- التكوين: الزجاجة على الجانب الأيسر، مساحة للنص على اليمين
- الأسلوب: تصوير إعلاني احترافي، واقعي 100%
- التفاصيل: انعكاسات طبيعية، ظلال ناعمة

IMPORTANT: Real product photography style, no artistic effects."""
        }
    }
    
    results = {}
    
    for size_name, template in templates.items():
        try:
            # استخدام Gemini Imagen 3
            url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-001:predict?key={GEMINI_API_KEY}"
            
            payload = {
                "instances": [{
                    "prompt": template["prompt"]
                }],
                "parameters": {
                    "sampleCount": 1,
                    "aspectRatio": template["size"].replace("x", ":"),
                    "safetyFilterLevel": "block_few",
                    "personGeneration": "allow_adult"
                }
            }
            
            response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                # استخراج الصورة من النتيجة
                image_data = result["predictions"][0]["bytesBase64Encoded"]
                image_bytes = base64.b64decode(image_data)
                results[size_name] = {
                    "success": True,
                    "image_bytes": image_bytes,
                    "size": template["size"]
                }
            else:
                results[size_name] = {
                    "success": False,
                    "error": f"فشل التوليد: {response.status_code}"
                }
                
        except Exception as e:
            results[size_name] = {
                "success": False,
                "error": str(e)
            }
        
        # انتظار قصير بين الطلبات
        time.sleep(2)
    
    return results

# ══════════════════════════════════════════════════════════════
# دوال Luma AI
# ══════════════════════════════════════════════════════════════

def generate_video_luma(analysis, image_bytes):
    """توليد فيديو قصير باستخدام Luma AI Dream Machine"""
    
    try:
        # رفع الصورة أولاً
        upload_url = "https://api.lumalabs.ai/dream-machine/v1/generations/image"
        
        files = {
            'image': ('perfume.jpg', image_bytes, 'image/jpeg')
        }
        
        headers = {
            'Authorization': f'Bearer {LUMA_API_KEY}'
        }
        
        # رفع الصورة
        upload_response = requests.post(upload_url, files=files, headers=headers, timeout=30)
        
        if upload_response.status_code != 200:
            return {"success": False, "error": f"فشل رفع الصورة: {upload_response.status_code}"}
        
        image_id = upload_response.json()["id"]
        
        # إنشاء الفيديو
        product_name = analysis.get("name", "عطر فاخر")
        brand = analysis.get("brand", "")
        
        video_prompt = f"""Professional product video for {product_name} perfume:

- Slow 360° rotation of the perfume bottle
- Smooth camera movement, cinematic lighting
- Elegant and luxurious atmosphere
- Soft reflections and shadows
- Duration: 5 seconds
- Style: High-end product photography

IMPORTANT: The perfume bottle must maintain 100% realistic appearance throughout the video."""
        
        generation_url = "https://api.lumalabs.ai/dream-machine/v1/generations"
        
        payload = {
            "image_url": image_id,
            "prompt": video_prompt,
            "aspect_ratio": "16:9",
            "loop": False
        }
        
        gen_response = requests.post(generation_url, json=payload, headers=headers, timeout=30)
        
        if gen_response.status_code != 200:
            return {"success": False, "error": f"فشل إنشاء الفيديو: {gen_response.status_code}"}
        
        generation_id = gen_response.json()["id"]
        
        # انتظار اكتمال التوليد (polling)
        max_attempts = 60  # 5 دقائق كحد أقصى
        for attempt in range(max_attempts):
            status_url = f"https://api.lumalabs.ai/dream-machine/v1/generations/{generation_id}"
            status_response = requests.get(status_url, headers=headers, timeout=15)
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                state = status_data.get("state")
                
                if state == "completed":
                    video_url = status_data.get("video", {}).get("url")
                    if video_url:
                        # تحميل الفيديو
                        video_response = requests.get(video_url, timeout=60)
                        if video_response.status_code == 200:
                            return {
                                "success": True,
                                "video_bytes": video_response.content,
                                "video_url": video_url
                            }
                    return {"success": False, "error": "لم يتم العثور على رابط الفيديو"}
                
                elif state == "failed":
                    return {"success": False, "error": "فشل توليد الفيديو"}
                
            time.sleep(5)  # انتظار 5 ثواني قبل المحاولة التالية
        
        return {"success": False, "error": "انتهت مهلة التوليد (5 دقائق)"}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

# ══════════════════════════════════════════════════════════════
# دوال توليد المحتوى النصي
# ══════════════════════════════════════════════════════════════

def generate_descriptions(analysis):
    """توليد 5 نسخ من الوصف بأطوال مختلفة"""
    
    product_name = analysis.get("name", "عطر فاخر")
    brand = analysis.get("brand", "")
    perfume_type = analysis.get("type", "Eau de Parfum")
    size = analysis.get("size", "100ml")
    style = analysis.get("style", "فاخر")
    gender = analysis.get("gender", "للجنسين")
    
    prompt = f"""أنشئ 5 نسخ مختلفة من وصف المنتج التالي:

المنتج: {product_name}
العلامة: {brand}
النوع: {perfume_type}
الحجم: {size}
الطابع: {style}
الفئة: {gender}

النسخ المطلوبة:

1. **وصف قصير (Story)** - 50-80 كلمة
   - جذاب ومباشر
   - مناسب لقصص Instagram/Snapchat
   - يركز على الشعور والتجربة

2. **وصف متوسط (Post)** - 100-150 كلمة
   - تفصيلي أكثر
   - يذكر المكونات الرئيسية
   - يصف المناسبات المناسبة
   - مناسب للمنشورات العادية

3. **وصف طويل (مقال)** - 200-300 كلمة
   - شامل ومفصل
   - يتحدث عن قصة العطر
   - يذكر المكونات بالتفصيل
   - يصف الرحلة العطرية (المقدمة، القلب، القاعدة)
   - مناسب لصفحة المنتج

4. **وصف إعلاني** - 30-50 كلمة
   - قوي وجذاب
   - يحفز على الشراء
   - يتضمن دعوة واضحة للعمل (CTA)
   - مناسب للإعلانات المدفوعة

5. **وصف SEO** - 150-200 كلمة
   - محسّن لمحركات البحث
   - يتضمن كلمات مفتاحية طبيعية
   - يتضمن عنوان SEO (60 حرف)
   - يتضمن وصف ميتا (160 حرف)
   - يتضمن 10 وسوم (tags)

قواعد مهمة:
- استخدم اللغة العربية الفصحى الجميلة
- كن احترافياً وواقعياً (لا مبالغة)
- اتبع معايير SEO وGoogle
- استخدم الإيموجي بذكاء
- اجعل كل نسخة فريدة تماماً

أعد النتيجة بصيغة JSON:
{{
  "short": "...",
  "medium": "...",
  "long": "...",
  "ad": "...",
  "seo": {{
    "title": "...",
    "meta_description": "...",
    "content": "...",
    "tags": ["...", "..."]
  }}
}}"""
    
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.8,
                "topP": 0.95,
                "topK": 40,
                "maxOutputTokens": 4096,
            }
        }
        
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            text = result["candidates"][0]["content"]["parts"][0]["text"]
            
            # استخراج JSON
            text = text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()
            
            descriptions = json.loads(text)
            return {"success": True, "descriptions": descriptions}
        else:
            return {"success": False, "error": f"خطأ في API: {response.status_code}"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

def generate_platform_captions(analysis):
    """توليد Captions مخصصة لكل منصة (Instagram, Twitter, Snapchat, WhatsApp, Telegram, TikTok, Facebook)"""
    
    product_name = analysis.get("name", "عطر فاخر")
    brand = analysis.get("brand", "")
    perfume_type = analysis.get("type", "Eau de Parfum")
    size = analysis.get("size", "100ml")
    style = analysis.get("style", "فاخر")
    gender = analysis.get("gender", "للجنسين")
    
    prompt = f"""أنشئ Captions مخصصة لكل منصة للمنتج التالي:

المنتج: {product_name}
العلامة: {brand}
النوع: {perfume_type}
الحجم: {size}
الطابع: {style}
الفئة: {gender}

أنشئ 7 Captions مختلفة حسب معايير كل منصة:

**1. Instagram Caption:**
- الطول: 125-150 كلمة
- السطر الأول: جذاب جداً (يظهر قبل "...المزيد")
- الهاشتاقات: 20-30 هاشتاق في النهاية (عربي + إنجليزي)
- الإيموجي: كثير ✨💎🌟
- CTA: "اطلبه الآن من البايو 🔗" أو "تواصل معنا للطلب 📲"
- الأسلوب: بصري، قصصي، جذاب

**2. Twitter/X Caption:**
- الطول: 250-280 حرف فقط
- 2-3 هاشتاقات مدمجة في النص
- CTA: "اطلب الآن 👇"
- الأسلوب: مباشر، سريع، مختصر

**3. Snapchat Caption:**
- الطول: 50-80 حرف
- 1-2 هاشتاق
- إيموجي بسيط
- الأسلوب: عفوي، شبابي
- مثال: "عطر ديور الجديد 🔥 #عطور #مهووس"

**4. WhatsApp Status Caption:**
- الطول: 100-150 كلمة
- بدون هاشتاقات
- CTA: "تواصل معنا للطلب 📲" + رقم الواتساب
- الأسلوب: شخصي، ودود، مباشر

**5. Telegram Post Caption:**
- الطول: 300-500 كلمة
- 5-10 هاشتاقات
- تنسيق Markdown: **bold** و *italic*
- CTA: "اطلب الآن من القناة"
- الأسلوب: تفصيلي، احترافي

**6. TikTok Caption:**
- الطول: 100-150 حرف
- 3-5 هاشتاقات ترندينج (#fyp #viral #عطور)
- إيموجي كثير
- CTA: "شوف الرابط في البايو 👆"
- الأسلوب: ترندي، جذاب، شبابي

**7. Facebook Caption:**
- الطول: 200-300 كلمة
- 3-5 هاشتاقات
- CTA: "اطلب الآن من المتجر"
- الأسلوب: قصصي، عاطفي، تفصيلي

قواعد مهمة:
- استخدم اللغة العربية الفصحى الجميلة
- كن احترافياً وواقعياً (لا مبالغة)
- اجعل كل Caption فريد تماماً
- التزم بالطول المحدد لكل منصة
- استخدم الإيموجي بذكاء حسب المنصة

أعد النتيجة بصيغة JSON:
{{
  "instagram": {{
    "caption": "...",
    "hashtags": ["#...", "#...", ...],
    "character_count": 0
  }},
  "twitter": {{
    "caption": "...",
    "character_count": 0
  }},
  "snapchat": {{
    "caption": "...",
    "character_count": 0
  }},
  "whatsapp": {{
    "caption": "...",
    "word_count": 0
  }},
  "telegram": {{
    "caption": "...",
    "hashtags": ["#...", "#...", ...],
    "word_count": 0
  }},
  "tiktok": {{
    "caption": "...",
    "hashtags": ["#...", "#...", ...],
    "character_count": 0
  }},
  "facebook": {{
    "caption": "...",
    "hashtags": ["#...", "#...", ...],
    "word_count": 0
  }}
}}"""
    
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.8,
                "topP": 0.95,
                "topK": 40,
                "maxOutputTokens": 8192,
            }
        }
        
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            text = result["candidates"][0]["content"]["parts"][0]["text"]
            
            # استخراج JSON
            text = text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()
            
            captions = json.loads(text)
            return {"success": True, "captions": captions}
        else:
            return {"success": False, "error": f"خطأ في API: {response.status_code}"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

def generate_hashtags(analysis):
    """توليد 30 هاشتاق ذكي (عربي + إنجليزي)"""
    
    product_name = analysis.get("name", "عطر فاخر")
    brand = analysis.get("brand", "")
    style = analysis.get("style", "فاخر")
    gender = analysis.get("gender", "للجنسين")
    
    prompt = f"""أنشئ 30 هاشتاق احترافي للمنتج التالي:

المنتج: {product_name}
العلامة: {brand}
الطابع: {style}
الفئة: {gender}

المتطلبات:
- 15 هاشتاق عربي
- 15 هاشتاق إنجليزي
- مزيج من:
  * هاشتاقات عامة (عطور، perfumes)
  * هاشتاقات خاصة بالعلامة ({brand})
  * هاشتاقات ترندينج
  * هاشتاقات محلية (السعودية، الخليج)
  * هاشتاقات موسمية (إن وجدت)

أعد النتيجة بصيغة JSON:
{{
  "arabic": ["#...", "#...", ...],
  "english": ["#...", "#...", ...]
}}"""
    
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "topP": 0.95,
                "topK": 40,
                "maxOutputTokens": 1024,
            }
        }
        
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            text = result["candidates"][0]["content"]["parts"][0]["text"]
            
            # استخراج JSON
            text = text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()
            
            hashtags = json.loads(text)
            return {"success": True, "hashtags": hashtags}
        else:
            return {"success": False, "error": f"خطأ في API: {response.status_code}"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

# ══════════════════════════════════════════════════════════════
# دوال رفع الملفات والنشر التلقائي
# ══════════════════════════════════════════════════════════════

def upload_to_s3(file_bytes, filename):
    """رفع ملف إلى S3 والحصول على رابط CDN"""
    try:
        # حفظ الملف مؤقتاً
        temp_path = f"/tmp/{filename}"
        with open(temp_path, "wb") as f:
            f.write(file_bytes)
        
        # رفع عبر manus-upload-file
        import subprocess
        result = subprocess.run(
            ["manus-upload-file", temp_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            # استخراج الرابط من المخرجات
            url = result.stdout.strip()
            return {"success": True, "url": url}
        else:
            return {"success": False, "error": result.stderr}
    except Exception as e:
        return {"success": False, "error": str(e)}

def publish_to_platforms(data):
    """نشر المحتوى على جميع المنصات عبر Make.com"""
    
    # Webhook URL من Streamlit Secrets
    try:
        WEBHOOK_PUBLISH = st.secrets.get("WEBHOOK_PUBLISH_CONTENT", "")
    except:
        WEBHOOK_PUBLISH = os.getenv("WEBHOOK_PUBLISH_CONTENT", "")
    
    if not WEBHOOK_PUBLISH:
        return {"success": False, "error": "Webhook URL غير موجود في Secrets"}
    
    try:
        response = requests.post(
            WEBHOOK_PUBLISH,
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            return {"success": True, "message": "تم إرسال المحتوى إلى Make.com بنجاح"}
        else:
            return {"success": False, "error": f"خطأ في الإرسال: {response.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ══════════════════════════════════════════════════════════════
# الواجهة الرئيسية
# ══════════════════════════════════════════════════════════════

def show_studio_page():
    """عرض صفحة استديو مهووس الذكي"""
    
    st.markdown("# 🎬 استديو مهووس الذكي")
    st.markdown("> **نظام متكامل لتوليد المحتوى التسويقي للعطور بالذكاء الصناعي**")
    st.markdown("---")
    
    # التحقق من المفاتيح
    if not GEMINI_API_KEY or GEMINI_API_KEY.strip() == "":
        st.error("❌ **مفتاح Gemini API غير موجود أو فارغ!**")
        st.info("🔑 أضف `GEMINI_API_KEY` في Streamlit Cloud Secrets (الإعدادات > Secrets)")
        st.code(f"القيمة الحالية: '{GEMINI_API_KEY}'", language="text")
        return
    
    if not LUMA_API_KEY:
        st.warning("⚠️ مفتاح Luma AI غير موجود - لن تتمكن من توليد الفيديوهات")
    
    # رفع الصورة
    st.markdown("### 📸 الخطوة 1: ارفع صورة العطر")
    
    uploaded_file = st.file_uploader(
        "اختر صورة واضحة للعطر",
        type=["jpg", "jpeg", "png", "webp"],
        help="ارفع صورة واضحة لزجاجة العطر على خلفية نظيفة"
    )
    
    if uploaded_file is not None:
        # عرض الصورة الأصلية
        image_bytes = uploaded_file.read()
        image = Image.open(BytesIO(image_bytes))
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(image, caption="الصورة الأصلية", use_container_width=True)
        
        with col2:
            st.markdown("### ⚙️ الخطوة 2: اختر المخرجات")
            
            generate_images = st.checkbox("🎨 توليد 3 صور احترافية (Story, Post, Twitter)", value=True)
            generate_video = st.checkbox("🎬 توليد فيديو قصير (Luma AI)", value=True, disabled=not LUMA_API_KEY)
            generate_desc = st.checkbox("✍️ توليد 5 نسخ من الوصف", value=True)
            generate_captions = st.checkbox("📱 توليد Captions لكل منصة (7 منصات)", value=True)
            generate_tags = st.checkbox("#️⃣ توليد 30 هاشتاق", value=True)
            
            st.markdown("---")
            auto_publish = st.checkbox("🚀 نشر تلقائي عبر Make.com", value=False, help="سيتم رفع الصور والفيديو إلى S3 ثم إرسال كل شيء إلى Make.com")
        
        st.markdown("---")
        
        if st.button("🚀 ابدأ التوليد", type="primary", use_container_width=True):
            
            # الخطوة 1: تحليل الصورة
            st.markdown("### 🔍 جاري تحليل الصورة...")
            with st.spinner("⏳ Gemini Vision يحلل الصورة..."):
                analysis_result = analyze_perfume_image(image_bytes)
            
            if not analysis_result["success"]:
                st.error(f"❌ فشل التحليل: {analysis_result['error']}")
                return
            
            analysis = analysis_result["analysis"]
            
            st.success("✅ تم تحليل الصورة بنجاح!")
            
            # عرض نتائج التحليل
            with st.expander("📊 نتائج التحليل", expanded=True):
                col1, col2, col3 = st.columns(3)
                col1.metric("🏷️ اسم العطر", analysis.get("name", "غير محدد"))
                col2.metric("🏢 العلامة", analysis.get("brand", "غير محدد"))
                col3.metric("📏 الحجم", analysis.get("size", "غير محدد"))
                
                col1, col2, col3 = st.columns(3)
                col1.metric("🎨 الطابع", analysis.get("style", "غير محدد"))
                col2.metric("👤 الفئة", analysis.get("gender", "غير محدد"))
                col3.metric("🍾 الشكل", analysis.get("bottle_shape", "غير محدد"))
                
                st.markdown(f"**🎨 الألوان:** {', '.join(analysis.get('colors', []))}")
            
            st.markdown("---")
            
            # الخطوة 2: توليد الصور
            if generate_images:
                st.markdown("### 🎨 جاري توليد الصور الاحترافية...")
                with st.spinner("⏳ Gemini Imagen يولد 3 صور... (قد يستغرق 1-2 دقيقة)"):
                    images_result = generate_product_images(analysis, image_bytes)
                
                st.markdown("#### 📸 الصور المولدة")
                
                cols = st.columns(3)
                for idx, (size_name, result) in enumerate(images_result.items()):
                    with cols[idx]:
                        if result["success"]:
                            img = Image.open(BytesIO(result["image_bytes"]))
                            st.image(img, caption=f"{size_name.upper()} ({result['size']})", use_container_width=True)
                            
                            # زر تحميل
                            st.download_button(
                                label=f"💾 تحميل {size_name.upper()}",
                                data=result["image_bytes"],
                                file_name=f"mahwous_{analysis.get('name', 'perfume')}_{size_name}.jpg",
                                mime="image/jpeg",
                                use_container_width=True
                            )
                        else:
                            st.error(f"❌ {result['error']}")
                
                st.markdown("---")
            
            # الخطوة 3: توليد الفيديو
            if generate_video and LUMA_API_KEY:
                st.markdown("### 🎬 جاري توليد الفيديو...")
                with st.spinner("⏳ Luma AI يولد الفيديو... (قد يستغرق 3-5 دقائق)"):
                    video_result = generate_video_luma(analysis, image_bytes)
                
                if video_result["success"]:
                    st.success("✅ تم توليد الفيديو بنجاح!")
                    
                    st.video(video_result["video_bytes"])
                    
                    st.download_button(
                        label="💾 تحميل الفيديو",
                        data=video_result["video_bytes"],
                        file_name=f"mahwous_{analysis.get('name', 'perfume')}_video.mp4",
                        mime="video/mp4",
                        use_container_width=True
                    )
                else:
                    st.error(f"❌ فشل توليد الفيديو: {video_result['error']}")
                
                st.markdown("---")
            
            # الخطوة 4: توليد الأوصاف
            if generate_desc:
                st.markdown("### ✍️ جاري توليد الأوصاف...")
                with st.spinner("⏳ Gemini يكتب 5 نسخ من الوصف..."):
                    desc_result = generate_descriptions(analysis)
                
                if desc_result["success"]:
                    descriptions = desc_result["descriptions"]
                    
                    st.markdown("#### 📝 الأوصاف المولدة")
                    
                    tabs = st.tabs(["📱 قصير (Story)", "📄 متوسط (Post)", "📚 طويل (مقال)", "📢 إعلاني", "🔍 SEO"])
                    
                    with tabs[0]:
                        st.markdown("**وصف قصير (50-80 كلمة)**")
                        st.markdown(descriptions.get("short", ""))
                        st.code(descriptions.get("short", ""), language=None)
                    
                    with tabs[1]:
                        st.markdown("**وصف متوسط (100-150 كلمة)**")
                        st.markdown(descriptions.get("medium", ""))
                        st.code(descriptions.get("medium", ""), language=None)
                    
                    with tabs[2]:
                        st.markdown("**وصف طويل (200-300 كلمة)**")
                        st.markdown(descriptions.get("long", ""))
                        st.code(descriptions.get("long", ""), language=None)
                    
                    with tabs[3]:
                        st.markdown("**وصف إعلاني (30-50 كلمة)**")
                        st.markdown(descriptions.get("ad", ""))
                        st.code(descriptions.get("ad", ""), language=None)
                    
                    with tabs[4]:
                        seo = descriptions.get("seo", {})
                        st.markdown("**عنوان SEO:**")
                        st.code(seo.get("title", ""), language=None)
                        
                        st.markdown("**وصف ميتا:**")
                        st.code(seo.get("meta_description", ""), language=None)
                        
                        st.markdown("**المحتوى:**")
                        st.markdown(seo.get("content", ""))
                        
                        st.markdown("**الوسوم (Tags):**")
                        st.code(", ".join(seo.get("tags", [])), language=None)
                else:
                    st.error(f"❌ فشل توليد الأوصاف: {desc_result['error']}")
                
                st.markdown("---")
            
            # الخطوة 5: توليد Captions لكل منصة
            platform_captions_data = None
            if generate_captions:
                st.markdown("### 📱 جاري توليد Captions لكل منصة...")
                with st.spinner("⏳ Gemini يولد Captions مخصصة لـ 7 منصات..."):
                    captions_result = generate_platform_captions(analysis)
                
                if captions_result["success"]:
                    platform_captions_data = captions_result["captions"]
                    
                    st.markdown("#### 📱 Captions لكل منصة")
                    
                    tabs = st.tabs(["📸 Instagram", "🐦 Twitter", "👻 Snapchat", "📲 WhatsApp", "✈️ Telegram", "🎵 TikTok", "👍 Facebook"])
                    
                    with tabs[0]:  # Instagram
                        ig = platform_captions_data.get("instagram", {})
                        st.markdown("**Caption:**")
                        st.markdown(ig.get("caption", ""))
                        st.code(ig.get("caption", ""), language=None)
                        
                        st.markdown("**Hashtags:**")
                        hashtags_str = " ".join(ig.get("hashtags", []))
                        st.code(hashtags_str, language=None)
                        
                        st.info(f"📊 عدد الأحرف: {ig.get('character_count', 0)}")
                    
                    with tabs[1]:  # Twitter
                        tw = platform_captions_data.get("twitter", {})
                        st.markdown("**Tweet:**")
                        st.markdown(tw.get("caption", ""))
                        st.code(tw.get("caption", ""), language=None)
                        st.info(f"📊 عدد الأحرف: {tw.get('character_count', 0)}/280")
                    
                    with tabs[2]:  # Snapchat
                        snap = platform_captions_data.get("snapchat", {})
                        st.markdown("**Caption:**")
                        st.markdown(snap.get("caption", ""))
                        st.code(snap.get("caption", ""), language=None)
                        st.info(f"📊 عدد الأحرف: {snap.get('character_count', 0)}")
                    
                    with tabs[3]:  # WhatsApp
                        wa = platform_captions_data.get("whatsapp", {})
                        st.markdown("**Status:**")
                        st.markdown(wa.get("caption", ""))
                        st.code(wa.get("caption", ""), language=None)
                        st.info(f"📊 عدد الكلمات: {wa.get('word_count', 0)}")
                    
                    with tabs[4]:  # Telegram
                        tg = platform_captions_data.get("telegram", {})
                        st.markdown("**Post:**")
                        st.markdown(tg.get("caption", ""))
                        st.code(tg.get("caption", ""), language=None)
                        
                        st.markdown("**Hashtags:**")
                        tg_hashtags = " ".join(tg.get("hashtags", []))
                        st.code(tg_hashtags, language=None)
                        
                        st.info(f"📊 عدد الكلمات: {tg.get('word_count', 0)}")
                    
                    with tabs[5]:  # TikTok
                        tt = platform_captions_data.get("tiktok", {})
                        st.markdown("**Caption:**")
                        st.markdown(tt.get("caption", ""))
                        st.code(tt.get("caption", ""), language=None)
                        
                        st.markdown("**Hashtags:**")
                        tt_hashtags = " ".join(tt.get("hashtags", []))
                        st.code(tt_hashtags, language=None)
                        
                        st.info(f"📊 عدد الأحرف: {tt.get('character_count', 0)}")
                    
                    with tabs[6]:  # Facebook
                        fb = platform_captions_data.get("facebook", {})
                        st.markdown("**Post:**")
                        st.markdown(fb.get("caption", ""))
                        st.code(fb.get("caption", ""), language=None)
                        
                        st.markdown("**Hashtags:**")
                        fb_hashtags = " ".join(fb.get("hashtags", []))
                        st.code(fb_hashtags, language=None)
                        
                        st.info(f"📊 عدد الكلمات: {fb.get('word_count', 0)}")
                else:
                    st.error(f"❌ فشل توليد Captions: {captions_result['error']}")
                
                st.markdown("---")
            
            # الخطوة 6: توليد الهاشتاقات
            if generate_tags:
                st.markdown("### #️⃣ جاري توليد الهاشتاقات...")
                with st.spinner("⏳ Gemini يولد 30 هاشتاق..."):
                    tags_result = generate_hashtags(analysis)
                
                if tags_result["success"]:
                    hashtags = tags_result["hashtags"]
                    
                    st.markdown("#### #️⃣ الهاشتاقات المولدة")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**🇸🇦 عربي (15 هاشتاق)**")
                        arabic_tags = " ".join(hashtags.get("arabic", []))
                        st.markdown(arabic_tags)
                        st.code(arabic_tags, language=None)
                    
                    with col2:
                        st.markdown("**🇬🇧 إنجليزي (15 هاشتاق)**")
                        english_tags = " ".join(hashtags.get("english", []))
                        st.markdown(english_tags)
                        st.code(english_tags, language=None)
                    
                    st.markdown("**🌍 الكل (30 هاشتاق)**")
                    all_tags = arabic_tags + " " + english_tags
                    st.code(all_tags, language=None)
                else:
                    st.error(f"❌ فشل توليد الهاشتاقات: {tags_result['error']}")
            
            st.markdown("---")
            st.success("🎉 **اكتمل التوليد بنجاح!** يمكنك الآن تحميل جميع المخرجات.")
            
            # الخطوة 7: النشر التلقائي
            if auto_publish:
                st.markdown("---")
                st.markdown("### 🚀 جاري النشر التلقائي عبر Make.com...")
                
                with st.spinner("⏳ جاري رفع الصور والفيديو إلى S3..."):
                    # رفع الصور
                    uploaded_images = {}
                    if generate_images and images_result:
                        for size_name, result in images_result.items():
                            if result["success"]:
                                filename = f"mahwous_{analysis.get('name', 'perfume')}_{size_name}.jpg"
                                upload_result = upload_to_s3(result["image_bytes"], filename)
                                if upload_result["success"]:
                                    uploaded_images[size_name] = upload_result["url"]
                                    st.success(f"✅ تم رفع صورة {size_name.upper()}")
                                else:
                                    st.error(f"❌ فشل رفع {size_name}: {upload_result['error']}")
                    
                    # رفع الفيديو
                    video_url = None
                    if generate_video and video_result and video_result.get("success"):
                        filename = f"mahwous_{analysis.get('name', 'perfume')}_video.mp4"
                        upload_result = upload_to_s3(video_result["video_bytes"], filename)
                        if upload_result["success"]:
                            video_url = upload_result["url"]
                            st.success("✅ تم رفع الفيديو")
                        else:
                            st.error(f"❌ فشل رفع الفيديو: {upload_result['error']}")
                
                # إعداد البيانات للإرسال
                publish_data = {
                    "product_name": analysis.get("name", "عطر فاخر"),
                    "brand": analysis.get("brand", ""),
                    "type": analysis.get("type", ""),
                    "size": analysis.get("size", ""),
                    "style": analysis.get("style", ""),
                    "gender": analysis.get("gender", ""),
                    "images": uploaded_images,
                    "video": video_url,
                    "captions": platform_captions_data if generate_captions else {},
                    "descriptions": descriptions if generate_desc else {},
                    "hashtags": hashtags if generate_tags else {},
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                }
                
                # إرسال إلى Make.com
                with st.spinner("⏳ جاري إرسال المحتوى إلى Make.com..."):
                    publish_result = publish_to_platforms(publish_data)
                
                if publish_result["success"]:
                    st.success("✅ **تم إرسال المحتوى إلى Make.com بنجاح!**")
                    st.info("🔄 Make.com سيقوم بنشر المحتوى على جميع المنصات تلقائياً")
                    
                    # عرض ملخص المنصات
                    with st.expander("📊 ملخص النشر", expanded=True):
                        platforms_list = []
                        if platform_captions_data:
                            if "instagram" in platform_captions_data:
                                platforms_list.append("✅ Instagram (Post + Story)")
                            if "facebook" in platform_captions_data:
                                platforms_list.append("✅ Facebook (Page Post)")
                            if "twitter" in platform_captions_data:
                                platforms_list.append("✅ Twitter/X")
                            if "telegram" in platform_captions_data:
                                platforms_list.append("✅ Telegram Channel")
                            if "tiktok" in platform_captions_data:
                                platforms_list.append("✅ TikTok")
                            if "snapchat" in platform_captions_data:
                                platforms_list.append("✅ Snapchat")
                            if "whatsapp" in platform_captions_data:
                                platforms_list.append("✅ WhatsApp Status")
                        
                        for platform in platforms_list:
                            st.markdown(f"- {platform}")
                        
                        st.markdown("---")
                        st.markdown(f"**📸 عدد الصور:** {len(uploaded_images)}")
                        st.markdown(f"**🎬 الفيديو:** {'✅ مرفوع' if video_url else '❌ غير متوفر'}")
                        st.markdown(f"**📱 عدد المنصات:** {len(platforms_list)}")
                else:
                    st.error(f"❌ فشل النشر: {publish_result['error']}")
                    st.info("💡 تأكد من إضافة `WEBHOOK_PUBLISH_CONTENT` في Streamlit Secrets")
    
    else:
        st.info("📤 ارفع صورة العطر للبدء")
        
        # عرض أمثلة
        st.markdown("---")
        st.markdown("### 💡 نصائح للحصول على أفضل نتائج:")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
**✅ افعل:**
- استخدم صورة واضحة وعالية الجودة
- تأكد من ظهور الزجاجة كاملة
- استخدم خلفية نظيفة
- إضاءة جيدة
            """)
        
        with col2:
            st.markdown("""
**❌ لا تفعل:**
- صور مشوشة أو غير واضحة
- زوايا غريبة
- خلفية مزدحمة
- إضاءة سيئة
            """)
