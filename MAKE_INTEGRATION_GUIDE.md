# 🔄 دليل شامل لترحيل البيانات من التطبيق إلى Make.com

**التاريخ:** 18 فبراير 2026  
**الإصدار:** v16.0  

---

## 📋 **جدول المحتويات**

1. [نظرة عامة](#نظرة-عامة)
2. [البنية الحالية](#البنية-الحالية)
3. [أنواع البيانات المُرسلة](#أنواع-البيانات-المُرسلة)
4. [تنسيق JSON المُرسل](#تنسيق-json-المُرسل)
5. [سيناريوهات Make.com](#سيناريوهات-makecom)
6. [أمثلة عملية](#أمثلة-عملية)
7. [معالجة الأخطاء](#معالجة-الأخطاء)

---

## 🎯 **نظرة عامة**

### **ما هو Make.com؟**
Make.com (سابقاً Integromat) هو منصة أتمتة تربط التطبيقات المختلفة ببعضها. في حالتنا، نستخدمه لإرسال البيانات من تطبيق Streamlit إلى منصة سلة (Salla).

### **التدفق العام:**
```
Streamlit App → Make.com Webhook → Make.com Scenario → Salla API
```

---

## 🏗️ **البنية الحالية**

### **1. Webhooks المستخدمة**

| Webhook | الغرض | URL |
|---------|-------|-----|
| **تحديث الأسعار** | إرسال منتجات لتحديث أسعارها | `https://hook.eu2.make.com/99oljy0d6r3chwg6bdfsptcf6bk8htsd` |
| **منتجات جديدة** | إرسال منتجات جديدة للإضافة | `https://hook.eu2.make.com/xvubj23dmpxu8qzilstd25cnumrwtdxm` |
| **منتجات مفقودة** | إرسال منتجات مفقودة (مستقبلي) | غير مُفعّل حالياً |

---

## 📊 **أنواع البيانات المُرسلة**

### **جدول مقارنة أنواع البيانات**

| النوع | الحقول المطلوبة | الحقول الاختيارية | الاستخدام |
|-------|-----------------|-------------------|-----------|
| **تحديث سعر** | `product_name`, `new_price`, `old_price` | `competitor_name`, `competitor_price`, `confidence`, `risk` | تحديث سعر منتج موجود |
| **منتج جديد** | `product_name`, `price`, `brand`, `size` | `type`, `description`, `image_url` | إضافة منتج جديد |
| **منتج مفقود** | `product_name`, `competitor_name`, `competitor_price` | `recommendation`, `profitability` | تنبيه بمنتج مفقود |

---

## 📦 **تنسيق JSON المُرسل**

### **1. تحديث الأسعار (Price Update)**

#### **البنية الأساسية:**
```json
{
  "event_type": "price_update",
  "timestamp": "2026-02-18T01:15:00Z",
  "source": "perfume_pricing_system_v16",
  "total_products": 5,
  "products": [
    {
      "product_name": "عطر شانيل نمبر 5 او دي بارفان 100 مل",
      "old_price": 450.00,
      "new_price": 420.00,
      "price_change": -30.00,
      "price_change_pct": -6.67,
      "competitor_name": "عطور السعودية",
      "competitor_price": 410.00,
      "confidence": 95,
      "risk_level": "متوسط",
      "match_stage": "fast",
      "reason": "سعرنا أعلى بـ 6.67% من المنافس"
    }
  ]
}
```

#### **جدول الحقول:**

| الحقل | النوع | مطلوب؟ | الوصف | مثال |
|-------|------|--------|-------|------|
| `event_type` | string | ✅ | نوع الحدث | `"price_update"` |
| `timestamp` | string | ✅ | وقت الإرسال (ISO 8601) | `"2026-02-18T01:15:00Z"` |
| `source` | string | ✅ | مصدر البيانات | `"perfume_pricing_system_v16"` |
| `total_products` | integer | ✅ | عدد المنتجات | `5` |
| `products` | array | ✅ | قائمة المنتجات | `[...]` |
| `product_name` | string | ✅ | اسم المنتج الكامل | `"عطر شانيل نمبر 5..."` |
| `old_price` | float | ✅ | السعر القديم | `450.00` |
| `new_price` | float | ✅ | السعر الجديد | `420.00` |
| `price_change` | float | ✅ | الفرق بالريال | `-30.00` |
| `price_change_pct` | float | ✅ | الفرق بالنسبة % | `-6.67` |
| `competitor_name` | string | ⚠️ | اسم المنافس | `"عطور السعودية"` |
| `competitor_price` | float | ⚠️ | سعر المنافس | `410.00` |
| `confidence` | integer | ⚠️ | نسبة الثقة (0-100) | `95` |
| `risk_level` | string | ⚠️ | مستوى الخطورة | `"حرج"` / `"متوسط"` / `"عادي"` |
| `match_stage` | string | ⚠️ | مرحلة المطابقة | `"fast"` / `"medium"` / `"deep"` / `"gemini"` |
| `reason` | string | ⚠️ | سبب التحديث | `"سعرنا أعلى بـ..."` |

---

### **2. منتجات جديدة (New Products)**

#### **البنية الأساسية:**
```json
{
  "event_type": "new_products",
  "timestamp": "2026-02-18T01:15:00Z",
  "source": "perfume_pricing_system_v16",
  "total_products": 3,
  "products": [
    {
      "product_name": "عطر ديور سوفاج او دي بارفان 100 مل",
      "price": 380.00,
      "brand": "Dior",
      "size": "100ml",
      "type": "retail",
      "competitor_name": "عطور الرياض",
      "competitor_price": 390.00,
      "confidence": 92,
      "profitability": "عالية",
      "description": "عطر رجالي فاخر من ديور",
      "category": "عطور رجالية",
      "image_url": "https://example.com/image.jpg"
    }
  ]
}
```

#### **جدول الحقول:**

| الحقل | النوع | مطلوب؟ | الوصف | مثال |
|-------|------|--------|-------|------|
| `event_type` | string | ✅ | نوع الحدث | `"new_products"` |
| `timestamp` | string | ✅ | وقت الإرسال | `"2026-02-18T01:15:00Z"` |
| `source` | string | ✅ | مصدر البيانات | `"perfume_pricing_system_v16"` |
| `total_products` | integer | ✅ | عدد المنتجات | `3` |
| `products` | array | ✅ | قائمة المنتجات | `[...]` |
| `product_name` | string | ✅ | اسم المنتج | `"عطر ديور سوفاج..."` |
| `price` | float | ✅ | السعر المقترح | `380.00` |
| `brand` | string | ✅ | الماركة | `"Dior"` |
| `size` | string | ✅ | الحجم | `"100ml"` |
| `type` | string | ✅ | النوع | `"retail"` / `"tester"` / `"set"` |
| `competitor_name` | string | ⚠️ | اسم المنافس | `"عطور الرياض"` |
| `competitor_price` | float | ⚠️ | سعر المنافس | `390.00` |
| `confidence` | integer | ⚠️ | نسبة الثقة | `92` |
| `profitability` | string | ⚠️ | الربحية المتوقعة | `"عالية"` / `"متوسطة"` / `"منخفضة"` |
| `description` | string | ❌ | وصف المنتج | `"عطر رجالي فاخر..."` |
| `category` | string | ❌ | التصنيف | `"عطور رجالية"` |
| `image_url` | string | ❌ | رابط الصورة | `"https://..."` |

---

### **3. منتجات مفقودة (Missing Products)**

#### **البنية الأساسية:**
```json
{
  "event_type": "missing_products",
  "timestamp": "2026-02-18T01:15:00Z",
  "source": "perfume_pricing_system_v16",
  "total_products": 2,
  "products": [
    {
      "product_name": "عطر توم فورد بلاك اوركيد 100 مل",
      "competitor_name": "عطور جدة",
      "competitor_price": 520.00,
      "brand": "Tom Ford",
      "size": "100ml",
      "type": "retail",
      "recommendation": "إضافة فورية - طلب عالي",
      "profitability": "عالية جداً",
      "market_demand": "مرتفع",
      "competitors_count": 3,
      "avg_competitor_price": 530.00,
      "suggested_price": 510.00
    }
  ]
}
```

#### **جدول الحقول:**

| الحقل | النوع | مطلوب؟ | الوصف | مثال |
|-------|------|--------|-------|------|
| `event_type` | string | ✅ | نوع الحدث | `"missing_products"` |
| `product_name` | string | ✅ | اسم المنتج | `"عطر توم فورد..."` |
| `competitor_name` | string | ✅ | اسم المنافس | `"عطور جدة"` |
| `competitor_price` | float | ✅ | سعر المنافس | `520.00` |
| `brand` | string | ✅ | الماركة | `"Tom Ford"` |
| `size` | string | ✅ | الحجم | `"100ml"` |
| `type` | string | ✅ | النوع | `"retail"` |
| `recommendation` | string | ⚠️ | توصية AI | `"إضافة فورية..."` |
| `profitability` | string | ⚠️ | الربحية | `"عالية جداً"` |
| `market_demand` | string | ⚠️ | الطلب في السوق | `"مرتفع"` |
| `competitors_count` | integer | ⚠️ | عدد المنافسين | `3` |
| `avg_competitor_price` | float | ⚠️ | متوسط سعر المنافسين | `530.00` |
| `suggested_price` | float | ⚠️ | السعر المقترح | `510.00` |

---

## 🔧 **سيناريوهات Make.com**

### **السيناريو 1: تحديث الأسعار**

```
┌─────────────────┐
│  Webhook        │
│  (Receive Data) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Iterator       │
│  (Loop Products)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Salla: Search  │
│  Product by Name│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Salla: Update  │
│  Product Price  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Log to Google  │
│  Sheets         │
└─────────────────┘
```

#### **الخطوات التفصيلية:**

1. **Webhook Module:**
   - استقبال البيانات من Streamlit
   - التحقق من صحة JSON
   - استخراج `products` array

2. **Iterator Module:**
   - تكرار على كل منتج في `products`
   - تمرير كل منتج للخطوة التالية

3. **Salla Search Module:**
   - البحث عن المنتج في سلة باستخدام `product_name`
   - الحصول على `product_id`

4. **Salla Update Module:**
   - تحديث السعر باستخدام `product_id`
   - تحديث `new_price`

5. **Google Sheets Log:**
   - تسجيل العملية (نجحت/فشلت)
   - حفظ التفاصيل (التاريخ، المنتج، السعر القديم، الجديد)

---

### **السيناريو 2: إضافة منتجات جديدة**

```
┌─────────────────┐
│  Webhook        │
│  (Receive Data) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Iterator       │
│  (Loop Products)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Salla: Check   │
│  Product Exists │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Router         │
│  (If Not Exists)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Salla: Create  │
│  New Product    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Log to Google  │
│  Sheets         │
└─────────────────┘
```

---

## 💻 **أمثلة عملية**

### **مثال 1: إرسال تحديث أسعار من Streamlit**

```python
import requests
import json
from datetime import datetime

def send_price_updates(selected_products, webhook_url):
    """
    إرسال منتجات محددة لتحديث أسعارها عبر Make.com
    
    Args:
        selected_products: list of dict - قائمة المنتجات المحددة
        webhook_url: str - رابط webhook في Make.com
    
    Returns:
        dict - نتيجة الإرسال
    """
    
    # بناء البيانات
    payload = {
        "event_type": "price_update",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "source": "perfume_pricing_system_v16",
        "total_products": len(selected_products),
        "products": []
    }
    
    # إضافة كل منتج
    for product in selected_products:
        product_data = {
            "product_name": str(product.get('المنتج', '')),
            "old_price": float(product.get('السعر', 0)),
            "new_price": float(product.get('السعر الموصى', product.get('السعر', 0))),
            "price_change": 0.0,  # سيتم حسابه
            "price_change_pct": 0.0,  # سيتم حسابه
            "competitor_name": str(product.get('المنافس', '')).replace('.xlsx', '').replace('.csv', ''),
            "competitor_price": float(product.get('سعر المنافس', product.get('أقل سعر منافس', 0))),
            "confidence": int(product.get('الثقة %', 0)),
            "risk_level": str(product.get('الخطورة', 'عادي')),
            "match_stage": str(product.get('مرحلة المطابقة', 'unknown')),
            "reason": ""  # سيتم إضافته
        }
        
        # حساب الفرق
        price_change = product_data['new_price'] - product_data['old_price']
        product_data['price_change'] = round(price_change, 2)
        
        if product_data['old_price'] > 0:
            price_change_pct = (price_change / product_data['old_price']) * 100
            product_data['price_change_pct'] = round(price_change_pct, 2)
        
        # إضافة السبب
        if price_change < 0:
            product_data['reason'] = f"خفض السعر بـ {abs(price_change_pct):.1f}% ليكون أقرب للمنافس"
        elif price_change > 0:
            product_data['reason'] = f"رفع السعر بـ {price_change_pct:.1f}% لزيادة الربحية"
        else:
            product_data['reason'] = "السعر مناسب - لا تغيير"
        
        payload['products'].append(product_data)
    
    # الإرسال
    try:
        response = requests.post(
            webhook_url,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            return {
                "success": True,
                "message": f"تم إرسال {len(selected_products)} منتج بنجاح",
                "response": response.json() if response.text else {}
            }
        else:
            return {
                "success": False,
                "message": f"فشل الإرسال: {response.status_code}",
                "error": response.text
            }
    
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "message": "انتهت مهلة الاتصال (Timeout)",
            "error": "Request timeout after 30 seconds"
        }
    
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "message": f"خطأ في الاتصال: {str(e)}",
            "error": str(e)
        }
    
    except Exception as e:
        return {
            "success": False,
            "message": f"خطأ غير متوقع: {str(e)}",
            "error": str(e)
        }
```

---

### **مثال 2: إرسال منتجات جديدة**

```python
def send_new_products(selected_products, webhook_url):
    """
    إرسال منتجات جديدة للإضافة عبر Make.com
    """
    
    payload = {
        "event_type": "new_products",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "source": "perfume_pricing_system_v16",
        "total_products": len(selected_products),
        "products": []
    }
    
    for product in selected_products:
        # استخراج المكونات
        from engine import extract_brand, extract_size, classify_product
        
        product_name = str(product.get('المنتج', ''))
        brand = extract_brand(product_name)
        size = extract_size(product_name)
        product_type = classify_product(product_name)
        
        product_data = {
            "product_name": product_name,
            "price": float(product.get('سعر المنافس', product.get('أقل سعر منافس', 0))),
            "brand": brand if brand else "Unknown",
            "size": size if size else "Unknown",
            "type": product_type,
            "competitor_name": str(product.get('المنافس', '')).replace('.xlsx', '').replace('.csv', ''),
            "competitor_price": float(product.get('سعر المنافس', 0)),
            "confidence": int(product.get('الثقة %', 0)),
            "profitability": "عالية",  # يمكن حسابها بناءً على السعر
            "description": f"عطر {brand} {size}" if brand and size else product_name,
            "category": "عطور",
            "image_url": ""  # يمكن إضافة رابط صورة إذا متوفر
        }
        
        payload['products'].append(product_data)
    
    # الإرسال (نفس الطريقة السابقة)
    try:
        response = requests.post(webhook_url, json=payload, timeout=30)
        # ... معالجة النتيجة
    except Exception as e:
        # ... معالجة الأخطاء
        pass
```

---

### **مثال 3: استقبال البيانات في Make.com**

#### **في Make.com Webhook Module:**

```javascript
// الوصول للبيانات المُستقبلة
const eventType = data.event_type;
const timestamp = data.timestamp;
const products = data.products;
const totalProducts = data.total_products;

// تسجيل في Log
console.log(`Received ${totalProducts} products of type ${eventType}`);

// تمرير للخطوة التالية
return products;
```

#### **في Make.com Iterator:**

```javascript
// تكرار على كل منتج
for (const product of products) {
    // معالجة كل منتج
    console.log(`Processing: ${product.product_name}`);
    
    // تمرير للخطوة التالية (Salla API)
    yield product;
}
```

#### **في Make.com Salla Module:**

```javascript
// البحث عن المنتج
const searchResult = await salla.searchProduct({
    name: product.product_name
});

if (searchResult.found) {
    // تحديث السعر
    await salla.updateProduct({
        id: searchResult.product_id,
        price: product.new_price
    });
    
    return {
        success: true,
        product_id: searchResult.product_id,
        old_price: product.old_price,
        new_price: product.new_price
    };
} else {
    return {
        success: false,
        error: "Product not found in Salla"
    };
}
```

---

## ⚠️ **معالجة الأخطاء**

### **جدول الأخطاء الشائعة**

| الخطأ | السبب | الحل |
|-------|-------|------|
| **Timeout (408)** | Make.com لم يستجب خلال 30 ثانية | زيادة timeout أو تقليل عدد المنتجات |
| **Bad Request (400)** | JSON غير صحيح | التحقق من تنسيق البيانات |
| **Unauthorized (401)** | مفتاح API خاطئ | تحديث المفتاح في Make.com |
| **Not Found (404)** | Webhook URL خاطئ | التحقق من الرابط |
| **Internal Server Error (500)** | خطأ في Make.com | إعادة المحاولة لاحقاً |
| **Product Not Found** | المنتج غير موجود في سلة | إضافة المنتج يدوياً أولاً |

---

### **كود معالجة الأخطاء المحسن**

```python
def send_with_retry(payload, webhook_url, max_retries=3):
    """
    إرسال مع إعادة المحاولة عند الفشل
    """
    for attempt in range(max_retries):
        try:
            response = requests.post(
                webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            
            elif response.status_code == 408:  # Timeout
                if attempt < max_retries - 1:
                    time.sleep(5)  # انتظر 5 ثواني
                    continue
                else:
                    return {"success": False, "error": "Timeout after 3 retries"}
            
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
        
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                time.sleep(5)
                continue
            else:
                return {"success": False, "error": "Connection timeout"}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    return {"success": False, "error": "Max retries exceeded"}
```

---

## 📝 **ملاحظات مهمة**

1. **الحقول المطلوبة (✅):** يجب إرسالها دائماً
2. **الحقول الاختيارية (⚠️):** يُفضل إرسالها لتحسين الدقة
3. **الحقول الإضافية (❌):** اختيارية تماماً
4. **التوقيت:** استخدم UTC دائماً
5. **الترميز:** UTF-8 لدعم العربية
6. **الحجم:** لا تُرسل أكثر من 100 منتج في مرة واحدة
7. **Timeout:** 30 ثانية كافية لمعظم الحالات

---

## 🔗 **روابط مفيدة**

- **Make.com Docs:** https://www.make.com/en/help/webhooks
- **Salla API Docs:** https://docs.salla.dev/
- **JSON Validator:** https://jsonlint.com/

---

**آخر تحديث:** 18 فبراير 2026 - 03:15 صباحاً  
**الإصدار:** v16.0  
**الحالة:** مُفعّل ويعمل ✅
