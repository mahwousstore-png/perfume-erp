"""
قسم التحقق المجمع بالذكاء الصناعي
يتم إضافته في app.py
"""

# ══════════════════════════════════════════════════════════════
# قسم التحقق المجمع
# ══════════════════════════════════════════════════════════════

def show_batch_verification_section():
    """عرض قسم التحقق المجمع"""
    st.markdown("# 🤖 التحقق المجمع بالذكاء الصناعي")
    st.markdown("> تحقق ذكي من عدة منتجات دفعة واحدة")
    
    st.markdown("---")
    
    # الخيارات
    st.markdown("### ⚙️ خيارات التحقق")
    
    col1, col2 = st.columns(2)
    
    with col1:
        verification_type = st.selectbox(
            "نوع التحقق",
            ["البحث الإلكتروني فقط", "التحقق من ملف المتجر فقط", "تحقق شامل (الاثنين معاً)"],
            help="اختر نوع التحقق المطلوب"
        )
    
    with col2:
        store_file = None
        if "ملف المتجر" in verification_type or "شامل" in verification_type:
            store_file = st.file_uploader(
                "📄 ملف المتجر (CSV)",
                type=["csv"],
                help="ارفع ملف CSV الخاص بمتجرك للتحقق"
            )
    
    st.markdown("---")
    
    # اختيار المنتجات
    st.markdown("### 📦 اختيار المنتجات")
    
    if st.session_state.results:
        df_approved = st.session_state.results.get("approved")
        
        if df_approved is not None and not df_approved.empty:
            st.success(f"✅ {len(df_approved)} منتج متاح للتحقق")
            
            # خيارات التحديد
            selection_method = st.radio(
                "طريقة التحديد",
                ["تحديد يدوي", "تحديد الكل", "تحديد حسب النطاق"],
                horizontal=True
            )
            
            selected_products = []
            
            if selection_method == "تحديد يدوي":
                # عرض checkboxes لكل منتج
                st.markdown("#### اختر المنتجات:")
                
                for idx, row in df_approved.iterrows():
                    product_name = row.get('اسم المنتج', row.iloc[0])
                    product_price = row.get('السعر', row.iloc[1] if len(row) > 1 else 'N/A')
                    
                    if st.checkbox(
                        f"{product_name} - {product_price} ريال",
                        key=f"batch_select_{idx}"
                    ):
                        selected_products.append({
                            "name": product_name,
                            "price": float(product_price) if product_price != 'N/A' else 0
                        })
            
            elif selection_method == "تحديد الكل":
                selected_products = [
                    {
                        "name": row.get('اسم المنتج', row.iloc[0]),
                        "price": float(row.get('السعر', row.iloc[1] if len(row) > 1 else 0))
                    }
                    for _, row in df_approved.iterrows()
                ]
                st.info(f"📊 تم تحديد جميع المنتجات ({len(selected_products)} منتج)")
            
            else:  # تحديد حسب النطاق
                col_range1, col_range2 = st.columns(2)
                with col_range1:
                    start_idx = st.number_input("من", min_value=1, max_value=len(df_approved), value=1)
                with col_range2:
                    end_idx = st.number_input("إلى", min_value=1, max_value=len(df_approved), value=min(10, len(df_approved)))
                
                selected_products = [
                    {
                        "name": row.get('اسم المنتج', row.iloc[0]),
                        "price": float(row.get('السعر', row.iloc[1] if len(row) > 1 else 0))
                    }
                    for idx, row in df_approved.iloc[start_idx-1:end_idx].iterrows()
                ]
                st.info(f"📊 تم تحديد {len(selected_products)} منتج من النطاق")
            
            st.markdown("---")
            
            # زر البدء
            if len(selected_products) > 0:
                st.markdown(f"### 🚀 جاهز للتحقق من {len(selected_products)} منتج")
                
                if st.button("🤖 بدء التحقق المجمع", type="primary", use_container_width=True):
                    # حفظ ملف المتجر مؤقتاً إذا تم رفعه
                    store_file_path = None
                    if store_file:
                        import tempfile
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
                            tmp.write(store_file.getvalue())
                            store_file_path = tmp.name
                    
                    # بدء التحقق
                    with st.spinner("⏳ جاري التحقق المجمع... قد يستغرق بعض الوقت"):
                        from modules.ai_verification import batch_verification
                        
                        result = batch_verification(selected_products, store_file_path)
                        
                        if result["success"]:
                            st.success("✅ تم التحقق المجمع بنجاح!")
                            
                            # عرض الملخص
                            summary = result.get("summary")
                            if summary:
                                st.markdown("### 📊 ملخص النتائج")
                                
                                col_s1, col_s2, col_s3 = st.columns(3)
                                
                                with col_s1:
                                    st.metric(
                                        "إجمالي المنتجات",
                                        summary.get("total_products", 0)
                                    )
                                
                                with col_s2:
                                    st.metric(
                                        "منتجات تنافسية",
                                        summary.get("competitive_count", 0),
                                        delta="✅"
                                    )
                                
                                with col_s3:
                                    st.metric(
                                        "تحتاج تعديل",
                                        summary.get("needs_adjustment", 0),
                                        delta="⚠️"
                                    )
                                
                                # التوصيات
                                if summary.get("recommendations"):
                                    st.markdown("#### 💡 التوصيات:")
                                    for rec in summary["recommendations"]:
                                        st.info(f"• {rec}")
                                
                                # الملخص العام
                                if summary.get("summary"):
                                    st.markdown("#### 📝 الملخص العام:")
                                    st.write(summary["summary"])
                            
                            # عرض النتائج التفصيلية
                            st.markdown("---")
                            st.markdown("### 📋 النتائج التفصيلية")
                            
                            results_list = result.get("results", [])
                            
                            for i, res in enumerate(results_list, 1):
                                if res.get("success"):
                                    product_results = res["results"]
                                    
                                    with st.expander(f"🔍 {i}. {product_results['product_name']}"):
                                        # البحث الإلكتروني
                                        if product_results.get("online_search"):
                                            st.markdown("#### 🌐 البحث الإلكتروني:")
                                            st.json(product_results["online_search"])
                                        
                                        # التحقق من المتجر
                                        if product_results.get("store_verification"):
                                            st.markdown("#### 🏪 التحقق من المتجر:")
                                            st.json(product_results["store_verification"])
                                        
                                        # التحليل
                                        if product_results.get("analysis"):
                                            st.markdown("#### 🎯 التحليل الذكي:")
                                            st.json(product_results["analysis"])
                                else:
                                    st.error(f"❌ خطأ في المنتج {i}: {res.get('error', 'غير معروف')}")
                            
                            # تحميل النتائج
                            st.markdown("---")
                            st.markdown("### 📥 تحميل النتائج")
                            
                            import json
                            results_json = json.dumps(result, ensure_ascii=False, indent=2)
                            
                            st.download_button(
                                "📄 تحميل النتائج (JSON)",
                                data=results_json,
                                file_name=f"batch_verification_{datetime.now():%Y%m%d_%H%M%S}.json",
                                mime="application/json",
                                use_container_width=True
                            )
                        
                        else:
                            st.error(f"❌ فشل التحقق المجمع: {result.get('error', 'غير معروف')}")
            
            else:
                st.warning("⚠️ لم يتم تحديد أي منتجات")
        
        else:
            st.info("📋 لا توجد منتجات موافق عليها")
    
    else:
        st.info("📤 قم برفع الملفات وبدء المعالجة أولاً")


# ملاحظة: يتم إضافة هذه الدالة في app.py كقسم جديد في القائمة الجانبية
