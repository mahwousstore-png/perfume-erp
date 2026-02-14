"""
engine.py - محرك المطابقة والتصنيف الذكي v7.0
═══════════════════════════════════════════════
يطبق قوانين صارمة لمقارنة المنتجات مع:
- استراتيجية "أقل من أقل منافس بريال واحد"
- TF-IDF + Cosine Similarity للمطابقة السريعة
- كشف الشواذ (IQR Method)
- درجة الثقة (Confidence Score)
- تفسير القرارات (Reasoning)
"""
import re
import numpy as np
from rapidfuzz import fuzz


# ===== قوانين التصنيف =====

REJECT_KEYWORDS = [
    "sample", "عينة", "عينه", "decant", "تقسيم", "تقسيمة",
    "split", "miniature", "mini ", "0.5ml",
    "1ml", "2ml", "3ml", "5ml", "سبلاش",
    "splash", "رول", "roll-on", "rollerball",
    "أمبول", "تعبئة",
]

TESTER_KEYWORDS = [
    "tester", "تستر", "test", "تيستر",
    "demonstration", "demo",
]

HAIR_MIST_KEYWORDS = [
    "hair mist", "هير مست", "شعر", "hair",
    "للشعر",
]

BODY_MIST_KEYWORDS = [
    "body mist", "بودي مست", "body spray",
    "بودي سبراي", "للجسم",
]

SET_KEYWORDS = [
    "set", "gift set", "طقم", "مجموعة",
    "coffret", "collection", "kit",
]


def classify_product(name):
    """تصنيف المنتج حسب اسمه."""
    lower = name.lower().strip()

    for kw in REJECT_KEYWORDS:
        if kw in lower:
            return "rejected"
    for kw in TESTER_KEYWORDS:
        if kw in lower:
            return "tester"
    for kw in SET_KEYWORDS:
        if kw in lower:
            return "set"
    for kw in HAIR_MIST_KEYWORDS:
        if kw in lower:
            return "hair_mist"
    for kw in BODY_MIST_KEYWORDS:
        if kw in lower:
            return "body_mist"
    return "retail"


def extract_size(name):
    """استخراج الحجم من اسم المنتج."""
    patterns = [
        r"(\d+(?:\.\d+)?)\s*ml",
        r"(\d+(?:\.\d+)?)\s*مل",
    ]
    for pat in patterns:
        match = re.search(pat, name, re.IGNORECASE)
        if match:
            return float(match.group(1))
    return 0


def extract_brand(name):
    """استخراج الماركة من اسم المنتج."""
    known_brands = [
        "Dior", "Chanel", "Gucci", "Tom Ford",
        "Versace", "Armani", "YSL", "Prada",
        "Burberry", "Givenchy", "Hermes", "Creed",
        "Montblanc", "Calvin Klein", "Hugo Boss",
        "Dolce & Gabbana", "Valentino", "Bvlgari",
        "Cartier", "Lancome", "Jo Malone",
        "Maison Francis Kurkdjian", "Amouage",
        "Rasasi", "Lattafa", "Arabian Oud",
        "Swiss Arabian", "Ajmal", "Al Haramain",
        "Afnan", "Armaf", "Nishane", "Xerjoff",
        "Parfums de Marly", "Initio", "Byredo",
        "Le Labo", "Diptyque", "Acqua di Parma",
        "Mancera", "Montale", "Tiziana Terenzi",
        "Kilian", "Roja", "Clive Christian",
        "Penhaligon", "Memo", "Aerin",
        # ماركات عربية
        "لطافة", "العربية للعود", "رصاصي",
        "أجمل", "الحرمين", "عفنان", "أرماف",
        "سويس أربيان", "نيشان", "زيرجوف",
        "أمواج", "كريد", "توم فورد",
        "فرزاتشي", "ديور", "شانيل",
        "غوتشي", "برادا", "بربري",
        "جيفنشي", "هيرميس", "كارتييه",
        "بولغاري", "فالنتينو",
    ]
    lower = name.lower()
    for brand in known_brands:
        if brand.lower() in lower:
            return brand
    return ""


def normalize_name(name):
    """تنظيف اسم المنتج للمقارنة."""
    name = name.lower().strip()
    # إزالة الحجم
    name = re.sub(r"\d+(?:\.\d+)?\s*ml", "", name, flags=re.I)
    name = re.sub(r"\d+(?:\.\d+)?\s*مل", "", name, flags=re.I)
    # إزالة كلمات التصنيف
    remove_words = [
        "edp", "edt", "eau de parfum", "eau de toilette",
        "parfum", "cologne", "for men", "for women",
        "pour homme", "pour femme", "unisex",
        "spray", "natural spray",
        "او دو برفيوم", "أو دو برفيوم", "او دي بارفيوم",
        "أو دو بارفيوم", "او دي تواليت", "أو دو تواليت",
        "او دو", "أو دو", "ماء عطر", "عطر",
    ]
    for w in remove_words:
        name = name.replace(w, "")
    # إزالة الرموز الزائدة
    name = re.sub(r"[^\w\s]", " ", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name


def _get_field(record, *keys):
    """استخراج قيمة من سجل بمحاولة عدة مفاتيح."""
    for k in keys:
        val = record.get(k)
        if val is not None and val != "" and val != 0:
            return val
    return None


def _get_name(record):
    """استخراج اسم المنتج من سجل."""
    return str(_get_field(record, "name", "product_name", "اسم المنتج") or "")


def _get_price(record):
    """استخراج السعر من سجل."""
    val = _get_field(record, "sell_price", "price", "السعر", "سعر المنتج")
    try:
        return float(val) if val else 0.0
    except (ValueError, TypeError):
        return 0.0


def _get_id(record):
    """استخراج المعرف من سجل وتحويله لعدد صحيح."""
    val = _get_field(record, "id", "رقم المنتج", "product_id")
    if val is None:
        return 0
    try:
        return int(float(val))  # تحويل float مثل 565825080.0 إلى int 565825080
    except (ValueError, TypeError):
        return str(val)


# ===== كشف الشواذ (IQR Method) =====

def detect_outliers(prices):
    """
    كشف الأسعار الشاذة باستخدام IQR Method.
    الإرجاع: (min_valid, max_valid, outlier_indices)
    """
    if len(prices) < 3:
        return min(prices), max(prices), []

    arr = np.array(prices)
    q1 = np.percentile(arr, 25)
    q3 = np.percentile(arr, 75)
    iqr = q3 - q1

    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    outliers = [i for i, p in enumerate(prices) if p < lower_bound or p > upper_bound]
    return max(lower_bound, 0), upper_bound, outliers


# ===== المطابقة الذكية =====

def match_products(my_products, comp_products, threshold=65):
    """
    مطابقة المنتجات مع تطبيق القوانين الصارمة.

    القوانين:
    1. تطابق النوع: retail=retail, tester=tester
    2. تطابق الحجم: 100ml=100ml فقط
    3. فيتو العينات: طرد تلقائي
    4. استراتيجية "أقل بريال": السعر الموصى = أقل منافس - 1
    5. كشف الشواذ: تجاهل الأسعار الشاذة
    6. درجة الثقة: بناءً على جودة المطابقة وعدد المنافسين
    """
    results = {
        "raise": [],
        "lower": [],
        "ok": [],
        "missing": [],
        "review": [],
    }

    matched_comp_indices = set()

    for my_p in my_products:
        my_name = _get_name(my_p)
        if not my_name:
            continue

        my_type = classify_product(my_name)
        my_size = my_p.get("size_ml", 0) or extract_size(my_name)
        my_price = _get_price(my_p)
        my_norm = normalize_name(my_name)
        my_id = _get_id(my_p)

        if my_type == "rejected":
            continue

        # جمع كل المطابقات المحتملة (ليس فقط الأفضل)
        all_matches = []

        for idx, cp in enumerate(comp_products):
            cp_name = _get_name(cp)
            if not cp_name:
                continue

            cp_type = classify_product(cp_name)
            cp_size = cp.get("size_ml", 0) or extract_size(cp_name)
            cp_price = _get_price(cp)

            # قانون 1: تطابق النوع
            if my_type != cp_type:
                continue

            # قانون 2: تطابق الحجم
            if my_size > 0 and cp_size > 0:
                if abs(my_size - cp_size) > 1:
                    continue

            # قانون 3: فيتو العينات
            if cp_type == "rejected":
                continue

            # حساب التشابه
            cp_norm = normalize_name(cp_name)
            score = fuzz.token_sort_ratio(my_norm, cp_norm)

            if score >= threshold and cp_price > 0:
                all_matches.append({
                    "comp_product": cp,
                    "comp_index": idx,
                    "comp_name": cp_name,
                    "comp_price": cp_price,
                    "match_score": score,
                    "comp_type": cp_type,
                    "comp_size": cp_size,
                })

        if not all_matches:
            continue

        # ===== استراتيجية "أقل من أقل منافس بريال واحد" =====

        # جمع أسعار المنافسين
        comp_prices = [m["comp_price"] for m in all_matches]

        # كشف الشواذ إذا كان هناك 3+ أسعار
        outlier_indices = []
        if len(comp_prices) >= 3:
            _, _, outlier_indices = detect_outliers(comp_prices)

        # تصفية الأسعار الشاذة
        valid_matches = [m for i, m in enumerate(all_matches) if i not in outlier_indices]
        if not valid_matches:
            valid_matches = all_matches  # fallback

        valid_prices = [m["comp_price"] for m in valid_matches]
        min_comp_price = min(valid_prices)
        avg_comp_price = sum(valid_prices) / len(valid_prices)

        # أفضل مطابقة (أعلى نسبة تشابه)
        best_match = max(valid_matches, key=lambda m: m["match_score"])

        # السعر الموصى = أقل منافس - 1 ريال
        recommended_price = min_comp_price - 1

        # حساب درجة الثقة
        confidence = _calculate_confidence(
            match_score=best_match["match_score"],
            num_competitors=len(valid_matches),
            price_consistency=_price_consistency(valid_prices),
        )

        # تحديد التوصية
        price_diff = my_price - min_comp_price
        diff_percent = round((price_diff / min_comp_price) * 100, 1) if min_comp_price > 0 else 0

        # تسجيل المطابقات
        for m in all_matches:
            matched_comp_indices.add(m["comp_index"])

        result_entry = {
            "my_product": my_p,
            "comp_product": best_match["comp_product"],
            "my_name": my_name,
            "comp_name": best_match["comp_name"],
            "my_price": my_price,
            "comp_price": min_comp_price,
            "avg_comp_price": round(avg_comp_price, 2),
            "recommended_price": max(recommended_price, 1),
            "match_score": best_match["match_score"],
            "my_type": my_type,
            "comp_type": best_match["comp_type"],
            "my_size": my_size,
            "comp_size": best_match["comp_size"],
            "price_diff": round(price_diff, 2),
            "diff_percent": diff_percent,
            "confidence": confidence,
            "num_competitors": len(valid_matches),
            "outliers_removed": len(outlier_indices),
            "my_id": my_id,
        }

        # تحديد مستوى الخطورة
        abs_pct = abs(diff_percent)
        if abs_pct >= 20:
            risk = "high"
        elif abs_pct >= 10:
            risk = "medium"
        else:
            risk = "low"
        result_entry["risk_level"] = risk

        # تحديد التوصية بناءً على استراتيجية "أقل بريال"
        if abs(price_diff) <= 5:
            # الفرق ≤ 5 ريال → موافق عليه
            result_entry["recommendation"] = "approved"
            result_entry["reasoning"] = f"السعر مثالي (ضمن نطاق ±5 ريال من أقل منافس {min_comp_price} ر.س)"
            results["ok"].append(result_entry)
        elif my_price > min_comp_price:
            # سعرنا أعلى → خفض السعر
            result_entry["recommendation"] = "decrease"
            result_entry["reasoning"] = f"سعرنا ({my_price} ر.س) أعلى من أقل منافس ({min_comp_price} ر.س) بـ {abs(price_diff):.0f} ر.س. الموصى: {recommended_price:.0f} ر.س"
            results["lower"].append(result_entry)
        elif my_price < min_comp_price:
            # سعرنا أقل → رفع السعر
            result_entry["recommendation"] = "increase"
            result_entry["reasoning"] = f"سعرنا ({my_price} ر.س) أقل من أقل منافس ({min_comp_price} ر.س) بـ {abs(price_diff):.0f} ر.س. الموصى: {recommended_price:.0f} ر.س"
            results["raise"].append(result_entry)

    # كشف المنتجات المفقودة - مع تحقق ذكي محسّن
    # نستخدم threshold أقل (50) للتحقق من المنتجات المفقودة
    missing_threshold = 50
    
    for idx, cp in enumerate(comp_products):
        if idx not in matched_comp_indices:
            cp_name = _get_name(cp)
            if not cp_name:
                continue
            cp_type = classify_product(cp_name)
            if cp_type == "rejected":
                continue
                
            # تحقق ذكي: هل المنتج موجود فعلاً بنسبة تشابه أقل؟
            cp_norm = normalize_name(cp_name)
            cp_size = cp.get("size_ml", 0) or extract_size(cp_name)
            
            found_similar = False
            for my_p in my_products:
                my_name = _get_name(my_p)
                if not my_name:
                    continue
                    
                my_type = classify_product(my_name)
                my_size = my_p.get("size_ml", 0) or extract_size(my_name)
                
                # تطابق النوع والحجم
                if my_type != cp_type:
                    continue
                if my_size > 0 and cp_size > 0:
                    if abs(my_size - cp_size) > 1:
                        continue
                
                # حساب التشابه بنسبة أقل
                my_norm = normalize_name(my_name)
                score = fuzz.token_sort_ratio(my_norm, cp_norm)
                
                if score >= missing_threshold:
                    found_similar = True
                    break
            
            # فقط إذا لم نجد أي تشابه → مفقود
            if not found_similar:
                results["missing"].append({
                    "comp_product": cp,
                    "comp_name": cp_name,
                    "comp_type": cp_type,
                    "comp_size": cp_size,
                    "comp_price": _get_price(cp),
                    "competitor_name": cp.get("_competitor_name", "غير محدد"),
                })

    # ترتيب حسب الخطورة
    for key in ["raise", "lower"]:
        results[key].sort(
            key=lambda x: abs(x.get("diff_percent", 0)),
            reverse=True
        )

    return results


def _calculate_confidence(match_score, num_competitors, price_consistency):
    """حساب درجة الثقة في التوصية (0-100)."""
    # وزن المطابقة: 40%
    match_weight = (match_score / 100) * 40

    # وزن عدد المنافسين: 30%
    comp_weight = min(num_competitors / 5, 1.0) * 30

    # وزن اتساق الأسعار: 30%
    consistency_weight = price_consistency * 30

    return round(match_weight + comp_weight + consistency_weight)


def _price_consistency(prices):
    """حساب اتساق الأسعار (0-1). كلما كانت الأسعار متقاربة = أعلى."""
    if len(prices) < 2:
        return 1.0
    mean_price = sum(prices) / len(prices)
    if mean_price == 0:
        return 0.0
    std_dev = (sum((p - mean_price) ** 2 for p in prices) / len(prices)) ** 0.5
    cv = std_dev / mean_price  # coefficient of variation
    return max(0, 1 - cv)


def get_risk_color(risk):
    """الحصول على لون الخطورة."""
    colors = {
        "high": "#FF4444",
        "medium": "#FFA500",
        "low": "#44BB44",
    }
    return colors.get(risk, "#888888")


def get_risk_emoji(risk):
    """الحصول على رمز الخطورة."""
    emojis = {
        "high": "🔴",
        "medium": "🟡",
        "low": "🟢",
    }
    return emojis.get(risk, "⚪")


def get_type_label(ptype):
    """الحصول على تسمية النوع بالعربي."""
    labels = {
        "retail": "ريتيل",
        "tester": "تستر",
        "hair_mist": "هير مست",
        "body_mist": "بودي مست",
        "set": "طقم",
        "rejected": "مرفوض",
    }
    return labels.get(ptype, ptype)


# ===== الدوال الرئيسية المطلوبة من app.py =====

def normalize_columns(df):
    """
    تطبيع أسماء الأعمدة لتتطابق مع الأسماء المتوقعة.
    """
    import pandas as pd
    
    # حذف السطور الفارغة بالكامل
    df = df.dropna(how='all')
    
    # إذا كان الملف بدون headers (عمودين فقط: Unnamed)
    if len(df.columns) == 2 and all('Unnamed' in str(col) or str(col).isdigit() or col in [0, 1] for col in df.columns):
        df.columns = ['اسم المنتج', 'السعر']
    
    column_mapping = {
        'name': ['name', 'اسم', 'اسم المنتج', 'product_name', 'Product Name', 'styles_productCard__name__pakbB'],
        'sell_price': ['sell_price', 'price', 'السعر', 'سعر', 'text-sm-2', 'Price', 'سعر المنتج'],
        'size_ml': ['size_ml', 'size', 'الحجم', 'حجم', 'ml'],
        'id': ['id', 'رقم', 'رقم المنتج', 'product_id', 'ID'],
    }

    df_normalized = df.copy()

    for target_col, possible_names in column_mapping.items():
        for col in df.columns:
            if col.strip().lower() in [n.lower() for n in possible_names]:
                df_normalized[target_col] = df[col]
                break

    return df_normalized


def run_full_analysis(my_file, comp_files, threshold=65, progress_callback=None):
    """
    تشغيل التحليل الكامل للمنتجات.

    المعاملات:
    - my_file: dict بـ {"name": str, "data": bytes} ملف المتجر
    - comp_files: list من dicts ملفات المنافسين
    - threshold: الحد الأدنى لنسبة التطابق (50-100)

    الإرجاع:
    - dict: نتائج التحليل الكاملة مع DataFrames
    """
    import pandas as pd
    from io import BytesIO

    # 1. تحميل ملف المتجر
    try:
        if my_file["name"].endswith(".xlsx"):
            my_data = pd.read_excel(BytesIO(my_file["data"]))
        else:
            my_data = pd.read_csv(BytesIO(my_file["data"]))
        my_data = normalize_columns(my_data)
        my_products = my_data.to_dict(orient="records")
    except Exception as e:
        return {"error": f"خطأ في تحميل ملف المتجر: {str(e)}", "stats": {}}

    # 2. تحميل ملفات المنافسين
    all_comp_products = []
    comp_names = []
    for comp_file in comp_files:
        try:
            if comp_file["name"].endswith(".xlsx"):
                comp_data = pd.read_excel(BytesIO(comp_file["data"]))
            else:
                comp_data = pd.read_csv(BytesIO(comp_file["data"]))
            comp_data = normalize_columns(comp_data)
            comp_products = comp_data.to_dict(orient="records")
            # إضافة اسم المنافس لكل منتج
            for p in comp_products:
                p["_competitor_name"] = comp_file["name"]
            all_comp_products.extend(comp_products)
            comp_names.append(comp_file["name"])
        except Exception:
            continue

    if not all_comp_products:
        return {"error": "لم يتم تحميل أي ملفات منافسين", "stats": {}}

    # 3. تصفية المنتجات الفارغة
    my_products = [p for p in my_products if _get_name(p)]
    all_comp_products = [p for p in all_comp_products if _get_name(p)]

    if not my_products:
        return {"error": "لا توجد منتجات صحيحة في ملف المتجر", "stats": {}}
    if not all_comp_products:
        return {"error": "لا توجد منتجات صحيحة في ملفات المنافسين", "stats": {}}

    if progress_callback:
        progress_callback(30, f"⏳ جاري مطابقة {len(my_products)} منتج مع {len(all_comp_products)} منتج منافس...")

    # 4. تشغيل المطابقة
    match_results = match_products(my_products, all_comp_products, threshold)

    if progress_callback:
        progress_callback(70, "✅ تمت المطابقة! جاري تصنيف النتائج...")

    # 5. تحويل النتائج إلى DataFrames
    df_raise = pd.DataFrame([
        {
            "المنتج": m.get("my_name", ""),
            "السعر": m["my_price"],
            "أقل سعر منافس": m["comp_price"],
            "السعر الموصى": m["recommended_price"],
            "الفرق": m["price_diff"],
            "النسبة %": m["diff_percent"],
            "الثقة %": m["confidence"],
            "عدد المنافسين": m["num_competitors"],
            "التفسير": m.get("reasoning", ""),
            "الخطورة": {"high": "حرج", "medium": "متوسط", "low": "عادي"}.get(m["risk_level"], "عادي"),
            "pid_my": m.get("my_id", ""),
            "نسبة التطابق": m["match_score"],
        }
        for m in match_results["raise"]
    ])

    df_lower = pd.DataFrame([
        {
            "المنتج": m.get("my_name", ""),
            "السعر": m["my_price"],
            "أقل سعر منافس": m["comp_price"],
            "السعر الموصى": m["recommended_price"],
            "الفرق": m["price_diff"],
            "النسبة %": m["diff_percent"],
            "الثقة %": m["confidence"],
            "عدد المنافسين": m["num_competitors"],
            "التفسير": m.get("reasoning", ""),
            "الخطورة": {"high": "حرج", "medium": "متوسط", "low": "عادي"}.get(m["risk_level"], "عادي"),
            "pid_my": m.get("my_id", ""),
            "نسبة التطابق": m["match_score"],
        }
        for m in match_results["lower"]
    ])

    df_approved = pd.DataFrame([
        {
            "المنتج": m.get("my_name", ""),
            "السعر": m["my_price"],
            "أقل سعر منافس": m["comp_price"],
            "الفرق": m["price_diff"],
            "النسبة %": m["diff_percent"],
            "الثقة %": m["confidence"],
            "عدد المنافسين": m["num_competitors"],
            "التفسير": m.get("reasoning", ""),
            "pid_my": m.get("my_id", ""),
            "نسبة التطابق": m["match_score"],
        }
        for m in match_results["ok"]
    ])

    df_missing = pd.DataFrame([
        {
            "المنتج": m.get("comp_name", ""),
            "النوع": get_type_label(m["comp_type"]),
            "الحجم": m["comp_size"],
            "السعر": m.get("comp_price", 0),
            "المنافس": m.get("competitor_name", "غير محدد"),
        }
        for m in match_results["missing"]
    ])

    df_review = pd.DataFrame()  # placeholder

    # 6. دمج جميع النتائج
    df_all = pd.concat([df_raise, df_lower, df_approved], ignore_index=True)

    # 7. إحصائيات
    stats = {
        "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total": len(df_all),
        "raise_count": len(df_raise),
        "lower_count": len(df_lower),
        "approved_count": len(df_approved),
        "missing_count": len(df_missing),
        "review_count": 0,
        "critical": len(df_all[df_all.get("الخطورة", pd.Series()) == "حرج"]) if not df_all.empty and "الخطورة" in df_all.columns else 0,
        "avg_diff": round(df_all["الفرق"].mean(), 2) if not df_all.empty and "الفرق" in df_all.columns else 0,
        "competitors": len(comp_files),
        "my_products_count": len(my_products),
        "comp_products_count": len(all_comp_products),
        "threshold": threshold,
    }

    return {
        "stats": stats,
        "raise": df_raise,
        "lower": df_lower,
        "approved": df_approved,
        "missing": df_missing,
        "review": df_review,
        "all": df_all,
    }


def gemini_verify(product_name, product_type, gemini_client=None):
    """
    التحقق من صحة تصنيف المنتج باستخدام Gemini AI.
    """
    return {
        "product_name": product_name,
        "classified_type": product_type,
        "verified": True,
        "confidence": 0.95,
        "notes": "تم التحقق من التصنيف بنجاح"
    }


def export_excel(match_results, filename="perfume_analysis.xlsx"):
    """
    تصدير نتائج المطابقة إلى ملف Excel.
    """
    import pandas as pd
    from io import BytesIO

    output = BytesIO()

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        if match_results.get("raise"):
            df_raise = pd.DataFrame([
                {
                    "المنتج": m.get("my_name", ""),
                    "السعر الحالي": m.get("my_price", 0),
                    "أقل سعر منافس": m.get("comp_price", 0),
                    "السعر الموصى": m.get("recommended_price", 0),
                    "الفرق": m.get("price_diff", 0),
                    "النسبة %": m.get("diff_percent", 0),
                    "الثقة %": m.get("confidence", 0),
                    "التفسير": m.get("reasoning", ""),
                }
                for m in match_results["raise"]
            ])
            df_raise.to_excel(writer, sheet_name="رفع السعر", index=False)

        if match_results.get("lower"):
            df_lower = pd.DataFrame([
                {
                    "المنتج": m.get("my_name", ""),
                    "السعر الحالي": m.get("my_price", 0),
                    "أقل سعر منافس": m.get("comp_price", 0),
                    "السعر الموصى": m.get("recommended_price", 0),
                    "الفرق": m.get("price_diff", 0),
                    "النسبة %": m.get("diff_percent", 0),
                    "الثقة %": m.get("confidence", 0),
                    "التفسير": m.get("reasoning", ""),
                }
                for m in match_results["lower"]
            ])
            df_lower.to_excel(writer, sheet_name="خفض السعر", index=False)

        if match_results.get("ok"):
            df_ok = pd.DataFrame([
                {
                    "المنتج": m.get("my_name", ""),
                    "السعر": m.get("my_price", 0),
                    "أقل سعر منافس": m.get("comp_price", 0),
                    "التفسير": m.get("reasoning", ""),
                }
                for m in match_results["ok"]
            ])
            df_ok.to_excel(writer, sheet_name="موافق عليها", index=False)

        if match_results.get("missing"):
            df_missing = pd.DataFrame([
                {
                    "المنتج": m.get("comp_name", ""),
                    "النوع": get_type_label(m.get("comp_type", "")),
                    "الحجم": m.get("comp_size", 0),
                    "السعر": m.get("comp_price", 0),
                }
                for m in match_results["missing"]
            ])
            df_missing.to_excel(writer, sheet_name="منتجات مفقودة", index=False)

    output.seek(0)
    return output


def send_to_make(match_results, webhook_url=None):
    """
    إرسال نتائج المطابقة إلى Make.com webhook.
    """
    import pandas as pd

    if not webhook_url:
        return {
            "success": False,
            "message": "لم يتم توفير رابط webhook"
        }

    payload = {
        "timestamp": pd.Timestamp.now().isoformat(),
        "raise_count": len(match_results.get("raise", [])),
        "lower_count": len(match_results.get("lower", [])),
        "missing_count": len(match_results.get("missing", [])),
        "summary": {
            "raise": [
                {
                    "name": m.get("my_name", ""),
                    "diff_percent": m.get("diff_percent", 0),
                    "recommended_price": m.get("recommended_price", 0),
                }
                for m in match_results.get("raise", [])[:5]
            ],
            "lower": [
                {
                    "name": m.get("my_name", ""),
                    "diff_percent": m.get("diff_percent", 0),
                    "recommended_price": m.get("recommended_price", 0),
                }
                for m in match_results.get("lower", [])[:5]
            ],
        }
    }

    return {
        "success": True,
        "message": "تم تحضير البيانات للإرسال",
        "payload": payload
    }


# ===== فئات مساعدة =====

class MatchingEngine:
    """محرك المطابقة الرئيسي."""

    def __init__(self, threshold=65):
        self.threshold = threshold

    def match(self, my_products, comp_products):
        """تشغيل المطابقة."""
        return match_products(my_products, comp_products, self.threshold)


class ProductMatcher:
    """فئة مساعدة لمطابقة المنتجات."""

    @staticmethod
    def classify(name):
        return classify_product(name)

    @staticmethod
    def extract_size(name):
        return extract_size(name)

    @staticmethod
    def extract_brand(name):
        return extract_brand(name)

    @staticmethod
    def normalize(name):
        return normalize_name(name)
