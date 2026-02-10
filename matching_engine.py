# -*- coding: utf-8 -*-
"""
محرك المقارنة والمطابقة الصارم للعطور - الإصدار 3.
يشمل: تصنيف ذكي، مطابقة صارمة، كشف المنتجات المفقودة،
تقسيم النتائج (رفع/خفض/موافق)، وربط Gemini.
"""

import re
import hashlib
from io import BytesIO
from typing import Any, Dict, List, Tuple
from datetime import datetime

import pandas as pd
from rapidfuzz import fuzz, process

# ---------------------------------------------------------------
# ثوابت التصنيف
# ---------------------------------------------------------------
REJECTED_KW = ["عينة", "sample", "تقسيم", "decant", "miniature"]
TESTER_KW = ["تستر", "tester", "testeur", "demonstration"]
HAIR_MIST_KW = ["عطر شعر", "hair mist", "hair perfume"]
BODY_MIST_KW = ["body mist", "body spray", "ميست", "بودي"]
SET_KW = ["طقم", "set", "مجموعة", "gift set", "coffret"]

NOISE_WORDS = [
    "عطر", "perfume", "parfum", "ml", "مل",
    "edp", "edt", "eau", "de", "toilette", "pour",
    "spray", "intense", "original", "اصلي", "homme",
    "femme", "women", "men", "unisex", "new", "جديد",
]


def classify_product(name: str) -> Tuple[str, int, bool]:
    """تصنيف المنتج: (النوع، الحجم بالمل، مرفوض؟)."""
    low = str(name).lower()
    if any(k in low for k in REJECTED_KW):
        return "Rejected", 0, True
    if any(k in low for k in SET_KW):
        ptype = "Set"
    elif any(k in low for k in HAIR_MIST_KW):
        ptype = "Hair Mist"
    elif any(k in low for k in BODY_MIST_KW):
        ptype = "Body Mist"
    elif any(k in low for k in TESTER_KW):
        ptype = "Tester"
    else:
        ptype = "Retail"
    m = re.search(r"(\d+)\s*(?:ml|مل)", low)
    size = int(m.group(1)) if m else 0
    return ptype, size, False


def fingerprint(name: str) -> str:
    """بصمة نظيفة للمقارنة بين الأسماء."""
    if not isinstance(name, str):
        return ""
    txt = name.lower()
    txt = re.sub("[إأآا]", "ا", txt)
    txt = re.sub("ة", "ه", txt)
    for w in NOISE_WORDS:
        txt = txt.replace(w, "")
    txt = re.sub(r"[^\w\s]", "", txt)
    txt = re.sub(r"\d+", "", txt)
    return " ".join(sorted(txt.split())).strip()


def product_hash(name: str, size: int, ptype: str) -> str:
    """معرّف فريد للمنتج."""
    raw = f"{fingerprint(name)}|{size}|{ptype}"
    return hashlib.md5(raw.encode()).hexdigest()[:12]


# ---------------------------------------------------------------
# قراءة الملفات
# ---------------------------------------------------------------
def guess_columns(df: pd.DataFrame) -> Tuple[str, str]:
    """تخمين عمود الاسم وعمود السعر."""
    cols = list(df.columns)
    name_col, price_col = cols[0], cols[-1]
    for c in cols:
        cl = str(c).lower()
        if any(k in cl for k in ["اسم", "name", "منتج", "product"]):
            name_col = c
        if any(k in cl for k in ["سعر", "price", "cost"]):
            price_col = c
    return name_col, price_col


def read_upload(file_dict: Dict[str, Any]) -> pd.DataFrame:
    """قراءة ملف مرفوع {name, data}."""
    buf = BytesIO(file_dict["data"])
    fname = file_dict["name"].lower()
    if fname.endswith(".csv"):
        return pd.read_csv(buf)
    return pd.read_excel(buf, engine="openpyxl")


def parse_products(df: pd.DataFrame, source: str = "") -> List[Dict]:
    """تحويل DataFrame إلى قائمة منتجات مصنفة."""
    name_col, price_col = guess_columns(df)
    products = []
    for _, row in df.iterrows():
        raw = str(row[name_col]).strip()
        if not raw or raw == "nan":
            continue
        ptype, size, rejected = classify_product(raw)
        try:
            price = float(row[price_col])
        except (ValueError, TypeError):
            price = 0.0
        products.append({
            "name": raw,
            "price": price,
            "type": ptype,
            "size": size,
            "rejected": rejected,
            "fp": fingerprint(raw),
            "pid": product_hash(raw, size, ptype),
            "source": source,
        })
    return products


# ---------------------------------------------------------------
# المطابقة الصارمة
# ---------------------------------------------------------------
def strict_match(
    my_products: List[Dict],
    comp_products: List[Dict],
    comp_name: str,
    min_score: int = 75,
) -> List[Dict]:
    """مطابقة صارمة: نفس النوع + نفس الحجم + تشابه الاسم."""
    matches = []
    for my_p in my_products:
        if my_p["rejected"] or my_p["size"] == 0:
            continue
        candidates = [
            c for c in comp_products
            if not c["rejected"]
            and c["type"] == my_p["type"]
            and c["size"] == my_p["size"]
        ]
        if not candidates:
            continue
        fps = [c["fp"] for c in candidates]
        result = process.extractOne(
            my_p["fp"], fps, scorer=fuzz.WRatio
        )
        if result is None or result[1] < min_score:
            continue
        best = candidates[fps.index(result[0])]
        diff = round(best["price"] - my_p["price"], 2)
        pct = round((diff / my_p["price"]) * 100, 1) if my_p["price"] else 0

        if diff < 0:
            decision = "رفع_سعر"
            icon = "🔴"
            hint = "سعرك أقل - فرصة رفع"
        elif diff > 0:
            decision = "خفض_سعر"
            icon = "🟡"
            hint = "سعرك أعلى - خطر خسارة عملاء"
        else:
            decision = "موافق"
            icon = "🟢"
            hint = "سعرك متوازن مع السوق"

        severity = "عادي"
        if abs(pct) > 20:
            severity = "حرج"
        elif abs(pct) > 10:
            severity = "متوسط"

        matches.append({
            "اسم_منتجي": my_p["name"],
            "نوع_المنتج": my_p["type"],
            "الحجم_مل": my_p["size"],
            "سعري": my_p["price"],
            "المنافس": comp_name,
            "منتج_المنافس": best["name"],
            "سعر_المنافس": best["price"],
            "الفرق": diff,
            "الفرق_%": pct,
            "القرار": decision,
            "الأيقونة": icon,
            "التوصية": hint,
            "الخطورة": severity,
            "نسبة_التطابق": round(result[1]),
            "pid_my": my_p["pid"],
            "pid_comp": best["pid"],
        })
    return matches


# ---------------------------------------------------------------
# كشف المنتجات المفقودة
# ---------------------------------------------------------------
def find_missing_products(
    my_products: List[Dict],
    comp_products: List[Dict],
    comp_name: str,
    min_score: int = 70,
) -> List[Dict]:
    """منتجات موجودة عند المنافس وليست عندنا."""
    my_fps = [p["fp"] for p in my_products if not p["rejected"]]
    missing = []
    seen = set()
    for cp in comp_products:
        if cp["rejected"] or cp["size"] == 0:
            continue
        if cp["pid"] in seen:
            continue
        result = process.extractOne(
            cp["fp"], my_fps, scorer=fuzz.WRatio
        )
        if result is None or result[1] < min_score:
            seen.add(cp["pid"])
            missing.append({
                "منتج_المنافس": cp["name"],
                "نوع_المنتج": cp["type"],
                "الحجم_مل": cp["size"],
                "سعر_المنافس": cp["price"],
                "المنافس": comp_name,
                "أقرب_تطابق": result[0] if result else "",
                "نسبة_التشابه": round(result[1]) if result else 0,
            })
    return missing


# ---------------------------------------------------------------
# التحليل الشامل
# ---------------------------------------------------------------
def run_full_analysis(
    my_file: Dict[str, Any],
    comp_files: List[Dict[str, Any]],
    min_score: int = 75,
) -> Dict[str, Any]:
    """تشغيل التحليل الكامل وإرجاع النتائج مقسمة."""
    df_my = read_upload(my_file)
    my_products = parse_products(df_my, source="متجري")

    all_matches = []
    all_missing = []

    for cf in comp_files:
        cname = cf["name"].rsplit(".", 1)[0]
        df_c = read_upload(cf)
        comp_prods = parse_products(df_c, source=cname)

        matches = strict_match(my_products, comp_prods, cname, min_score)
        all_matches.extend(matches)

        missing = find_missing_products(
            my_products, comp_prods, cname, min_score
        )
        all_missing.extend(missing)

    # تقسيم النتائج
    df_all = pd.DataFrame(all_matches) if all_matches else pd.DataFrame()
    df_missing = pd.DataFrame(all_missing) if all_missing else pd.DataFrame()

    result = {
        "all": df_all,
        "raise": pd.DataFrame(),
        "lower": pd.DataFrame(),
        "approved": pd.DataFrame(),
        "missing": df_missing,
        "my_products": my_products,
        "stats": {},
    }

    if not df_all.empty:
        result["raise"] = df_all[df_all["القرار"] == "رفع_سعر"].copy()
        result["lower"] = df_all[df_all["القرار"] == "خفض_سعر"].copy()
        result["approved"] = df_all[df_all["القرار"] == "موافق"].copy()
        result["stats"] = {
            "total": len(df_all),
            "raise_count": len(result["raise"]),
            "lower_count": len(result["lower"]),
            "approved_count": len(result["approved"]),
            "missing_count": len(df_missing),
            "critical": len(df_all[df_all["الخطورة"] == "حرج"]),
            "avg_diff": round(df_all["الفرق"].mean(), 2),
            "competitors": df_all["المنافس"].nunique(),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }

    return result


# ---------------------------------------------------------------
# Gemini تحقق ذكي
# ---------------------------------------------------------------
def gemini_verify(
    product_name: str,
    my_price: float,
    comp_price: float,
    api_key: str,
) -> str:
    """تحقق ذكي من منتج واحد باستخدام Gemini."""
    if not api_key:
        return "مفتاح Gemini غير متوفر. أدخله في الإعدادات."
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")
        prompt = (
            f"أنت خبير تسعير عطور محترف. حلل هذا المنتج:\n"
            f"الاسم: {product_name}\n"
            f"سعري: {my_price} ريال\n"
            f"سعر المنافس: {comp_price} ريال\n"
            f"الفرق: {comp_price - my_price} ريال\n\n"
            f"أجب بإيجاز (3 أسطر):\n"
            f"1. هل السعر مناسب؟\n"
            f"2. التوصية (رفع/خفض/ثبات) وكم ريال؟\n"
            f"3. السبب باختصار."
        )
        resp = model.generate_content(prompt)
        return resp.text
    except Exception as exc:
        return f"خطأ في Gemini: {exc}"


# ---------------------------------------------------------------
# تصدير Excel
# ---------------------------------------------------------------
def export_excel(df: pd.DataFrame, sheet_name: str = "النتائج") -> bytes:
    """تصدير DataFrame إلى Excel bytes."""
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df.to_excel(w, sheet_name=sheet_name, index=False)
    return buf.getvalue()


# ---------------------------------------------------------------
# Make.com Webhook
# ---------------------------------------------------------------
def send_to_make(webhook_url: str, data: List[Dict]) -> Dict:
    """إرسال البيانات إلى Make.com عبر Webhook."""
    import requests
    try:
        resp = requests.post(
            webhook_url,
            json={"timestamp": datetime.now().isoformat(), "data": data},
            timeout=30,
        )
        return {"status": resp.status_code, "ok": resp.ok}
    except Exception as exc:
        return {"status": 0, "ok": False, "error": str(exc)}
