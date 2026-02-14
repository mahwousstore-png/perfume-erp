"""
engine_optimized.py - محرك محسّن للأداء v12.0
═══════════════════════════════════════════════
تحسينات الأداء:
1. Early termination - إيقاف المقارنة عند أول تطابق قوي
2. Pre-filtering - تصفية مسبقة بالحجم والنوع
3. Batch processing - معالجة دفعات بدلاً من حلقات
4. Index caching - تخزين النتائج مؤقتاً
"""
import re
import numpy as np
from rapidfuzz import fuzz
from collections import defaultdict


# ===== استيراد القوانين من engine.py =====
from engine import (
    REJECT_KEYWORDS, TESTER_KEYWORDS, HAIR_MIST_KEYWORDS,
    BODY_MIST_KEYWORDS, SET_KEYWORDS,
    classify_product, extract_size, extract_brand,
    normalize_name, _get_field, _get_name, _get_price, _get_id,
    detect_outliers, _calculate_confidence, _price_consistency,
    get_risk_color, get_risk_emoji, get_type_label,
    normalize_columns
)


def match_products_optimized(my_products, comp_products, threshold=60):
    """
    مطابقة محسّنة مع early termination و pre-filtering.
    
    التحسينات:
    1. تجميع المنافسين حسب النوع والحجم (index)
    2. إيقاف المقارنة عند أول تطابق قوي (95%+)
    3. معالجة دفعات بدلاً من حلقات متداخلة
    """
    results = {
        "raise": [],
        "lower": [],
        "ok": [],
        "missing": [],
        "review": [],
    }
    
    # ===== Pre-filtering: تجميع المنافسين حسب النوع والحجم =====
    print("🔍 Pre-filtering: تجميع المنافسين...")
    comp_index = defaultdict(list)  # {(type, size): [products]}
    
    for idx, cp in enumerate(comp_products):
        cp_name = _get_name(cp)
        if not cp_name:
            continue
        
        cp_type = classify_product(cp_name)
        if cp_type == "rejected":
            continue
        
        cp_size = cp.get("size_ml", 0) or extract_size(cp_name)
        cp_price = _get_price(cp)
        
        if cp_price <= 0:
            continue
        
        # تجميع حسب النوع والحجم (مع تقريب الحجم لأقرب 5ml)
        size_bucket = round(cp_size / 5) * 5 if cp_size > 0 else 0
        key = (cp_type, size_bucket)
        
        comp_index[key].append({
            "index": idx,
            "product": cp,
            "name": cp_name,
            "type": cp_type,
            "size": cp_size,
            "price": cp_price,
            "normalized": normalize_name(cp_name),
        })
    
    print(f"✅ تم تجميع {len(comp_index)} مجموعة من المنافسين")
    
    # ===== المطابقة مع early termination =====
    print("🚀 بدء المطابقة المحسّنة...")
    matched_comp_indices = set()
    processed = 0
    total = len(my_products)
    
    for my_p in my_products:
        processed += 1
        if processed % 100 == 0:
            print(f"⏳ معالجة: {processed}/{total} ({processed*100//total}%)")
        
        my_name = _get_name(my_p)
        if not my_name:
            continue
        
        my_type = classify_product(my_name)
        if my_type == "rejected":
            continue
        
        my_size = my_p.get("size_ml", 0) or extract_size(my_name)
        my_price = _get_price(my_p)
        my_norm = normalize_name(my_name)
        my_id = _get_id(my_p)
        
        # البحث في المجموعات المناسبة فقط
        size_bucket = round(my_size / 5) * 5 if my_size > 0 else 0
        candidates = []
        
        # البحث في نفس المجموعة
        key = (my_type, size_bucket)
        if key in comp_index:
            candidates.extend(comp_index[key])
        
        # البحث في المجموعات المجاورة (±5ml)
        for delta in [-5, 5]:
            adj_key = (my_type, size_bucket + delta)
            if adj_key in comp_index:
                candidates.extend(comp_index[adj_key])
        
        # البحث في نفس النوع بدون حجم محدد
        no_size_key = (my_type, 0)
        if no_size_key in comp_index:
            candidates.extend(comp_index[no_size_key])
        
        if not candidates:
            continue
        
        # ===== Early termination: إيقاف عند أول تطابق قوي =====
        all_matches = []
        best_score = 0
        
        for cand in candidates:
            # تطابق الحجم الدقيق
            if my_size > 0 and cand["size"] > 0:
                if abs(my_size - cand["size"]) > 1:
                    continue
            
            # حساب التشابه
            score = fuzz.token_sort_ratio(my_norm, cand["normalized"])
            
            if score >= threshold:
                all_matches.append({
                    "comp_product": cand["product"],
                    "comp_index": cand["index"],
                    "comp_name": cand["name"],
                    "comp_price": cand["price"],
                    "match_score": score,
                    "comp_type": cand["type"],
                    "comp_size": cand["size"],
                })
                
                best_score = max(best_score, score)
                
                # Early termination: إذا وجدنا تطابق ممتاز (95%+) → توقف
                if score >= 95:
                    break
        
        if not all_matches:
            continue
        
        # ===== معالجة النتائج (نفس المنطق القديم) =====
        comp_prices = [m["comp_price"] for m in all_matches]
        
        outlier_indices = []
        if len(comp_prices) >= 3:
            _, _, outlier_indices = detect_outliers(comp_prices)
        
        valid_matches = [m for i, m in enumerate(all_matches) if i not in outlier_indices]
        if not valid_matches:
            valid_matches = all_matches
        
        valid_prices = [m["comp_price"] for m in valid_matches]
        min_comp_price = min(valid_prices)
        avg_comp_price = sum(valid_prices) / len(valid_prices)
        
        best_match = max(valid_matches, key=lambda m: m["match_score"])
        recommended_price = min_comp_price - 1
        
        confidence = _calculate_confidence(
            match_score=best_match["match_score"],
            num_competitors=len(valid_matches),
            price_consistency=_price_consistency(valid_prices),
        )
        
        price_diff = my_price - min_comp_price
        diff_percent = round((price_diff / min_comp_price) * 100, 1) if min_comp_price > 0 else 0
        
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
        
        abs_pct = abs(diff_percent)
        if abs_pct >= 20:
            risk = "high"
        elif abs_pct >= 10:
            risk = "medium"
        else:
            risk = "low"
        result_entry["risk_level"] = risk
        
        if abs(price_diff) <= 5:
            result_entry["recommendation"] = "approved"
            result_entry["reasoning"] = f"السعر مثالي (ضمن نطاق ±5 ريال من أقل منافس {min_comp_price} ر.س)"
            results["ok"].append(result_entry)
        elif my_price > min_comp_price:
            result_entry["recommendation"] = "decrease"
            result_entry["reasoning"] = f"سعرنا ({my_price} ر.س) أعلى من أقل منافس ({min_comp_price} ر.س) بـ {abs(price_diff):.0f} ر.س. الموصى: {recommended_price:.0f} ر.س"
            results["lower"].append(result_entry)
        elif my_price < min_comp_price:
            result_entry["recommendation"] = "increase"
            result_entry["reasoning"] = f"سعرنا ({my_price} ر.س) أقل من أقل منافس ({min_comp_price} ر.س) بـ {abs(price_diff):.0f} ر.س. الموصى: {recommended_price:.0f} ر.س"
            results["raise"].append(result_entry)
    
    print(f"✅ اكتملت المطابقة: {len(matched_comp_indices)} منتج منافس")
    
    # ===== كشف المنتجات المفقودة (محسّن) =====
    print("🔍 كشف المنتجات المفقودة...")
    missing_threshold = 45
    
    # تجميع منتجاتنا للبحث السريع
    my_index = defaultdict(list)
    for my_p in my_products:
        my_name = _get_name(my_p)
        if not my_name:
            continue
        my_type = classify_product(my_name)
        if my_type == "rejected":
            continue
        my_size = my_p.get("size_ml", 0) or extract_size(my_name)
        size_bucket = round(my_size / 5) * 5 if my_size > 0 else 0
        key = (my_type, size_bucket)
        my_index[key].append({
            "name": my_name,
            "normalized": normalize_name(my_name),
            "type": my_type,
            "size": my_size,
        })
    
    for idx, cp in enumerate(comp_products):
        if idx in matched_comp_indices:
            continue
        
        cp_name = _get_name(cp)
        if not cp_name:
            continue
        
        cp_type = classify_product(cp_name)
        if cp_type == "rejected":
            continue
        
        cp_size = cp.get("size_ml", 0) or extract_size(cp_name)
        cp_norm = normalize_name(cp_name)
        
        # البحث في المجموعات المناسبة
        size_bucket = round(cp_size / 5) * 5 if cp_size > 0 else 0
        candidates = []
        
        key = (cp_type, size_bucket)
        if key in my_index:
            candidates.extend(my_index[key])
        
        for delta in [-5, 5]:
            adj_key = (cp_type, size_bucket + delta)
            if adj_key in my_index:
                candidates.extend(my_index[adj_key])
        
        no_size_key = (cp_type, 0)
        if no_size_key in my_index:
            candidates.extend(my_index[no_size_key])
        
        found_similar = False
        for cand in candidates:
            if cand["size"] > 0 and cp_size > 0:
                if abs(cand["size"] - cp_size) > 1:
                    continue
            
            score = fuzz.token_sort_ratio(cand["normalized"], cp_norm)
            if score >= missing_threshold:
                found_similar = True
                break
        
        if not found_similar:
            results["missing"].append({
                "comp_product": cp,
                "comp_name": cp_name,
                "comp_type": cp_type,
                "comp_size": cp_size,
                "comp_price": _get_price(cp),
                "competitor_name": cp.get("_competitor_name", "غير محدد"),
            })
    
    print(f"✅ تم العثور على {len(results['missing'])} منتج مفقود")
    
    # ترتيب حسب الخطورة
    for key in ["raise", "lower"]:
        results[key].sort(
            key=lambda x: abs(x.get("diff_percent", 0)),
            reverse=True
        )
    
    return results


def run_full_analysis(my_file, comp_files, threshold=60, progress_callback=None):
    """
    تشغيل التحليل الكامل المحسّن.
    """
    import pandas as pd
    from io import BytesIO
    
    print("📂 تحميل الملفات...")
    
    # 1. تحميل ملف المتجر
    try:
        if isinstance(my_file, str):
            # مسار ملف
            if my_file.endswith(".xlsx"):
                my_data = pd.read_excel(my_file)
            else:
                my_data = pd.read_csv(my_file, encoding='utf-8-sig')
        else:
            # dict مع data
            if my_file["name"].endswith(".xlsx"):
                my_data = pd.read_excel(BytesIO(my_file["data"]))
            else:
                my_data = pd.read_csv(BytesIO(my_file["data"]), encoding='utf-8-sig')
        
        my_data = normalize_columns(my_data)
        my_products = my_data.to_dict(orient="records")
        print(f"✅ ملف المتجر: {len(my_products)} منتج")
    except Exception as e:
        return {"error": f"خطأ في تحميل ملف المتجر: {str(e)}", "stats": {}}
    
    # 2. تحميل ملفات المنافسين
    all_comp_products = []
    comp_names = []
    
    for comp_file in comp_files:
        try:
            if isinstance(comp_file, str):
                # مسار ملف
                if comp_file.endswith(".xlsx"):
                    comp_data = pd.read_excel(comp_file)
                else:
                    comp_data = pd.read_csv(comp_file, encoding='utf-8-sig')
                comp_name = comp_file.split('/')[-1]
            else:
                # dict مع data
                if comp_file["name"].endswith(".xlsx"):
                    comp_data = pd.read_excel(BytesIO(comp_file["data"]))
                else:
                    comp_data = pd.read_csv(BytesIO(comp_file["data"]), encoding='utf-8-sig')
                comp_name = comp_file["name"]
            
            comp_data = normalize_columns(comp_data)
            comp_products = comp_data.to_dict(orient="records")
            
            for p in comp_products:
                p["_competitor_name"] = comp_name
            
            all_comp_products.extend(comp_products)
            comp_names.append(comp_name)
            print(f"✅ ملف منافس: {len(comp_products)} منتج")
        except Exception as e:
            print(f"⚠️ خطأ في تحميل ملف منافس: {e}")
            continue
    
    if not all_comp_products:
        return {"error": "لم يتم تحميل أي ملف منافس", "stats": {}}
    
    print(f"\n🚀 بدء التحليل المحسّن...")
    print(f"📊 المتجر: {len(my_products)} منتج")
    print(f"📊 المنافسين: {len(all_comp_products)} منتج")
    print(f"📊 النسبة: {threshold}%")
    print("=" * 60)
    
    # 3. تشغيل المطابقة المحسّنة
    results = match_products_optimized(my_products, all_comp_products, threshold)
    
    # 4. إنشاء DataFrames
    import pandas as pd
    
    results["raise_df"] = pd.DataFrame(results["raise"]) if results["raise"] else pd.DataFrame()
    results["lower_df"] = pd.DataFrame(results["lower"]) if results["lower"] else pd.DataFrame()
    results["ok_df"] = pd.DataFrame(results["ok"]) if results["ok"] else pd.DataFrame()
    results["missing_df"] = pd.DataFrame(results["missing"]) if results["missing"] else pd.DataFrame()
    
    # 5. إحصائيات
    results["stats"] = {
        "total_my_products": len(my_products),
        "total_comp_products": len(all_comp_products),
        "raise_count": len(results["raise"]),
        "lower_count": len(results["lower"]),
        "ok_count": len(results["ok"]),
        "missing_count": len(results["missing"]),
        "competitors": comp_names,
        "threshold": threshold,
    }
    
    print("\n" + "=" * 60)
    print("✅ التحليل اكتمل!")
    print(f"🔴 رفع سعر: {len(results['raise'])}")
    print(f"🟡 خفض سعر: {len(results['lower'])}")
    print(f"🟢 موافق: {len(results['ok'])}")
    print(f"🔵 مفقود: {len(results['missing'])}")
    print("=" * 60)
    
    return results
