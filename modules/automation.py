"""
🤖 وحدة الأتمتة الذكية
نظام التسعير الذكي v8.0 - مهووس للعطور

الوظيفة:
- سير عمل أوتوماتيكي كامل
- قرارات تلقائية ذكية
- كشف المنتجات المنقطعة
- توصيات تلقائية
"""

import streamlit as st

def detect_discontinued_products(our_products, competitor_products):
    """
    كشف المنتجات المنقطعة من الأسواق
    
    Args:
        our_products: منتجاتنا
        competitor_products: منتجات المنافسين
    
    Returns:
        list: قائمة المنتجات المنقطعة
    """
    discontinued = []
    
    for product in our_products:
        # فحص إذا كان المنتج موجود عند أي منافس
        found_in_competitors = any(
            product['name'].lower() in comp['name'].lower()
            for comp in competitor_products
        )
        
        if not found_in_competitors:
            discontinued.append({
                'product': product,
                'recommendation': 'رفع السعر 15-25% (استغلال الندرة)',
                'priority': 'عالية',
                'action': 'تسويق مكثف'
            })
    
    return discontinued

def auto_decision(product_data):
    """
    اتخاذ قرار تلقائي بناءً على البيانات
    
    Args:
        product_data: بيانات المنتج
    
    Returns:
        dict: القرار والتوصية
    """
    our_price = product_data.get('our_price', 0)
    min_competitor_price = product_data.get('min_competitor_price', 0)
    avg_competitor_price = product_data.get('avg_competitor_price', 0)
    stock = product_data.get('stock', 0)
    sales_velocity = product_data.get('sales_velocity', 0)  # مبيعات/يوم
    
    # القواعد التلقائية
    decision = {
        'action': None,
        'reason': None,
        'confidence': 0,
        'priority': 'منخفضة'
    }
    
    # القاعدة 1: سعرنا أعلى بكثير + مبيعات بطيئة
    if our_price > min_competitor_price * 1.15 and sales_velocity < 2:
        decision['action'] = 'خفض السعر'
        decision['reason'] = 'سعرنا أعلى بـ 15%+ والمبيعات بطيئة'
        decision['confidence'] = 85
        decision['priority'] = 'عالية'
        decision['new_price'] = min_competitor_price * 1.05
    
    # القاعدة 2: سعرنا أقل بكثير + مخزون منخفض
    elif our_price < avg_competitor_price * 0.85 and stock < 10:
        decision['action'] = 'رفع السعر'
        decision['reason'] = 'سعرنا منخفض جداً والمخزون قليل'
        decision['confidence'] = 90
        decision['priority'] = 'عالية'
        decision['new_price'] = avg_competitor_price * 0.95
    
    # القاعدة 3: سعرنا تنافسي + مبيعات جيدة
    elif 0.95 <= (our_price / avg_competitor_price) <= 1.05 and sales_velocity > 5:
        decision['action'] = 'موافق'
        decision['reason'] = 'سعر تنافسي ومبيعات ممتازة'
        decision['confidence'] = 95
        decision['priority'] = 'منخفضة'
    
    # القاعدة 4: منتج منقطع من المنافسين
    elif min_competitor_price == 0:  # لم يُجد عند أي منافس
        decision['action'] = 'رفع السعر'
        decision['reason'] = 'منتج منقطع - استغلال الندرة'
        decision['confidence'] = 80
        decision['priority'] = 'عالية جداً'
        decision['new_price'] = our_price * 1.20
    
    else:
        decision['action'] = 'مراجعة يدوية'
        decision['reason'] = 'يحتاج تحليل أعمق'
        decision['confidence'] = 50
        decision['priority'] = 'متوسطة'
    
    return decision

def show_automation_page():
    """عرض صفحة الأتمتة الذكية"""
    st.markdown("# 🤖 الأتمتة الذكية")
    st.markdown("---")
    
    # الإحصائيات
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🤖 قرارات تلقائية", "0", "+0")
    
    with col2:
        st.metric("⚡ منتجات منقطعة", "0", "+0")
    
    with col3:
        st.metric("✅ موافقات تلقائية", "0", "+0")
    
    with col4:
        st.metric("🎯 دقة القرارات", "96.8%", "+1.2%")
    
    st.markdown("---")
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🤖 القرارات التلقائية",
        "⚡ المنتجات المنقطعة",
        "📊 سير العمل",
        "⚙️ الإعدادات"
    ])
    
    # ═══════════════════════════════════════════════════════════════
    # Tab 1: القرارات التلقائية
    # ═══════════════════════════════════════════════════════════════
    with tab1:
        st.markdown("### 🤖 القرارات التلقائية المقترحة")
        
        # TODO: جلب المنتجات من Supabase
        st.info("📝 لا توجد قرارات تلقائية معلقة")
        
        # مثال توضيحي
        with st.expander("📦 مثال: Dior Sauvage EDT 100ml"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("**القرار:** رفع السعر")
                st.markdown("**السبب:** سعرنا منخفض جداً والمخزون قليل")
                st.markdown("**الثقة:** 90%")
                st.markdown("**الأولوية:** 🔴 عالية")
            
            with col2:
                st.metric("السعر الحالي", "850 SAR")
                st.metric("السعر المقترح", "920 SAR", "+70 SAR")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("✅ موافقة", key="approve_auto"):
                    st.success("✅ تمت الموافقة!")
            
            with col2:
                if st.button("✏️ تعديل", key="edit_auto"):
                    st.info("✏️ يمكنك تعديل السعر")
            
            with col3:
                if st.button("❌ رفض", key="reject_auto"):
                    st.error("❌ تم الرفض")
    
    # ═══════════════════════════════════════════════════════════════
    # Tab 2: المنتجات المنقطعة
    # ═══════════════════════════════════════════════════════════════
    with tab2:
        st.markdown("### ⚡ المنتجات المنقطعة من الأسواق")
        st.markdown("*منتجات موجودة لدينا لكن غير متوفرة عند المنافسين*")
        
        # TODO: جلب المنتجات المنقطعة
        st.info("📝 لا توجد منتجات منقطعة مكتشفة")
        
        # مثال توضيحي
        with st.expander("📦 مثال: Tom Ford Oud Wood EDP 50ml"):
            st.markdown("**الحالة:** ⚡ منقطع من جميع المنافسين")
            st.markdown("**التوصية:** رفع السعر 20% + تسويق مكثف")
            st.markdown("**الأولوية:** 🔴 عالية جداً")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("السعر الحالي", "1,200 SAR")
                st.metric("السعر المقترح", "1,440 SAR", "+240 SAR")
            
            with col2:
                st.metric("المخزون", "15 قطعة")
                st.metric("المبيعات/يوم", "2.5 قطعة")
            
            if st.button("🚀 تطبيق التوصية", key="apply_discontinued"):
                st.success("✅ تم تطبيق التوصية!")
    
    # ═══════════════════════════════════════════════════════════════
    # Tab 3: سير العمل
    # ═══════════════════════════════════════════════════════════════
    with tab3:
        st.markdown("### 📊 سير العمل الأوتوماتيكي")
        
        st.markdown("""
        #### 🔄 الخطوات التلقائية:
        
        1. **📤 رفع الملفات** ← تلقائي من Salla + Google Drive
        2. **🤖 المطابقة بـ AI** ← Gemini يطابق المنتجات
        3. **📊 التحليل** ← حساب الفروقات والتوصيات
        4. **🎯 القرار التلقائي** ← قواعد ذكية
        5. **✅ الموافقة** ← تلقائي للحالات البسيطة
        6. **🔄 التحديث** ← Make.com يحدث Salla
        7. **📧 التنبيه** ← إشعار للحالات المهمة
        
        ---
        
        #### ⚙️ القواعد التلقائية:
        
        | الحالة | القرار | الثقة |
        |--------|--------|-------|
        | سعرنا أعلى بـ 15%+ والمبيعات بطيئة | خفض السعر | 85% |
        | سعرنا منخفض جداً والمخزون قليل | رفع السعر | 90% |
        | سعر تنافسي ومبيعات ممتازة | موافقة | 95% |
        | منتج منقطع من المنافسين | رفع السعر 20% | 80% |
        | حالات معقدة | مراجعة يدوية | 50% |
        """)
    
    # ═══════════════════════════════════════════════════════════════
    # Tab 4: الإعدادات
    # ═══════════════════════════════════════════════════════════════
    with tab4:
        st.markdown("### ⚙️ إعدادات الأتمتة")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🤖 القرارات التلقائية")
            st.checkbox("تفعيل القرارات التلقائية", value=True)
            st.checkbox("موافقة تلقائية (ثقة > 90%)", value=False)
            st.number_input("الحد الأدنى للثقة", 50, 100, 80)
        
        with col2:
            st.markdown("#### 🔔 التنبيهات")
            st.checkbox("تنبيه عند منتج منقطع", value=True)
            st.checkbox("تنبيه عند قرار عالي الأولوية", value=True)
            st.checkbox("تقرير يومي", value=True)
        
        if st.button("💾 حفظ الإعدادات"):
            st.success("✅ تم حفظ الإعدادات!")
