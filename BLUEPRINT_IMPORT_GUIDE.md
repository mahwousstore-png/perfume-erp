# 📥 دليل استيراد Make.com Blueprint

## 🎯 نظرة عامة

هذا الدليل يشرح كيفية استيراد **Mahwous Studio Blueprint** الجاهز إلى Make.com في **أقل من 5 دقائق**.

---

## 📦 الملف المطلوب

**اسم الملف:** `mahwous_studio_make_blueprint.json`

**المحتوى:**
- ✅ Webhook (استقبال البيانات)
- ✅ Router (توزيع على المنصات)
- ✅ Instagram (Post + Story)
- ✅ Facebook (Page Post)
- ✅ Twitter/X (Tweet)
- ✅ Telegram (Channel Message)
- ✅ TikTok (Video Upload)
- ✅ LinkedIn (Post)
- ✅ Pinterest (Pin)

---

## 🚀 خطوات الاستيراد

### الخطوة 1: تسجيل الدخول إلى Make.com
1. اذهب إلى https://www.make.com
2. سجّل دخول بحسابك
3. إذا لم يكن لديك حساب، أنشئ حساب جديد (مجاني)

---

### الخطوة 2: استيراد Blueprint

#### أ. افتح صفحة الاستيراد
1. في الصفحة الرئيسية، اضغط **"Scenarios"** من القائمة الجانبية
2. اضغط **"Create a new scenario"**
3. في الزاوية السفلية اليسرى، اضغط على أيقونة **"..."** (ثلاث نقاط)
4. اختر **"Import Blueprint"**

#### ب. رفع الملف
1. اضغط **"Choose file"**
2. اختر الملف: `mahwous_studio_make_blueprint.json`
3. اضغط **"Import"**

#### ج. انتظر التحميل
- ستظهر رسالة: "Blueprint imported successfully"
- سيظهر الـ Scenario كاملاً مع جميع الـ Modules

---

### الخطوة 3: ربط الحسابات

الآن تحتاج إلى ربط حساباتك على كل منصة:

#### 1️⃣ **Instagram**
1. اضغط على Module "Instagram - Create Media Object"
2. اضغط **"Add"** بجانب "Connection"
3. اختر **"Instagram Business Account"**
4. اضغط **"Authorize"**
5. سجّل دخول بحسابك على Instagram
6. وافق على الصلاحيات
7. كرر نفس الخطوات لـ "Instagram - Create Story"

#### 2️⃣ **Facebook**
1. اضغط على Module "Facebook - Create Page Post"
2. اضغط **"Add"** بجانب "Connection"
3. اختر **"Facebook Page"**
4. اضغط **"Authorize"**
5. سجّل دخول بحسابك على Facebook
6. اختر الصفحة المطلوبة
7. وافق على الصلاحيات

#### 3️⃣ **Twitter/X**
1. اضغط على Module "Twitter - Post Tweet"
2. اضغط **"Add"** بجانب "Connection"
3. اختر **"Twitter API v2"**
4. اضغط **"Authorize"**
5. سجّل دخول بحسابك على Twitter
6. وافق على الصلاحيات

#### 4️⃣ **Telegram**
1. افتح Telegram وابحث عن `@BotFather`
2. أرسل `/newbot`
3. اتبع التعليمات لإنشاء Bot
4. انسخ **Bot Token**
5. في Make.com، اضغط على Module "Telegram - Send Message"
6. اضغط **"Add"** بجانب "Connection"
7. الصق **Bot Token**
8. اضغط **"Save"**
9. **مهم:** أضف الـ Bot إلى قناتك وامنحه صلاحيات الإرسال
10. عدّل `chat_id` في الـ Module إلى `@your_channel_username`

#### 5️⃣ **TikTok**
1. اضغط على Module "TikTok - Upload Video"
2. اضغط **"Add"** بجانب "Connection"
3. اختر **"TikTok Business Account"**
4. اضغط **"Authorize"**
5. سجّل دخول بحسابك على TikTok
6. وافق على الصلاحيات
7. **ملاحظة:** يجب أن يكون حسابك Business Account

#### 6️⃣ **LinkedIn**
1. اضغط على Module "LinkedIn - Create Post"
2. اضغط **"Add"** بجانب "Connection"
3. اختر **"LinkedIn Page"**
4. اضغط **"Authorize"**
5. سجّل دخول بحسابك على LinkedIn
6. اختر الصفحة المطلوبة
7. وافق على الصلاحيات

#### 7️⃣ **Pinterest**
1. اضغط على Module "Pinterest - Create Pin"
2. اضغط **"Add"** بجانب "Connection"
3. اختر **"Pinterest Business Account"**
4. اضغط **"Authorize"**
5. سجّل دخول بحسابك على Pinterest
6. اختر اللوحة (Board) المطلوبة
7. وافق على الصلاحيات

---

### الخطوة 4: إعداد Webhook

#### أ. الحصول على Webhook URL
1. اضغط على Module "Webhook" (الأول في الـ Scenario)
2. اضغط **"Copy address to clipboard"**
3. انسخ الـ URL - ستحتاجه في الخطوة التالية

**مثال على الـ URL:**
```
https://hook.us1.make.com/123456789abcdefghijklmnop
```

#### ب. إضافة الـ URL في Streamlit Secrets
1. افتح مشروعك على Streamlit Cloud
2. اذهب إلى **Settings** → **Secrets**
3. أضف السطر التالي:

```toml
WEBHOOK_PUBLISH_CONTENT = "https://hook.us1.make.com/YOUR_WEBHOOK_ID"
```

4. اضغط **"Save"**
5. أعد تشغيل التطبيق (Reboot app)

---

### الخطوة 5: اختبار الـ Scenario

#### أ. تفعيل الـ Scenario
1. في Make.com، اضغط **"Turn on"** في الزاوية العلوية اليسرى
2. ستظهر رسالة: "Scenario is now active"

#### ب. إرسال بيانات اختبار
من التطبيق (استديو مهووس):

1. افتح **استديو مهووس الذكي**
2. ارفع صورة عطر
3. اختر المخرجات:
   - ✅ توليد 3 صور احترافية
   - ✅ توليد فيديو قصير
   - ✅ توليد Captions لكل منصة
   - ✅ توليد 30 هاشتاق
4. فعّل **"نشر تلقائي عبر Make.com"**
5. اضغط **"ابدأ التوليد"**

#### ج. مراقبة التنفيذ
1. في Make.com، اضغط **"Execution history"** (أسفل الصفحة)
2. ستجد سجل المحاولة الأخيرة
3. تحقق من الأخطاء (إن وجدت)
4. تحقق من نشر المحتوى على جميع المنصات

---

## ✅ التحقق من النجاح

بعد إرسال البيانات، تحقق من:

| المنصة | ما تتحقق منه |
|--------|--------------|
| Instagram | Post جديد + Story جديدة |
| Facebook | Post جديد على الصفحة |
| Twitter | Tweet جديد |
| Telegram | رسالة جديدة في القناة |
| TikTok | فيديو جديد |
| LinkedIn | Post جديد على الصفحة |
| Pinterest | Pin جديد في اللوحة |

---

## 🔧 تخصيص الـ Blueprint

### تعديل Telegram Chat ID
إذا كنت تريد النشر في قناة مختلفة:

1. في Module "Telegram - Send Message"
2. عدّل حقل `chat_id` من `@mahwous_channel` إلى `@your_channel`

### تعديل Pinterest Link
إذا كنت تريد تغيير رابط المتجر:

1. في Module "Pinterest - Create Pin"
2. عدّل حقل `link` من `https://mahwous.com` إلى رابطك

### إضافة منصات إضافية
إذا كنت تريد إضافة منصات أخرى (مثل Snapchat, WhatsApp):

1. اضغط **"+ Add a module"** بعد الـ Router
2. ابحث عن المنصة المطلوبة
3. اتبع نفس الخطوات

---

## ⚠️ استكشاف الأخطاء

### المشكلة: "Webhook URL غير صحيح"
**الحل:**
- تأكد من نسخ الـ URL كاملاً بدون مسافات
- تأكد من أن الـ Scenario مفعّل (Turn on)

### المشكلة: "فشل الاتصال بـ Instagram"
**الحل:**
- تحقق من أن الحساب Business Account
- تحقق من صلاحيات الـ Token
- أعد ربط الحساب

### المشكلة: "الرسالة لم تُرسل إلى Telegram"
**الحل:**
- تأكد من أن الـ Bot موجود في القناة
- تأكد من أن الـ Bot له صلاحيات الإرسال
- تحقق من أن `chat_id` صحيح

### المشكلة: "فشل رفع الفيديو على TikTok"
**الحل:**
- تحقق من أن الحساب Business Account
- تحقق من حجم الفيديو (أقل من 500MB)
- تحقق من صيغة الفيديو (MP4)

### المشكلة: "Execution failed"
**الحل:**
1. افتح **Execution history**
2. اضغط على المحاولة الفاشلة
3. اقرأ رسالة الخطأ
4. عالج المشكلة حسب الرسالة

---

## 📊 الإعدادات المتقدمة

### تأخير التنفيذ
إذا كنت تريد تأخير النشر على منصة معينة:

1. اضغط **"+ Add a module"** بعد الـ Module المطلوب
2. ابحث عن **"Sleep"**
3. اختر **"Sleep"**
4. حدد المدة (مثلاً 5 دقائق)

### معالجة الأخطاء
إذا كنت تريد الاستمرار حتى لو فشلت منصة:

1. اضغط بزر الماوس الأيمن على الـ Module
2. اختر **"Add error handler"**
3. اختر **"Ignore"** أو **"Continue"**

### إضافة شروط
إذا كنت تريد نشر Instagram فقط إذا كان هناك صورة:

1. اضغط على الخط بين Router و Instagram Module
2. اضغط **"Set up a filter"**
3. أضف الشرط: `{{1.images.post}}` exists

---

## 🎉 الخلاصة

بعد إكمال هذا الدليل، ستكون لديك:

✅ Scenario كامل جاهز للعمل  
✅ جميع المنصات مربوطة  
✅ Webhook متصل بالتطبيق  
✅ نشر تلقائي على 7 منصات  

**كل هذا بضغطة زر واحدة!** 🚀

---

## 📞 الدعم

إذا واجهت مشاكل:
1. اقرأ قسم "استكشاف الأخطاء" أعلاه
2. تحقق من Execution History في Make.com
3. تأكد من صلاحيات الحسابات
4. اتصل بـ Make.com Support: https://www.make.com/en/help

---

## 📝 ملاحظات مهمة

### ✅ **أفضل الممارسات:**
- راجع الـ Logs بانتظام
- احفظ نسخة احتياطية من الـ Blueprint
- استخدم أسماء واضحة للـ Scenarios
- اختبر قبل الاستخدام الفعلي

### ⚠️ **التحذيرات:**
- لا تشارك Webhook URL مع أحد
- تأكد من صلاحيات الحسابات
- راجع حدود كل منصة (عدد المنشورات/اليوم)
- احفظ المفاتيح في متغيرات البيئة

### 💰 **التكاليف:**
- Make.com: خطة مجانية (1000 عملية/شهر)
- Make.com Pro: $9/شهر (10,000 عملية/شهر)
- Make.com Team: $16/شهر (10,000 عملية/شهر + فريق)

---

**آخر تحديث:** 2026-02-13  
**الإصدار:** v1.0  
**الحالة:** جاهز للاستخدام ✅

---

## 🔗 روابط مفيدة

- **Make.com:** https://www.make.com
- **Make.com Help:** https://www.make.com/en/help
- **Make.com Community:** https://community.make.com
- **GitHub Repository:** https://github.com/mahwousstore-png/perfume-erp
