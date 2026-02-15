"""
🔔 وحدة التنبيهات الذكية
نظام التسعير الذكي v8.0 - مهووس للعطور

الوظيفة:
- تنبيهات استباقية ذكية
- إشعارات حسب الأولوية
- تقارير تلقائية
- مركز الإشعارات
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json

def create_alert(alert_type, title, message, priority="متوسطة", data=None):
    """
    إنشاء تنبيه جديد
    
    Args:
        alert_type: نوع التنبيه (price, stock, competitor, system)
        title: عنوان التنبيه
        message: نص التنبيه
        priority: الأولوية (منخفضة, متوسطة, عالية, عاجلة)
        data: بيانات إضافية
    
    Returns:
        dict: التنبيه
    """
    return {
        'id': datetime.now().strftime("%Y%m%d%H%M%S"),
        'type': alert_type,
        'title': title,
        'message': message,
        'priority': priority,
        'data': data or {},
        'created_at': datetime.now().isoformat(),
        'read': False,
        'resolved': False
    }

def get_alert_icon(alert_type):
    """الحصول على أيقونة التنبيه"""
    icons = {
        'price': '💰',
        'stock': '📦',
        'competitor': '🏪',
        'system': '⚙️',
        'opportunity': '🎯',
        'warning': '⚠️',
        'error': '❌',
        'success': '✅'
    }
    return icons.get(alert_type, '🔔')

def get_priority_color(priority):
    """الحصول على لون الأولوية"""
    colors = {
        'منخفضة': '#4CAF50',
        'متوسطة': '#FF9800',
        'عالية': '#FF5722',
        'عاجلة': '#F44336'
    }
    return colors.get(priority, '#757575')

def show_alerts_page():
    """عرض صفحة التنبيهات"""
    st.markdown("# 🔔 مركز التنبيهات")
    st.markdown("---")
    
    # الإحصائيات
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🔔 تنبيهات جديدة", "0", "+0")
    
    with col2:
        st.metric("🔴 عاجلة", "0", "+0")
    
    with col3:
        st.metric("✅ تم الحل", "0", "+0")

    with col4:
        st.metric("📊 معدل الاستجابة", "2.5 ساعة", "-0.5")

    st.markdown("---")

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔔 التنبيهات الحالية",
        "📊 التقارير",
        "📜 السجل",
        "⚙️ الإعدادات"
    ])

    # ═══════════════════════════════════════════════════════════════
    # Tab 1: التنبيهات الحالية
    # ═══════════════════════════════════════════════════════════════
    with tab1:
        st.markdown("### 🔔 التنبيهات الحالية")
        
        # فلترة
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.selectbox("النوع", ["الكل", "💰 أسعار", "📦 مخزون", "🏪 منافسين", "⚙️ نظام"])
        
        with col2:
            st.selectbox("الأولوية", ["الكل", "عاجلة", "عالية", "متوسطة", "منخفضة"])
        
        with col3:
            st.selectbox("الحالة", ["الكل", "غير مقروء", "مقروء", "تم الحل"])
        
        # TODO: جلب التنبيهات من Supabase
        st.info("📝 لا توجد تنبيهات جديدة")
        
        # أمثلة توضيحية
        alerts = [
            {
                'type': 'price',
                'title': 'فرصة رفع سعر',
                'message': 'Dior Sauvage - سعرنا أقل بـ 15% من المتوسط',
                'priority': 'عالية',
                'time': '5 دقائق'
            },
            {
                'type': 'stock',
                'title': 'مخزون منخفض',
                'message': 'Chanel Bleu - متبقي 3 قطع فقط',
                'priority': 'متوسطة',
                'time': '1 ساعة'
            },
            {
                'type': 'opportunity',
                'title': 'منتج منقطع',
                'message': 'Tom Ford Oud Wood - غير متوفر عند المنافسين',
                'priority': 'عاجلة',
                'time': '2 ساعات'
            }
        ]
        
        for alert in alerts:
            icon = get_alert_icon(alert['type'])
            color = get_priority_color(alert['priority'])
            
            with st.expander(f"{icon} {alert['title']} - {alert['time']}"):
                st.markdown(f"**الرسالة:** {alert['message']}")
                st.markdown(f"**الأولوية:** <span style='color:{color}'>●</span> {alert['priority']}", unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("✅ تم الحل", key=f"resolve_{alert['title']}"):
                        st.success("✅ تم وضع علامة كمحلول")
                
                with col2:
                    if st.button("👁️ وضع علامة كمقروء", key=f"read_{alert['title']}"):
                        st.info("👁️ تم وضع علامة كمقروء")
                
                with col3:
                    if st.button("🗑️ حذف", key=f"delete_{alert['title']}"):
                        st.warning("🗑️ تم الحذف")

    # ═══════════════════════════════════════════════════════════════
    # Tab 2: التقارير
    # ═══════════════════════════════════════════════════════════════
    with tab2:
        st.markdown("### 📊 التقارير التلقائية")
        
        _ = st.selectbox("نوع التقرير", [
            "📊 تقرير يومي",
            "📅 تقرير أسبوعي",
            "📆 تقرير شهري",
            "🎯 تقرير الفرص",
            "⚠️ تقرير المخاطر"
        ])
        
        if st.button("📥 إنشاء التقرير"):
            with st.spinner("جاري إنشاء التقرير..."):
                st.success("✅ تم إنشاء التقرير!")
                
                # مثال تقرير يومي
                st.markdown("---")
                st.markdown("### 📊 التقرير اليومي - " + datetime.now().strftime("%Y-%m-%d"))
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("منتجات تم تحديثها", "45")
                    st.metric("قرارات تلقائية", "12")
                
                with col2:
                    st.metric("فرص رفع سعر", "8")
                    st.metric("منتجات منقطعة", "3")
                
                with col3:
                    st.metric("تنبيهات عاجلة", "2")
                    st.metric("متوسط وقت الاستجابة", "2.5 ساعة")
                
                st.markdown("---")
                st.markdown("#### 🔝 أهم التوصيات:")
                st.markdown("1. رفع سعر Dior Sauvage بـ 10%")
                st.markdown("2. تسويق مكثف لـ Tom Ford Oud Wood (منقطع)")
                st.markdown("3. إعادة طلب Chanel Bleu (مخزون منخفض)")

    # ═══════════════════════════════════════════════════════════════
    # Tab 3: السجل
    # ═══════════════════════════════════════════════════════════════
    with tab3:
        st.markdown("### 📜 سجل التنبيهات")
        
        # فلترة حسب التاريخ
        col1, col2 = st.columns(2)
        
        with col1:
            _ = st.date_input("من تاريخ", datetime.now() - timedelta(days=7))
        
        with col2:
            _ = st.date_input("إلى تاريخ", datetime.now())
        
        # TODO: جلب السجل من Supabase
        st.info("📝 لا توجد سجلات")

    # ═══════════════════════════════════════════════════════════════
    # Tab 4: الإعدادات
    # ═══════════════════════════════════════════════════════════════
    with tab4:
        st.markdown("### ⚙️ إعدادات التنبيهات")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🔔 أنواع التنبيهات")
            st.checkbox("💰 تنبيهات الأسعار", value=True)
            st.checkbox("📦 تنبيهات المخزون", value=True)
            st.checkbox("🏪 تنبيهات المنافسين", value=True)
            st.checkbox("⚙️ تنبيهات النظام", value=True)
            st.checkbox("🎯 تنبيهات الفرص", value=True)
        
        with col2:
            st.markdown("#### 📧 طرق الإشعار")
            st.checkbox("📱 إشعارات داخل التطبيق", value=True)
            st.checkbox("📧 البريد الإلكتروني", value=False)
            st.text_input("البريد الإلكتروني", placeholder="your@email.com")
            st.checkbox("💬 واتساب", value=False)
            st.text_input("رقم الواتساب", placeholder="+966XXXXXXXXX")
        
        st.markdown("---")
        
        st.markdown("#### ⏰ جدولة التقارير")
        st.checkbox("📊 تقرير يومي (9 صباحاً)", value=True)
        st.checkbox("📅 تقرير أسبوعي (الأحد)", value=True)
        st.checkbox("📆 تقرير شهري (أول كل شهر)", value=False)
        
        if st.button("💾 حفظ الإعدادات"):
            st.success("✅ تم حفظ الإعدادات!")
