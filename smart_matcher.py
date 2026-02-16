"""
محرك المطابقة الذكي متعدد المستويات
يستخدم التقسيم الذكي لتحسين الدقة والسرعة
"""

import pandas as pd
from collections import defaultdict
from smart_classifier import create_product_signature
from brand_matcher import load_brands


def create_smart_groups(df, brands_list):
    """
    تقسيم المنتجات إلى مجموعات ذكية متعددة المستويات
    
    المستويات:
    1. النوع (male/female/unisex)
    2. الحجم (small/medium/large)
    3. الماركة
    4. التركيز (edp/edt/parfum/etc.)
    5. نوع المنتج (perfume/tester/set)
    
    Returns:
        dict: {signature: [product_indices]}
    """
    print("🔄 بناء المجموعات الذكية...")
    
    groups = defaultdict(list)
    
    for idx, row in df.iterrows():
        product_name = str(row.get('اسم المنتج', ''))
        
        # تصنيف المنتج
        classification = create_product_signature(product_name, brands_list)
        signature = classification['signature']
        
        # إضافة المنتج للمجموعة المناسبة
        groups[signature].append(idx)
    
    print(f"✅ تم إنشاء {len(groups)} مجموعة ذكية")
    
    # إحصائيات
    group_sizes = [len(indices) for indices in groups.values()]
    print(f"📊 متوسط حجم المجموعة: {sum(group_sizes) / len(group_sizes):.1f}")
    print(f"📊 أكبر مجموعة: {max(group_sizes)} منتج")
    print(f"📊 أصغر مجموعة: {min(group_sizes)} منتج")
    
    return groups


def match_within_groups(store_df, competitor_df, brands_list, progress_callback=None):
    """
    مطابقة المنتجات داخل نفس المجموعات فقط
    
    Args:
        store_df: DataFrame للمتجر
        competitor_df: DataFrame للمنافس
        brands_list: قائمة الماركات
        progress_callback: دالة لتحديث التقدم
    
    Returns:
        list: قائمة المطابقات
    """
    print("\n🚀 بدء المطابقة الذكية...")
    
    # بناء المجموعات
    print("\n📦 تجميع منتجات المتجر...")
    store_groups = create_smart_groups(store_df, brands_list)
    
    print("\n📦 تجميع منتجات المنافس...")
    competitor_groups = create_smart_groups(competitor_df, brands_list)
    
    # إيجاد المجموعات المشتركة
    common_signatures = set(store_groups.keys()) & set(competitor_groups.keys())
    print(f"\n🔗 عدد المجموعات المشتركة: {len(common_signatures)}")
    
    # حساب إجمالي المقارنات
    total_comparisons = 0
    for sig in common_signatures:
        total_comparisons += len(store_groups[sig]) * len(competitor_groups[sig])
    
    print(f"📊 إجمالي المقارنات المطلوبة: {total_comparisons:,}")
    
    # المطابقة
    matches = []
    comparisons_done = 0
    
    for sig_idx, signature in enumerate(common_signatures, 1):
        store_indices = store_groups[signature]
        competitor_indices = competitor_groups[signature]
        
        print(f"\n🔍 [{sig_idx}/{len(common_signatures)}] معالجة المجموعة: {signature}")
        print(f"   المتجر: {len(store_indices)} منتج | المنافس: {len(competitor_indices)} منتج")
        
        # مقارنة داخل المجموعة
        for store_idx in store_indices:
            store_product = store_df.iloc[store_idx]['اسم المنتج']
            store_price = store_df.iloc[store_idx].get('السعر', 0)
            
            for comp_idx in competitor_indices:
                comp_product = competitor_df.iloc[comp_idx]['اسم المنتج']
                comp_price = competitor_df.iloc[comp_idx].get('السعر', 0)
                
                # مطابقة بسيطة (يمكن تحسينها لاحقاً)
                if are_similar_products(store_product, comp_product):
                    matches.append({
                        'store_product': store_product,
                        'store_price': store_price,
                        'competitor_product': comp_product,
                        'competitor_price': comp_price,
                        'signature': signature
                    })
                
                comparisons_done += 1
                
                # تحديث التقدم
                if progress_callback and comparisons_done % 100 == 0:
                    progress = (comparisons_done / total_comparisons) * 100
                    progress_callback(progress, comparisons_done, total_comparisons)
    
    print(f"\n✅ اكتملت المطابقة! تم إيجاد {len(matches)} مطابقة")
    return matches


def are_similar_products(product1, product2, threshold=85):
    """
    التحقق من تشابه منتجين باستخدام fuzzywuzzy
    """
    from rapidfuzz import fuzz
    
    # إزالة المسافات الزائدة وتوحيد الحالة
    p1 = ' '.join(str(product1).lower().split())
    p2 = ' '.join(str(product2).lower().split())
    
    # مطابقة سريعة
    ratio = fuzz.ratio(p1, p2)
    return ratio >= threshold


def analyze_matches(matches):
    """
    تحليل نتائج المطابقة
    """
    if not matches:
        print("⚠️ لا توجد مطابقات!")
        return
    
    df = pd.DataFrame(matches)
    
    print("\n📊 تحليل النتائج:")
    print(f"✅ إجمالي المطابقات: {len(matches)}")
    
    # تحليل حسب التوقيع
    print("\n📋 توزيع المطابقات حسب التوقيع:")
    signature_counts = df['signature'].value_counts()
    for sig, count in signature_counts.head(10).items():
        print(f"   {sig}: {count} مطابقة")
    
    # تحليل الأسعار
    df['price_diff'] = df['store_price'] - df['competitor_price']
    df['price_diff_percent'] = (df['price_diff'] / df['competitor_price'] * 100).round(2)
    
    print("\n💰 تحليل الأسعار:")
    print(f"   متوسط فرق السعر: {df['price_diff'].mean():.2f} ريال")
    print(f"   متوسط نسبة الفرق: {df['price_diff_percent'].mean():.2f}%")
    
    higher_price = len(df[df['price_diff'] > 0])
    lower_price = len(df[df['price_diff'] < 0])
    same_price = len(df[df['price_diff'] == 0])
    
    print(f"   أعلى من المنافس: {higher_price} ({higher_price/len(df)*100:.1f}%)")
    print(f"   أقل من المنافس: {lower_price} ({lower_price/len(df)*100:.1f}%)")
    print(f"   نفس السعر: {same_price} ({same_price/len(df)*100:.1f}%)")
    
    return df


if __name__ == "__main__":
    print("🧪 اختبار محرك المطابقة الذكي")
    print("=" * 50)
    
    # إنشاء بيانات تجريبية
    store_data = {
        'اسم المنتج': [
            'عطر شانيل بلو دي شانيل الرجالي او دو بارفيوم 100مل',
            'عطر ديور سوفاج الرجالي او دو تواليت 60مل',
            'عطر لانكوم لا في است بيل النسائي او دو بارفيوم 50مل',
        ],
        'السعر': [450, 380, 420]
    }
    
    competitor_data = {
        'اسم المنتج': [
            'عطر شانيل بلو دي شانيل الرجالي او دو بارفيوم 100مل',
            'عطر ديور سوفاج الرجالي او دو تواليت 60مل',
            'عطر توم فورد بلاك اوركيد النسائي او دو بارفيوم 100مل',
        ],
        'السعر': [430, 390, 550]
    }
    
    store_df = pd.DataFrame(store_data)
    competitor_df = pd.DataFrame(competitor_data)
    
    # تحميل الماركات
    brands = load_brands()
    
    # المطابقة
    matches = match_within_groups(
        store_df,
        competitor_df,
        brands
    )
    
    # التحليل
    analyze_matches(matches)
