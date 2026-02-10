"""
engine.py - محرك المطابقة والتصنيف الذكي
يطبق قوانين صارمة لمقارنة المنتجات
"""
import re
from rapidfuzz import fuzz


# ===== قوانين التصنيف =====

REJECT_KEYWORDS = [
    "sample", "عينة", "decant", "تقسيم",
    "split", "miniature", "mini ", "0.5ml",
    "1ml", "2ml", "3ml", "5ml", "سبلاش",
    "splash", "رول", "roll-on", "rollerball",
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

    # 1. فحص الرفض أولاً
    for kw in REJECT_KEYWORDS:
        if kw in lower:
            return "rejected"

    # 2. فحص التستر
    for kw in TESTER_KEYWORDS:
        if kw in lower:
            return "tester"

    # 3. فحص الطقم
    for kw in SET_KEYWORDS:
        if kw in lower:
            return "set"

    # 4. فحص هير مست
    for kw in HAIR_MIST_KEYWORDS:
        if kw in lower:
            return "hair_mist"

    # 5. فحص بودي مست
    for kw in BODY_MIST_KEYWORDS:
        if kw in lower:
            return "body_mist"

    # 6. الافتراضي = retail
    return "retail"


def extract_size(name):
    """استخراج الحجم من اسم المنتج."""
    patterns = [
        r"(\d+(?:\.\d+)?)\s*ml",
        r"(\d+(?:\.\d+)?)\s*مل",
        r"(\d+(?:\.\d+)?)\s*ML",
        r"(\d+(?:\.\d+)?)\s*Ml",
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
    ]
    for w in remove_words:
        name = name.replace(w, "")
    # إزالة الرموز الزائدة
    name = re.sub(r"[^\w\s]", " ", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name


def match_products(my_products, comp_products,
                   threshold=65):
    """
    مطابقة المنتجات مع تطبيق القوانين الصارمة.

    القوانين:
    1. تطابق النوع: retail=retail, tester=tester
    2. تطابق الحجم: 100ml=100ml فقط
    3. فيتو العينات: طرد تلقائي
    4. التحقق البصري: عرض الاسم الأصلي
    """
    results = {
        "raise": [],
        "lower": [],
        "ok": [],
        "missing": [],
    }

    matched_comp_ids = set()

    for my_p in my_products:
        my_name = my_p.get("name", "")
        my_type = classify_product(my_name)
        my_size = my_p.get("size_ml", 0) or extract_size(my_name)
        my_price = float(my_p.get("sell_price", 0) or 0)
        my_norm = normalize_name(my_name)

        if my_type == "rejected":
            continue

        best_match = None
        best_score = 0

        for cp in comp_products:
            cp_name = cp.get("product_name", cp.get("name", ""))
            cp_type = classify_product(cp_name)
            cp_size = (
                cp.get("size_ml", 0) or extract_size(cp_name)
            )
            cp_price = float(cp.get("price", 0) or 0)

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

            if score > best_score and score >= threshold:
                best_score = score
                best_match = {
                    "my_product": my_p,
                    "comp_product": cp,
                    "my_price": my_price,
                    "comp_price": cp_price,
                    "match_score": score,
                    "my_type": my_type,
                    "comp_type": cp_type,
                    "my_size": my_size,
                    "comp_size": cp_size,
                }

        if best_match and best_match["comp_price"] > 0:
            cp_id = best_match["comp_product"].get("id", 0)
            matched_comp_ids.add(cp_id)

            diff = (
                best_match["my_price"] - best_match["comp_price"]
            )
            if best_match["comp_price"] > 0:
                diff_pct = (diff / best_match["comp_price"]) * 100
            else:
                diff_pct = 0

            best_match["price_diff"] = diff
            best_match["diff_percent"] = round(diff_pct, 1)

            # تحديد مستوى الخطورة
            abs_pct = abs(diff_pct)
            if abs_pct >= 20:
                risk = "high"
            elif abs_pct >= 10:
                risk = "medium"
            else:
                risk = "low"
            best_match["risk_level"] = risk

            # تحديد التوصية
            if diff > 0:
                best_match["recommendation"] = "lower"
                results["lower"].append(best_match)
            elif diff < 0:
                best_match["recommendation"] = "raise"
                results["raise"].append(best_match)
            else:
                best_match["recommendation"] = "ok"
                results["ok"].append(best_match)

    # كشف المنتجات المفقودة
    for cp in comp_products:
        cp_id = cp.get("id", 0)
        if cp_id not in matched_comp_ids:
            cp_name = cp.get("product_name", cp.get("name", ""))
            cp_type = classify_product(cp_name)
            if cp_type != "rejected":
                results["missing"].append({
                    "comp_product": cp,
                    "comp_type": cp_type,
                    "comp_size": (
                        cp.get("size_ml", 0)
                        or extract_size(cp_name)
                    ),
                })

    # ترتيب حسب الخطورة
    for key in ["raise", "lower"]:
        results[key].sort(
            key=lambda x: abs(x.get("diff_percent", 0)),
            reverse=True
        )

    return results


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
