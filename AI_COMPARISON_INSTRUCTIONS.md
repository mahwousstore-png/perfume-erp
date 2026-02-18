# 🤖 تعليمات الذكاء الاصطناعي - طريقة المقارنة المتقدمة للعطور

**التاريخ:** 18 فبراير 2026  
**الإصدار:** v16.0  
**الغرض:** دليل شامل للذكاء الاصطناعي لاتباع نفس منهجية المقارنة المتقدمة

---

## 🎯 **الهدف الرئيسي**

أنت نظام ذكاء اصطناعي متخصص في **مقارنة ومطابقة أسماء العطور** بين متجر وقائمة منافسين. مهمتك هي:

1. ✅ تحديد ما إذا كان منتجان **نفس المنتج** أم لا
2. ✅ حساب **نسبة الثقة** (0-100%)
3. ✅ تقييم **مستوى الخطورة** (حرج/متوسط/عادي)
4. ✅ تقديم **توصية تسعير** ذكية
5. ✅ شرح **السبب** وراء كل قرار

---

## 📋 **خوارزمية المقارنة المتقدمة (4 مراحل)**

### **المرحلة 1: Fast Match (⚡ مطابقة سريعة)**

#### **الهدف:**
مطابقة مباشرة بعد تنظيف الأسماء (أسرع طريقة، دقة 100%)

#### **الخطوات:**

```python
def fast_match(product1, product2):
    """
    المرحلة الأولى: مطابقة سريعة بعد التنظيف
    """
    # 1. تنظيف الاسمين
    clean1 = clean_product_name(product1)
    clean2 = clean_product_name(product2)
    
    # 2. مقارنة مباشرة
    if clean1 == clean2:
        return {
            "match": True,
            "confidence": 100,
            "stage": "fast",
            "reason": "تطابق تام بعد التنظيف"
        }
    
    return None  # لم يتطابق، انتقل للمرحلة التالية
```

#### **دالة التنظيف:**

```python
def clean_product_name(name):
    """
    تنظيف اسم المنتج من الكلمات الزائدة والأحرف الخاصة
    """
    import re
    
    # 1. تحويل للأحرف الصغيرة
    name = name.lower()
    
    # 2. إزالة الكلمات الشائعة (stopwords)
    stopwords = [
        'عطر', 'perfume', 'fragrance', 'scent',
        'او دي بارفان', 'eau de parfum', 'edp',
        'او دي تواليت', 'eau de toilette', 'edt',
        'بارفان', 'parfum',
        'للرجال', 'للنساء', 'for men', 'for women',
        'unisex', 'للجنسين',
        'original', 'اصلي', 'authentic'
    ]
    
    for word in stopwords:
        name = name.replace(word, ' ')
    
    # 3. إزالة الأحرف الخاصة والأرقام (ما عدا الحجم)
    name = re.sub(r'[^\w\s\d]', ' ', name)
    
    # 4. توحيد المسافات
    name = ' '.join(name.split())
    
    # 5. إزالة المسافات من البداية والنهاية
    name = name.strip()
    
    return name
```

#### **مثال:**

```
المدخل 1: "عطر شانيل نمبر 5 او دي بارفان للنساء 100 مل"
المدخل 2: "Chanel No 5 EDP for Women 100ml"

بعد التنظيف:
النتيجة 1: "شانيل نمبر 5 100 مل"
النتيجة 2: "chanel no 5 100ml"

بعد الترجمة:
النتيجة 1: "chanel no 5 100ml"
النتيجة 2: "chanel no 5 100ml"

✅ تطابق تام → confidence = 100%
```

---

### **المرحلة 2: Medium Match (🔍 مطابقة متوسطة)**

#### **الهدف:**
استخدام FuzzyWuzzy لمقارنة النصوص (دقة 85-99%)

#### **الخوارزميات الثلاث:**

```python
from fuzzywuzzy import fuzz

def medium_match(product1, product2):
    """
    المرحلة الثانية: مطابقة باستخدام FuzzyWuzzy
    """
    # 1. حساب 3 نسب تطابق
    scores = {
        'token_sort': fuzz.token_sort_ratio(product1, product2),
        'token_set': fuzz.token_set_ratio(product1, product2),
        'partial': fuzz.partial_ratio(product1, product2)
    }
    
    # 2. أخذ أعلى نسبة
    best_score = max(scores.values())
    best_method = max(scores, key=scores.get)
    
    # 3. إذا كانت النسبة >= 85%، اعتبره تطابق
    if best_score >= 85:
        return {
            "match": True,
            "confidence": best_score,
            "stage": "medium",
            "method": best_method,
            "reason": f"تطابق {best_score}% باستخدام {best_method}"
        }
    
    return None  # لم يتطابق، انتقل للمرحلة التالية
```

#### **الفرق بين الخوارزميات:**

| الخوارزمية | الوصف | مثالي لـ | مثال |
|-----------|-------|---------|------|
| **token_sort_ratio** | يرتب الكلمات أبجدياً ثم يقارن | الأسماء المعكوسة | "شانيل 5" vs "5 شانيل" |
| **token_set_ratio** | يتجاهل الكلمات المكررة | الأسماء الطويلة | "عطر شانيل عطر 5" vs "شانيل 5" |
| **partial_ratio** | يبحث عن أفضل تطابق جزئي | الأسماء المختصرة | "شانيل 5 100مل" vs "شانيل 5" |

#### **أمثلة:**

```python
# مثال 1: token_sort_ratio
product1 = "شانيل نمبر 5 100 مل"
product2 = "100 مل نمبر 5 شانيل"
score = fuzz.token_sort_ratio(product1, product2)
# النتيجة: 100% (لأنه يرتب الكلمات أولاً)

# مثال 2: token_set_ratio
product1 = "عطر شانيل عطر نمبر 5 عطر 100 مل"
product2 = "شانيل نمبر 5 100 مل"
score = fuzz.token_set_ratio(product1, product2)
# النتيجة: 100% (لأنه يتجاهل التكرار)

# مثال 3: partial_ratio
product1 = "شانيل نمبر 5 او دي بارفان للنساء 100 مل اصلي"
product2 = "شانيل نمبر 5 100 مل"
score = fuzz.partial_ratio(product1, product2)
# النتيجة: 100% (لأنه يبحث عن أفضل تطابق جزئي)
```

---

### **المرحلة 3: Deep Match (🔬 مطابقة عميقة)**

#### **الهدف:**
استخراج المكونات الأساسية (ماركة + حجم + نوع) ومقارنتها (دقة 75-95%)

#### **الخطوات:**

```python
def deep_match(product1, product2):
    """
    المرحلة الثالثة: مطابقة بناءً على المكونات الأساسية
    """
    # 1. استخراج المكونات
    brand1, size1, type1 = extract_components(product1)
    brand2, size2, type2 = extract_components(product2)
    
    # 2. مقارنة الماركة
    brand_match = (brand1 == brand2)
    
    # 3. مقارنة الحجم (مع تسامح ±30ml)
    size_match = False
    if size1 and size2:
        size_diff = abs(size1 - size2)
        size_match = (size_diff <= 30)
    
    # 4. مقارنة النوع (تستر = ريتيل في المطابقة)
    type_match = (type1 == type2) or \
                 (type1 == 'tester' and type2 == 'retail') or \
                 (type1 == 'retail' and type2 == 'tester')
    
    # 5. حساب الثقة
    if brand_match and size_match and type_match:
        confidence = calculate_confidence(
            brand_match=True,
            size_match=True,
            type_match=True,
            size_diff=size_diff
        )
        
        return {
            "match": True,
            "confidence": confidence,
            "stage": "deep",
            "components": {
                "brand": brand1,
                "size": size1,
                "type": type1
            },
            "reason": f"تطابق المكونات: {brand1} {size1}ml {type1}"
        }
    
    return None  # لم يتطابق، انتقل للمرحلة الأخيرة
```

#### **دالة استخراج المكونات:**

```python
def extract_components(product_name):
    """
    استخراج الماركة + الحجم + النوع من اسم المنتج
    """
    brand = extract_brand(product_name)
    size = extract_size(product_name)
    product_type = classify_product(product_name)
    
    return brand, size, product_type
```

#### **دالة استخراج الماركة:**

```python
def extract_brand(name):
    """
    استخراج الماركة من قاموس 77 ماركة
    """
    BRANDS = {
        'chanel': ['chanel', 'شانيل', 'شنل'],
        'dior': ['dior', 'ديور', 'ديوار'],
        'gucci': ['gucci', 'غوتشي', 'قوتشي'],
        'versace': ['versace', 'فيرساتشي', 'فرزاتشي'],
        'tom ford': ['tom ford', 'توم فورد', 'تومفورد'],
        'ysl': ['ysl', 'yves saint laurent', 'ايف سان لوران', 'سان لوران'],
        'armani': ['armani', 'ارماني', 'جورجيو ارماني'],
        'prada': ['prada', 'برادا', 'برادة'],
        'burberry': ['burberry', 'بربري', 'بيربري'],
        'givenchy': ['givenchy', 'جيفنشي', 'جفنشي'],
        # ... (77 ماركة إجمالاً)
    }
    
    name_lower = name.lower()
    
    for brand, variants in BRANDS.items():
        for variant in variants:
            if variant in name_lower:
                return brand
    
    return None
```

#### **دالة استخراج الحجم:**

```python
import re

def extract_size(name):
    """
    استخراج الحجم بالـ ml من اسم المنتج
    """
    # البحث عن أنماط الحجم
    patterns = [
        r'(\d+)\s*ml',           # 100 ml
        r'(\d+)\s*مل',           # 100 مل
        r'(\d+)\s*ملي',          # 100 ملي
        r'(\d+)\s*milliliter',   # 100 milliliter
        r'(\d+\.?\d*)\s*oz'      # 3.4 oz (سيتم تحويله)
    ]
    
    for pattern in patterns:
        match = re.search(pattern, name.lower())
        if match:
            size = float(match.group(1))
            
            # تحويل oz إلى ml
            if 'oz' in pattern:
                size = size * 29.5735  # 1 oz = 29.5735 ml
            
            return int(size)
    
    return None
```

#### **دالة تصنيف النوع:**

```python
def classify_product(name):
    """
    تصنيف المنتج: retail / tester / set / hair_mist / body_mist / rejected
    """
    name_lower = name.lower()
    
    # تستر
    if any(word in name_lower for word in ['tester', 'تستر', 'test']):
        return 'tester'
    
    # سيت/مجموعة
    if any(word in name_lower for word in ['set', 'سيت', 'مجموعة', 'gift', 'هدية']):
        return 'set'
    
    # هير مست
    if any(word in name_lower for word in ['hair', 'شعر', 'هير']):
        return 'hair_mist'
    
    # بودي مست
    if any(word in name_lower for word in ['body', 'بودي', 'جسم', 'mist']):
        return 'body_mist'
    
    # مرفوض (عينات، مينياتشر، إلخ)
    if any(word in name_lower for word in ['sample', 'عينة', 'miniature', 'مينياتشر', 'travel size']):
        return 'rejected'
    
    # ريتيل (افتراضي)
    return 'retail'
```

#### **دالة حساب الثقة:**

```python
def calculate_confidence(brand_match, size_match, type_match, size_diff=0):
    """
    حساب نسبة الثقة بناءً على المكونات
    """
    confidence = 0
    
    # الماركة (50% من الثقة)
    if brand_match:
        confidence += 50
    
    # الحجم (30% من الثقة)
    if size_match:
        if size_diff == 0:
            confidence += 30  # تطابق تام
        elif size_diff <= 10:
            confidence += 25  # تسامح صغير
        elif size_diff <= 30:
            confidence += 20  # تسامح متوسط
    
    # النوع (20% من الثقة)
    if type_match:
        confidence += 20
    
    return min(confidence, 100)
```

#### **أمثلة:**

```python
# مثال 1: تطابق كامل
product1 = "عطر شانيل نمبر 5 او دي بارفان 100 مل"
product2 = "Chanel No 5 EDP 100ml"

brand1, size1, type1 = extract_components(product1)
# النتيجة: ('chanel', 100, 'retail')

brand2, size2, type2 = extract_components(product2)
# النتيجة: ('chanel', 100, 'retail')

# المقارنة:
# brand_match = True (chanel == chanel)
# size_match = True (100 == 100)
# type_match = True (retail == retail)
# confidence = 50 + 30 + 20 = 100%

# مثال 2: تسامح في الحجم
product1 = "ديور سوفاج 100 مل"
product2 = "Dior Sauvage 120ml"

# المقارنة:
# brand_match = True (dior == dior)
# size_match = True (|100-120| = 20 <= 30)
# type_match = True (retail == retail)
# confidence = 50 + 25 + 20 = 95%

# مثال 3: تستر vs ريتيل
product1 = "توم فورد بلاك اوركيد 100 مل تستر"
product2 = "Tom Ford Black Orchid 100ml"

# المقارنة:
# brand_match = True (tom ford == tom ford)
# size_match = True (100 == 100)
# type_match = True (tester == retail مسموح)
# confidence = 50 + 30 + 20 = 100%
```

---

### **المرحلة 4: AI Match (🤖 ذكاء اصطناعي)**

#### **الهدف:**
استخدام Gemini 2.0 Flash للحالات المعقدة (دقة 70-90%)

#### **متى تستخدم AI Match؟**

- ❌ المراحل الثلاث السابقة فشلت
- ❌ الاسمان مختلفان جداً ظاهرياً
- ❌ يوجد اختصارات أو أسماء بديلة
- ❌ يوجد أخطاء إملائية

#### **Prompt المُستخدم:**

```python
def ai_match(product1, product2):
    """
    المرحلة الرابعة: مطابقة باستخدام الذكاء الاصطناعي
    """
    import google.generativeai as genai
    
    prompt = f"""
أنت خبير في مقارنة أسماء العطور. قارن هذين المنتجين وحدد ما إذا كانا نفس المنتج:

**المنتج 1:** {product1}
**المنتج 2:** {product2}

**تعليمات المقارنة:**
1. قارن الماركة (Brand)
2. قارن الحجم (Size) - تسامح ±30ml
3. قارن النوع (Type) - تستر = ريتيل في المطابقة
4. تجاهل الاختلافات الطفيفة في الكتابة
5. تجاهل الكلمات الزائدة (عطر، او دي بارفان، إلخ)

**أجب بالتنسيق التالي فقط:**
```json
{{
  "match": true/false,
  "confidence": 0-100,
  "reason": "سبب واضح ومختصر",
  "components": {{
    "brand_match": true/false,
    "size_match": true/false,
    "type_match": true/false
  }}
}}
```

**لا تضف أي نص خارج JSON.**
"""
    
    try:
        # استدعاء Gemini API
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        response = model.generate_content(prompt)
        
        # استخراج JSON من الرد
        import json
        result = json.loads(response.text)
        
        if result['match'] and result['confidence'] >= 75:
            return {
                "match": True,
                "confidence": result['confidence'],
                "stage": "ai",
                "reason": result['reason'],
                "components": result['components']
            }
    
    except Exception as e:
        print(f"AI Match Error: {e}")
    
    return None  # لم يتطابق
```

#### **أمثلة:**

```python
# مثال 1: اختصارات
product1 = "YSL La Nuit De L'Homme 100ml"
product2 = "ايف سان لوران لا نوي دو لوم 100 مل"

# AI يفهم أن:
# YSL = Yves Saint Laurent = ايف سان لوران
# La Nuit De L'Homme = لا نوي دو لوم
# النتيجة: match=True, confidence=90%

# مثال 2: أخطاء إملائية
product1 = "Versaci Eros 100ml"  # خطأ: Versaci بدلاً من Versace
product2 = "فيرساتشي ايروس 100 مل"

# AI يفهم أن Versaci = Versace (خطأ إملائي)
# النتيجة: match=True, confidence=85%

# مثال 3: أسماء بديلة
product1 = "Armani Code 75ml"
product2 = "جورجيو ارماني كود 75 مل"

# AI يفهم أن Armani = Giorgio Armani
# النتيجة: match=True, confidence=95%
```

---

## 🔄 **الخوارزمية الكاملة (Pipeline)**

```python
def compare_products(product1, product2):
    """
    الخوارزمية الكاملة: 4 مراحل متتالية
    """
    # المرحلة 1: Fast Match
    result = fast_match(product1, product2)
    if result:
        return result
    
    # المرحلة 2: Medium Match
    result = medium_match(product1, product2)
    if result:
        return result
    
    # المرحلة 3: Deep Match
    result = deep_match(product1, product2)
    if result:
        return result
    
    # المرحلة 4: AI Match
    result = ai_match(product1, product2)
    if result:
        return result
    
    # لم يتطابق في أي مرحلة
    return {
        "match": False,
        "confidence": 0,
        "stage": "none",
        "reason": "لا يوجد تطابق"
    }
```

---

## ⚠️ **نظام تقييم الخطورة (Risk Assessment)**

### **الهدف:**
تحديد مدى خطورة فرق السعر بين المتجر والمنافس

### **الخوارزمية:**

```python
def assess_risk(our_price, competitor_price, confidence):
    """
    تقييم الخطورة بناءً على فرق السعر ونسبة الثقة
    """
    # حساب الفرق بالنسبة المئوية
    diff_pct = ((our_price - competitor_price) / competitor_price) * 100
    
    # حرج (🔴)
    if diff_pct > 20 and confidence >= 85:
        return {
            "level": "حرج",
            "color": "red",
            "icon": "🔴",
            "action": "خفض السعر فوراً"
        }
    
    # متوسط (🟡)
    elif diff_pct > 10 and confidence >= 75:
        return {
            "level": "متوسط",
            "color": "yellow",
            "icon": "🟡",
            "action": "مراجعة السعر"
        }
    
    # عادي (🟢)
    else:
        return {
            "level": "عادي",
            "color": "green",
            "icon": "🟢",
            "action": "السعر مناسب"
        }
```

### **أمثلة:**

```python
# مثال 1: حرج
our_price = 500
competitor_price = 400
confidence = 95
risk = assess_risk(our_price, competitor_price, confidence)
# النتيجة: diff_pct = 25% → حرج 🔴

# مثال 2: متوسط
our_price = 450
competitor_price = 400
confidence = 80
risk = assess_risk(our_price, competitor_price, confidence)
# النتيجة: diff_pct = 12.5% → متوسط 🟡

# مثال 3: عادي
our_price = 420
competitor_price = 400
confidence = 90
risk = assess_risk(our_price, competitor_price, confidence)
# النتيجة: diff_pct = 5% → عادي 🟢
```

---

## 💡 **نظام التوصيات الذكية (Smart Recommendations)**

### **الهدف:**
تقديم توصية تسعير ذكية بناءً على:
- فرق السعر
- نسبة الثقة
- مستوى الخطورة
- نوع القسم (رفع/خفض/موافق/مفقود)

### **الخوارزمية:**

```python
def generate_recommendation(section, our_price, competitor_price, confidence, risk_level):
    """
    توليد توصية ذكية بناءً على القسم والبيانات
    """
    diff = our_price - competitor_price
    diff_pct = (diff / competitor_price) * 100
    
    # قسم رفع سعر
    if section == "رفع سعر":
        if risk_level == "حرج":
            return {
                "action": "خفض السعر فوراً",
                "new_price": competitor_price + 10,  # أعلى بـ 10 ريال
                "reason": f"سعرنا أعلى بـ {diff_pct:.1f}% ({diff:.0f} ريال) - خطر فقدان العملاء",
                "urgency": "عالية"
            }
        elif risk_level == "متوسط":
            return {
                "action": "خفض السعر تدريجياً",
                "new_price": (our_price + competitor_price) / 2,  # متوسط السعرين
                "reason": f"سعرنا أعلى بـ {diff_pct:.1f}% - يُفضل التقارب",
                "urgency": "متوسطة"
            }
    
    # قسم خفض سعر
    elif section == "خفض سعر":
        if confidence >= 90:
            return {
                "action": "رفع السعر لزيادة الربحية",
                "new_price": competitor_price - 10,  # أقل بـ 10 ريال فقط
                "reason": f"سعرنا أقل بـ {abs(diff_pct):.1f}% - يمكن زيادة الربح",
                "urgency": "متوسطة"
            }
    
    # قسم موافق عليها
    elif section == "موافق عليها":
        return {
            "action": "الحفاظ على السعر الحالي",
            "new_price": our_price,
            "reason": f"السعر مناسب (فرق {abs(diff_pct):.1f}% فقط)",
            "urgency": "منخفضة"
        }
    
    # قسم منتجات مفقودة
    elif section == "منتجات مفقودة":
        # حساب الربحية المتوقعة
        suggested_price = competitor_price * 0.95  # أقل بـ 5%
        profit_margin = (suggested_price - competitor_price * 0.6) / suggested_price * 100
        
        return {
            "action": "إضافة المنتج فوراً",
            "new_price": suggested_price,
            "reason": f"منتج مطلوب - ربحية متوقعة {profit_margin:.1f}%",
            "urgency": "عالية"
        }
    
    return {
        "action": "مراجعة يدوية",
        "new_price": our_price,
        "reason": "بيانات غير كافية",
        "urgency": "منخفضة"
    }
```

---

## 📝 **قواعد مهمة يجب اتباعها**

### **1. الدقة أولاً**
- ✅ لا تتسرع في المطابقة
- ✅ استخدم كل المراحل بالترتيب
- ✅ لا تتجاوز مرحلة إلا إذا فشلت

### **2. التسامح المحدود**
- ✅ الحجم: ±30ml فقط
- ✅ السعر: لا تسامح (استخدم الرقم الدقيق)
- ✅ الماركة: يجب أن تتطابق تماماً

### **3. تستر = ريتيل**
- ✅ في المطابقة: تستر يساوي ريتيل
- ✅ في السعر: تستر عادة أرخص بـ 10-20%
- ✅ في التوصية: اذكر الفرق

### **4. الثقة الصادقة**
- ✅ لا تبالغ في نسبة الثقة
- ✅ إذا كنت غير متأكد، قل ذلك
- ✅ اشرح سبب الثقة المنخفضة

### **5. التوصيات الواقعية**
- ✅ لا تقترح أسعار غير منطقية
- ✅ ضع في الاعتبار الربحية
- ✅ اشرح سبب التوصية

---

## 🎯 **أمثلة شاملة**

### **مثال 1: حالة بسيطة (Fast Match)**

```
المدخل:
product1 = "عطر شانيل نمبر 5 او دي بارفان 100 مل"
product2 = "Chanel No 5 EDP 100ml"
our_price = 450
competitor_price = 420

الخطوات:
1. fast_match() → تطابق تام بعد التنظيف
2. confidence = 100%
3. risk = متوسط (فرق 7.1%)
4. recommendation = "خفض السعر إلى 430 ريال"

النتيجة:
{
  "match": true,
  "confidence": 100,
  "stage": "fast",
  "risk": "متوسط",
  "recommendation": {
    "action": "خفض السعر تدريجياً",
    "new_price": 430,
    "reason": "سعرنا أعلى بـ 7.1% - يُفضل التقارب"
  }
}
```

---

### **مثال 2: حالة متوسطة (Medium Match)**

```
المدخل:
product1 = "ديور سوفاج او دي تواليت 100 مل للرجال"
product2 = "Dior Sauvage EDT Men 100ml"
our_price = 380
competitor_price = 390

الخطوات:
1. fast_match() → فشل (اختلاف طفيف)
2. medium_match() → token_sort_ratio = 92%
3. confidence = 92%
4. risk = عادي (فرق -2.6%)
5. recommendation = "رفع السعر إلى 385 ريال"

النتيجة:
{
  "match": true,
  "confidence": 92,
  "stage": "medium",
  "method": "token_sort",
  "risk": "عادي",
  "recommendation": {
    "action": "رفع السعر لزيادة الربحية",
    "new_price": 385,
    "reason": "سعرنا أقل بـ 2.6% - يمكن زيادة الربح"
  }
}
```

---

### **مثال 3: حالة معقدة (Deep Match)**

```
المدخل:
product1 = "توم فورد بلاك اوركيد 100 مل تستر"
product2 = "Tom Ford Black Orchid EDP 100ml"
our_price = 480
competitor_price = 520

الخطوات:
1. fast_match() → فشل
2. medium_match() → 78% (أقل من 85%)
3. deep_match() → نجح!
   - brand: tom ford == tom ford ✅
   - size: 100 == 100 ✅
   - type: tester == retail ✅ (مسموح)
4. confidence = 95%
5. risk = عادي (سعرنا أقل)
6. recommendation = "رفع السعر إلى 510 ريال"

النتيجة:
{
  "match": true,
  "confidence": 95,
  "stage": "deep",
  "components": {
    "brand": "tom ford",
    "size": 100,
    "type": "tester"
  },
  "risk": "عادي",
  "recommendation": {
    "action": "رفع السعر (تستر عادة أرخص)",
    "new_price": 510,
    "reason": "سعرنا أقل بـ 7.7% - يمكن زيادة الربح (تستر vs ريتيل)"
  }
}
```

---

### **مثال 4: حالة AI (AI Match)**

```
المدخل:
product1 = "YSL La Nuit De L'Homme 100ml"
product2 = "ايف سان لوران لا نوي دو لوم 100 مل"
our_price = 420
competitor_price = 400

الخطوات:
1. fast_match() → فشل (اختلاف كبير)
2. medium_match() → 65% (أقل من 85%)
3. deep_match() → فشل (لم يتعرف على YSL)
4. ai_match() → نجح!
   - AI فهم أن YSL = Yves Saint Laurent
   - AI فهم أن La Nuit = لا نوي
5. confidence = 88%
6. risk = عادي (فرق 5%)
7. recommendation = "خفض السعر إلى 410 ريال"

النتيجة:
{
  "match": true,
  "confidence": 88,
  "stage": "ai",
  "reason": "AI تعرف على الاختصارات والترجمة",
  "risk": "عادي",
  "recommendation": {
    "action": "خفض السعر قليلاً",
    "new_price": 410,
    "reason": "سعرنا أعلى بـ 5% - يُفضل التقارب"
  }
}
```

---

## 🚫 **أخطاء شائعة يجب تجنبها**

### **1. المطابقة المتسرعة**
```python
# ❌ خطأ
if "شانيل" in product1 and "شانيل" in product2:
    return True  # خطأ! قد يكونا منتجين مختلفين

# ✅ صحيح
if extract_brand(product1) == extract_brand(product2) and \
   extract_size(product1) == extract_size(product2):
    return True
```

### **2. تجاهل النوع**
```python
# ❌ خطأ
# مطابقة "شانيل 5 100مل تستر" مع "شانيل 5 100مل سيت"
# هذا خطأ! تستر ≠ سيت

# ✅ صحيح
# تستر = ريتيل فقط (مسموح)
# تستر ≠ سيت / hair_mist / body_mist
```

### **3. ثقة مبالغ فيها**
```python
# ❌ خطأ
confidence = 100  # دائماً

# ✅ صحيح
confidence = calculate_confidence(...)  # بناءً على المكونات
```

### **4. توصيات غير واقعية**
```python
# ❌ خطأ
new_price = competitor_price  # نفس سعر المنافس تماماً

# ✅ صحيح
new_price = competitor_price + 10  # أعلى قليلاً للربحية
```

---

## 📊 **معايير الأداء**

### **الدقة المطلوبة:**
- ✅ Fast Match: 100% دقة
- ✅ Medium Match: 95%+ دقة
- ✅ Deep Match: 90%+ دقة
- ✅ AI Match: 85%+ دقة

### **السرعة المطلوبة:**
- ⚡ Fast Match: < 0.01 ثانية
- ⚡ Medium Match: < 0.1 ثانية
- ⚡ Deep Match: < 0.5 ثانية
- ⚡ AI Match: < 2 ثانية

### **نسبة الاستخدام:**
- 📊 Fast Match: 40% من الحالات
- 📊 Medium Match: 35% من الحالات
- 📊 Deep Match: 20% من الحالات
- 📊 AI Match: 5% من الحالات

---

## 🎓 **ملخص نهائي**

### **الخطوات الأساسية:**

1. ✅ **نظف الأسماء** (إزالة الكلمات الزائدة)
2. ✅ **طابق مباشرة** (Fast Match)
3. ✅ **استخدم FuzzyWuzzy** (Medium Match)
4. ✅ **استخرج المكونات** (Deep Match)
5. ✅ **استخدم AI** (AI Match)
6. ✅ **احسب الثقة** (0-100%)
7. ✅ **قيّم الخطورة** (حرج/متوسط/عادي)
8. ✅ **قدم توصية** (سعر جديد + سبب)

### **القواعد الذهبية:**

1. 🥇 **الدقة أولاً** - لا تتسرع
2. 🥈 **الشفافية ثانياً** - اشرح كل قرار
3. 🥉 **الواقعية ثالثاً** - توصيات منطقية

---

**آخر تحديث:** 18 فبراير 2026 - 03:30 صباحاً  
**الإصدار:** v16.0  
**الحالة:** جاهز للاستخدام ✅
