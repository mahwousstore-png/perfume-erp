# 🔗 إعداد Webhook في Streamlit Cloud

## ✅ Webhook URL الخاص بك:

```
https://hook.eu2.make.com/28v9yfukz2u1yotgsemg8j32jhwegag2
```

---

## 📝 خطوات الإضافة:

### 1️⃣ افتح Streamlit Cloud
1. اذهب إلى: https://share.streamlit.io/
2. ابحث عن تطبيق `perfume-erp`
3. اضغط على **"..."** → **"Settings"**

### 2️⃣ أضف Webhook في Secrets
1. اذهب إلى tab **"Secrets"**
2. أضف هذا السطر في نهاية الملف:

```toml
WEBHOOK_PUBLISH_CONTENT = "https://hook.eu2.make.com/28v9yfukz2u1yotgsemg8j32jhwegag2"
```

3. اضغط **"Save"**

### 3️⃣ أعد تشغيل التطبيق
1. اضغط **"Reboot app"**
2. انتظر حتى يكتمل التشغيل

---

## ✅ اختبار الاتصال

### في استديو مهووس:
1. ارفع صورة عطر
2. فعّل **"نشر تلقائي عبر Make.com"**
3. اضغط **"ابدأ التوليد"**

### في Make.com:
1. اذهب إلى **"Execution history"**
2. ستجد سجل المحاولة
3. تحقق من البيانات المستلمة

---

## 📊 البيانات المُرسلة

عند الضغط على "نشر تلقائي"، سيتم إرسال:

```json
{
  "product_name": "عطر ديور سوفاج",
  "brand": "Dior",
  "type": "EDT",
  "size": "100ml",
  "images": {
    "story": "https://cdn.example.com/story.jpg",
    "post": "https://cdn.example.com/post.jpg",
    "twitter": "https://cdn.example.com/twitter.jpg"
  },
  "video": "https://cdn.example.com/video.mp4",
  "captions": {
    "instagram": {
      "caption": "نص Instagram...",
      "hashtags": ["#عطور", "#مهووس", ...]
    },
    "facebook": {
      "caption": "نص Facebook...",
      "hashtags": [...]
    },
    "twitter": {
      "caption": "نص Twitter..."
    },
    "telegram": {
      "caption": "نص Telegram..."
    },
    "tiktok": {
      "caption": "نص TikTok..."
    },
    "linkedin": {
      "caption": "نص LinkedIn..."
    },
    "pinterest": {
      "caption": "نص Pinterest..."
    }
  },
  "descriptions": {
    "short": "وصف قصير...",
    "medium": "وصف متوسط...",
    "long": "وصف طويل...",
    "ad": "وصف إعلاني...",
    "seo": "وصف محسّن لـ SEO..."
  },
  "hashtags": {
    "arabic": ["#عطور", "#مهووس", ...],
    "english": ["#perfume", "#fragrance", ...]
  }
}
```

---

## 🎯 الخطوة التالية

بعد إضافة الـ Webhook، اتبع **MAKE_MANUAL_SETUP_GUIDE.md** لإعداد المنصات في Make.com:

1. ✅ **Telegram** (3 دقائق)
2. ✅ **Discord** (1 دقيقة)
3. ✅ **Instagram** (15 دقيقة)
4. ✅ **Facebook** (10 دقائق)
5. ✅ **Twitter** (10 دقيقة)

---

## 🔐 ملاحظات الأمان

⚠️ **لا تشارك Webhook URL مع أحد!**

- هذا الـ URL يسمح بإرسال بيانات مباشرة إلى Make.com
- إذا تم تسريبه، يمكن لأي شخص إرسال بيانات وهمية
- احتفظ به في مكان آمن

---

## 📞 استكشاف الأخطاء

### المشكلة: "Webhook URL not set"
**الحل:**
- تأكد من إضافة `WEBHOOK_PUBLISH_CONTENT` في Secrets
- تأكد من عدم وجود مسافات إضافية
- أعد تشغيل التطبيق

### المشكلة: "Failed to send data"
**الحل:**
- تحقق من أن Webhook URL صحيح
- تحقق من أن Scenario مفعّل في Make.com
- تحقق من Execution History في Make.com

---

**آخر تحديث:** 2026-02-13  
**الحالة:** جاهز للاستخدام ✅
