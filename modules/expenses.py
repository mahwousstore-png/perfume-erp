"""
💰 نظام مذكرة المصروفات الشهرية
نظام التسعير الذكي v8.0
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
from typing import List, Dict, Optional

# ============================================
# فئات المصروفات
# ============================================

EXPENSE_CATEGORIES = [
    "💼 رواتب وأجور",
    "🏢 إيجار",
    "⚡ كهرباء وماء",
    "📱 اتصالات وإنترنت",
    "📦 شحن وتوصيل",
    "📢 تسويق وإعلانات",
    "🛠️ صيانة",
    "📄 مستلزمات مكتبية",
    "🚗 مواصلات",
    "☕ ضيافة",
    "📚 تدريب",
    "🏦 رسوم بنكية",
    "📊 محاسبة وقانونية",
    "💻 برامج واشتراكات",
    "🎁 هدايا وعينات",
    "🔧 أخرى"
]

# ============================================
# دوال قاعدة البيانات
# ============================================

def get_expenses(_month: int, _year: int) -> pd.DataFrame:
    """
    جلب المصروفات لشهر معين
    
    Args:
        month: الشهر (1-12)
        year: السنة
    
    Returns:
        DataFrame مع بيانات المصروفات
    """
    try:
        # TODO: الاستعلام من Supabase
        # من supabase import get_supabase
        # supabase = get_supabase()
        # start_date = date(year, month, 1)
        # end_date = date(year, month, calendar.monthrange(year, month)[1])
        # result = supabase.table('expenses').select('*').gte('date', start_date).lte('date', end_date).order('date', desc=True).execute()
        # return pd.DataFrame(result.data)
        
        # للتطوير: بيانات تجريبية
        return pd.DataFrame([
            {
                'id': 1,
                'date': '2026-02-01',
                'category': '🏢 إيجار',
                'description': 'إيجار المحل - فبراير',
                'amount': 15000,
                'payment_method': 'تحويل بنكي',
                'receipt_number': 'REC-2026-001',
                'notes': 'دفعة شهرية',
                'created_by': 'admin'
            },
            {
                'id': 2,
                'date': '2026-02-05',
                'category': '💼 رواتب وأجور',
                'description': 'رواتب الموظفين',
                'amount': 25000,
                'payment_method': 'تحويل بنكي',
                'receipt_number': 'REC-2026-002',
                'notes': 'رواتب فبراير',
                'created_by': 'admin'
            },
            {
                'id': 3,
                'date': '2026-02-10',
                'category': '📢 تسويق وإعلانات',
                'description': 'حملة إعلانية - سناب شات',
                'amount': 3500,
                'payment_method': 'بطاقة ائتمان',
                'receipt_number': 'REC-2026-003',
                'notes': 'حملة أسبوعية',
                'created_by': 'admin'
            },
            {
                'id': 4,
                'date': '2026-02-12',
                'category': '⚡ كهرباء وماء',
                'description': 'فاتورة الكهرباء',
                'amount': 1200,
                'payment_method': 'نقداً',
                'receipt_number': 'REC-2026-004',
                'notes': '',
                'created_by': 'admin'
            }
        ])
    except Exception as e:
        st.error(f"خطأ في جلب المصروفات: {str(e)}")
        return pd.DataFrame()

def add_expense(expense_data: Dict) -> bool:
    """
    إضافة مصروف جديد
    
    Args:
        expense_data: بيانات المصروف
    
    Returns:
        True إذا نجحت العملية
    """
    try:
        # TODO: الإضافة إلى Supabase
        # من supabase import get_supabase
        # supabase = get_supabase()
        # supabase.table('expenses').insert(expense_data).execute()
        
        # تسجيل العملية
        from modules.auth import log_action
        log_action('add_expense', {
            'category': expense_data.get('category'),
            'amount': expense_data.get('amount')
        })
        
        return True
    except Exception as e:
        st.error(f"خطأ في إضافة المصروف: {str(e)}")
        return False

def update_expense(expense_id: int, updates: Dict) -> bool:
    """
    تحديث مصروف
    
    Args:
        expense_id: معرف المصروف
        updates: التحديثات
    
    Returns:
        True إذا نجحت العملية
    """
    try:
        # TODO: التحديث في Supabase
        # من supabase import get_supabase
        # supabase = get_supabase()
        # supabase.table('expenses').update(updates).eq('id', expense_id).execute()
        
        # تسجيل العملية
        from modules.auth import log_action
        log_action('update_expense', {'expense_id': expense_id, 'updates': updates})
        
        return True
    except Exception as e:
        st.error(f"خطأ في تحديث المصروف: {str(e)}")
        return False

def delete_expense(expense_id: int) -> bool:
    """
    حذف مصروف
    
    Args:
        expense_id: معرف المصروف
    
    Returns:
        True إذا نجحت العملية
    """
    try:
        # TODO: الحذف من Supabase
        # من supabase import get_supabase
        # supabase = get_supabase()
        # supabase.table('expenses').delete().eq('id', expense_id).execute()
        
        # تسجيل العملية
        from modules.auth import log_action
        log_action('delete_expense', {'expense_id': expense_id})
        
        return True
    except Exception as e:
        st.error(f"خطأ في حذف المصروف: {str(e)}")
        return False

def get_expenses_stats(month: int, year: int) -> Dict:
    """
    إحصائيات المصروفات لشهر معين
    
    Args:
        month: الشهر (1-12)
        year: السنة
    
    Returns:
        Dict مع الإحصائيات
    """
    try:
        expenses = get_expenses(month, year)
        
        if expenses.empty:
            return {
                'total_expenses': 0,
                'total_amount': 0,
                'avg_expense': 0,
                'max_expense': 0,
                'by_category': {}
            }
        
        by_category = expenses.groupby('category')['amount'].sum().to_dict()
        
        return {
            'total_expenses': len(expenses),
            'total_amount': expenses['amount'].sum(),
            'avg_expense': expenses['amount'].mean(),
            'max_expense': expenses['amount'].max(),
            'by_category': by_category
        }
    except Exception as e:
        st.error(f"خطأ في حساب الإحصائيات: {str(e)}")
        return {}

def get_yearly_comparison() -> pd.DataFrame:
    """
    مقارنة المصروفات الشهرية (آخر 12 شهر)
    
    Returns:
        DataFrame مع المقارنة الشهرية
    """
    try:
        # TODO: الاستعلام من Supabase
        # للتطوير: بيانات تجريبية
        months = ['يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو', 
                  'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر']
        
        return pd.DataFrame({
            'الشهر': months[:2],  # فقط يناير وفبراير للتجربة
            'المصروفات': [42000, 44700]
        })
    except Exception as e:
        st.error(f"خطأ في حساب المقارنة السنوية: {str(e)}")
        return pd.DataFrame()

# ============================================
# واجهة المستخدم
# ============================================

def show_expenses_page():
    """
    عرض صفحة مذكرة المصروفات
    """
    from modules.auth import check_permission
    
    # التحقق من الصلاحية
    if not check_permission('add_expense'):
        st.error("⛔ ليس لديك صلاحية للوصول إلى هذه الصفحة")
        return
    
    st.markdown('<div class="section-title">💰 مذكرة المصروفات الشهرية</div>', unsafe_allow_html=True)
    
    # اختيار الشهر والسنة
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        current_month = datetime.now().month
        months_ar = ['يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو', 
                     'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر']
        selected_month_name = st.selectbox("الشهر", months_ar, index=current_month-1)
        selected_month = months_ar.index(selected_month_name) + 1
    
    with col2:
        selected_year = st.number_input("السنة", min_value=2020, max_value=2030, value=datetime.now().year)
    
    with col3:
        st.write("")  # مسافة
        if st.button("🔄 تحديث", use_container_width=True):
            st.rerun()
    
    # الإحصائيات
    stats = get_expenses_stats(selected_month, selected_year)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        from modules.styles import render_metric_card
        st.markdown(render_metric_card(
            str(stats.get('total_expenses', 0)),
            "عدد المصروفات",
            "💰"
        ), unsafe_allow_html=True)
    
    with col2:
        amount = stats.get('total_amount', 0)
        st.markdown(render_metric_card(
            f"{amount:,.0f}",
            "الإجمالي (SAR)",
            "💵"
        ), unsafe_allow_html=True)
    
    with col3:
        avg = stats.get('avg_expense', 0)
        st.markdown(render_metric_card(
            f"{avg:,.0f}",
            "متوسط المصروف",
            "📊"
        ), unsafe_allow_html=True)
    
    with col4:
        max_exp = stats.get('max_expense', 0)
        st.markdown(render_metric_card(
            f"{max_exp:,.0f}",
            "أعلى مصروف",
            "🔝"
        ), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # التبويبات
    tab1, tab2, tab3 = st.tabs(["📋 قائمة المصروفات", "➕ إضافة مصروف", "📊 التقارير"])
    
    with tab1:
        show_expenses_list(selected_month, selected_year)
    
    with tab2:
        show_add_expense_form(selected_month, selected_year)
    
    with tab3:
        show_expenses_reports(selected_month, selected_year)

def show_expenses_list(month: int, year: int):
    """
    عرض قائمة المصروفات
    """
    st.markdown("### 📋 قائمة المصروفات")
    
    expenses = get_expenses(month, year)
    
    if expenses.empty:
        st.info("📭 لا يوجد مصروفات في هذا الشهر")
        return
    
    # فلترة
    col1, col2 = st.columns(2)
    
    with col1:
        search = st.text_input("🔍 بحث", placeholder="الوصف، رقم الإيصال...")
    
    with col2:
        category_filter = st.selectbox("الفئة", ["الكل"] + EXPENSE_CATEGORIES)
    
    # تطبيق الفلاتر
    if search:
        expenses = expenses[
            expenses['description'].str.contains(search, case=False, na=False) |
            expenses['receipt_number'].str.contains(search, case=False, na=False)
        ]
    
    if category_filter != "الكل":
        expenses = expenses[expenses['category'] == category_filter]
    
    # عرض الجدول
    display_df = expenses[['date', 'category', 'description', 'amount', 'payment_method', 'receipt_number']]
    display_df.columns = ['التاريخ', 'الفئة', 'الوصف', 'المبلغ', 'طريقة الدفع', 'رقم الإيصال']
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # الإجمالي
    total = expenses['amount'].sum()
    st.success(f"💰 **الإجمالي:** {total:,.0f} SAR")
    
    # أزرار التصدير
    col1, col2 = st.columns(2)
    
    with col1:
        csv = display_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            "📥 تصدير CSV",
            csv,
            f"expenses_{year}_{month:02d}.csv",
            "text/csv",
            use_container_width=True
        )

def show_add_expense_form(_month: int, _year: int):
    """
    نموذج إضافة مصروف جديد
    """
    st.markdown("### ➕ إضافة مصروف جديد")
    
    with st.form("add_expense_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            expense_date = st.date_input("التاريخ *", value=date.today())
            category = st.selectbox("الفئة *", EXPENSE_CATEGORIES)
            description = st.text_input("الوصف *", placeholder="مثال: إيجار المحل - فبراير")
            amount = st.number_input("المبلغ (SAR) *", min_value=0.0, value=0.0, step=10.0)
        
        with col2:
            payment_method = st.selectbox("طريقة الدفع *", ["نقداً", "تحويل بنكي", "بطاقة ائتمان", "شيك"])
            receipt_number = st.text_input("رقم الإيصال", placeholder="REC-2026-XXX")
            notes = st.text_area("ملاحظات", placeholder="أي معلومات إضافية...")
        
        submitted = st.form_submit_button("➕ إضافة المصروف", use_container_width=True, type="primary")
        
        if submitted:
            if not description or amount <= 0:
                st.error("⚠️ الرجاء ملء الحقول المطلوبة (*)")
            else:
                expense_data = {
                    'date': expense_date.isoformat(),
                    'category': category,
                    'description': description,
                    'amount': amount,
                    'payment_method': payment_method,
                    'receipt_number': receipt_number or '',
                    'notes': notes or '',
                    'created_by': st.session_state.get('username', 'unknown'),
                    'created_at': datetime.now().isoformat()
                }
                
                if add_expense(expense_data):
                    st.success(f"✅ تم إضافة المصروف: {description}")
                    st.rerun()

def show_expenses_reports(month: int, year: int):
    """
    تقارير المصروفات
    """
    st.markdown("### 📊 تقارير المصروفات")
    
    expenses = get_expenses(month, year)
    
    if expenses.empty:
        st.info("📭 لا يوجد بيانات لعرض التقارير")
        return
    
    # التوزيع حسب الفئة
    st.markdown("#### 📊 التوزيع حسب الفئة")
    by_category = expenses.groupby('category')['amount'].sum().reset_index()
    by_category.columns = ['الفئة', 'المبلغ']
    by_category = by_category.sort_values('المبلغ', ascending=False)
    
    # إضافة النسبة المئوية
    total = by_category['المبلغ'].sum()
    by_category['النسبة %'] = (by_category['المبلغ'] / total * 100).round(1)
    
    st.dataframe(by_category, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # المقارنة الشهرية
    st.markdown("#### 📅 المقارنة الشهرية")
    yearly = get_yearly_comparison()
    if not yearly.empty:
        st.dataframe(yearly, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # أعلى 10 مصروفات
    st.markdown("#### 🔝 أعلى 10 مصروفات")
    top_expenses = expenses.nlargest(10, 'amount')[['date', 'category', 'description', 'amount']]
    top_expenses.columns = ['التاريخ', 'الفئة', 'الوصف', 'المبلغ']
    st.dataframe(top_expenses, use_container_width=True, hide_index=True)
