# 📱 Blueprint الكامل - دليل سريع

## 🎯 ما هو هذا Blueprint؟

**Blueprint كامل ومحدّث** يحتوي على **جميع أنواع المنشورات** لكل منصة مع **جميع الإعدادات** جاهزة.

**أنت فقط تربط الحسابات - كل شيء آخر جاهز!** ✅

---

## 📦 المنصات والأنواع المدعومة

### 1️⃣ **Instagram** (3 أنواع)
- ✅ **Post** - منشور عادي (صورة 1080x1080)
- ✅ **Story** - قصة (صورة 1080x1920)
- ✅ **Reels** - فيديو قصير (9:16)

**الإعدادات:**
- Caption (2200 حرف)
- Hashtags (30 هاشتاق)
- Alt Text
- Location (اختياري)
- User Tags (اختياري)

---

### 2️⃣ **Facebook** (2 نوع)
- ✅ **Page Post** - منشور على الصفحة (صورة 1080x1080)
- ✅ **Story** - قصة (صورة 1080x1920)

**الإعدادات:**
- Message (بدون حد)
- Picture URL
- Published (منشور/مسودة)
- Targeting (استهداف جغرافي: السعودية، الإمارات، الكويت، قطر، البحرين، عمان)

---

### 3️⃣ **Twitter/X** (1 نوع)
- ✅ **Tweet** - تغريدة (صورة 1200x675)

**الإعدادات:**
- Text (280 حرف)
- Media (صورة/فيديو)
- Reply Settings (من يمكنه الرد: الجميع/المتابعين/المذكورين)

---

### 4️⃣ **Telegram** (1 نوع)
- ✅ **Photo Message** - رسالة مع صورة (1080x1080)

**الإعدادات:**
- Chat ID (@channel_username)
- Photo URL
- Caption (1024 حرف)
- Parse Mode (HTML/Markdown)
- Disable Notification (لا)
- Protect Content (لا)

---

### 5️⃣ **TikTok** (1 نوع)
- ✅ **Video Upload** - رفع فيديو (9:16)

**الإعدادات:**
- Video URL
- Caption (150 حرف)
- Privacy Level (Public)
- Disable Duet (لا)
- Disable Stitch (لا)
- Disable Comment (لا)
- Video Cover Timestamp (1 ثانية)

---

### 6️⃣ **LinkedIn** (1 نوع)
- ✅ **Post** - منشور (صورة 1080x1080)

**الإعدادات:**
- Account Type (Organization)
- Organization (صفحتك)
- Text (3000 حرف)
- Visibility (Public)
- Media (صورة + Alt Text)

---

### 7️⃣ **Pinterest** (1 نوع)
- ✅ **Pin** - دبوس (صورة 1080x1080)

**الإعدادات:**
- Board (اللوحة)
- Image URL
- Title (100 حرف)
- Description (500 حرف)
- Link (رابط المتجر)
- Alt Text

---

### 8️⃣ **YouTube** (1 نوع)
- ✅ **Community Post** - منشور في المجتمع (صورة 1080x1080)

**الإعدادات:**
- Text (بدون حد)
- Image URL

---

### 9️⃣ **Discord** (1 نوع)
- ✅ **Message** - رسالة في القناة (صورة 1080x1080)

**الإعدادات:**
- Webhook URL
- Content (2000 حرف)
- Embeds (عنوان + وصف + صورة + لون)

---

## 🚀 خطوات الاستخدام

### الخطوة 1: استيراد Blueprint
1. افتح Make.com → **"Create a new scenario"**
2. اضغط **"..."** → **"Import Blueprint"**
3. ارفع الملف: `mahwous_studio_complete_blueprint.json`
4. اضغط **"Import"**

### الخطوة 2: ربط الحسابات (فقط!)

#### Instagram:
- اضغط على "Instagram Post" → **"Add"** → **"Authorize"**
- كرر لـ "Instagram Story" و "Instagram Reels"

#### Facebook:
- اضغط على "Facebook Post" → **"Add"** → **"Authorize"**
- كرر لـ "Facebook Story"

#### Twitter:
- اضغط على "Twitter Tweet" → **"Add"** → **"Authorize"**

#### Telegram:
1. أنشئ Bot عبر @BotFather
2. انسخ Bot Token
3. اضغط على "Telegram Post" → **"Add"** → الصق Token
4. عدّل `chat_id` إلى `@your_channel`

#### TikTok:
- اضغط على "TikTok Video" → **"Add"** → **"Authorize"**
- **مهم:** يجب أن يكون حسابك Business Account

#### LinkedIn:
- اضغط على "LinkedIn Post" → **"Add"** → **"Authorize"**

#### Pinterest:
- اضغط على "Pinterest Pin" → **"Add"** → **"Authorize"**
- اختر اللوحة (Board)

#### YouTube:
- اضغط على "YouTube Community" → **"Add"** → **"Authorize"**

#### Discord:
1. أنشئ Webhook في Discord Server
2. انسخ Webhook URL
3. اضغط على "Discord Message" → الصق URL

### الخطوة 3: إعداد Webhook
1. انسخ Webhook URL من Make.com
2. أضفه في Streamlit Secrets:
```toml
WEBHOOK_PUBLISH_CONTENT = "https://hook.us1.make.com/YOUR_ID"
```

### الخطوة 4: تفعيل
- اضغط **"Turn on"** في Make.com

### الخطوة 5: اختبار
1. في استديو مهووس، ارفع صورة عطر
2. فعّل "نشر تلقائي"
3. اضغط "ابدأ التوليد"
4. **سينشر على جميع المنصات تلقائياً!** 🎉

---

## 📊 ملخص المنصات

| # | المنصة | الأنواع | الإعدادات |
|---|--------|---------|-----------|
| 1 | Instagram | Post + Story + Reels | ✅ كاملة |
| 2 | Facebook | Post + Story | ✅ كاملة |
| 3 | Twitter | Tweet | ✅ كاملة |
| 4 | Telegram | Photo Message | ✅ كاملة |
| 5 | TikTok | Video Upload | ✅ كاملة |
| 6 | LinkedIn | Post | ✅ كاملة |
| 7 | Pinterest | Pin | ✅ كاملة |
| 8 | YouTube | Community Post | ✅ كاملة |
| 9 | Discord | Message | ✅ كاملة |

**المجموع:** 9 منصات، 13 نوع منشور، 100% جاهز! ✅

---

## ⚙️ الإعدادات الجاهزة

### ✅ **أحجام الصور:**
- Story: 1080x1920 (9:16)
- Post: 1080x1080 (1:1)
- Twitter: 1200x675 (16:9)

### ✅ **حدود النصوص:**
- Instagram: 2200 حرف
- Twitter: 280 حرف
- TikTok: 150 حرف
- Telegram: 1024 حرف
- LinkedIn: 3000 حرف
- Pinterest: 500 حرف
- Discord: 2000 حرف

### ✅ **الخصوصية:**
- Instagram: Public
- Facebook: Public (مع استهداف جغرافي)
- Twitter: Public (الجميع يمكنه الرد)
- TikTok: Public (Duet/Stitch/Comment مفعّلة)
- LinkedIn: Public

### ✅ **الاستهداف الجغرافي (Facebook):**
- السعودية 🇸🇦
- الإمارات 🇦🇪
- الكويت 🇰🇼
- قطر 🇶🇦
- البحرين 🇧🇭
- عمان 🇴🇲

---

## 🎉 الخلاصة

**Blueprint كامل 100%** يحتوي على:

✅ 9 منصات  
✅ 13 نوع منشور  
✅ جميع الإعدادات جاهزة  
✅ أحجام الصور محددة  
✅ حدود النصوص محددة  
✅ الخصوصية محددة  
✅ الاستهداف الجغرافي محدد  

**أنت فقط تربط الحسابات - كل شيء آخر جاهز!** 🚀

---

## 📝 ملاحظات مهمة

### ✅ **قبل الاستخدام:**
- تأكد من أن حساباتك Business Accounts (Instagram, TikTok, Pinterest)
- أنشئ Telegram Bot
- أنشئ Discord Webhook
- احفظ Webhook URL في Streamlit Secrets

### ⚠️ **حدود المنصات:**
- Instagram: 25 منشور/يوم
- TikTok: 5 فيديوهات/يوم (حساب جديد)
- Twitter: 300 تغريدة/3 ساعات
- Telegram: 30 رسالة/ثانية

### 💰 **التكاليف:**
- Make.com Free: 1000 عملية/شهر
- Make.com Pro: $9/شهر → 10,000 عملية

---

**آخر تحديث:** 2026-02-13  
**الإصدار:** v2.0 (Complete)  
**الحالة:** جاهز للاستخدام ✅
