# 📋 دليل استخدام ملف التكوين - جميع المنصات

## 🎯 نظرة عامة

ملف `ALL_PLATFORMS_CONFIG.json` يحتوي على **تكوين كامل** لجميع المنصات مع:

✅ **جميع الإعدادات** جاهزة  
✅ **تعليمات خطوة بخطوة** لكل منصة  
✅ **أولوية الإعداد** (من الأسهل إلى الأصعب)  
✅ **وقت الإعداد** المتوقع  
✅ **أمثلة كاملة** للطلبات  

---

## 🚀 الاستخدام السريع

### الخطوة 1: افتح الملف
```bash
/home/ubuntu/perfume-erp/ALL_PLATFORMS_CONFIG.json
```

### الخطوة 2: ابدأ بالمنصات السهلة

#### 1️⃣ **Telegram** (⭐ الأسهل - 3 دقائق)

**التعليمات:**
1. افتح Telegram → ابحث عن `@BotFather`
2. أرسل `/newbot`
3. اتبع التعليمات
4. انسخ Bot Token
5. في الملف، استبدل:
   ```json
   "bot_token": "YOUR_TELEGRAM_BOT_TOKEN_HERE"
   ```
   بـ:
   ```json
   "bot_token": "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
   ```

**في Make.com:**
1. أضف module **"Telegram Bot"** → **"Send a Photo"**
2. Connection: الصق Bot Token
3. Chat ID: `@mahwous_channel`
4. Photo: `{{1.images.post}}`
5. Caption: `{{1.captions.telegram.caption}}`
6. Parse Mode: `HTML`

**إضافة Bot للقناة:**
1. افتح قناتك
2. Settings → Administrators → Add Administrator
3. ابحث عن Bot وأضفه
4. امنحه صلاحية **"Post Messages"**

---

#### 2️⃣ **Discord** (⭐ الأسهل - 1 دقيقة)

**التعليمات:**
1. افتح Discord Server
2. Server Settings → Integrations → Create Webhook
3. سمّه: `Mahwous Studio`
4. اختر القناة
5. انسخ Webhook URL
6. في الملف، استبدل:
   ```json
   "webhook_url": "YOUR_DISCORD_WEBHOOK_URL_HERE"
   ```
   بـ:
   ```json
   "webhook_url": "https://discord.com/api/webhooks/123456789/abcdefg"
   ```

**في Make.com:**
1. أضف module **"HTTP"** → **"Make a request"**
2. URL: الصق Webhook URL
3. Method: `POST`
4. Headers:
   - Name: `Content-Type`
   - Value: `application/json`
5. Body Type: `Raw`
6. Body:
   ```json
   {
     "content": "{{1.captions.instagram.caption}}",
     "embeds": [{
       "title": "{{1.product_name}}",
       "description": "{{1.descriptions.short}}",
       "image": {"url": "{{1.images.post}}"},
       "color": 3447003
     }]
   }
   ```

---

### الخطوة 3: أضف المنصات المتوسطة (اختياري)

#### 3️⃣ **Facebook** (⭐⭐ متوسط - 10 دقائق)

**التعليمات:**
1. اذهب إلى https://developers.facebook.com
2. في **Graph API Explorer**:
   - اختر صفحتك
   - Permissions: `pages_manage_posts`, `pages_read_engagement`
   - اضغط **"Generate Access Token"**
3. انسخ Token
4. أرسل `GET /me/accounts` للحصول على Page ID
5. في الملف، استبدل:
   ```json
   "page_access_token": "YOUR_FACEBOOK_PAGE_ACCESS_TOKEN_HERE",
   "page_id": "YOUR_FACEBOOK_PAGE_ID_HERE"
   ```

**في Make.com:**
1. أضف module **"HTTP"** → **"Make a request"**
2. URL: `https://graph.facebook.com/v18.0/{PAGE_ID}/photos`
3. Method: `POST`
4. Query String:
   - `access_token`: الصق Token
   - `url`: `{{1.images.post}}`
   - `caption`: `{{1.captions.facebook.caption}}`

---

#### 4️⃣ **Instagram** (⭐⭐ متوسط - 15 دقيقة)

**التعليمات:**
1. في **Graph API Explorer**:
   - Permissions: `instagram_basic`, `instagram_content_publish`, `pages_read_engagement`
   - اضغط **"Generate Access Token"**
2. أرسل `GET /me/accounts` → انسخ Page ID
3. أرسل `GET /{page_id}?fields=instagram_business_account`
4. انسخ `instagram_business_account.id`
5. في الملف، استبدل:
   ```json
   "access_token": "YOUR_INSTAGRAM_ACCESS_TOKEN_HERE",
   "ig_account_id": "YOUR_IG_BUSINESS_ACCOUNT_ID_HERE"
   ```

**في Make.com:**
1. أضف module **"HTTP"** → **"Make a request"**
2. URL: `https://graph.facebook.com/v18.0/{IG_ACCOUNT_ID}/media`
3. Method: `POST`
4. Query String:
   - `access_token`: الصق Token
   - `image_url`: `{{1.images.post}}`
   - `caption`: `{{1.captions.instagram.caption}}`

---

#### 5️⃣ **Twitter/X** (⭐⭐ متوسط - 10 دقائق)

**التعليمات:**
1. اذهب إلى https://developer.twitter.com
2. أنشئ App جديد
3. Keys and tokens → انسخ **Bearer Token**
4. في الملف، استبدل:
   ```json
   "bearer_token": "YOUR_TWITTER_BEARER_TOKEN_HERE"
   ```

**في Make.com:**
1. أضف module **"HTTP"** → **"Make a request"**
2. URL: `https://api.twitter.com/2/tweets`
3. Method: `POST`
4. Headers:
   - Name: `Authorization`
   - Value: `Bearer {BEARER_TOKEN}`
   - Name: `Content-Type`
   - Value: `application/json`
5. Body Type: `Raw`
6. Body:
   ```json
   {"text": "{{1.captions.twitter.caption}}"}
   ```

---

## 📊 ملخص المنصات

| # | المنصة | الصعوبة | الوقت | الأولوية | الحالة |
|---|--------|---------|-------|----------|--------|
| 1 | Telegram | ⭐ سهل | 3 دقائق | عالية | ✅ موصى به |
| 2 | Discord | ⭐ سهل | 1 دقيقة | عالية | ✅ موصى به |
| 3 | Facebook | ⭐⭐ متوسط | 10 دقائق | متوسطة | ⚪ اختياري |
| 4 | Instagram | ⭐⭐ متوسط | 15 دقيقة | متوسطة | ⚪ اختياري |
| 5 | Twitter | ⭐⭐ متوسط | 10 دقائق | متوسطة | ⚪ اختياري |
| 6 | TikTok | ⭐⭐⭐ صعب | 30 دقيقة | منخفضة | ⚪ اختياري |
| 7 | LinkedIn | ⭐⭐⭐ صعب | 20 دقيقة | منخفضة | ⚪ اختياري |
| 8 | Pinterest | ⭐⭐ متوسط | 15 دقيقة | منخفضة | ⚪ اختياري |

---

## 🎯 الترتيب الموصى به

### المرحلة 1: الأساسيات (4 دقائق)
1. ✅ Telegram
2. ✅ Discord

**بعد هذه المرحلة:** لديك نظام نشر تلقائي عامل على منصتين!

### المرحلة 2: التوسع (35 دقيقة)
3. ⚪ Facebook
4. ⚪ Instagram
5. ⚪ Twitter

**بعد هذه المرحلة:** لديك نظام نشر على 5 منصات رئيسية!

### المرحلة 3: الاحتراف (65 دقيقة)
6. ⚪ Pinterest
7. ⚪ LinkedIn
8. ⚪ TikTok

**بعد هذه المرحلة:** لديك نظام نشر شامل على 8 منصات!

---

## 🔧 نصائح مهمة

### ✅ **قبل البدء:**
- تأكد من أن حساباتك Business Accounts (Instagram, TikTok, Pinterest)
- احفظ جميع الـ Tokens في مكان آمن
- لا تشارك الـ Tokens مع أحد

### ⚠️ **أثناء الإعداد:**
- اختبر كل منصة على حدة
- استخدم Postman لاختبار الـ APIs
- راجع Execution History في Make.com

### 🔐 **الأمان:**
- استخدم Environment Variables للـ Tokens
- لا تكتب الـ Tokens مباشرة في الكود
- قم بتجديد الـ Tokens بانتظام

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

ملف `ALL_PLATFORMS_CONFIG.json` يحتوي على **كل ما تحتاجه** لإعداد جميع المنصات:

✅ تعليمات خطوة بخطوة  
✅ أمثلة كاملة  
✅ ترتيب موصى به  
✅ وقت الإعداد المتوقع  
✅ نصائح الأمان  

**ابدأ الآن بـ Telegram و Discord - الأسهل والأسرع!** 🚀

---

**آخر تحديث:** 2026-02-13  
**الإصدار:** v1.0  
**الحالة:** جاهز للاستخدام ✅
