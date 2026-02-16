"""
error_detection_section.py - قسم كشف الأخطاء الذكي في التطبيق
"""

# هذا الكود يجب إضافته بعد قسم "التحقق المجمع AI" في app.py
# السطر 1813 تقريباً

ERROR_DETECTION_SECTION = '''
# ══════════════════════════════════════════════════════════════
# 9.5. كشف الأخطاء الذكي
# ══════════════════════════════════════════════════════════════
elif section == "🔬 كشف الأخطاء الذكي":
    from error_detection_ui import show_error_detection_tab, show_individual_verification
    
    st.markdown("# 🔬 كشف الأخطاء الذكي")
    st.markdown("> نظام ذكي لاكتشاف الأخطاء في المطابقة باستخدام Gemini AI")
    st.markdown("---")
    
    # إدخال مفتاح Gemini API
    gemini_key = st.text_input(
        "🔑 مفتاح Gemini API",
        value=st.session_state.get("gemini_api_key", ""),
        type="password",
        help="أدخل مفتاح Gemini API الخاص بك"
    )
    
    if gemini_key:
        st.session_state.gemini_api_key = gemini_key
    
    st.markdown("---")
    
    # اختيار نوع التحليل
    analysis_mode = st.radio(
        "نوع التحليل",
        ["📊 تحليل المطابقات", "🔍 تحقق فردي"],
        horizontal=True
    )
    
    if analysis_mode == "📊 تحليل المطابقات":
        # تحليل المطابقات الموجودة
        if st.session_state.results:
            # استخراج المطابقات من النتائج
            matches = []
            
            # من المنتجات الموافق عليها
            df_approved = st.session_state.results.get("approved")
            if df_approved is not None and not df_approved.empty:
                for _, row in df_approved.iterrows():
                    matches.append({
                        "my_product": row.get('اسم المنتج', ''),
                        "competitor_product": row.get('اسم المنتج المنافس', ''),
                        "my_price": float(row.get('السعر', 0)),
                        "competitor_price": float(row.get('سعر المنافس', 0)),
                        "similarity": row.get('التشابه', 1.0)
                    })
            
            # من منتجات رفع السعر
            df_raise = st.session_state.results.get("raise")
            if df_raise is not None and not df_raise.empty:
                for _, row in df_raise.iterrows():
                    matches.append({
                        "my_product": row.get('اسم المنتج', ''),
                        "competitor_product": row.get('اسم المنتج المنافس', ''),
                        "my_price": float(row.get('السعر', 0)),
                        "competitor_price": float(row.get('سعر المنافس', 0)),
                        "similarity": row.get('التشابه', 0.8)
                    })
            
            # من منتجات خفض السعر
            df_lower = st.session_state.results.get("lower")
            if df_lower is not None and not df_lower.empty:
                for _, row in df_lower.iterrows():
                    matches.append({
                        "my_product": row.get('اسم المنتج', ''),
                        "competitor_product": row.get('اسم المنتج المنافس', ''),
                        "my_price": float(row.get('السعر', 0)),
                        "competitor_price": float(row.get('سعر المنافس', 0)),
                        "similarity": row.get('التشابه', 0.8)
                    })
            
            show_error_detection_tab(matches, gemini_key)
        else:
            st.info("📤 لا توجد نتائج للتحليل. قم برفع الملفات وبدء المعالجة أولاً.")
    
    else:
        # التحقق الفردي
        show_individual_verification(gemini_key)
'''

print(ERROR_DETECTION_SECTION)
