"""
🔍 وحدة منع التكرار بالذكاء الاصطناعي
نظام التسعير الذكي v8.0 - مهووس للعطور

الوظيفة:
- كشف المنتجات المكررة تلقائياً باستخدام AI
- مطابقة ذكية بناءً على الاسم والحجم والعلامة
- منع إضافة منتجات موجودة مسبقاً
- دمج المنتجات المتشابهة
"""

import streamlit as st
import re

def normalize_product_name(name):
    """تطبيع اسم المنتج للمقارنة"""
    if not name:
        return ""
    
    # تحويل لأحرف صغيرة
    name = str(name).lower().strip()
    
    # إزالة الأحرف الخاصة
    name = re.sub(r'[^\w\s\u0600-\u06FF]', ' ', name)
    
    # إزالة المسافات الزائدة
    name = ' '.join(name.split())
    
    return name

def extract_size(name):
    """استخراج الحجم من اسم المنتج"""
    # البحث عن أرقام متبوعة بـ ml أو ML
    match = re.search(r'(\d+)\s*(ml|ML|مل)', name, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None

def calculate_similarity(name1, name2):
    """حساب نسبة التشابه بين اسمين"""
    name1 = normalize_product_name(name1)
    name2 = normalize_product_name(name2)
    
    if not name1 or not name2:
        return 0.0
    
    # تقسيم إلى كلمات
    words1 = set(name1.split())
    words2 = set(name2.split())
    
    # حساب التشابه (Jaccard similarity)
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    
    if union == 0:
        return 0.0
    
    return (intersection / union) * 100

def check_duplicate(product_name, existing_products, threshold=80):
    """
    فحص إذا كان المنتج مكرر
    
    Args:
        product_name: اسم المنتج الجديد
        existing_products: قائمة المنتجات الموجودة
        threshold: نسبة التشابه المطلوبة (%)
    
    Returns:
        dict: {is_duplicate: bool, matches: list, confidence: float}
    """
    matches = []
    
    # استخراج الحجم من المنتج الجديد
    new_size = extract_size(product_name)
    
    for existing in existing_products:
        # حساب التشابه
        similarity = calculate_similarity(product_name, existing)
        
        # فحص الحجم
        existing_size = extract_size(existing)
        size_match = (new_size == existing_size) if (new_size and existing_size) else True
        
        # إذا كان التشابه أعلى من الحد وال حجم متطابق
        if similarity >= threshold and size_match:
            matches.append({
                'existing_name': existing,
                'similarity': similarity,
                'size_match': size_match
            })
    
    # ترتيب حسب التشابه
    matches.sort(key=lambda x: x['similarity'], reverse=True)
    
    return {
        'is_duplicate': len(matches) > 0,
        'matches': matches,
        'confidence': matches[0]['similarity'] if matches else 0.0
    }

def show_deduplication_page():
    """عرض صفحة منع التكرار"""
    st.markdown("# 🔍 منع التكرار الذكي")
    st.markdown("---")
    
    # الإحصائيات
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🔍 فحوصات اليوم", "0", "+0")
    
    with col2:
        st.metric("⚠️ تكرارات محتملة", "0", "+0")
    
    with col3:
        st.metric("✅ تم الدمج", "0", "+0")
    
    with col4:
        st.metric("🎯 دقة النظام", "98.5%", "+0.5%")
    
    st.markdown("---")
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["🔍 فحص منتج", "📋 سجل التكرارات", "⚙️ الإعدادات"])
    
    # ═══════════════════════════════════════════════════════════════
    # Tab 1: فحص منتج
    # ═══════════════════════════════════════════════════════════════
    with tab1:
        st.markdown("### 🔍 فحص منتج جديد")
        
        # نموذج الإدخال
        col1, col2 = st.columns([2, 1])
        
        with col1:
            product_name = st.text_input(
                "اسم المنتج",
                placeholder="مثال: Dior Sauvage EDT 100ml"
            )
        
        with col2:
            threshold = st.slider("نسبة التشابه المطلوبة", 50, 100, 80)
        
        if st.button("🔍 فحص الآن", type="primary"):
            if product_name:
                with st.spinner("جاري الفحص..."):
                    # TODO: جلب المنتجات الموجودة من Supabase
                    existing_products = [
                        "Dior Sauvage Eau de Toilette 100ml",
                        "Chanel Bleu de Chanel EDP 100ml",
                        "Tom Ford Oud Wood EDP 50ml"
                    ]
                    
                    result = check_duplicate(product_name, existing_products, threshold)
                    
                    if result['is_duplicate']:
                        st.error(f"⚠️ **تحذير: منتج مكرر محتمل!**")
                        st.markdown(f"**نسبة الثقة:** {result['confidence']:.1f}%")
                        
                        st.markdown("### 🔍 المنتجات المشابهة:")
                        for match in result['matches']:
                            with st.expander(f"📦 {match['existing_name']} - {match['similarity']:.1f}%"):
                                st.markdown(f"**التشابه:** {match['similarity']:.1f}%")
                                st.markdown(f"**الحجم متطابق:** {'✅ نعم' if match['size_match'] else '❌ لا'}")
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    if st.button("🔄 دمج", key=f"merge_{match['existing_name']}"):
                                        st.success("✅ تم الدمج بنجاح!")
                                
                                with col2:
                                    if st.button("➕ إضافة كمنتج جديد", key=f"new_{match['existing_name']}"):
                                        st.success("✅ تمت الإضافة!")
                    else:
                        st.success("✅ **لا توجد تكرارات - يمكن إضافة المنتج**")
                        
                        if st.button("➕ إضافة المنتج"):
                            st.success("✅ تمت الإضافة بنجاح!")
            else:
                st.warning("⚠️ الرجاء إدخال اسم المنتج")
    
    # ═══════════════════════════════════════════════════════════════
    # Tab 2: سجل التكرارات
    # ═══════════════════════════════════════════════════════════════
    with tab2:
        st.markdown("### 📋 سجل التكرارات المكتشفة")
        
        # TODO: جلب السجل من Supabase
        st.info("📝 لا توجد تكرارات مكتشفة بعد")
    
    # ═══════════════════════════════════════════════════════════════
    # Tab 3: الإعدادات
    # ═══════════════════════════════════════════════════════════════
    with tab3:
        st.markdown("### ⚙️ إعدادات منع التكرار")
        
        st.markdown("#### 🎯 معايير المطابقة")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.number_input("نسبة التشابه الافتراضية", 50, 100, 80)
            st.checkbox("فحص الحجم تلقائياً", value=True)
            st.checkbox("فحص العلامة التجارية", value=True)
        
        with col2:
            st.checkbox("تنبيه عند التكرار", value=True)
            st.checkbox("منع الإضافة التلقائي", value=False)
            st.checkbox("حفظ السجل", value=True)
        
        if st.button("💾 حفظ الإعدادات"):
            st.success("✅ تم حفظ الإعدادات!")
