"""
صفحة عرض تفاصيل المطابقة
تعرض كيف تمت المطابقة بالتفصيل
"""

import streamlit as st
import pandas as pd


def render_match_details_page():
    """عرض تفاصيل المطابقة"""
    
    st.title("🔍 تفاصيل المطابقة")
    st.markdown("---")
    
    # التحقق من وجود نتائج
    if "analysis_result" not in st.session_state or st.session_state.analysis_result is None:
        st.warning("⚠️ لا توجد نتائج تحليل. يرجى تشغيل التحليل أولاً من صفحة 'رفع الملفات'.")
        return
    
    result = st.session_state.analysis_result
    
    # اختيار القسم
    section = st.selectbox(
        "اختر القسم:",
        ["رفع سعر", "خفض سعر", "موافق عليها"]
    )
    
    st.markdown("---")
    
    # عرض التفاصيل حسب القسم
    if section == "رفع سعر":
        df = result.get("df_raise", pd.DataFrame())
        st.subheader("📈 تفاصيل منتجات رفع السعر")
        
    elif section == "خفض سعر":
        df = result.get("df_lower", pd.DataFrame())
        st.subheader("📉 تفاصيل منتجات خفض السعر")
        
    else:  # موافق عليها
        df = result.get("df_approved", pd.DataFrame())
        st.subheader("✅ تفاصيل منتجات موافق عليها")
    
    if df.empty:
        st.info(f"لا توجد منتجات في قسم '{section}'")
        return
    
    # عرض عدد المنتجات
    st.metric("عدد المنتجات", len(df))
    
    st.markdown("---")
    
    # اختيار منتج للتفاصيل
    product_names = df["اسم المنتج"].tolist()
    selected_product = st.selectbox("اختر منتجاً لعرض التفاصيل:", product_names)
    
    if selected_product:
        # الحصول على بيانات المنتج
        product_data = df[df["اسم المنتج"] == selected_product].iloc[0]
        
        st.markdown("---")
        st.subheader(f"📦 تفاصيل: {selected_product}")
        
        # عرض المقارنة
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🏪 منتجنا")
            st.markdown(f"**الاسم:** {product_data.get('اسم المنتج', 'N/A')}")
            st.markdown(f"**الماركة:** {product_data.get('ماركتنا', 'N/A')}")
            st.markdown(f"**التركيز:** {product_data.get('تركيزنا', 'N/A')}")
            st.markdown(f"**الحجم:** {product_data.get('حجمنا', 'N/A')} مل")
            st.markdown(f"**السعر:** {product_data.get('سعرنا', 'N/A')} ر.س")
        
        with col2:
            st.markdown("### 🏬 المنافس")
            st.markdown(f"**الاسم:** {product_data.get('اسم المنافس', 'N/A')}")
            st.markdown(f"**الماركة:** {product_data.get('ماركة المنافس', 'N/A')}")
            st.markdown(f"**التركيز:** {product_data.get('تركيز المنافس', 'N/A')}")
            st.markdown(f"**الحجم:** {product_data.get('حجم المنافس', 'N/A')} مل")
            st.markdown(f"**السعر:** {product_data.get('أقل سعر منافس', 'N/A')} ر.س")
        
        st.markdown("---")
        
        # عرض تفاصيل المطابقة
        st.subheader("🤖 تفاصيل التحقق بالذكاء الصناعي")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            confidence = product_data.get('ثقة AI %', 0)
            st.metric("ثقة AI", f"{confidence}%")
        
        with col2:
            status = product_data.get('حالة التحقق', 'N/A')
            st.metric("حالة التحقق", status)
        
        with col3:
            match_score = product_data.get('نسبة التطابق %', 0)
            st.metric("نسبة التطابق", f"{match_score}%")
        
        # عرض التفسير
        st.markdown("### 📝 تفسير AI")
        reasoning = product_data.get('تفسير AI', 'لا يوجد تفسير')
        st.info(reasoning)
        
        # عرض المقارنة البصرية
        st.markdown("---")
        st.subheader("🆚 المقارنة البصرية")
        comparison = product_data.get('المقارنة', 'N/A')
        st.markdown(f"### {comparison}")
        
        # عرض التوصية (إن وجدت)
        if 'السعر الموصى' in product_data:
            st.markdown("---")
            st.subheader("💡 التوصية")
            recommended_price = product_data.get('السعر الموصى', 'N/A')
            st.success(f"السعر الموصى به: **{recommended_price} ر.س**")
