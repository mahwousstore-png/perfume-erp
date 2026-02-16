# 🔧 دليل الإعداد اليدوي - Make.com Scenario

## 🎯 نظرة عامة

هذا الدليل يشرح كيفية إنشاء Scenario **يدوياً** في Make.com خطوة بخطوة.

**لماذا يدوياً؟**
- ✅ أضمن للعمل 100%
- ✅ لا توجد أخطاء "Module Not Found"
- ✅ تتحكم في كل التفاصيل
- ✅ سهل الفهم والتعديل

---

## 🚀 الخطوة 1: إنشاء Scenario جديد

1. افتح https://www.make.com
2. اضغط **"Create a new scenario"**
3. سمّه: `Mahwous Studio - Auto Publish`

---

## 📥 الخطوة 2: إضافة Webhook

### 2.1 إضافة Module
1. اضغط **"+ Add a module"**
2. ابحث عن **"Webhooks"**
3. اختر **"Custom webhook"**

### 2.2 إنشاء Webhook
1. اضغط **"Create a webhook"**
2. سمّه: `Mahwous Studio Webhook`
3. اضغط **"Save"**
4. **انسخ الـ URL** - ستحتاجه لاحقاً

### 2.3 تحديد هيكل البيانات
1. اضغط **"Determine the data structure"**
2. افتح Terminal وأرسل هذا الأمر:

```bash
curl -X POST "YOUR_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "عطر ديور سوفاج",
    "images": {
      "post": "https://example.com/post.jpg",
      "story": "https://example.com/story.jpg"
    },
    "video": "https://example.com/video.mp4",
    "captions": {
      "instagram": {"caption": "نص Instagram"},
      "facebook": {"caption": "نص Facebook"},
      "twitter": {"caption": "نص Twitter"},
      "telegram": {"caption": "نص Telegram"}
    }
  }'
```

3. اضغط **"OK"** في Make.com

---

## 🔀 الخطوة 3: إضافة Router

1. اضغط **"+ Add a module"** بعد الـ Webhook
2. ابحث عن **"Flow control"**
3. اختر **"Router"**

الآن لديك Router جاهز لتوزيع المحتوى على المنصات!

---

## 📱 الخطوة 4: إضافة المنصات

### 4.1 Telegram (الأسهل - نبدأ به)

#### أ. إنشاء Bot
1. افتح Telegram وابحث عن `@BotFather`
2. أرسل `/newbot`
3. اتبع التعليمات
4. انسخ **Bot Token**

#### ب. إضافة Module في Make.com
1. اضغط **"+ Add a module"** على أحد مسارات الـ Router
2. ابحث عن **"Telegram Bot"**
3. اختر **"Send a Photo"**

#### ج. إعداد الاتصال
1. اضغط **"Add"** بجانب Connection
2. سمّه: `Mahwous Telegram Bot`
3. الصق **Bot Token**
4. اضغط **"Save"**

#### د. إعداد الرسالة
```
Chat ID: @mahwous_channel (أو رقم القناة)
Photo: {{1.images.post}}
Caption: {{1.captions.telegram.caption}}
Parse Mode: HTML
```

#### هـ. إضافة Bot إلى القناة
1. افتح قناتك في Telegram
2. اذهب إلى **Settings** → **Administrators**
3. اضغط **"Add Administrator"**
4. ابحث عن اسم الـ Bot وأضفه
5. امنحه صلاحية **"Post Messages"**

---

### 4.2 Instagram

#### أ. الحصول على Access Token
1. اذهب إلى https://developers.facebook.com
2. أنشئ App جديد → **"Business"**
3. أضف **"Instagram Graph API"**
4. اذهب إلى **Tools** → **Graph API Explorer**
5. اختر صفحتك
6. اختر Permissions:
   - `instagram_basic`
   - `instagram_content_publish`
   - `pages_read_engagement`
7. اضغط **"Generate Access Token"**
8. **انسخ الـ Token**

#### ب. الحصول على Instagram Business Account ID
1. في Graph API Explorer، أرسل:
```
GET /me/accounts
```
2. انسخ `id` للصفحة
3. أرسل:
```
GET /{page_id}?fields=instagram_business_account
```
4. انسخ `instagram_business_account.id`

#### ج. إضافة Module في Make.com
1. اضغط **"+ Add a module"** على مسار جديد من الـ Router
2. ابحث عن **"HTTP"**
3. اختر **"Make a request"**

#### د. إعداد الطلب
```
URL: https://graph.facebook.com/v18.0/{{YOUR_IG_ACCOUNT_ID}}/media
Method: POST
Query String:
  - access_token: {{YOUR_ACCESS_TOKEN}}
  - image_url: {{1.images.post}}
  - caption: {{1.captions.instagram.caption}}
Parse response: Yes
```

---

### 4.3 Facebook

#### أ. الحصول على Page Access Token
1. في Graph API Explorer (نفس الخطوات السابقة)
2. اختر صفحتك
3. اختر Permissions:
   - `pages_manage_posts`
   - `pages_read_engagement`
4. اضغط **"Generate Access Token"**
5. **انسخ الـ Token**

#### ب. إضافة Module
1. اضغط **"+ Add a module"** على مسار جديد
2. ابحث عن **"HTTP"**
3. اختر **"Make a request"**

#### ج. إعداد الطلب
```
URL: https://graph.facebook.com/v18.0/{{YOUR_PAGE_ID}}/photos
Method: POST
Query String:
  - access_token: {{YOUR_PAGE_ACCESS_TOKEN}}
  - url: {{1.images.post}}
  - caption: {{1.captions.facebook.caption}}
Parse response: Yes
```

---

### 4.4 Twitter/X

#### أ. الحصول على API Keys
1. اذهب إلى https://developer.twitter.com
2. أنشئ App جديد
3. اذهب إلى **Keys and tokens**
4. انسخ:
   - API Key
   - API Secret Key
   - Bearer Token

#### ب. إضافة Module
1. اضغط **"+ Add a module"** على مسار جديد
2. ابحث عن **"HTTP"**
3. اختر **"Make a request"**

#### ج. إعداد الطلب
```
URL: https://api.twitter.com/2/tweets
Method: POST
Headers:
  - Authorization: Bearer {{YOUR_BEARER_TOKEN}}
  - Content-Type: application/json
Body Type: Raw
Body: {"text": "{{1.captions.twitter.caption}}"}
Parse response: Yes
```

---

### 4.5 Discord

#### أ. إنشاء Webhook
1. افتح Discord Server
2. اذهب إلى **Server Settings** → **Integrations**
3. اضغط **"Create Webhook"**
4. سمّه: `Mahwous Studio`
5. اختر القناة
6. **انسخ الـ Webhook URL**

#### ب. إضافة Module
1. اضغط **"+ Add a module"** على مسار جديد
2. ابحث عن **"HTTP"**
3. اختر **"Make a request"**

#### ج. إعداد الطلب
```
URL: {{YOUR_DISCORD_WEBHOOK_URL}}
Method: POST
Headers:
  - Content-Type: application/json
Body Type: Raw
Body:
{
  "content": "{{1.captions.instagram.caption}}",
  "embeds": [{
    "title": "{{1.product_name}}",
    "description": "{{1.descriptions.short}}",
    "image": {"url": "{{1.images.post}}"},
    "color": 3447003
  }]
}
Parse response: Yes
```

---

## ✅ الخطوة 5: اختبار الـ Scenario

### 5.1 تفعيل الـ Scenario
1. اضغط **"Turn on"** في الزاوية العلوية اليسرى
2. ستظهر رسالة: "Scenario is now active"

### 5.2 إضافة Webhook URL في Streamlit
1. افتح مشروعك على Streamlit Cloud
2. اذهب إلى **Settings** → **Secrets**
3. أضف:
```toml
WEBHOOK_PUBLISH_CONTENT = "YOUR_WEBHOOK_URL"
```
4. اضغط **"Save"**
5. أعد تشغيل التطبيق (Reboot)

### 5.3 إرسال بيانات اختبار
1. افتح استديو مهووس
2. ارفع صورة عطر
3. فعّل "نشر تلقائي عبر Make.com"
4. اضغط "ابدأ التوليد"

### 5.4 مراقبة التنفيذ
1. في Make.com، اضغط **"Execution history"**
2. ستجد سجل المحاولة الأخيرة
3. تحقق من الأخطاء (إن وجدت)

---

## 📊 ملخص المنصات

| المنصة | الطريقة | الصعوبة |
|--------|---------|---------|
| Telegram | Telegram Bot API | ⭐ سهل جداً |
| Discord | Discord Webhook | ⭐ سهل جداً |
| Instagram | Facebook Graph API | ⭐⭐ متوسط |
| Facebook | Facebook Graph API | ⭐⭐ متوسط |
| Twitter | Twitter API v2 | ⭐⭐ متوسط |
| TikTok | TikTok API | ⭐⭐⭐ صعب |
| LinkedIn | LinkedIn API | ⭐⭐⭐ صعب |
| Pinterest | Pinterest API | ⭐⭐ متوسط |

---

## 🔧 نصائح مهمة

### ✅ **أفضل الممارسات:**
1. ابدأ بـ Telegram و Discord (الأسهل)
2. اختبر كل منصة على حدة
3. احفظ جميع الـ Tokens في مكان آمن
4. استخدم Postman لاختبار الـ APIs قبل إضافتها في Make.com

### ⚠️ **تجنب هذه الأخطاء:**
1. لا تنسخ الـ Tokens بمسافات إضافية
2. تأكد من صلاحيات الـ Tokens
3. تأكد من أن الحسابات Business Accounts (Instagram, TikTok)
4. لا تشارك الـ Tokens مع أحد

### 🔐 **الأمان:**
1. استخدم Environment Variables للـ Tokens
2. لا تكتب الـ Tokens مباشرة في الكود
3. قم بتجديد الـ Tokens بانتظام
4. راقب الـ Logs بانتظام

---

## 📞 استكشاف الأخطاء

### المشكلة: "Invalid access token"
**الحل:**
- تحقق من أن الـ Token صحيح
- تحقق من صلاحيات الـ Token
- جدّد الـ Token

### المشكلة: "Chat not found" (Telegram)
**الحل:**
- تأكد من أن الـ Bot موجود في القناة
- تأكد من أن `chat_id` صحيح (يبدأ بـ @)
- تأكد من أن الـ Bot له صلاحيات الإرسال

### المشكلة: "Webhook URL not found" (Discord)
**الحل:**
- تأكد من نسخ الـ URL كاملاً
- تأكد من أن الـ Webhook لم يُحذف
- أعد إنشاء الـ Webhook

---

## 🎉 الخلاصة

بعد إكمال هذا الدليل، ستكون لديك:

✅ Scenario كامل جاهز للعمل  
✅ Telegram متصل  
✅ Discord متصل  
✅ Instagram متصل (اختياري)  
✅ Facebook متصل (اختياري)  
✅ Twitter متصل (اختياري)  

**كل هذا بدون أخطاء "Module Not Found"!** 🚀

---

**آخر تحديث:** 2026-02-13  
**الإصدار:** v1.0 (Manual Setup)  
**الحالة:** جاهز للاستخدام ✅
