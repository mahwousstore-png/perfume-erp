"""
🏪 نظام إدارة الموردين
نظام التسعير الذكي v8.0
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional

# ============================================
# دوال قاعدة البيانات
# ============================================

def get_all_suppliers() -> pd.DataFrame:
    """
    جلب جميع الموردين من Supabase
    
    Returns:
        DataFrame مع بيانات الموردين
    """
    try:
        # TODO: الاستعلام من Supabase
        # من supabase import get_supabase
        # supabase = get_supabase()
        # result = supabase.table('suppliers').select('*').order('rating', desc=True).execute()
        # return pd.DataFrame(result.data)
        
        # للتطوير: بيانات تجريبية
        return pd.DataFrame([
            {
                'id': 1,
                'name': 'مورد الرياض للعطور',
                'contact_person': 'أحمد محمد',
                'phone': '0501234567',
                'email': 'ahmad@supplier1.com',
                'address': 'الرياض، حي الملز',
                'rating': 4.5,
                'total_purchases': 150,
                'total_amount': 450000,
                'payment_terms': 'نقداً',
                'notes': 'مورد موثوق، أسعار منافسة',
                'is_active': True,
                'created_at': '2025-01-15'
            },
            {
                'id': 2,
                'name': 'عطور جدة المميزة',
                'contact_person': 'خالد عبدالله',
                'phone': '0509876543',
                'email': 'khaled@supplier2.com',
                'address': 'جدة، حي الزهراء',
                'rating': 4.2,
                'total_purchases': 98,
                'total_amount': 320000,
                'payment_terms': 'آجل 30 يوم',
                'notes': 'تشكيلة واسعة، توصيل سريع',
                'is_active': True,
                'created_at': '2025-02-01'
            }
        ])
    except Exception as e:
        st.error(f"خطأ في جلب الموردين: {str(e)}")
        return pd.DataFrame()

def add_supplier(supplier_data: Dict) -> bool:
    """
    إضافة مورد جديد
    
    Args:
        supplier_data: بيانات المورد
    
    Returns:
        True إذا نجحت العملية
    """
    try:
        # TODO: الإضافة إلى Supabase
        # من supabase import get_supabase
        # supabase = get_supabase()
        # supabase.table('suppliers').insert(supplier_data).execute()
        
        # تسجيل العملية
        from modules.auth import log_action
        log_action('add_supplier', {'supplier_name': supplier_data.get('name')})
        
        return True
    except Exception as e:
        st.error(f"خطأ في إضافة المورد: {str(e)}")
        return False

def update_supplier(supplier_id: int, updates: Dict) -> bool:
    """
    تحديث بيانات مورد
    
    Args:
        supplier_id: معرف المورد
        updates: التحديثات
    
    Returns:
        True إذا نجحت العملية
    """
    try:
        # TODO: التحديث في Supabase
        # من supabase import get_supabase
        # supabase = get_supabase()
        # supabase.table('suppliers').update(updates).eq('id', supplier_id).execute()
        
        # تسجيل العملية
        from modules.auth import log_action
        log_action('update_supplier', {'supplier_id': supplier_id, 'updates': updates})
        
        return True
    except Exception as e:
        st.error(f"خطأ في تحديث المورد: {str(e)}")
        return False

def delete_supplier(supplier_id: int) -> bool:
    """
    حذف مورد (soft delete - تعطيل فقط)
    
    Args:
        supplier_id: معرف المورد
    
    Returns:
        True إذا نجحت العملية
    """
    try:
        # TODO: التعطيل في Supabase
        # من supabase import get_supabase
        # supabase = get_supabase()
        # supabase.table('suppliers').update({'is_active': False}).eq('id', supplier_id).execute()
        
        # تسجيل العملية
        from modules.auth import log_action
        log_action('delete_supplier', {'supplier_id': supplier_id})
        
        return True
    except Exception as e:
        st.error(f"خطأ في حذف المورد: {str(e)}")
        return False

def get_supplier_purchases(_supplier_id: int) -> pd.DataFrame:
    """
    جلب مشتريات مورد معين
    
    Args:
        _supplier_id: معرف المورد
    
    Returns:
        DataFrame مع المشتريات
    """
    try:
        # TODO: الاستعلام من Supabase
        # من supabase import get_supabase
        # supabase = get_supabase()
        # result = supabase.table('purchases').select('*').eq('supplier_id', supplier_id).order('date', desc=True).execute()
        # return pd.DataFrame(result.data)
        
        # للتطوير: بيانات تجريبية
        return pd.DataFrame([
            {
                'date': '2026-02-10',
                'product_name': 'Dior Sauvage EDT 100ml',
                'quantity': 5,
                'unit_price': 650,
                'total': 3250,
                'payment_method': 'نقداً'
            },
            {
                'date': '2026-02-12',
                'product_name': 'Chanel Bleu EDP 100ml',
                'quantity': 3,
                'unit_price': 850,
                'total': 2550,
                'payment_method': 'نقداً'
            }
        ])
    except Exception as e:
        st.error(f"خطأ في جلب المشتريات: {str(e)}")
        return pd.DataFrame()

def get_supplier_stats() -> Dict:
    """
    إحصائيات الموردين
    
    Returns:
        Dict مع الإحصائيات
    """
    try:
        suppliers = get_all_suppliers()
        
        if suppliers.empty:
            return {
                'total_suppliers': 0,
                'active_suppliers': 0,
                'total_purchases': 0,
                'total_amount': 0,
                'avg_rating': 0
            }
        
        return {
            'total_suppliers': len(suppliers),
            'active_suppliers': len(suppliers[suppliers['is_active'] == True]),
            'total_purchases': suppliers['total_purchases'].sum(),
            'total_amount': suppliers['total_amount'].sum(),
            'avg_rating': suppliers['rating'].mean()
        }
    except Exception as e:
        st.error(f"خطأ في حساب الإحصائيات: {str(e)}")
        return {}

# ============================================
# واجهة المستخدم
# ============================================

def show_suppliers_page():
    """
    عرض صفحة إدارة الموردين
    """
    from modules.auth import check_permission
    
    # التحقق من الصلاحية
    if not check_permission('manage_suppliers'):
        st.error("⛔ ليس لديك صلاحية للوصول إلى هذه الصفحة")
        return
    
    st.markdown('<div class="section-title">🏪 إدارة الموردين</div>', unsafe_allow_html=True)
    
    # الإحصائيات
    stats = get_supplier_stats()
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        from modules.styles import render_metric_card
        st.markdown(render_metric_card(
            str(stats.get('total_suppliers', 0)),
            "إجمالي الموردين",
            "🏪"
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown(render_metric_card(
            str(stats.get('active_suppliers', 0)),
            "موردين نشطين",
            "✅"
        ), unsafe_allow_html=True)
    
    with col3:
        st.markdown(render_metric_card(
            str(stats.get('total_purchases', 0)),
            "إجمالي المشتريات",
            "📦"
        ), unsafe_allow_html=True)
    
    with col4:
        amount = stats.get('total_amount', 0)
        st.markdown(render_metric_card(
            f"{amount:,.0f} SAR",
            "إجمالي المبلغ",
            "💰"
        ), unsafe_allow_html=True)
    
    with col5:
        rating = stats.get('avg_rating', 0)
        st.markdown(render_metric_card(
            f"{rating:.1f}⭐",
            "متوسط التقييم",
            "📊"
        ), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # التبويبات
    tab1, tab2, tab3 = st.tabs(["📋 قائمة الموردين", "➕ إضافة مورد", "📊 التقارير"])
    
    with tab1:
        show_suppliers_list()
    
    with tab2:
        show_add_supplier_form()
    
    with tab3:
        show_suppliers_reports()

def show_suppliers_list():
    """
    عرض قائمة الموردين
    """
    st.markdown("### 📋 قائمة الموردين")
    
    suppliers = get_all_suppliers()
    
    if suppliers.empty:
        st.info("📭 لا يوجد موردين حالياً")
        return
    
    # فلترة
    col1, col2 = st.columns(2)
    
    with col1:
        search = st.text_input("🔍 بحث", placeholder="اسم المورد، رقم الهاتف، البريد...")
    
    with col2:
        status_filter = st.selectbox("الحالة", ["الكل", "نشط", "غير نشط"])
    
    # تطبيق الفلاتر
    if search:
        suppliers = suppliers[
            suppliers['name'].str.contains(search, case=False, na=False) |
            suppliers['phone'].str.contains(search, case=False, na=False) |
            suppliers['email'].str.contains(search, case=False, na=False)
        ]
    
    if status_filter == "نشط":
        suppliers = suppliers[suppliers['is_active'] == True]
    elif status_filter == "غير نشط":
        suppliers = suppliers[suppliers['is_active'] == False]
    
    # عرض البطاقات
    for _, supplier in suppliers.iterrows():
        with st.expander(f"🏪 {supplier['name']} - ⭐ {supplier['rating']:.1f}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                **معلومات الاتصال:**
                - 👤 {supplier['contact_person']}
                - 📞 {supplier['phone']}
                - 📧 {supplier['email']}
                - 📍 {supplier['address']}
                """)
            
            with col2:
                st.markdown(f"""
                **إحصائيات:**
                - 📦 المشتريات: {supplier['total_purchases']}
            - 💰 المبلغ: {supplier['total_amount']:,.0f} SAR
            - 💳 الدفع: {supplier['payment_terms']}
            - 📅 تاريخ الإضافة: {supplier['created_at']}
            """)
        
        if supplier['notes']:
            st.info(f"📝 **ملاحظات:** {supplier['notes']}")
        
        # الأزرار
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("📊 المشتريات", key=f"purchases_{supplier['id']}"):
                show_supplier_purchases_dialog(supplier['id'], supplier['name'])
        
        with col2:
            if st.button("✏️ تعديل", key=f"edit_{supplier['id']}"):
                show_edit_supplier_dialog(supplier)
        
        with col3:
            if st.button("⭐ تقييم", key=f"rate_{supplier['id']}"):
                show_rate_supplier_dialog(supplier['id'], supplier['name'])
        
        with col4:
            if supplier['is_active'] and st.button("🔴 تعطيل", key=f"disable_{supplier['id']}"):
                if delete_supplier(supplier['id']):
                    st.success("تم تعطيل المورد")
                    st.rerun()
            else:
                if st.button("🟢 تفعيل", key=f"enable_{supplier['id']}"):
                    if update_supplier(supplier['id'], {'is_active': True}):
                        st.success("تم تفعيل المورد")
                        st.rerun()

def show_add_supplier_form():
    """
    نموذج إضافة مورد جديد
    """
    st.markdown("### ➕ إضافة مورد جديد")
    
    with st.form("add_supplier_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("اسم المورد *", placeholder="مثال: مورد الرياض للعطور")
            contact_person = st.text_input("الشخص المسؤول *", placeholder="مثال: أحمد محمد")
            phone = st.text_input("رقم الهاتف *", placeholder="05xxxxxxxx")
            email = st.text_input("البريد الإلكتروني", placeholder="example@email.com")
        
        with col2:
            address = st.text_area("العنوان", placeholder="المدينة، الحي، الشارع...")
            payment_terms = st.selectbox("شروط الدفع", ["نقداً", "آجل 7 أيام", "آجل 15 يوم", "آجل 30 يوم", "آجل 60 يوم"])
            rating = st.slider("التقييم الأولي", 1.0, 5.0, 3.0, 0.5)
            notes = st.text_area("ملاحظات", placeholder="أي معلومات إضافية...")
        
        submitted = st.form_submit_button("➕ إضافة المورد", use_container_width=True, type="primary")
        
        if submitted:
            if not name or not contact_person or not phone:
                st.error("⚠️ الرجاء ملء الحقول المطلوبة (*)")
            else:
                supplier_data = {
                    'name': name,
                    'contact_person': contact_person,
                    'phone': phone,
                    'email': email or '',
                    'address': address or '',
                    'payment_terms': payment_terms,
                    'rating': rating,
                    'notes': notes or '',
                    'is_active': True,
                    'total_purchases': 0,
                    'total_amount': 0,
                    'created_at': datetime.now().isoformat()
                }
                
                if add_supplier(supplier_data):
                    st.success(f"✅ تم إضافة المورد: {name}")
                    st.rerun()

def show_suppliers_reports():
    """
    تقارير الموردين
    """
    st.markdown("### 📊 تقارير الموردين")
    
    suppliers = get_all_suppliers()
    
    if suppliers.empty:
        st.info("📭 لا يوجد بيانات لعرض التقارير")
        return
    
    # أفضل الموردين
    st.markdown("#### 🏆 أفضل الموردين (حسب التقييم)")
    top_rated = suppliers.nlargest(5, 'rating')[['name', 'rating', 'total_purchases', 'total_amount']]
    st.dataframe(top_rated, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # أكثر الموردين مشتريات
    st.markdown("#### 📦 أكثر الموردين مشتريات")
    top_purchases = suppliers.nlargest(5, 'total_purchases')[['name', 'total_purchases', 'total_amount', 'rating']]
    st.dataframe(top_purchases, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # التوزيع حسب شروط الدفع
    st.markdown("#### 💳 التوزيع حسب شروط الدفع")
    payment_dist = suppliers.groupby('payment_terms').size().reset_index(name='count')
    st.dataframe(payment_dist, use_container_width=True, hide_index=True)

def show_supplier_purchases_dialog(supplier_id: int, supplier_name: str):
    """
    عرض مشتريات مورد معين
    """
    st.markdown(f"#### 📊 مشتريات: {supplier_name}")
    
    purchases = get_supplier_purchases(supplier_id)
    
    if purchases.empty:
        st.info("📭 لا يوجد مشتريات من هذا المورد")
    else:
        st.dataframe(purchases, use_container_width=True, hide_index=True)
        
        total = purchases['total'].sum()
        st.success(f"💰 **الإجمالي:** {total:,.0f} SAR")

def show_edit_supplier_dialog(supplier: pd.Series):
    """
    نموذج تعديل مورد
    """
    st.markdown(f"#### ✏️ تعديل: {supplier['name']}")
    
    # TODO: نموذج تعديل كامل
    st.info("🚧 قيد التطوير")

def show_rate_supplier_dialog(supplier_id: int, supplier_name: str):
    """
    نموذج تقييم مورد
    """
    st.markdown(f"#### ⭐ تقييم: {supplier_name}")
    
    new_rating = st.slider("التقييم الجديد", 1.0, 5.0, 3.0, 0.5)
    
    if st.button("💾 حفظ التقييم") and update_supplier(supplier_id, {'rating': new_rating}):
        st.success("✅ تم تحديث التقييم")
        st.rerun()
