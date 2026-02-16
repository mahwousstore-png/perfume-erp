# نظام التسعير الذكي للعطور - Streamlit Sharing

## 🚀 نشر التطبيق على Streamlit Sharing

### الخطوات:

1. **رفع الكود إلى GitHub:**
   - تأكد من رفع جميع الملفات إلى repository على GitHub
   - الملف الرئيسي: `app.py`

2. **إعداد Streamlit Sharing:**
   - اذهب إلى [share.streamlit.io](https://share.streamlit.io)
   - سجل الدخول بحساب GitHub
   - اختر الـ repository الخاص بك
   - حدد الفرع الرئيسي (main)

3. **إعداد Secrets (مفاتيح API):**
   - في لوحة تحكم Streamlit Sharing، اذهب إلى "Secrets"
   - أضف المفاتيح التالية:
     ```
     GEMINI_API_KEY = "your_gemini_api_key_here"
     OPENROUTER_API_KEY = "your_openrouter_api_key_here"  # اختياري
     ```

4. **تشغيل التطبيق:**
   - اضغط "Deploy"
   - انتظر حتى يتم بناء التطبيق
   - ستحصل على رابط عام للتطبيق

## 🔑 الحصول على مفاتيح API

### Gemini API:
- اذهب إلى [Google AI Studio](https://ai.google.dev/)
- أنشئ مشروع جديد
- اذهب إلى API Keys
- أنشئ مفتاح جديد
- انسخ المفتاح وضعه في Secrets

### OpenRouter API (اختياري):
- اذهب إلى [OpenRouter](https://openrouter.ai/)
- سجل حساب جديد
- اذهب إلى API Keys
- أنشئ مفتاح جديد
- انسخ المفتاح وضعه في Secrets

## 📋 المتطلبات

- Python 3.9+
- جميع المكتبات في `requirements.txt`
- مفاتيح API صحيحة في Secrets

## 🐛 استكشاف الأخطاء

إذا واجهت مشاكل:
1. تحقق من أن جميع الملفات مرفوعة
2. تأكد من صحة مفاتيح API
3. تحقق من logs البناء في Streamlit Sharing
4. تأكد من أن `requirements.txt` محدث

## 📞 الدعم

للمساعدة، يرجى فتح issue في الـ repository.