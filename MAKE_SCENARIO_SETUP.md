# 🔄 Make.com Scenario - دليل الإعداد الكامل

## 📋 نظرة عامة

هذا الدليل يشرح كيفية إنشاء **Make.com Scenario** متكامل يربط **استديو مهووس الذكي** بجميع منصات التواصل الاجتماعي.

---

## 🎯 تدفق البيانات

```
استديو مهووس الذكي
        ↓
   Webhook (استقبال)
        ↓
   Router (توزيع)
        ↓
   ┌─────────────────────────────────────────────┐
   ↓          ↓          ↓          ↓          ↓
Instagram  Facebook  Twitter  Telegram  TikTok
   ↓          ↓          ↓          ↓          ↓
LinkedIn  Pinterest  (منصات أخرى)
```

---

## 🔧 الخطوة 1: إنشاء Scenario جديد في Make.com

### 1.1 تسجيل الدخول
1. اذهب إلى https://www.make.com
2. سجّل دخول أو أنشئ حساب جديد
3. اضغط **"Create a new scenario"**

### 1.2 إضافة Webhook (استقبال البيانات)
1. اضغط **"+ Add a module"**
2. ابحث عن **"Webhooks"**
3. اختر **"Custom Webhook"**
4. اضغط **"Create a webhook"**
5. سمّها: `Mahwous Studio Webhook`
6. انسخ الـ **Webhook URL** - ستحتاجها لاحقاً

**مثال على الـ Webhook URL:**
```
https://hook.us1.make.com/123456789abcdefghijklmnop
```

### 1.3 اختبار الـ Webhook
1. اضغط **"Determine the data structure"**
2. انسخ الـ JSON التالي وأرسله عبر `curl` أو Postman:

```bash
curl -X POST "https://hook.us1.make.com/YOUR_WEBHOOK_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "عطر ديور سوفاج",
    "brand": "Dior",
    "type": "Eau de Parfum",
    "size": "100ml",
    "images": {
      "story": "https://example.com/story.jpg",
      "post": "https://example.com/post.jpg",
      "twitter": "https://example.com/twitter.jpg"
    },
    "video": "https://example.com/video.mp4",
    "captions": {
      "instagram": {
        "caption": "✨ عطر ديور سوفاج...",
        "hashtags": ["#عطور", "#ديور"]
      },
      "twitter": {
        "caption": "عطر ديور سوفاج 🔥"
      },
      "facebook": {
        "caption": "اكتشف عطر ديور سوفاج..."
      },
      "telegram": {
        "caption": "عطر ديور سوفاج الفاخر..."
      },
      "tiktok": {
        "caption": "عطر جديد 🎵"
      }
    }
  }'
```

---

## 📱 الخطوة 2: ربط منصات التواصل

### 2.1 Instagram (Post + Story)

#### أ. إضافة Module Instagram
1. اضغط **"+ Add a module"** بعد الـ Webhook
2. ابحث عن **"Instagram"**
3. اختر **"Create a media object"**
4. اضغط **"Add"** → **"Create a connection"**

#### ب. ربط حسابك
1. اختر **"Instagram Business Account"**
2. اضغط **"Authorize"**
3. سجّل دخول بحسابك على Instagram
4. وافق على الصلاحيات

#### ج. إعدادات الـ Post
```
Module: Instagram → Create a media object
Fields:
- Account ID: [اختر حسابك]
- Media Type: IMAGE
- Image URL: {{1.images.post}}
- Caption: {{1.captions.instagram.caption}}
- Alt Text: {{1.product_name}}
```

#### د. إضافة Story
1. أضف module جديد: **Instagram → Create a story**
```
Module: Instagram → Create a story
Fields:
- Account ID: [اختر حسابك]
- Media URL: {{1.images.story}}
- Media Type: IMAGE
```

---

### 2.2 Facebook (Page Post)

#### أ. إضافة Module Facebook
1. اضغط **"+ Add a module"**
2. ابحث عن **"Facebook"**
3. اختر **"Create a post"**
4. اضغط **"Add"** → **"Create a connection"**

#### ب. ربط صفحتك
1. اختر **"Facebook Page"**
2. اضغط **"Authorize"**
3. سجّل دخول بحسابك على Facebook
4. اختر الصفحة المطلوبة

#### ج. إعدادات الـ Post
```
Module: Facebook → Create a post
Fields:
- Page ID: [اختر صفحتك]
- Message: {{1.captions.facebook.caption}}
- Image URL: {{1.images.post}}
- Link: [رابط المتجر]
```

---

### 2.3 Twitter/X (Tweet)

#### أ. إضافة Module Twitter
1. اضغط **"+ Add a module"**
2. ابحث عن **"Twitter"**
3. اختر **"Post a tweet"**
4. اضغط **"Add"** → **"Create a connection"**

#### ب. ربط حسابك
1. اختر **"Twitter API v2"**
2. اضغط **"Authorize"**
3. سجّل دخول بحسابك على Twitter
4. وافق على الصلاحيات

#### ج. إعدادات الـ Tweet
```
Module: Twitter → Post a tweet
Fields:
- Text: {{1.captions.twitter.caption}}
- Media: {{1.images.twitter}}
```

---

### 2.4 Telegram (Channel Message)

#### أ. إضافة Module Telegram
1. اضغط **"+ Add a module"**
2. ابحث عن **"Telegram"**
3. اختر **"Send a message"**
4. اضغط **"Add"** → **"Create a connection"**

#### ب. إنشاء Telegram Bot
1. افتح Telegram وابحث عن `@BotFather`
2. أرسل `/newbot`
3. اتبع التعليمات
4. انسخ **Bot Token**

#### ج. ربط الـ Bot
1. في Make.com، اختر **"Telegram Bot"**
2. الصق **Bot Token**
3. اضغط **"Save"**

#### د. إعدادات الرسالة
```
Module: Telegram → Send a message
Fields:
- Chat ID: @your_channel_username
- Text: {{1.captions.telegram.caption}}
- Image URL: {{1.images.post}}
- Parse Mode: HTML
```

---

### 2.5 TikTok (Upload Video)

#### أ. إضافة Module TikTok
1. اضغط **"+ Add a module"**
2. ابحث عن **"TikTok"**
3. اختر **"Upload a video"**
4. اضغط **"Add"** → **"Create a connection"**

#### ب. ربط حسابك
1. اختر **"TikTok Business Account"**
2. اضغط **"Authorize"**
3. سجّل دخول بحسابك على TikTok
4. وافق على الصلاحيات

#### ج. إعدادات الفيديو
```
Module: TikTok → Upload a video
Fields:
- Account ID: [اختر حسابك]
- Video URL: {{1.video}}
- Caption: {{1.captions.tiktok.caption}}
- Hashtags: {{join(1.captions.tiktok.hashtags; " ")}}
- Visibility: PUBLIC
```

---

### 2.6 LinkedIn (Post)

#### أ. إضافة Module LinkedIn
1. اضغط **"+ Add a module"**
2. ابحث عن **"LinkedIn"**
3. اختر **"Create a post"**
4. اضغط **"Add"** → **"Create a connection"**

#### ب. ربط حسابك
1. اختر **"LinkedIn Page"**
2. اضغط **"Authorize"**
3. سجّل دخول بحسابك على LinkedIn
4. اختر الصفحة المطلوبة

#### ج. إعدادات الـ Post
```
Module: LinkedIn → Create a post
Fields:
- Account Type: ORGANIZATION
- Organization ID: [اختر صفحتك]
- Text: {{1.captions.linkedin.caption}}
- Image URL: {{1.images.post}}
```

---

### 2.7 Pinterest (Create a Pin)

#### أ. إضافة Module Pinterest
1. اضغط **"+ Add a module"**
2. ابحث عن **"Pinterest"**
3. اختر **"Create a pin"**
4. اضغط **"Add"** → **"Create a connection"**

#### ب. ربط حسابك
1. اختر **"Pinterest Business Account"**
2. اضغط **"Authorize"**
3. سجّل دخول بحسابك على Pinterest
4. وافق على الصلاحيات

#### ج. إعدادات الـ Pin
```
Module: Pinterest → Create a pin
Fields:
- Board ID: [اختر لوحة]
- Image URL: {{1.images.post}}
- Description: {{1.captions.pinterest.caption}}
- Link: [رابط المتجر]
- Alt Text: {{1.product_name}}
```

---

## 🔄 الخطوة 3: إضافة Router (توزيع اختياري)

إذا كنت تريد تشغيل بعض المنصات فقط في بعض الحالات:

### 3.1 إضافة Router
1. اضغط **"+ Add a module"** بعد الـ Webhook
2. ابحث عن **"Router"**
3. اختر **"Router"**

### 3.2 إضافة شروط
```
Route 1: Instagram فقط
Condition: {{1.captions.instagram}} exists

Route 2: جميع المنصات
Condition: Always

Route 3: بدون TikTok
Condition: {{1.captions.tiktok}} does not exist
```

---

## 🧪 الخطوة 4: اختبار الـ Scenario

### 4.1 تفعيل الـ Scenario
1. اضغط **"Turn on"** في الزاوية العلوية اليسرى
2. ستظهر رسالة: "Scenario is now active"

### 4.2 إرسال بيانات اختبار
من التطبيق (استديو مهووس):
1. ارفع صورة عطر
2. اختر المخرجات
3. فعّل **"نشر تلقائي عبر Make.com"**
4. اضغط **"ابدأ التوليد"**

### 4.3 مراقبة التنفيذ
1. في Make.com، اضغط **"Execution history"**
2. ستجد سجل جميع المحاولات
3. تحقق من الأخطاء (إن وجدت)

---

## 📊 مثال على JSON الكامل

```json
{
  "product_name": "عطر ديور سوفاج",
  "brand": "Dior",
  "type": "Eau de Parfum",
  "size": "100ml",
  "style": "فاخر",
  "gender": "رجالي",
  "images": {
    "story": "https://cdn.manus.im/mahwous_dior_sauvage_story.jpg",
    "post": "https://cdn.manus.im/mahwous_dior_sauvage_post.jpg",
    "twitter": "https://cdn.manus.im/mahwous_dior_sauvage_twitter.jpg"
  },
  "video": "https://cdn.manus.im/mahwous_dior_sauvage_video.mp4",
  "captions": {
    "instagram": {
      "caption": "✨ عطر ديور سوفاج الفاخر - رائحة الرجولة والأناقة 💎\n\nاكتشف العطر الذي يعكس شخصيتك الفريدة. بنوتات عطرية عميقة مع لمسات من الفلفل والأمبروكسان.\n\n🏪 متوفر الآن في متجرنا\n📦 توصيل سريع\n💳 دفع آمن\n\nاطلبه الآن من البايو 🔗",
      "hashtags": ["#عطور", "#ديور", "#عطور_رجالية", "#سوفاج", "#عطور_فاخرة", "#مهووس"],
      "character_count": 1250
    },
    "twitter": {
      "caption": "عطر ديور سوفاج الجديد 🔥 رائحة الرجولة والأناقة 💎 متوفر الآن في متجرنا #عطور #Dior",
      "character_count": 95
    },
    "facebook": {
      "caption": "اكتشف عطر ديور سوفاج الفاخر - رائحة الرجولة والأناقة. بنوتات عطرية عميقة مع لمسات من الفلفل والأمبروكسان. متوفر الآن في متجرنا بأفضل الأسعار!",
      "hashtags": ["#عطور", "#ديور", "#سوفاج"]
    },
    "telegram": {
      "caption": "✨ **عطر ديور سوفاج الفاخر** ✨\n\n🏷️ **النوع:** Eau de Parfum\n📏 **الحجم:** 100 مل\n👨 **الجنس:** رجالي\n💎 **الطابع:** فاخر\n\n**الوصف:**\nعطر ديور سوفاج يعكس شخصيتك الفريدة. بنوتات عطرية عميقة مع لمسات من الفلفل والأمبروكسان.\n\n🛒 **اطلب الآن:**\nرابط المتجر\n\n#عطور #ديور #سوفاج #عطور_رجالية",
      "hashtags": ["#عطور", "#ديور", "#سوفاج", "#عطور_رجالية"]
    },
    "tiktok": {
      "caption": "عطر ديور سوفاج الجديد 🔥 رائحة الرجولة والأناقة 💎 #عطور #ديور #سوفاج #عطور_رجالية #fyp #viral",
      "hashtags": ["#عطور", "#ديور", "#سوفاج", "#fyp", "#viral"]
    },
    "linkedin": {
      "caption": "نفخر بتقديم عطر ديور سوفاج الفاخر - رائحة الرجولة والأناقة. اكتشف مجموعتنا الحصرية من العطور الفاخرة."
    },
    "pinterest": {
      "caption": "عطر ديور سوفاج الفاخر - رائحة الرجولة والأناقة 💎"
    }
  },
  "descriptions": {
    "short": "عطر ديور سوفاج الفاخر برائحة الرجولة والأناقة. بنوتات عطرية عميقة مع لمسات من الفلفل والأمبروكسان.",
    "medium": "اكتشف عطر ديور سوفاج الفاخر - رائحة الرجولة والأناقة التي تعكس شخصيتك الفريدة. بنوتات عطرية عميقة مع لمسات من الفلفل والأمبروكسان. متوفر الآن في متجرنا بأفضل الأسعار.",
    "long": "عطر ديور سوفاج الفاخر يعكس شخصيتك الفريدة مع رائحة الرجولة والأناقة. يتميز بنوتات عطرية عميقة مع لمسات من الفلفل والأمبروكسان التي تضيف عمقاً وسحراً. مثالي للرجل الحديث الذي يقدر الجودة والفخامة. متوفر الآن في متجرنا بأفضل الأسعار مع توصيل سريع وآمن.",
    "ad": "عطر ديور سوفاج الفاخر - رائحة الرجولة والأناقة 💎 متوفر الآن بأفضل الأسعار!",
    "seo": {
      "title": "عطر ديور سوفاج او دو برفيوم 100مل | مهووس للعطور",
      "meta_description": "اشتري عطر ديور سوفاج الفاخر برائحة الرجولة والأناقة. توصيل سريع وآمن. أفضل الأسعار.",
      "content": "محتوى SEO محسّن...",
      "tags": ["عطور رجالية", "ديور", "سوفاج", "عطور فاخرة", "عطور برفيوم"]
    }
  },
  "hashtags": {
    "arabic": ["#عطور", "#ديور", "#سوفاج", "#عطور_رجالية", "#عطور_فاخرة", "#مهووس", "#عطور_برفيوم", "#رجالي", "#فاخر", "#أناقة", "#رائحة", "#جودة", "#متجر_عطور", "#عطور_أصلية", "#توصيل_سريع"],
    "english": ["#perfumes", "#Dior", "#Sauvage", "#MensPerfume", "#LuxuryFragrance", "#Mahwous", "#Parfum", "#Fragrance", "#Cologne", "#MensStyle", "#Elegance", "#Quality", "#PerfumeShop", "#OriginalPerfumes", "#FastDelivery"]
  },
  "timestamp": "2026-02-13 18:30:00"
}
```

---

## ⚙️ الإعدادات المتقدمة

### تأخير التنفيذ
إذا كنت تريد تأخير النشر (مثلاً نشر الـ Instagram بعد 5 دقائق):

```
Module: Sleep
Duration: 5 minutes
```

### شروط مخصصة
إذا كنت تريد نشر Instagram فقط إذا كان عدد الهاشتاقات أكثر من 20:

```
Module: Instagram → Create a media object
Condition: {{length(1.captions.instagram.hashtags)}} > 20
```

### معالجة الأخطاء
إذا فشل النشر على منصة ما:

```
Module: Error Handler
Action: Continue scenario
```

---

## 🔐 الأمان والخصوصية

### نصائح مهمة:
1. ✅ **لا تشارك Webhook URL** مع أحد
2. ✅ **استخدم HTTPS** فقط
3. ✅ **قيّد الوصول** إلى Scenario
4. ✅ **راجع الـ Logs** بانتظام
5. ✅ **استخدم VPN** إذا لزم الأمر

---

## 📞 استكشاف الأخطاء

### المشكلة: "Webhook URL غير صحيح"
**الحل:** تأكد من نسخ الـ URL كاملاً بدون مسافات

### المشكلة: "فشل الاتصال بـ Instagram"
**الحل:** تحقق من صلاحيات الحساب والـ Token

### المشكلة: "الرسالة لم تُرسل إلى Telegram"
**الحل:** تأكد من أن الـ Bot موجود في القناة وله صلاحيات الإرسال

### المشكلة: "فشل رفع الفيديو على TikTok"
**الحل:** تحقق من أن الحساب Business Account وليس شخصي

---

## 🎉 الخلاصة

بعد إكمال هذا الدليل، ستكون لديك:

✅ Webhook متصل بـ استديو مهووس  
✅ Instagram متصل (Post + Story)  
✅ Facebook متصل  
✅ Twitter متصل  
✅ Telegram متصل  
✅ TikTok متصل  
✅ LinkedIn متصل  
✅ Pinterest متصل  

**كل هذا بضغطة زر واحدة!** 🚀

---

## 📝 ملاحظات إضافية

- **التحديثات:** Make.com يحدّث ميزاته باستمرار، قد تختلف بعض الخطوات
- **الدعم:** اتصل بـ Make.com Support إذا واجهت مشاكل
- **التكاليف:** Make.com له خطة مجانية وخطط مدفوعة
- **الحدود:** بعض المنصات لها حدود على عدد الرسائل/اليوم

---

**آخر تحديث:** 2026-02-13  
**الإصدار:** v1.0  
**الحالة:** جاهز للاستخدام ✅
