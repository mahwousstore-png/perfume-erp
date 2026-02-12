# 🔒 إعداد المفاتيح السرية (Secrets Setup)

## 📋 **نظرة عامة:**

هذا التطبيق يستخدم **Streamlit Secrets** لتخزين المفاتيح السرية بشكل آمن.

---

## 🏠 **للتطوير المحلي (Local Development):**

### **1. إنشاء ملف Secrets:**

```bash
mkdir -p .streamlit
nano .streamlit/secrets.toml
```

### **2. إضافة المفاتيح:**

```toml
# Gemini API Key
GEMINI_API_KEY = "your-gemini-key-here"

# OpenRouter API Key
OPENROUTER_API_KEY = "your-openrouter-key-here"

# Make.com Webhooks (اختياري)
WEBHOOK_UPDATE_PRICES = "https://hook.eu2.make.com/..."
WEBHOOK_NEW_PRODUCTS = "https://hook.eu2.make.com/..."

# Google Drive (اختياري)
GOOGLE_DRIVE_FOLDER_ID = "your-folder-id"

# Supabase (اختياري)
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-supabase-key"
```

### **3. تشغيل التطبيق:**

```bash
streamlit run app.py
```

---

## ☁️ **للنشر على Streamlit Cloud:**

### **1. افتح إعدادات التطبيق:**
- اذهب إلى: https://share.streamlit.io/
- افتح تطبيقك
- اضغط على **⚙️ Settings**

### **2. أضف Secrets:**
- اضغط على **Secrets**
- الصق المحتوى:

```toml
GEMINI_API_KEY = "your-gemini-key-here"
OPENROUTER_API_KEY = "your-openrouter-key-here"
```

### **3. احفظ:**
- اضغط **Save**
- التطبيق سيعيد التشغيل تلقائياً

---

## 🔑 **الحصول على المفاتيح:**

### **Gemini API Key:**
1. اذهب إلى: https://aistudio.google.com/app/apikey
2. اضغط **Create API Key**
3. انسخ المفتاح

### **OpenRouter API Key:**
1. اذهب إلى: https://openrouter.ai/keys
2. سجّل دخول
3. أنشئ مفتاح جديد

---

## ⚠️ **تحذيرات أمنية:**

### **❌ لا تفعل:**
- لا ترفع `.streamlit/secrets.toml` إلى Git
- لا ترسل المفاتيح في الرسائل
- لا تضع المفاتيح في الكود مباشرة
- لا تشارك المفاتيح علناً

### **✅ افعل:**
- استخدم Streamlit Secrets دائماً
- احفظ المفاتيح في مكان آمن
- غيّر المفاتيح إذا تم كشفها
- استخدم `.gitignore` لحماية `secrets.toml`

---

## 🔧 **استكشاف الأخطاء:**

### **المشكلة: "GEMINI_API_KEY not found"**
**الحل:**
1. تأكد من وجود ملف `.streamlit/secrets.toml`
2. تأكد من وجود `GEMINI_API_KEY` في الملف
3. أعد تشغيل التطبيق

### **المشكلة: "Your API key was reported as leaked"**
**الحل:**
1. احذف المفتاح القديم من Google
2. أنشئ مفتاح جديد
3. حدّث `secrets.toml`
4. أعد تشغيل التطبيق

### **المشكلة: "Rate limit exceeded"**
**الحل:**
1. انتظر 60 ثانية
2. التطبيق سيعيد المحاولة تلقائياً
3. أو استخدم OpenRouter كبديل

---

## 📚 **موارد إضافية:**

- [Streamlit Secrets Documentation](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)
- [Gemini API Documentation](https://ai.google.dev/gemini-api/docs)
- [OpenRouter Documentation](https://openrouter.ai/docs)

---

## ✅ **التحقق من الإعداد:**

بعد إضافة المفاتيح:

1. افتح التطبيق
2. اذهب إلى **الإعدادات** في القائمة الجانبية
3. اضغط **🔄 اختبار Gemini**
4. يجب أن يظهر: ✅ متصل! النموذج: gemini-2.0-flash

---

**إذا واجهت أي مشاكل، راجع قسم استكشاف الأخطاء أعلاه! 🔧**
