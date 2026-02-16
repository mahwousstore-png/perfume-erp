# 🎬 دليل إنشاء Scenario خطوة بخطوة - مصور بالكامل

## 🎯 الهدف
إنشاء Scenario جديد نظيف يربط **استديو مهووس** بـ **Telegram** و **Discord** (5 دقائق فقط!)

---

## 📋 المتطلبات

✅ حساب Make.com  
✅ Webhook URL: `https://hook.eu2.make.com/28v9yfukz2u1yotgsemg8j32jhwegag2`  
✅ Telegram Bot Token (سنحصل عليه في الخطوة 3)  
✅ Discord Webhook URL (سنحصل عليه في الخطوة 4)  

---

## 🚀 الخطوات

### الخطوة 1: إنشاء Scenario جديد (30 ثانية)

1. **افتح Make.com:**
   ```
   https://eu2.make.com/2934620/scenarios
   ```

2. **اضغط زر "Create scenario"** (الزر الأرجواني في الأعلى)

3. **سمّ الـ Scenario:**
   ```
   Mahwous Studio - Auto Publish
   ```

4. **احفظ** (Ctrl+S أو زر Save)

---

### الخطوة 2: إضافة Webhook (1 دقيقة)

1. **اضغط على الدائرة الكبيرة** في وسط الشاشة

2. **ابحث عن "Webhooks"** في مربع البحث

3. **اختر "Webhooks"** → **"Custom webhook"**

4. **في نافذة الإعدادات:**
   - **Webhook name:** `Mahwous Studio Webhook`
   - **اضغط "Add"**

5. **انسخ Webhook URL:**
   ```
   https://hook.eu2.make.com/28v9yfukz2u1yotgsemg8j32jhwegag2
   ```
   
   ⚠️ **مهم:** هذا الـ URL موجود بالفعل! فقط تأكد من استخدامه.

6. **اضغط "OK"**

---

### الخطوة 3: إضافة Router (30 ثانية)

1. **اضغط على "+"** بعد module الـ Webhooks

2. **ابحث عن "Router"**

3. **اختر "Flow control"** → **"Router"**

4. **اضغط "OK"**

الآن لديك:
```
Webhooks → Router
```

---

### الخطوة 4: إضافة Telegram (3 دقائق)

#### 4.1 الحصول على Bot Token

1. **افتح Telegram** على هاتفك أو الكمبيوتر

2. **ابحث عن:** `@BotFather`

3. **أرسل:** `/newbot`

4. **اتبع التعليمات:**
   ```
   Bot Name: Mahwous Studio Bot
   Username: mahwous_studio_bot
   ```

5. **انسخ Bot Token:**
   ```
   مثال: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
   ```

#### 4.2 إضافة Bot للقناة

1. **افتح قناتك** (مثال: @mahwous_channel)

2. **اذهب إلى:** Settings → Administrators → Add Administrator

3. **ابحث عن:** `@mahwous_studio_bot`

4. **أضفه** وامنحه صلاحية **"Post Messages"**

#### 4.3 إضافة Telegram في Make.com

1. **اضغط على "+"** بعد الـ Router (المسار الأول)

2. **ابحث عن "Telegram"**

3. **اختر "Telegram Bot"** → **"Send a Photo"**

4. **في نافذة Connection:**
   - **اضغط "Add"**
   - **Connection name:** `Mahwous Telegram Bot`
   - **Bot Token:** الصق Token الذي حصلت عليه
   - **اضغط "Save"**

5. **في نافذة الإعدادات:**
   - **Chat ID:** `@mahwous_channel` (أو ID قناتك)
   - **Photo:** اضغط على الحقل → اختر `1. images` → `post`
   - **Caption:** اضغط على الحقل → اختر `1. captions` → `telegram` → `caption`
   - **Parse Mode:** `HTML`

6. **اضغط "OK"**

---

### الخطوة 5: إضافة Discord (1 دقيقة)

#### 5.1 الحصول على Webhook URL

1. **افتح Discord Server**

2. **اذهب إلى:** Server Settings → Integrations

3. **اضغط "Create Webhook"**

4. **سمّه:** `Mahwous Studio`

5. **اختر القناة** التي تريد النشر فيها

6. **اضغط "Copy Webhook URL"**
   ```
   مثال: https://discord.com/api/webhooks/123456789/abcdefg
   ```

#### 5.2 إضافة Discord في Make.com

1. **اضغط على "+"** بعد الـ Router (المسار الثاني)

2. **ابحث عن "HTTP"**

3. **اختر "HTTP"** → **"Make a request"**

4. **في نافذة الإعدادات:**
   - **URL:** الصق Discord Webhook URL
   - **Method:** `POST`
   - **Headers:** اضغط "Add item"
     - **Name:** `Content-Type`
     - **Value:** `application/json`
   - **Body type:** `Raw`
   - **Request content:** الصق هذا:
     ```json
     {
       "content": "{{1.captions.instagram.caption}}",
       "embeds": [{
         "title": "{{1.product_name}}",
         "description": "{{1.descriptions.short}}",
         "image": {
           "url": "{{1.images.post}}"
         },
         "color": 3447003
       }]
     }
     ```

5. **اضغط "OK"**

---

### الخطوة 6: حفظ واختبار (1 دقيقة)

1. **احفظ الـ Scenario:** اضغط زر **"Save"** (أو Ctrl+S)

2. **فعّل الـ Scenario:** اضغط زر **"ON"** في الأسفل

3. **اختبر الآن:**
   - افتح **استديو مهووس**
   - ارفع صورة عطر
   - فعّل **"نشر تلقائي عبر Make.com"**
   - اضغط **"ابدأ التوليد"**

4. **تحقق من النتيجة:**
   - افتح قناة Telegram
   - افتح قناة Discord
   - يجب أن ترى المنشور في كلاهما! 🎉

---

## 📊 الشكل النهائي

```
┌─────────────┐
│  Webhooks   │
│  (استقبال)  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Router    │
│   (توزيع)   │
└──┬───────┬──┘
   │       │
   ▼       ▼
┌──────┐ ┌──────┐
│Telegram Discord│
│ (نشر) │ (نشر) │
└──────┘ └──────┘
```

---

## 🎯 إضافة منصات إضافية (اختياري)

بعد أن تعمل Telegram و Discord، يمكنك إضافة:

### Facebook (10 دقائق)
- اضغط "+" بعد Router (المسار الثالث)
- HTTP → Make a request
- URL: `https://graph.facebook.com/v18.0/{PAGE_ID}/photos`
- Method: POST
- Query String:
  - `access_token`: {YOUR_TOKEN}
  - `url`: `{{1.images.post}}`
  - `caption`: `{{1.captions.facebook.caption}}`

### Instagram (15 دقيقة)
- اضغط "+" بعد Router (المسار الرابع)
- HTTP → Make a request
- URL: `https://graph.facebook.com/v18.0/{IG_ACCOUNT_ID}/media`
- Method: POST
- Query String:
  - `access_token`: {YOUR_TOKEN}
  - `image_url`: `{{1.images.post}}`
  - `caption`: `{{1.captions.instagram.caption}}`

### Twitter (10 دقائق)
- اضغط "+" بعد Router (المسار الخامس)
- HTTP → Make a request
- URL: `https://api.twitter.com/2/tweets`
- Method: POST
- Headers:
  - `Authorization`: `Bearer {YOUR_TOKEN}`
  - `Content-Type`: `application/json`
- Body: `{"text": "{{1.captions.twitter.caption}}"}`

---

## 🔍 استكشاف الأخطاء

### المشكلة: "Chat not found" (Telegram)
**الحل:**
- تأكد من أن الـ Bot موجود في القناة كـ Administrator
- تأكد من أن `chat_id` يبدأ بـ `@` (مثال: `@mahwous_channel`)
- أو استخدم Chat ID الرقمي (مثال: `-1001234567890`)

### المشكلة: "Invalid Webhook URL" (Discord)
**الحل:**
- تأكد من نسخ الـ URL كاملاً
- تأكد من أن الـ Webhook لم يُحذف من Discord
- أعد إنشاء Webhook جديد

### المشكلة: "No data received" (Make.com)
**الحل:**
- تأكد من أن Webhook URL في Streamlit Secrets صحيح
- تأكد من أن Scenario مفعّل (ON)
- جرّب "Run once" في Make.com

---

## 📞 الدعم

إذا واجهت مشاكل:

1. **راجع Execution History:**
   - Make.com → Scenarios → اضغط على Scenario
   - اضغط "History" في الأسفل
   - شاهد الأخطاء

2. **اختبر كل module على حدة:**
   - اضغط Right-click على module
   - اختر "Run this module only"

3. **راجع الأدلة الأخرى:**
   - `ALL_PLATFORMS_CONFIG.json`
   - `PLATFORMS_CONFIG_GUIDE.md`
   - `WEBHOOK_SETUP.md`

---

## 🎉 الخلاصة

الآن لديك Scenario عامل 100% يربط:

✅ **استديو مهووس** → **Webhook** → **Router** → **Telegram + Discord**

**الوقت الإجمالي:** 5-7 دقائق  
**الصعوبة:** ⭐ سهل جداً  
**النتيجة:** نشر تلقائي على منصتين!  

---

## 📸 لقطات الشاشة (للمساعدة)

### 1. إنشاء Scenario جديد
```
[Create scenario] → أدخل الاسم → [Save]
```

### 2. إضافة Webhooks
```
[+] → Webhooks → Custom webhook → [Add] → [OK]
```

### 3. إضافة Router
```
[+] → Flow control → Router → [OK]
```

### 4. إضافة Telegram
```
[+] → Telegram Bot → Send a Photo → [Add connection] → الصق Token → [Save] → ملء الحقول → [OK]
```

### 5. إضافة Discord
```
[+] → HTTP → Make a request → الصق Webhook URL → ملء الحقول → [OK]
```

---

**آخر تحديث:** 2026-02-13  
**الإصدار:** v1.0  
**الحالة:** جاهز للاستخدام ✅

**ابدأ الآن!** 🚀
