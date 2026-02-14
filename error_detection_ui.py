"""
error_detection_ui.py - واجهة عرض الأخطاء في Streamlit
═══════════════════════════════════════════════════════════
واجهة تفاعلية لعرض وتحليل الأخطاء في المطابقة
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, List
from smart_error_detector import SmartErrorDetector


def show_error_detection_tab(matches: List[Dict[str, Any]], api_key: str = ""):
    """
    عرض تبويب كشف الأخطاء.
    
    Args:
        matches: قائمة المطابقات
        api_key: مفتاح Gemini API
    """
    st.markdown("## 🔍 كشف الأخطاء الذكي")
    st.markdown("---")
    
    if not matches:
        st.info("📤 لا توجد مطابقات للتحليل. قم برفع الملفات وبدء المعالجة أولاً.")
        return
    
    # تهيئة النظام
    detector = SmartErrorDetector(api_key)
    
    # خيارات التحليل
    col1, col2 = st.columns(2)
    
    with col1:
        analysis_type = st.selectbox(
            "نوع التحليل",
            ["تحليل سريع", "تحليل عميق مع AI", "تحليل شامل"]
        )
    
    with col2:
        threshold = st.slider(
            "حد الثقة",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.05,
            help="المطابقات أقل من هذا الحد ستعتبر مشبوهة"
        )
    
    st.markdown("---")
    
    if st.button("🚀 بدء التحليل", type="primary"):
        with st.spinner("⏳ جاري تحليل المطابقات..."):
            
            # التحليل السريع
            if analysis_type == "تحليل سريع":
                errors = detector.detect_matching_errors(matches, threshold)
                show_error_report(errors)
            
            # التحليل العميق
            elif analysis_type == "تحليل عميق مع AI":
                if not api_key:
                    st.error("⚠️ يرجى إدخال مفتاح Gemini API أولاً!")
                    return
                
                sample_size = st.number_input(
                    "عدد العينات للتحليل",
                    min_value=10,
                    max_value=100,
                    value=50,
                    step=10
                )
                
                analysis = detector.analyze_batch(matches, sample_size)
                show_ai_analysis(analysis)
            
            # التحليل الشامل
            else:
                if not api_key:
                    st.error("⚠️ يرجى إدخال مفتاح Gemini API أولاً!")
                    return
                
                errors = detector.detect_matching_errors(matches, threshold)
                show_error_report(errors)
                
                st.markdown("---")
                st.markdown("### 🤖 التحقق بالذكاء الصناعي")
                
                analysis = detector.analyze_batch(matches, 50)
                show_ai_analysis(analysis)


def show_error_report(errors: Dict[str, Any]):
    """عرض تقرير الأخطاء."""
    
    # الإحصائيات
    st.markdown("### 📊 الإحصائيات العامة")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("إجمالي المطابقات", errors['total_matches'])
    col2.metric("المطابقات المحللة", errors['analyzed_matches'])
    col3.metric("معدل الأخطاء", f"{errors['error_rate']}%")
    col4.metric("المطابقات المشبوهة", len(errors['suspicious_matches']))
    
    st.markdown("---")
    
    # المطابقات المشبوهة
    if errors['suspicious_matches']:
        st.markdown("### ⚠️ المطابقات المشبوهة")
        
        df_suspicious = pd.DataFrame(errors['suspicious_matches'])
        st.dataframe(df_suspicious, use_container_width=True, height=300)
        
        # تحميل CSV
        csv = df_suspicious.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 تحميل المطابقات المشبوهة (CSV)",
            data=csv,
            file_name="suspicious_matches.csv",
            mime="text/csv"
        )
    else:
        st.success("✅ لا توجد مطابقات مشبوهة!")
    
    st.markdown("---")
    
    # فروقات الأسعار
    if errors['price_anomalies']:
        st.markdown("### 💰 فروقات الأسعار الغريبة")
        
        df_anomalies = pd.DataFrame(errors['price_anomalies'])
        st.dataframe(df_anomalies, use_container_width=True, height=300)
        
        # رسم بياني
        import plotly.express as px
        fig = px.bar(
            df_anomalies.head(20),
            x='my_product',
            y='difference_pct',
            title='أكبر 20 فرق سعر',
            labels={'my_product': 'المنتج', 'difference_pct': 'نسبة الفرق (%)'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # تحميل CSV
        csv = df_anomalies.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 تحميل فروقات الأسعار (CSV)",
            data=csv,
            file_name="price_anomalies.csv",
            mime="text/csv"
        )
    else:
        st.success("✅ لا توجد فروقات أسعار غريبة!")
    
    st.markdown("---")
    
    # البيانات المفقودة
    if errors['missing_data']:
        st.markdown("### 📝 البيانات المفقودة")
        st.warning(f"⚠️ {len(errors['missing_data'])} مطابقة تحتوي على بيانات ناقصة")
    else:
        st.success("✅ جميع البيانات كاملة!")


def show_ai_analysis(analysis: Dict[str, Any]):
    """عرض تحليل الذكاء الصناعي."""
    
    st.markdown("### 🤖 تحليل الذكاء الصناعي")
    
    # الإحصائيات
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("حجم العينة", analysis['sample_size'])
    col2.metric("الدقة", f"{analysis['accuracy']}%")
    col3.metric("مطابقات صحيحة", analysis['correct_matches'])
    col4.metric("مطابقات خاطئة", analysis['incorrect_matches'])
    
    st.markdown("---")
    
    # النتائج التفصيلية
    if analysis['verified_matches']:
        st.markdown("### 📋 النتائج التفصيلية")
        
        for i, match in enumerate(analysis['verified_matches'][:10], 1):
            with st.expander(f"المطابقة {i}: {match['my_product'][:50]}..."):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**منتجنا:**")
                    st.write(match['my_product'])
                    st.markdown(f"**التشابه الأصلي:** {match['original_similarity']:.2f}")
                
                with col2:
                    st.markdown("**منتج المنافس:**")
                    st.write(match['competitor_product'])
                
                verification = match['ai_verification']
                
                if verification.get('is_match'):
                    st.success(f"✅ مطابقة صحيحة (ثقة: {verification.get('confidence', 0):.2f})")
                else:
                    st.error(f"❌ مطابقة خاطئة (ثقة: {verification.get('confidence', 0):.2f})")
                
                st.markdown(f"**السبب:** {verification.get('reason', 'غير متوفر')}")
                
                if 'extracted_info' in verification:
                    st.json(verification['extracted_info'])


def show_individual_verification(api_key: str = ""):
    """عرض واجهة التحقق الفردي."""
    
    st.markdown("## 🔎 التحقق الفردي من المطابقة")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        product1 = st.text_area(
            "المنتج الأول",
            placeholder="مثال: عطر ديور سوفاج او دو بارفان 100 مل رجالي",
            height=100
        )
    
    with col2:
        product2 = st.text_area(
            "المنتج الثاني",
            placeholder="مثال: ديور سوفاج edp 100ml للرجال",
            height=100
        )
    
    if st.button("🔍 تحقق من المطابقة", type="primary"):
        if not product1 or not product2:
            st.error("⚠️ يرجى إدخال اسمي المنتجين!")
            return
        
        if not api_key:
            st.error("⚠️ يرجى إدخال مفتاح Gemini API أولاً!")
            return
        
        with st.spinner("⏳ جاري التحقق..."):
            detector = SmartErrorDetector(api_key)
            result = detector.verify_match_with_ai(product1, product2)
            
            st.markdown("---")
            st.markdown("### 📊 النتيجة")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if result.get('is_match'):
                    st.success("✅ مطابقة")
                else:
                    st.error("❌ غير متطابقة")
            
            with col2:
                confidence = result.get('confidence', 0)
                st.metric("الثقة", f"{confidence:.2%}")
            
            with col3:
                if confidence > 0.8:
                    st.success("🎯 ثقة عالية")
                elif confidence > 0.5:
                    st.warning("⚠️ ثقة متوسطة")
                else:
                    st.error("❌ ثقة منخفضة")
            
            st.markdown("---")
            st.markdown(f"**السبب:** {result.get('reason', 'غير متوفر')}")
            
            if 'extracted_info' in result:
                st.markdown("### 📝 المعلومات المستخرجة")
                st.json(result['extracted_info'])
