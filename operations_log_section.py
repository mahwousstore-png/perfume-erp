# ══════════════════════════════════════════════════════════════
# قسم سجل العمليات
# ══════════════════════════════════════════════════════════════

import streamlit as st
import pandas as pd
from database import get_operations, get_statistics, get_modified_products, get_added_products, clear_old_operations

def show_operations_log():
    """عرض سجل العمليات"""
    st.markdown("# 📊 سجل العمليات")
    st.markdown("> تتبع جميع العمليات المنفذة في النظام")
    st.markdown("---")
    
    # الإحصائيات
    stats = get_statistics()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📊 إجمالي العمليات", stats["total_operations"])
    with col2:
        st.metric("✅ العمليات الناجحة", stats["successful_operations"])
    with col3:
        st.metric("🔄 منتجات معدلة", stats["modified_products"])
    with col4:
        st.metric("➕ منتجات مضافة", stats["added_products"])
    
    st.markdown("---")
    
    # التبويبات
    tab1, tab2, tab3, tab4 = st.tabs([
        "📜 سجل العمليات",
        "🔄 المنتجات المعدلة",
        "➕ المنتجات المضافة",
        "⚙️ الإعدادات"
    ])
    
    # ═══════════════════════════════════════════════════════════
    # تبويب 1: سجل العمليات
    # ═══════════════════════════════════════════════════════════
    with tab1:
        st.markdown("### 📜 سجل العمليات")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            operation_filter = st.selectbox(
                "نوع العملية",
                ["الكل", "price_update", "product_add", "ai_check", "batch_verification"]
            )
        with col2:
            status_filter = st.selectbox(
                "الحالة",
                ["الكل", "success", "failed", "pending"]
            )
        with col3:
            limit = st.number_input("عدد السجلات", min_value=10, max_value=1000, value=100, step=10)
        
        # جلب العمليات
        operations = get_operations(
            limit=limit,
            operation_type=None if operation_filter == "الكل" else operation_filter,
            status=None if status_filter == "الكل" else status_filter
        )
        
        if operations:
            # تحويل إلى DataFrame
            df = pd.DataFrame(operations)
            
            # ترجمة الأعمدة
            column_names = {
                "id": "المعرف",
                "timestamp": "التاريخ والوقت",
                "operation_type": "نوع العملية",
                "product_name": "اسم المنتج",
                "old_price": "السعر القديم",
                "new_price": "السعر الجديد",
                "status": "الحالة",
                "user_action": "إجراء المستخدم"
            }
            
            df_display = df[[
                "id", "timestamp", "operation_type", "product_name", 
                "old_price", "new_price", "status", "user_action"
            ]].rename(columns=column_names)
            
            # تلوين الحالة
            def highlight_status(row):
                if row["الحالة"] == "success":
                    return ['background-color: #d4edda'] * len(row)
                elif row["الحالة"] == "failed":
                    return ['background-color: #f8d7da'] * len(row)
                else:
                    return ['background-color: #fff3cd'] * len(row)
            
            st.dataframe(
                df_display.style.apply(highlight_status, axis=1),
                use_container_width=True,
                height=500
            )
            
            # تحميل CSV
            csv = df_display.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 تحميل CSV",
                data=csv,
                file_name="operations_log.csv",
                mime="text/csv"
            )
        else:
            st.info("📭 لا توجد عمليات مسجلة")
    
    # ═══════════════════════════════════════════════════════════
    # تبويب 2: المنتجات المعدلة
    # ═══════════════════════════════════════════════════════════
    with tab2:
        st.markdown("### 🔄 المنتجات المعدلة")
        st.markdown("> المنتجات التي تم تعديل أسعارها")
        
        modified = get_modified_products()
        
        if modified:
            df = pd.DataFrame(modified)
            
            column_names = {
                "id": "المعرف",
                "product_name": "اسم المنتج",
                "last_modified": "آخر تعديل",
                "modification_count": "عدد التعديلات",
                "last_operation": "آخر عملية"
            }
            
            df_display = df.rename(columns=column_names)
            
            st.dataframe(df_display, use_container_width=True, height=500)
            
            # إحصائيات
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("📊 إجمالي المنتجات المعدلة", len(modified))
            with col2:
                st.metric("🔄 متوسط التعديلات", f"{df['modification_count'].mean():.1f}")
            
            # تحميل CSV
            csv = df_display.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 تحميل CSV",
                data=csv,
                file_name="modified_products.csv",
                mime="text/csv"
            )
        else:
            st.info("📭 لا توجد منتجات معدلة")
    
    # ═══════════════════════════════════════════════════════════
    # تبويب 3: المنتجات المضافة
    # ═══════════════════════════════════════════════════════════
    with tab3:
        st.markdown("### ➕ المنتجات المضافة")
        st.markdown("> المنتجات الجديدة التي تم إضافتها")
        
        added = get_added_products()
        
        if added:
            df = pd.DataFrame(added)
            
            column_names = {
                "id": "المعرف",
                "product_name": "اسم المنتج",
                "added_date": "تاريخ الإضافة",
                "source": "المصدر",
                "status": "الحالة"
            }
            
            df_display = df.rename(columns=column_names)
            
            st.dataframe(df_display, use_container_width=True, height=500)
            
            # إحصائيات
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("📊 إجمالي المنتجات المضافة", len(added))
            with col2:
                sources = df['source'].value_counts()
                st.metric("📌 أكثر مصدر", sources.index[0] if len(sources) > 0 else "N/A")
            
            # تحميل CSV
            csv = df_display.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 تحميل CSV",
                data=csv,
                file_name="added_products.csv",
                mime="text/csv"
            )
        else:
            st.info("📭 لا توجد منتجات مضافة")
    
    # ═══════════════════════════════════════════════════════════
    # تبويب 4: الإعدادات
    # ═══════════════════════════════════════════════════════════
    with tab4:
        st.markdown("### ⚙️ إعدادات قاعدة البيانات")
        
        st.markdown("#### 🗑️ تنظيف البيانات القديمة")
        st.markdown("> حذف العمليات الأقدم من عدد معين من الأيام")
        
        days = st.number_input("عدد الأيام", min_value=7, max_value=365, value=30, step=7)
        
        if st.button("🗑️ حذف العمليات القديمة", type="secondary"):
            with st.spinner("⏳ جاري الحذف..."):
                deleted = clear_old_operations(days)
                st.success(f"✅ تم حذف {deleted} عملية قديمة")
        
        st.markdown("---")
        st.markdown("#### 📊 معلومات قاعدة البيانات")
        
        if stats["last_operation"]["timestamp"]:
            st.info(f"""
            **آخر عملية:**
            - **التاريخ:** {stats["last_operation"]["timestamp"]}
            - **النوع:** {stats["last_operation"]["type"]}
            """)
        else:
            st.info("لا توجد عمليات مسجلة")
