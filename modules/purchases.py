"""
🛒 نظام المشتريات اليومية
نظام التسعير الذكي v8.0
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional
import json

# ============================================
# دوال قاعدة البيانات
# ============================================

def get_purchases(start_date: Optional[date] = None, end_date: Optional[date] = None) -> pd.DataFrame:
    """
    جلب المشتريات من Supabase
    
    Args:
        start_date: تاريخ البداية
        end_date: تاريخ النهاية
    
    Returns:
        DataFrame مع بيانات المشتريات
    """
    try:
        # TODO: الاستعلام من Supabase
        # من supabase import get_supabase
        # supabase = get_supabase()
        # query = supabase.table('purchases').select('*, suppliers(name)')
        # if start_date:
        #     query = query.gte('date', start_date.isoformat())
        # if end_date:
        #     query = query.lte('date', end_date.isoformat())
        # result = query.order('date', desc=True).execute()
        # return pd.DataFrame(result.data)
        
        # للتطوير: بيانات تجريبية
        return pd.DataFrame([
            {
                'id': 1,
                'date': '2026-02-13',
                'supplier_id': 1,
                'supplier_name': 'مورد الرياض للعطور',
                'product_name': 'Dior Sauvage EDT 100ml',
                'quantity': 5,
                'unit_price': 650,
                'total': 3250,
                'payment_method': 'نقداً',
                'invoice_number': 'INV-2026-001',
                'notes': 'شحنة جديدة',
                'created_by': 'admin'
            },
            {
                'id': 2,
                'date': '2026-02-12',
                'supplier_id': 2,
                'supplier_name': 'عطور جدة المميزة',
                'product_name': 'Chanel Bleu EDP 100ml',
                'quantity': 3,
                'unit_price': 850,
                'total': 2550,
                'payment_method': 'آجل 30 يوم',
                'invoice_number': 'INV-2026-002',
                'notes': '',
                'created_by': 'admin'
            },
            {
                'id': 3,
                'date': '2026-02-10',
                'supplier_id': 1,
                'supplier_name': 'مورد الرياض للعطور',
                'product_name': 'Tom Ford Oud Wood EDP 100ml',
                'quantity': 2,
                'unit_price': 1200,
                'total': 2400,
                'payment_method': 'نقداً',
                'invoice_number': 'INV-2026-003',
                'notes': 'طلب خاص',
                'created_by': 'admin'
            }
        ])
    except Exception as e:
        st.error(f"خطأ في جلب المشتريات: {str(e)}")
        return pd.DataFrame()

def add_purchase(purchase_data: Dict) -> bool:
    """
    إضافة مشترى جديد
    
    Args:
        purchase_data: بيانات المشترى
    
    Returns:
        True إذا نجحت العملية
    """
    try:
        # TODO: الإضافة إلى Supabase
        # من supabase import get_supabase
        # supabase = get_supabase()
        # supabase.table('purchases').insert(purchase_data).execute()
        
        # تحديث إحصائيات المورد
        # supabase.rpc('update_supplier_stats', {'supplier_id': purchase_data['supplier_id']}).execute()
        
        # تسجيل العملية
        from modules.auth import log_action
        log_action('add_purchase', {
            'product': purchase_data.get('product_name'),
            'quantity': purchase_data.get('quantity'),
            'total': purchase_data.get('total')
        })
        
        return True
    except Exception as e:
        st.error(f"خطأ في إضافة المشترى: {str(e)}")
        return False

def delete_purchase(purchase_id: int) -> bool:
    """
    حذف مشترى
    
    Args:
        purchase_id: معرف المشترى
    
    Returns:
        True إذا نجحت العملية
    """
    try:
        # TODO: الحذف من Supabase
        # من supabase import get_supabase
        # supabase = get_supabase()
        # supabase.table('purchases').delete().eq('id', purchase_id).execute()
        
        # تسجيل العملية
        from modules.auth import log_action
        log_action('delete_purchase', {'purchase_id': purchase_id})
        
        return True
    except Exception as e:
        st.error(f"خطأ في حذف المشترى: {str(e)}")
        return False

def get_purchases_stats(start_date: Optional[date] = None, end_date: Optional[date] = None) -> Dict:
    """
    إحصائيات المشتريات
    
    Args:
        start_date: تاريخ البداية
        end_date: تاريخ النهاية
    
    Returns:
        Dict مع الإحصائيات
    """
    try:
        purchases = get_purchases(start_date, end_date)
        
        if purchases.empty:
            return {
                'total_purchases': 0,
                'total_amount': 0,
                'total_quantity': 0,
                'avg_purchase': 0,
                'unique_products': 0,
                'unique_suppliers': 0
            }
        
        return {
            'total_purchases': len(purchases),
            'total_amount': purchases['total'].sum(),
            'total_quantity': purchases['quantity'].sum(),
            'avg_purchase': purchases['total'].mean(),
            'unique_products': purchases['product_name'].nunique(),
            'unique_suppliers': purchases['supplier_name'].nunique()
        }
    except Exception as e:
        st.error(f"خطأ في حساب الإحصائيات: {str(e)}")
        return {}

def get_daily_purchases_summary() -> pd.DataFrame:
    """
    ملخص المشتريات اليومية (آخر 30 يوم)
    
    Returns:
        DataFrame مع الملخص اليومي
    """
    try:
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        
        purchases = get_purchases(start_date, end_date)
        
        if purchases.empty:
            return pd.DataFrame()
        
        # تحويل date إلى datetime
        purchases['date'] = pd.to_datetime(purchases['date'])
        
        # تجميع حسب التاريخ
        daily = purchases.groupby(purchases['date'].dt.date).agg({
            'id': 'count',
            'total': 'sum',
            'quantity': 'sum'
        }).reset_index()
        
        daily.columns = ['التاريخ', 'عدد المشتريات', 'المبلغ', 'الكمية']
        
        return daily
    except Exception as e:
        st.error(f"خطأ في حساب الملخص اليومي: {str(e)}")
        return pd.DataFrame()

# ============================================
# واجهة المستخدم
# ============================================

def show_purchases_page():
    """
    عرض صفحة المشتريات اليومية
    """
    from modules.auth import check_permission
    
    # التحقق من الصلاحية
    if not check_permission('add_purchase'):
        st.error("⛔ ليس لديك صلاحية للوصول إلى هذه الصفحة")
        return
    
    st.markdown('<div class="section-title">🛒 المشتريات اليومية</div>', unsafe_allow_html=True)
    
    # فلتر التاريخ
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        start_date = st.date_input("من تاريخ", value=date.today() - timedelta(days=30))
    
    with col2:
        end_date = st.date_input("إلى تاريخ", value=date.today())
    
    with col3:
        st.write("")  # مسافة
        if st.button("🔄 تحديث", use_container_width=True):
            st.rerun()
    
    # الإحصائيات
    stats = get_purchases_stats(start_date, end_date)
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        from modules.styles import render_metric_card
        st.markdown(render_metric_card(
            str(stats.get('total_purchases', 0)),
            "إجمالي المشتريات",
            "🛒"
        ), unsafe_allow_html=True)
    
    with col2:
        amount = stats.get('total_amount', 0)
        st.markdown(render_metric_card(
            f"{amount:,.0f}",
            "المبلغ (SAR)",
            "💰"
        ), unsafe_allow_html=True)
    
    with col3:
        st.markdown(render_metric_card(
            str(stats.get('total_quantity', 0)),
            "الكمية",
            "📦"
        ), unsafe_allow_html=True)
    
    with col4:
        avg = stats.get('avg_purchase', 0)
        st.markdown(render_metric_card(
            f"{avg:,.0f}",
            "متوسط المشترى",
            "📊"
        ), unsafe_allow_html=True)
    
    with col5:
        st.markdown(render_metric_card(
            str(stats.get('unique_products', 0)),
            "منتجات مختلفة",
            "🎁"
        ), unsafe_allow_html=True)
    
    with col6:
        st.markdown(render_metric_card(
            str(stats.get('unique_suppliers', 0)),
            "موردين",
            "🏪"
        ), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # التبويبات
    tab1, tab2, tab3 = st.tabs(["📋 قائمة المشتريات", "➕ إضافة مشترى", "📊 التقارير"])
    
    with tab1:
        show_purchases_list(start_date, end_date)
    
    with tab2:
        show_add_purchase_form()
    
    with tab3:
        show_purchases_reports(start_date, end_date)

def show_purchases_list(start_date: date, end_date: date):
    """
    عرض قائمة المشتريات
    """
    st.markdown("### 📋 قائمة المشتريات")
    
    purchases = get_purchases(start_date, end_date)
    
    if purchases.empty:
        st.info("📭 لا يوجد مشتريات في هذه الفترة")
        return
    
    # فلترة
    col1, col2 = st.columns(2)
    
    with col1:
        search = st.text_input("🔍 بحث", placeholder="اسم المنتج، المورد، رقم الفاتورة...")
    
    with col2:
        payment_filter = st.selectbox("طريقة الدفع", ["الكل", "نقداً", "آجل 7 أيام", "آجل 15 يوم", "آجل 30 يوم", "آجل 60 يوم"])
    
    # تطبيق الفلاتر
    if search:
        purchases = purchases[
            purchases['product_name'].str.contains(search, case=False, na=False) |
            purchases['supplier_name'].str.contains(search, case=False, na=False) |
            purchases['invoice_number'].str.contains(search, case=False, na=False)
        ]
    
    if payment_filter != "الكل":
        purchases = purchases[purchases['payment_method'] == payment_filter]
    
    # عرض الجدول
    display_df = purchases[['date', 'supplier_name', 'product_name', 'quantity', 'unit_price', 'total', 'payment_method', 'invoice_number']]
    display_df.columns = ['التاريخ', 'المورد', 'المنتج', 'الكمية', 'سعر الوحدة', 'الإجمالي', 'الدفع', 'رقم الفاتورة']
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # الإجمالي
    total = purchases['total'].sum()
    st.success(f"💰 **الإجمالي:** {total:,.0f} SAR")
    
    # أزرار التصدير
    col1, col2 = st.columns(2)
    
    with col1:
        csv = display_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            "📥 تصدير CSV",
            csv,
            f"purchases_{start_date}_{end_date}.csv",
            "text/csv",
            use_container_width=True
        )
    
    with col2:
        excel = display_df.to_excel(index=False, engine='openpyxl')
        # TODO: تصدير Excel

def show_add_purchase_form():
    """
    نموذج إضافة مشترى جديد
    """
    st.markdown("### ➕ إضافة مشترى جديد")
    
    # جلب قائمة الموردين
    from modules.suppliers import get_all_suppliers
    suppliers = get_all_suppliers()
    
    if suppliers.empty:
        st.warning("⚠️ لا يوجد موردين! الرجاء إضافة مورد أولاً من صفحة الموردين")
        return
    
    with st.form("add_purchase_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            purchase_date = st.date_input("التاريخ *", value=date.today())
            
            supplier_options = {row['name']: row['id'] for _, row in suppliers.iterrows()}
            supplier_name = st.selectbox("المورد *", list(supplier_options.keys()))
            supplier_id = supplier_options[supplier_name]
            
            product_name = st.text_input("اسم المنتج *", placeholder="مثال: Dior Sauvage EDT 100ml")
            quantity = st.number_input("الكمية *", min_value=1, value=1)
        
        with col2:
            unit_price = st.number_input("سعر الوحدة (SAR) *", min_value=0.0, value=0.0, step=10.0)
            total = quantity * unit_price
            st.metric("الإجمالي", f"{total:,.2f} SAR")
            
            payment_method = st.selectbox("طريقة الدفع *", ["نقداً", "آجل 7 أيام", "آجل 15 يوم", "آجل 30 يوم", "آجل 60 يوم"])
            invoice_number = st.text_input("رقم الفاتورة", placeholder="INV-2026-XXX")
        
        notes = st.text_area("ملاحظات", placeholder="أي معلومات إضافية...")
        
        submitted = st.form_submit_button("➕ إضافة المشترى", use_container_width=True, type="primary")
        
        if submitted:
            if not product_name or unit_price <= 0:
                st.error("⚠️ الرجاء ملء الحقول المطلوبة (*)")
            else:
                purchase_data = {
                    'date': purchase_date.isoformat(),
                    'supplier_id': supplier_id,
                    'product_name': product_name,
                    'quantity': quantity,
                    'unit_price': unit_price,
                    'total': total,
                    'payment_method': payment_method,
                    'invoice_number': invoice_number or '',
                    'notes': notes or '',
                    'created_by': st.session_state.get('username', 'unknown'),
                    'created_at': datetime.now().isoformat()
                }
                
                if add_purchase(purchase_data):
                    st.success(f"✅ تم إضافة المشترى: {product_name}")
                    st.rerun()

def show_purchases_reports(start_date: date, end_date: date):
    """
    تقارير المشتريات
    """
    st.markdown("### 📊 تقارير المشتريات")
    
    purchases = get_purchases(start_date, end_date)
    
    if purchases.empty:
        st.info("📭 لا يوجد بيانات لعرض التقارير")
        return
    
    # الملخص اليومي
    st.markdown("#### 📅 الملخص اليومي")
    daily = get_daily_purchases_summary()
    if not daily.empty:
        st.dataframe(daily, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # أكثر المنتجات شراءً
    st.markdown("#### 🏆 أكثر المنتجات شراءً")
    top_products = purchases.groupby('product_name').agg({
        'quantity': 'sum',
        'total': 'sum'
    }).reset_index().nlargest(10, 'quantity')
    top_products.columns = ['المنتج', 'الكمية', 'المبلغ']
    st.dataframe(top_products, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # التوزيع حسب المورد
    st.markdown("#### 🏪 التوزيع حسب المورد")
    by_supplier = purchases.groupby('supplier_name').agg({
        'id': 'count',
        'total': 'sum'
    }).reset_index()
    by_supplier.columns = ['المورد', 'عدد المشتريات', 'المبلغ']
    st.dataframe(by_supplier, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # التوزيع حسب طريقة الدفع
    st.markdown("#### 💳 التوزيع حسب طريقة الدفع")
    by_payment = purchases.groupby('payment_method').agg({
        'id': 'count',
        'total': 'sum'
    }).reset_index()
    by_payment.columns = ['طريقة الدفع', 'عدد المشتريات', 'المبلغ']
    st.dataframe(by_payment, use_container_width=True, hide_index=True)
