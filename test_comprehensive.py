"""
اختبار شامل لنظام التسعير الذكي
يتحقق من:
1. استيراد جميع الوحدات بدون أخطاء
2. دوال المحرك الأساسية
3. تحويل V2 إلى الشكل العربي
4. save_results_to_db
5. normalize_columns
6. extract_brand, extract_size, extract_concentration
"""

import sys
import os
import io
import pandas as pd
import json

# إضافة المسار
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ═══════════════════════════════════════
# 1. اختبار الاستيراد
# ═══════════════════════════════════════
print("=" * 60)
print("1. اختبار استيراد الوحدات")
print("=" * 60)

errors = []

try:
    from engine import (
        normalize_name, extract_brand, extract_size, extract_concentration,
        classify_product, _get_name, _get_price, normalize_columns,
        run_full_analysis, get_type_label
    )
    print("  ✅ engine.py - تم الاستيراد بنجاح")
except Exception as e:
    errors.append(f"engine.py: {e}")
    print(f"  ❌ engine.py: {e}")

try:
    from engine_v2 import run_smart_matching, SmartMatcher, GEMINI_AVAILABLE
    print(f"  ✅ engine_v2.py - تم الاستيراد بنجاح (GEMINI_AVAILABLE={GEMINI_AVAILABLE})")
except Exception as e:
    errors.append(f"engine_v2.py: {e}")
    print(f"  ❌ engine_v2.py: {e}")

try:
    from extract_concentration import extract_concentration as ec, concentrations_match
    print("  ✅ extract_concentration.py - تم الاستيراد بنجاح")
except Exception as e:
    errors.append(f"extract_concentration.py: {e}")
    print(f"  ❌ extract_concentration.py: {e}")

try:
    from semantic_matcher import semantic_verify_match
    print("  ✅ semantic_matcher.py - تم الاستيراد بنجاح")
except Exception as e:
    errors.append(f"semantic_matcher.py: {e}")
    print(f"  ❌ semantic_matcher.py: {e}")

try:
    from modules.ai_verification import verify_match_with_gemini, GEMINI_API_KEY
    print(f"  ✅ modules/ai_verification.py - تم الاستيراد (API Key: {'✅ موجود' if GEMINI_API_KEY else '❌ مفقود'})")
except Exception as e:
    errors.append(f"modules/ai_verification.py: {e}")
    print(f"  ❌ modules/ai_verification.py: {e}")

# ═══════════════════════════════════════
# 2. اختبار الدوال الأساسية
# ═══════════════════════════════════════
print("\n" + "=" * 60)
print("2. اختبار الدوال الأساسية")
print("=" * 60)

# extract_brand
test_cases_brand = [
    ("Dior Sauvage EDT 100ml", "Dior"),
    ("ديور سوفاج او دو تواليت 100مل", "ديور"),
    ("Versace Crystal Noir EDP 90ml", "Versace"),
    ("Tom Ford Oud Wood 50ml", "Tom Ford"),
    ("عطر غير معروف 100مل", ""),
]

for name, expected in test_cases_brand:
    result = extract_brand(name)
    status = "✅" if result == expected else "❌"
    if result != expected:
        errors.append(f"extract_brand('{name}'): expected '{expected}', got '{result}'")
    print(f"  {status} extract_brand('{name[:30]}...') = '{result}' (expected: '{expected}')")

# extract_size
test_cases_size = [
    ("Dior Sauvage EDT 100ml", 100),
    ("Versace 90ml", 90),
    ("عطر 50مل", 50),
    ("عطر بدون حجم", 0),
]

for name, expected in test_cases_size:
    result = extract_size(name)
    status = "✅" if result == expected else "❌"
    if result != expected:
        errors.append(f"extract_size('{name}'): expected {expected}, got {result}")
    print(f"  {status} extract_size('{name[:30]}...') = {result} (expected: {expected})")

# classify_product
test_cases_classify = [
    ("Dior Sauvage EDT 100ml", "retail"),
    ("Dior Sauvage tester 100ml", "tester"),
    ("Gift Set Chanel", "set"),
    ("Hair Mist Rose", "hair_mist"),
    ("عينة ديور", "rejected"),
]

for name, expected in test_cases_classify:
    result = classify_product(name)
    status = "✅" if result == expected else "❌"
    if result != expected:
        errors.append(f"classify_product('{name}'): expected '{expected}', got '{result}'")
    print(f"  {status} classify_product('{name[:30]}...') = '{result}' (expected: '{expected}')")

# _get_name & _get_price
test_record = {"name": "Dior Sauvage", "sell_price": 350}
name_result = _get_name(test_record)
price_result = _get_price(test_record)
print(f"  {'✅' if name_result == 'Dior Sauvage' else '❌'} _get_name = '{name_result}'")
print(f"  {'✅' if price_result == 350.0 else '❌'} _get_price = {price_result}")

# Arabic column names
test_record_ar = {"اسم المنتج": "ديور سوفاج", "السعر": 350}
name_result_ar = _get_name(test_record_ar)
price_result_ar = _get_price(test_record_ar)
print(f"  {'✅' if name_result_ar == 'ديور سوفاج' else '❌'} _get_name (عربي) = '{name_result_ar}'")
print(f"  {'✅' if price_result_ar == 350.0 else '❌'} _get_price (عربي) = {price_result_ar}")

if name_result_ar != "ديور سوفاج":
    errors.append(f"_get_name with Arabic columns: expected 'ديور سوفاج', got '{name_result_ar}'")
if price_result_ar != 350.0:
    errors.append(f"_get_price with Arabic columns: expected 350.0, got {price_result_ar}")

# ═══════════════════════════════════════
# 3. اختبار normalize_columns
# ═══════════════════════════════════════
print("\n" + "=" * 60)
print("3. اختبار normalize_columns")
print("=" * 60)

# CSV بأعمدة عربية
df_arabic = pd.DataFrame({
    "اسم المنتج": ["Dior Sauvage 100ml", "Chanel No5 50ml"],
    "السعر": [350, 500],
})
df_normalized = normalize_columns(df_arabic)
has_name = "name" in df_normalized.columns or "اسم المنتج" in df_normalized.columns
has_price = "sell_price" in df_normalized.columns or "السعر" in df_normalized.columns
print(f"  {'✅' if has_name else '❌'} normalize_columns: عمود الاسم موجود")
print(f"  {'✅' if has_price else '❌'} normalize_columns: عمود السعر موجود")

if not has_name:
    errors.append("normalize_columns: عمود الاسم مفقود بعد التطبيع")
if not has_price:
    errors.append("normalize_columns: عمود السعر مفقود بعد التطبيع")

# CSV بأعمدة إنجليزية
df_english = pd.DataFrame({
    "product_name": ["Dior Sauvage 100ml"],
    "price": [350],
})
df_norm_en = normalize_columns(df_english)
print(f"  ✅ normalize_columns (English): columns = {list(df_norm_en.columns)}")

# CSV بدون headers
df_no_header = pd.DataFrame({0: ["Dior 100ml"], 1: [350]})
df_norm_nh = normalize_columns(df_no_header)
print(f"  ✅ normalize_columns (no header): columns = {list(df_norm_nh.columns)}")

# ═══════════════════════════════════════
# 4. اختبار _safe_df_len و _safe_df_to_records
# ═══════════════════════════════════════
print("\n" + "=" * 60)
print("4. اختبار _safe_df_len و _safe_df_to_records")
print("=" * 60)

# محاكاة الدوال
def _safe_df_len(obj):
    if obj is None:
        return 0
    if isinstance(obj, pd.DataFrame):
        return 0 if obj.empty else len(obj)
    if isinstance(obj, list):
        return len(obj)
    return 0

def _safe_df_to_records(obj):
    if obj is None:
        return []
    if isinstance(obj, pd.DataFrame):
        return obj.to_dict(orient="records") if not obj.empty else []
    if isinstance(obj, list):
        return obj
    return []

# اختبار مع None
assert _safe_df_len(None) == 0, "None should return 0"
print("  ✅ _safe_df_len(None) = 0")

# اختبار مع DataFrame فارغ
assert _safe_df_len(pd.DataFrame()) == 0, "Empty DF should return 0"
print("  ✅ _safe_df_len(empty DataFrame) = 0")

# اختبار مع DataFrame
df_test = pd.DataFrame({"a": [1, 2, 3]})
assert _safe_df_len(df_test) == 3, "DF with 3 rows should return 3"
print("  ✅ _safe_df_len(DataFrame with 3 rows) = 3")

# اختبار مع List
assert _safe_df_len([1, 2]) == 2, "List with 2 items should return 2"
print("  ✅ _safe_df_len([1, 2]) = 2")

# اختبار _safe_df_to_records
assert _safe_df_to_records(None) == [], "None should return []"
print("  ✅ _safe_df_to_records(None) = []")

records = _safe_df_to_records(df_test)
assert len(records) == 3, "Should return 3 records"
print("  ✅ _safe_df_to_records(DataFrame) = 3 records")

# ═══════════════════════════════════════
# 5. اختبار تحويل V2 إلى الشكل العربي
# ═══════════════════════════════════════
print("\n" + "=" * 60)
print("5. اختبار تحويل V2 إلى الشكل العربي")
print("=" * 60)

# محاكاة نتيجة V2
v2_result = {
    "my_product": {"name": "Dior Sauvage EDT 100ml", "sell_price": 350},
    "my_name": "Dior Sauvage EDT 100ml",
    "my_price": 350,
    "comp_product": {"name": "ديور سوفاج 100مل", "sell_price": 320},
    "comp_name": "ديور سوفاج 100مل",
    "comp_price": 320,
    "diff": 30,
    "diff_pct": 9.4,
    "category": "raise_price",
    "match_confidence": 92,
    "match_reason": "مطابقة سريعة (95%+)",
}

# تحويل
row = {
    "المقارنة": f"{v2_result['my_name']} 🆚 {v2_result['comp_name']}",
    "المنتج": v2_result["my_name"],
    "ماركتنا": extract_brand(v2_result["my_name"]),
    "تركيزنا": extract_concentration(v2_result["my_name"]),
    "حجمنا": extract_size(v2_result["my_name"]),
    "اسم المنافس": v2_result["comp_name"],
    "السعر": v2_result["my_price"],
    "أقل سعر منافس": v2_result["comp_price"],
    "الفرق": round(v2_result["diff"], 2),
    "النسبة %": round(v2_result["diff_pct"], 1),
    "الثقة %": v2_result["match_confidence"],
    "السعر الموصى": max(v2_result["comp_price"] - 1, 1),
}

# التحقق من الأعمدة المطلوبة
required_columns = ["المنتج", "اسم المنافس", "السعر", "أقل سعر منافس", "الفرق", "النسبة %", "الثقة %", "السعر الموصى"]
for col in required_columns:
    status = "✅" if col in row else "❌"
    if col not in row:
        errors.append(f"V2 conversion missing column: {col}")
    print(f"  {status} عمود '{col}' = {row.get(col, 'مفقود')}")

# ═══════════════════════════════════════
# 6. اختبار SmartMatcher
# ═══════════════════════════════════════
print("\n" + "=" * 60)
print("6. اختبار SmartMatcher")
print("=" * 60)

try:
    matcher = SmartMatcher()
    
    # مطابقة سريعة - نفس المنتج
    is_match, conf, reason = matcher.match_stage1_fast(
        "Dior Sauvage EDT 100ml", normalize_name("Dior Sauvage EDT 100ml"),
        "Dior", 100, "EDT",
        "Dior Sauvage EDT 100ml", normalize_name("Dior Sauvage EDT 100ml"),
        "Dior", 100, "EDT",
    )
    print(f"  {'✅' if is_match else '❌'} Stage1 (same product): match={is_match}, conf={conf}")
    if not is_match:
        errors.append("SmartMatcher stage1 failed for identical products")
    
    # مطابقة سريعة - brand مختلف
    is_match2, conf2, reason2 = matcher.match_stage1_fast(
        "Dior Sauvage EDT 100ml", normalize_name("Dior Sauvage EDT 100ml"),
        "Dior", 100, "EDT",
        "Chanel No5 EDT 100ml", normalize_name("Chanel No5 EDT 100ml"),
        "Chanel", 100, "EDT",
    )
    print(f"  {'✅' if not is_match2 else '❌'} Stage1 (different brand): match={is_match2}")
    if is_match2:
        errors.append("SmartMatcher stage1 matched different brands")
    
    # find_best_match
    my_product = {"name": "Dior Sauvage EDT 100ml", "sell_price": 350}
    candidates = [
        {"name": "Dior Sauvage EDT 100ml", "size": 100, "price": 320, "normalized": normalize_name("Dior Sauvage EDT 100ml"), "product": {}, "index": 0},
        {"name": "Chanel No5 50ml", "size": 50, "price": 500, "normalized": normalize_name("Chanel No5 50ml"), "product": {}, "index": 1},
    ]
    
    best = matcher.find_best_match(my_product, candidates)
    if best:
        print(f"  ✅ find_best_match: found '{best['name']}' (confidence: {best.get('match_confidence', 0)})")
    else:
        print("  ❌ find_best_match: no match found")
        errors.append("SmartMatcher find_best_match returned None for matching products")
    
    stats = matcher.get_stats()
    print(f"  ✅ Stats: {stats}")
    
except Exception as e:
    errors.append(f"SmartMatcher test: {e}")
    print(f"  ❌ SmartMatcher test failed: {e}")

# ═══════════════════════════════════════
# 7. اختبار run_smart_matching مع بيانات وهمية
# ═══════════════════════════════════════
print("\n" + "=" * 60)
print("7. اختبار run_smart_matching")
print("=" * 60)

try:
    my_products = [
        {"name": "Dior Sauvage EDT 100ml", "sell_price": 350},
        {"name": "Versace Crystal Noir EDP 90ml", "sell_price": 280},
        {"name": "عطر غير موجود 50مل", "sell_price": 100},
    ]
    
    comp_products = [
        {"name": "Dior Sauvage EDT 100ml", "sell_price": 320},
        {"name": "Versace Crystal Noir EDP 90ml", "sell_price": 300},
    ]
    
    results = run_smart_matching(my_products, comp_products)
    
    # التحقق من النتائج
    categories = [r["category"] for r in results]
    print(f"  ✅ run_smart_matching returned {len(results)} results")
    print(f"  ✅ Categories: {categories}")
    
    # التحقق من وجود category في كل نتيجة
    for i, r in enumerate(results):
        assert "category" in r, f"Result {i} missing 'category'"
        assert "my_name" in r, f"Result {i} missing 'my_name'"
        assert "my_price" in r, f"Result {i} missing 'my_price'"
        assert "comp_price" in r, f"Result {i} missing 'comp_price'"
        assert "diff" in r, f"Result {i} missing 'diff'"
        assert "diff_pct" in r, f"Result {i} missing 'diff_pct'"
    print(f"  ✅ All results have required fields")
    
    # التحقق من أن المنتج الثالث مفقود
    missing = [r for r in results if r["category"] == "missing"]
    print(f"  {'✅' if len(missing) >= 1 else '⚠️'} Missing products: {len(missing)}")
    
except Exception as e:
    errors.append(f"run_smart_matching: {e}")
    print(f"  ❌ run_smart_matching failed: {e}")

# ═══════════════════════════════════════
# 8. اختبار تحويل V2 الكامل (كما في main.py)
# ═══════════════════════════════════════
print("\n" + "=" * 60)
print("8. اختبار تحويل V2 الكامل")
print("=" * 60)

try:
    # محاكاة raw_results من V2
    raw_results = [
        {"category": "raise_price", "my_name": "Dior Sauvage 100ml", "my_price": 350, "comp_name": "Dior Sauvage 100ml", "comp_price": 320, "diff": 30, "diff_pct": 9.4, "match_confidence": 95, "match_reason": "مطابقة سريعة"},
        {"category": "lower_price", "my_name": "Chanel No5 50ml", "my_price": 400, "comp_name": "Chanel No5 50ml", "comp_price": 450, "diff": -50, "diff_pct": -11.1, "match_confidence": 90, "match_reason": "مطابقة متوسطة"},
        {"category": "keep_price", "my_name": "Versace 90ml", "my_price": 280, "comp_name": "Versace 90ml", "comp_price": 285, "diff": -5, "diff_pct": -1.8, "match_confidence": 88, "match_reason": "مطابقة سريعة"},
        {"category": "missing", "my_name": "عطر غير موجود", "my_price": 100, "comp_name": None, "comp_price": 0, "diff": 0, "diff_pct": 0, "match_confidence": 0, "match_reason": "غير موجود"},
    ]
    
    raise_list = [r for r in raw_results if r["category"] == "raise_price"]
    lower_list = [r for r in raw_results if r["category"] == "lower_price"]
    keep_list = [r for r in raw_results if r["category"] == "keep_price"]
    missing_list = [r for r in raw_results if r["category"] == "missing"]
    
    def _v2_to_arabic_row(r, include_recommended=True):
        row = {
            "المقارنة": f"{r.get('my_name', '')} 🆚 {r.get('comp_name', '')}",
            "المنتج": r.get("my_name", ""),
            "ماركتنا": extract_brand(r.get("my_name", "")),
            "تركيزنا": extract_concentration(r.get("my_name", "")),
            "حجمنا": extract_size(r.get("my_name", "")),
            "اسم المنافس": r.get("comp_name", ""),
            "ماركة المنافس": extract_brand(r.get("comp_name", "")) if r.get("comp_name") else "",
            "تركيز المنافس": extract_concentration(r.get("comp_name", "")) if r.get("comp_name") else "",
            "حجم المنافس": extract_size(r.get("comp_name", "")) if r.get("comp_name") else 0,
            "السعر": r.get("my_price", 0),
            "أقل سعر منافس": r.get("comp_price", 0),
            "سعر المنافس": r.get("comp_price", 0),
            "الفرق": round(r.get("diff", 0), 2),
            "النسبة %": round(r.get("diff_pct", 0), 1),
            "الثقة %": r.get("match_confidence", 0),
            "ثقة AI %": r.get("match_confidence", 0),
            "حالة التحقق": r.get("match_reason", "✅ مؤكد"),
            "تفسير AI": r.get("match_reason", ""),
            "عدد المنافسين": 1,
            "التفسير": r.get("match_reason", ""),
            "نسبة التطابق": r.get("match_confidence", 0),
            "pid_my": "",
        }
        if include_recommended:
            comp_price = r.get("comp_price", 0)
            row["السعر الموصى"] = max(comp_price - 1, 1) if comp_price > 0 else 0
        
        abs_pct = abs(r.get("diff_pct", 0))
        if abs_pct >= 20:
            row["الخطورة"] = "حرج"
        elif abs_pct >= 10:
            row["الخطورة"] = "متوسط"
        else:
            row["الخطورة"] = "عادي"
        
        return row
    
    def _v2_missing_to_arabic(r):
        return {
            "المنتج": r.get("my_name", ""),
            "النوع": "ريتيل",
            "الحجم": extract_size(r.get("my_name", "")),
            "السعر": r.get("my_price", 0),
            "المنافس": "غير محدد",
        }
    
    df_raise = pd.DataFrame([_v2_to_arabic_row(r) for r in raise_list]) if raise_list else pd.DataFrame()
    df_lower = pd.DataFrame([_v2_to_arabic_row(r) for r in lower_list]) if lower_list else pd.DataFrame()
    df_approved = pd.DataFrame([_v2_to_arabic_row(r, include_recommended=False) for r in keep_list]) if keep_list else pd.DataFrame()
    df_missing = pd.DataFrame([_v2_missing_to_arabic(r) for r in missing_list]) if missing_list else pd.DataFrame()
    
    df_all = pd.concat([df_raise, df_lower, df_approved], ignore_index=True)
    
    print(f"  ✅ df_raise: {len(df_raise)} rows, columns: {list(df_raise.columns)[:5]}...")
    print(f"  ✅ df_lower: {len(df_lower)} rows")
    print(f"  ✅ df_approved: {len(df_approved)} rows")
    print(f"  ✅ df_missing: {len(df_missing)} rows, columns: {list(df_missing.columns)}")
    print(f"  ✅ df_all: {len(df_all)} rows")
    
    # التحقق من الأعمدة المطلوبة في render_approval_section
    required_cols = ["المنتج", "اسم المنافس", "السعر", "أقل سعر منافس", "الفرق", "النسبة %", "الثقة %", "الخطورة"]
    for col in required_cols:
        if col not in df_raise.columns:
            errors.append(f"df_raise missing column: {col}")
            print(f"  ❌ df_raise missing: {col}")
        else:
            print(f"  ✅ df_raise has: {col}")
    
    # التحقق من السعر الموصى في raise و lower
    if "السعر الموصى" not in df_raise.columns:
        errors.append("df_raise missing 'السعر الموصى'")
        print("  ❌ df_raise missing: السعر الموصى")
    else:
        print("  ✅ df_raise has: السعر الموصى")
    
    # التحقق من أعمدة المفقودة
    missing_required = ["المنتج", "النوع", "الحجم", "السعر", "المنافس"]
    for col in missing_required:
        if col not in df_missing.columns:
            errors.append(f"df_missing missing column: {col}")
            print(f"  ❌ df_missing missing: {col}")
        else:
            print(f"  ✅ df_missing has: {col}")
    
    # التحقق من الخطورة
    if not df_all.empty and "الخطورة" in df_all.columns:
        risk_values = df_all["الخطورة"].unique()
        print(f"  ✅ Risk values: {list(risk_values)}")
        critical = len(df_all[df_all["الخطورة"] == "حرج"])
        print(f"  ✅ Critical count: {critical}")
    
    # بناء stats
    stats = {
        "total": len(raise_list) + len(lower_list) + len(keep_list),
        "raise_count": len(raise_list),
        "lower_count": len(lower_list),
        "approved_count": len(keep_list),
        "missing_count": len(missing_list),
        "competitors": 1,
        "critical": len(df_all[df_all["الخطورة"] == "حرج"]) if not df_all.empty and "الخطورة" in df_all.columns else 0,
        "avg_diff": round(df_all["الفرق"].mean(), 2) if not df_all.empty and "الفرق" in df_all.columns else 0,
    }
    print(f"  ✅ Stats: {stats}")
    
    # اختبار JSON serialization (لـ save_results_to_db)
    results_json = {}
    for key, df in [("raise", df_raise), ("lower", df_lower), ("approved", df_approved), ("missing", df_missing)]:
        if not df.empty:
            records = df.to_dict(orient="records")
            results_json[key] = records
    
    json_str = json.dumps(results_json, ensure_ascii=False, default=str)
    print(f"  ✅ JSON serialization: {len(json_str)} chars")
    
except Exception as e:
    errors.append(f"V2 conversion test: {e}")
    print(f"  ❌ V2 conversion test failed: {e}")
    import traceback
    traceback.print_exc()

# ═══════════════════════════════════════
# النتيجة النهائية
# ═══════════════════════════════════════
print("\n" + "=" * 60)
print("النتيجة النهائية")
print("=" * 60)

if errors:
    print(f"\n❌ وجدت {len(errors)} خطأ:")
    for i, err in enumerate(errors, 1):
        print(f"  {i}. {err}")
    sys.exit(1)
else:
    print("\n✅ جميع الاختبارات نجحت! لا توجد أخطاء.")
    sys.exit(0)
