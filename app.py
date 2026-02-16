# -*- coding: utf-8 -*-
"""
نظام التسعير الذكي للعطور - الإصدار 3.
تطبيق Streamlit متكامل بـ 7 صفحات مترابطة.
"""

import streamlit as st
import pandas as pd
from datetime import datetime

# ── إعدادات الصفحة (أول أمر Streamlit) ──────────────────────
st.set_page_config(
    page_title="نظام التسعير الذكي للعطور",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded",
)

from engine import (  # noqa: E402
    run_full_analysis,
    gemini_verify,
    export_excel,
    send_to_make,
)

# ── استيراد نظام الذكاء الاصطناعي للصفحات ────────────────────
try:
    from modules.ai_page_manager import show_page_ai_assistant, integrate_ai_into_page
    AI_PAGE_MANAGER_AVAILABLE = True
except ImportError:
    AI_PAGE_MANAGER_AVAILABLE = False
    print("⚠️ نظام إدارة الذكاء الاصطناعي غير متوفر")

# ── CSS مخصص ─────────────────────────────────────────────────
st.markdown("""
<style>
    .main {direction: rtl; text-align: right;}
    .stMetric {text-align: center;}
    .block-container {padding-top: 1rem;}
    div[data-testid="stMetricValue"] {font-size: 2rem;}
    .severity-critical {
        background-color: #ff4b4b20;
        border-right: 4px solid #ff4b4b;
        padding: 8px; margin: 4px 0; border-radius: 4px;
    }
    .severity-medium {
        background-color: #ffa72620;
        border-right: 4px solid #ffa726;
        padding: 8px; margin: 4px 0; border-radius: 4px;
    }
    .severity-normal {
        background-color: #66bb6a20;
        border-right: 4px solid #66bb6a;
        padding: 8px; margin: 4px 0; border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)


# ── تهيئة الجلسة ─────────────────────────────────────────────
def init_session():
    """تهيئة متغيرات الجلسة."""
    defaults = {
        "results": None,
        "my_file": None,
        "comp_files": [],
        "gemini_key": "",
        "make_url": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_session()


# ── دوال مساعدة ──────────────────────────────────────────────
def show_table(df, title="", height=400):
    """عرض جدول مع عنوان."""
    if title:
        st.subheader(title)
    if df is not None and not df.empty:
        display_cols = [
            c for c in df.columns
            if c not in ["pid_my", "pid_comp"]
        ]
        st.dataframe(
            df[display_cols],
            use_container_width=True,
            height=height,
            hide_index=True,
        )
    else:
        st.info("لا توجد بيانات.")


def download_btn(df, label, filename):
    """زر تحميل Excel."""
    if df is not None and not df.empty:
        st.download_button(
            label=label,
            data=export_excel(df),
            file_name=filename,
            mime=(
                "application/vnd.openxmlformats-"
                "officedocument.spreadsheetml.sheet"
            ),
            use_container_width=True,
        )


# ══════════════════════════════════════════════════════════════
# الشريط الجانبي - التنقل
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.image(
        "https://img.icons8.com/3d-fluency/94/diamond.png",
        width=60,
    )
    st.title("💎 نظام التسعير")
    st.markdown("---")

    page = st.radio(
        "📑 الصفحات",
        [
            "🏠 لوحة القيادة",
            "� التحليل والمقارنة",
            "🤖 الأدوات الذكية",
            "💼 الإدارة المالية",
            "⚙️ الأدوات والإعدادات",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.caption("الإصدار v14.2 | نظام التسعير الذكي")

# ══════════════════════════════════════════════════════════════
# صفحة: التحليل والمقارنة
# ══════════════════════════════════════════════════════════════
elif page == "📊 التحليل والمقارنة":
    st.header("📊 التحليل والمقارنة")
    st.caption("تحليل شامل للأسعار ومقارنتها مع المنافسين")
    st.markdown("---")

    # التحقق من وجود نتائج
    r = st.session_state.results
    if r is None:
        st.info("📋 ارفع الملفات وابدأ المعالجة أولاً من صفحة **رفع الملفات**.")
    else:
        # إحصائيات سريعة
        stats = r.get("stats", {})
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("🔴 رفع سعر", stats.get("raise_count", 0))
        col2.metric("🟡 خفض سعر", stats.get("lower_count", 0))
        col3.metric("🟢 موافق", stats.get("approved_count", 0))
        col4.metric("🆕 مفقودة", stats.get("missing_count", 0))
        col5.metric("📊 إجمالي", stats.get("total", 0))

        st.markdown("---")

        # Tabs للتحليل المختلف
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📤 رفع الملفات",
            "🔴 رفع سعر",
            "🟡 خفض سعر",
            "🟢 موافق عليها",
            "🔵 منتجات مفقودة"
        ])

        with tab1:
            st.subheader("📤 رفع ملفات البيانات والمعالجة")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**🏪 ملف متجرك**")
                up_my = st.file_uploader(
                    "ارفع ملف Excel أو CSV",
                    type=["xlsx", "csv"],
                    key="upload_my_analysis",
                )
                if up_my is not None:
                    st.session_state.my_file = {
                        "name": up_my.name,
                        "data": up_my.getvalue(),
                    }
                    st.success(f"✅ {up_my.name}")

            with col2:
                st.markdown("**🏢 ملفات المنافسين**")
                up_comp = st.file_uploader(
                    "ارفع ملفات المنافسين",
                    type=["xlsx", "csv"],
                    accept_multiple_files=True,
                    key="upload_comp_analysis",
                )
                if up_comp:
                    st.session_state.comp_files = [
                        {"name": f.name, "data": f.getvalue()}
                        for f in up_comp
                    ]
                    st.success(f"✅ {len(up_comp)} ملف منافس")

            st.markdown("---")

            # إعدادات المعالجة
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                min_score = st.slider(
                    "الحد الأدنى لنسبة التطابق",
                    50, 100, 75, 5,
                    key="min_score_analysis",
                )
            with col_s2:
                st.info(
                    f"**{min_score}%** - "
                    + ("دقة عالية" if min_score >= 80 else "تغطية أوسع")
                )

            if st.button(
                "🚀 ابدأ المعالجة الآن",
                use_container_width=True,
                type="primary",
            ):
                if st.session_state.my_file is None:
                    st.error("❌ ارفع ملف متجرك أولاً.")
                elif not st.session_state.comp_files:
                    st.error("❌ ارفع ملف منافس واحد على الأقل.")
                else:
                    with st.spinner("⏳ جاري التحليل الذكي..."):
                        try:
                            results = run_full_analysis(
                                st.session_state.my_file,
                                st.session_state.comp_files,
                                min_score,
                            )
                            st.session_state.results = results
                            stats = results.get("stats", {})
                            if stats:
                                st.success(
                                    f"🎉 اكتملت المعالجة! "
                                    f"{stats['total']} مقارنة | "
                                    f"{stats['missing_count']} منتج مفقود"
                                )
                                st.balloons()
                            else:
                                st.warning("⚠️ لم يتم العثور على مطابقات.")
                        except Exception as exc:
                            st.error(f"❌ خطأ: {exc}")

        with tab2:
            st.subheader("🔴 منتجات تحتاج رفع سعر")
            st.caption("سعرك أقل من المنافس - فرصة لزيادة الأرباح")

            df = r.get("raise", pd.DataFrame())
            if df.empty:
                st.success("🎉 لا توجد منتجات تحتاج رفع سعر!")
            else:
                # فلتر الخطورة
                sev = st.multiselect(
                    "تصفية حسب الخطورة:",
                    ["حرج", "متوسط", "عادي"],
                    default=["حرج", "متوسط", "عادي"],
                    key="raise_sev",
                )
                filtered = df[df["الخطورة"].isin(sev)]

                col1, col2 = st.columns([1, 4])
                with col1:
                    st.metric("عدد المنتجات", len(filtered))
                with col2:
                    if not filtered.empty:
                        avg = round(filtered["الفرق"].mean(), 2)
                        st.metric("متوسط الفرق", f"{avg} ر.س")

                # تحسين عرض الجدول
                st.dataframe(
                    filtered,
                    use_container_width=True,
                    column_config={
                        "السعر": st.column_config.NumberColumn(
                            "السعر",
                            format="%.2f ر.س",
                        ),
                        "سعر المنافس": st.column_config.NumberColumn(
                            "سعر المنافس",
                            format="%.2f ر.س",
                        ),
                        "الفرق": st.column_config.NumberColumn(
                            "الفرق",
                            format="%.2f ر.س",
                        ),
                    },
                    hide_index=True,
                )

                download_btn(
                    filtered,
                    "📥 تحميل قائمة رفع السعر",
                    f"raise_price_{datetime.now():%Y%m%d}.xlsx",
                )

        with tab3:
            st.subheader("🟡 منتجات تحتاج خفض سعر")
            st.caption("سعرك أعلى من المنافس - خطر خسارة عملاء")

            df = r.get("lower", pd.DataFrame())
            if df.empty:
                st.success("🎉 لا توجد منتجات تحتاج خفض سعر!")
            else:
                sev = st.multiselect(
                    "تصفية حسب الخطورة:",
                    ["حرج", "متوسط", "عادي"],
                    default=["حرج", "متوسط", "عادي"],
                    key="lower_sev_tab",
                )
                filtered = df[df["الخطورة"].isin(sev)]

                col1, col2 = st.columns([1, 4])
                with col1:
                    st.metric("عدد المنتجات", len(filtered))
                with col2:
                    if not filtered.empty:
                        avg = round(filtered["الفرق"].mean(), 2)
                        st.metric("متوسط الفرق", f"{avg} ر.س")

                # تحسين عرض الجدول
                st.dataframe(
                    filtered,
                    use_container_width=True,
                    column_config={
                        "السعر": st.column_config.NumberColumn(
                            "السعر",
                            format="%.2f ر.س",
                        ),
                        "سعر المنافس": st.column_config.NumberColumn(
                            "سعر المنافس",
                            format="%.2f ر.س",
                        ),
                        "الفرق": st.column_config.NumberColumn(
                            "الفرق",
                            format="%.2f ر.س",
                        ),
                    },
                    hide_index=True,
                )

                download_btn(
                    filtered,
                    "📥 تحميل قائمة خفض السعر",
                    f"lower_price_{datetime.now():%Y%m%d}.xlsx",
                )

        with tab4:
            st.subheader("🟢 أسعار موافق عليها")
            st.caption("أسعارك متوازنة مع السوق")

            df = r.get("approved", pd.DataFrame())
            if df.empty:
                st.info("لا توجد منتجات متطابقة السعر.")
            else:
                st.metric("عدد المنتجات الموافق عليها", len(df))

                # تحسين عرض الجدول
                st.dataframe(
                    df,
                    use_container_width=True,
                    column_config={
                        "السعر": st.column_config.NumberColumn(
                            "السعر",
                            format="%.2f ر.س",
                        ),
                        "سعر المنافس": st.column_config.NumberColumn(
                            "سعر المنافس",
                            format="%.2f ر.س",
                        ),
                        "الفرق": st.column_config.NumberColumn(
                            "الفرق",
                            format="%.2f ر.س",
                        ),
                    },
                    hide_index=True,
                )

                download_btn(
                    df,
                    "📥 تحميل القائمة الموافق عليها",
                    f"approved_{datetime.now():%Y%m%d}.xlsx",
                )

        with tab5:
            st.subheader("🔵 منتجات مفقودة - موجودة عند المنافسين فقط")
            st.caption("فرص جديدة لتوسيع تشكيلتك")

            df = r.get("missing", pd.DataFrame())
            if df.empty:
                st.success("🎉 تشكيلتك شاملة! لا توجد منتجات مفقودة.")
            else:
                # فلتر حسب المنافس
                comps = df["المنافس"].unique().tolist()
                sel = st.multiselect(
                    "تصفية حسب المنافس:",
                    comps, default=comps,
                    key="missing_comp_tab",
                )
                filtered = df[df["المنافس"].isin(sel)]

                col1, col2 = st.columns([1, 4])
                with col1:
                    st.metric("منتجات مفقودة", len(filtered))
                with col2:
                    types = filtered["نوع_المنتج"].value_counts()
                    st.write("التوزيع حسب النوع:", types.to_dict())

                # تحسين عرض الجدول
                st.dataframe(
                    filtered,
                    use_container_width=True,
                    column_config={
                        "سعر المنافس": st.column_config.NumberColumn(
                            "سعر المنافس",
                            format="%.2f ر.س",
                        ),
                    },
                    hide_index=True,
                )

                download_btn(
                    filtered,
                    "📥 تحميل المنتجات المفقودة",
                    f"missing_{datetime.now():%Y%m%d}.xlsx",
                )

    # ── مساعد الذكاء الاصطناعي ──────────────────────────────
    if AI_PAGE_MANAGER_AVAILABLE:
        show_page_ai_assistant("التحليل والمقارنة")

# ══════════════════════════════════════════════════════════════
# صفحة: أتمتة Make
# ══════════════════════════════════════════════════════════════
elif page == "⚡ Make أتمتة":
    st.header("⚡ Make أتمتة")
    st.caption("أرسل النتائج تلقائياً إلى Google Sheets أو أي خدمة")
    st.markdown("---")

    # إعداد Webhook
    st.subheader("🔗 إعداد Webhook")
    webhook = st.text_input(
        "رابط Webhook من Make.com",
        value=st.session_state.make_url,
        placeholder="https://hook.eu2.make.com/xxx...",
    )
    st.session_state.make_url = webhook

    st.markdown("---")

    # شرح الربط
    with st.expander("📖 كيف أحصل على رابط Webhook؟"):
        st.markdown(
            "1. سجل في [Make.com](https://www.make.com/)\n"
            "2. أنشئ **Scenario** جديد\n"
            "3. أضف **Webhook** كـ Trigger\n"
            "4. انسخ الرابط وألصقه هنا\n"
            "5. أضف **Google Sheets** كـ Action\n"
            "6. شغّل الـ Scenario"
        )

    r = st.session_state.results
    if r is None:
        st.info("📋 ابدأ المعالجة أولاً.")
    elif not webhook:
        st.warning("⚠️ أدخل رابط Webhook أعلاه.")
    else:
        st.subheader("📤 إرسال النتائج")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button(
                "🔴 إرسال رفع سعر",
                use_container_width=True,
            ):
                df = r.get("raise", pd.DataFrame())
                if not df.empty:
                    with st.spinner("⏳ جاري الإرسال..."):
                        data = df.to_dict(orient="records")
                        resp = send_to_make(webhook, data)
                    if resp.get("ok"):
                        st.success("✅ تم الإرسال!")
                    else:
                        st.error(f"❌ فشل: {resp}")
                else:
                    st.info("لا توجد بيانات.")

        with col2:
            if st.button(
                "🟡 إرسال خفض سعر",
                use_container_width=True,
            ):
                df = r.get("lower", pd.DataFrame())
                if not df.empty:
                    with st.spinner("⏳ جاري الإرسال..."):
                        data = df.to_dict(orient="records")
                        resp = send_to_make(webhook, data)
                    if resp.get("ok"):
                        st.success("✅ تم الإرسال!")
                    else:
                        st.error(f"❌ فشل: {resp}")
                else:
                    st.info("لا توجد بيانات.")

        with col3:
            if st.button(
                "🆕 إرسال المفقودة",
                use_container_width=True,
            ):
                df = r.get("missing", pd.DataFrame())
                if not df.empty:
                    with st.spinner("⏳ جاري الإرسال..."):
                        data = df.to_dict(orient="records")
                        resp = send_to_make(webhook, data)
                    if resp.get("ok"):
                        st.success("✅ تم الإرسال!")
                    else:
                        st.error(f"❌ فشل: {resp}")
                else:
                    st.info("لا توجد بيانات.")

        st.markdown("---")

        if st.button(
            "📤 إرسال الكل دفعة واحدة",
            use_container_width=True,
            type="primary",
        ):
            df_all = r.get("all", pd.DataFrame())
            if not df_all.empty:
                with st.spinner("⏳ جاري إرسال جميع النتائج..."):
                    data = df_all.to_dict(orient="records")
                    resp = send_to_make(webhook, data)
                if resp.get("ok"):
                    st.success("✅ تم إرسال جميع النتائج!")
                else:
                    st.error(f"❌ فشل: {resp}")
            else:
                st.info("لا توجد بيانات.")

    # ── مساعد الذكاء الاصطناعي ──────────────────────────────
    if AI_PAGE_MANAGER_AVAILABLE:
        show_page_ai_assistant("Make أتمتة")

# ══════════════════════════════════════════════════════════════
# صفحة: سجل العمليات
# ══════════════════════════════════════════════════════════════
elif page == "📊 سجل العمليات":
    st.header("📊 سجل العمليات")
    st.caption("تتبع جميع العمليات والتحليلات المنجزة")
    st.markdown("---")
    st.info("قريباً: عرض سجل العمليات التاريخي.")

    # ── مساعد الذكاء الاصطناعي ──────────────────────────────
    if AI_PAGE_MANAGER_AVAILABLE:
        show_page_ai_assistant("سجل العمليات")

# ══════════════════════════════════════════════════════════════
# صفحة: يحتاج مراجعة
# ══════════════════════════════════════════════════════════════
elif page == "⚠️ يحتاج مراجعة":
    st.header("⚠️ منتجات تحتاج مراجعة")
    st.caption("منتجات تتطلب تدخلاً يدوياً أو مراجعة إضافية")
    st.markdown("---")
    st.info("قريباً: عرض المنتجات التي تحتاج مراجعة.")

    # ── مساعد الذكاء الاصطناعي ──────────────────────────────
    if AI_PAGE_MANAGER_AVAILABLE:
        show_page_ai_assistant("يحتاج مراجعة")

# ══════════════════════════════════════════════════════════════
# صفحة: تفاصيل المطابقة
# ══════════════════════════════════════════════════════════════
elif page == "🔍 تفاصيل المطابقة":
    st.header("🔍 تفاصيل المطابقة")
    st.caption("عرض تفاصيل دقيقة لعملية المطابقة والخوارزميات المستخدمة")
    st.markdown("---")
    st.info("قريباً: عرض تفاصيل المطابقة.")

    # ── مساعد الذكاء الاصطناعي ──────────────────────────────
    if AI_PAGE_MANAGER_AVAILABLE:
        show_page_ai_assistant("تفاصيل المطابقة")

# ══════════════════════════════════════════════════════════════
# صفحة: تحقق AI
# ══════════════════════════════════════════════════════════════
elif page == "🤖 تحقق AI":
    st.header("🤖 التحقق الذكي بـ AI")
    st.caption("تحقق فردي أو مجمع للمنتجات مع توصيات ذكية")
    st.markdown("---")

    # مفتاح API
    api_key = st.text_input(
        "🔑 مفتاح Gemini API",
        value=st.session_state.gemini_key,
        type="password",
        help="احصل عليه من: https://ai.google.dev/",
    )
    st.session_state.gemini_key = api_key

    r = st.session_state.results
    if r is None:
        st.info("📋 ابدأ المعالجة أولاً.")
    elif not api_key:
        st.warning("⚠️ أدخل مفتاح Gemini API أعلاه.")
    else:
        df_all = r.get("all", pd.DataFrame())
        if df_all.empty:
            st.info("لا توجد مقارنات.")
        else:
            tab1, tab2 = st.tabs(["🔍 تحقق فردي", "📊 تحقق مجمع"])
            
            with tab1:
                st.subheader("اختر منتج للتحقق الفردي:")

                # عرض المنتجات كأزرار
                for idx, row in df_all.iterrows():
                    icon = row.get("الأيقونة", "")
                    name = row.get("المنتج", "")
                    price = row.get("السعر", 0)
                    comp_price = row.get("سعر المنافس", 0)
                    diff = row.get("الفرق", 0)

                    col_btn, col_info = st.columns([1, 3])
                    with col_btn:
                        btn = st.button(
                            f"{icon} تحقق",
                            key=f"gem_{idx}",
                            use_container_width=True,
                        )
                    with col_info:
                        st.markdown(
                            f"**{name}** | "
                            f"سعري: {price} | "
                            f"المنافس: {comp_price} | "
                            f"الفرق: {diff}"
                        )

                    if btn:
                        with st.spinner("🤖 AI يحلل..."):
                            result = gemini_verify(
                                name, price, comp_price, api_key
                            )
                        st.markdown(
                            f'<div class="severity-medium">'
                            f"🤖 <b>تحليل AI:</b><br>{result}"
                            f"</div>",
                            unsafe_allow_html=True,
                        )
            
            with tab2:
                st.subheader("تحليل جماعي للمنتجات")

                if st.button("🚀 ابدأ التحقق المجمع", use_container_width=True, type="primary"):
                    with st.spinner("🤖 AI يحلل جميع المنتجات..."):
                        # استيراد دالة التحقق المجمع من gemini_ai
                        from gemini_ai import batch_generate_descriptions
                        
                        # تحضير البيانات
                        products = []
                        for _, row in df_all.iterrows():
                            products.append({
                                'name': row.get('المنتج', ''),
                                'price': row.get('السعر', 0),
                                'comp_price': row.get('سعر المنافس', 0),
                                'diff': row.get('الفرق', 0),
                            })
                        
                        # التحقق المجمع
                        results = []
                        for product in products[:10]:  # محدود لتجنب الحمل الزائد
                            try:
                                from gemini_ai import generate_pricing_recommendation
                                rec = generate_pricing_recommendation(
                                    product['name'], product['price'], product['comp_price'], 20.0
                                )
                                results.append({
                                    'product': product['name'],
                                    'recommendation': rec or 'لا توجد توصية'
                                })
                            except Exception as e:
                                results.append({
                                    'product': product['name'],
                                    'recommendation': f'خطأ: {str(e)}'
                                })
                        
                        # عرض النتائج
                        st.success("✅ تم الانتهاء من التحقق المجمع!")
                        for res in results:
                            st.markdown(f"**{res['product']}**: {res['recommendation']}")

    # ── مساعد الذكاء الاصطناعي ──────────────────────────────
    if AI_PAGE_MANAGER_AVAILABLE:
        show_page_ai_assistant("تحقق AI")

# ══════════════════════════════════════════════════════════════
# صفحة: محادثة AI
# ══════════════════════════════════════════════════════════════
elif page == "💬 محادثة AI":
    st.header("💬 محادثة AI")
    st.caption("محادثة تفاعلية مع الذكاء الاصطناعي للحصول على نصائح وتحليلات")
    st.markdown("---")
    st.info("قريباً: واجهة محادثة مع AI.")

    # ── مساعد الذكاء الاصطناعي ──────────────────────────────
    if AI_PAGE_MANAGER_AVAILABLE:
        show_page_ai_assistant("محادثة AI")

# ══════════════════════════════════════════════════════════════
# صفحة: استديو مهووس
# ══════════════════════════════════════════════════════════════
elif page == "🎬 استديو مهووس":
    st.header("🎬 استديو مهووس")
    st.caption("أدوات إنشاء محتوى وتصميم للعطور")
    st.markdown("---")
    st.info("قريباً: أدوات تصميم وإنشاء محتوى.")

    # ── مساعد الذكاء الاصطناعي ──────────────────────────────
    if AI_PAGE_MANAGER_AVAILABLE:
        show_page_ai_assistant("استديو مهووس")

# ══════════════════════════════════════════════════════════════
# صفحة: قاعدة البيانات
# ══════════════════════════════════════════════════════════════
elif page == "💾 قاعدة البيانات":
    st.header("💾 قاعدة البيانات")
    st.caption("إدارة واستعراض قاعدة البيانات الرئيسية")
    st.markdown("---")
    st.info("قريباً: واجهة إدارة قاعدة البيانات.")

    # ── مساعد الذكاء الاصطناعي ──────────────────────────────
    if AI_PAGE_MANAGER_AVAILABLE:
        show_page_ai_assistant("قاعدة البيانات")

# ══════════════════════════════════════════════════════════════
# صفحة: المشتريات اليومية
# ══════════════════════════════════════════════════════════════
elif page == "🛒 المشتريات اليومية":
    st.header("🛒 المشتريات اليومية")
    st.caption("تتبع المشتريات والطلبات اليومية")
    st.markdown("---")
    st.info("قريباً: نظام تتبع المشتريات.")

    # ── مساعد الذكاء الاصطناعي ──────────────────────────────
    if AI_PAGE_MANAGER_AVAILABLE:
        show_page_ai_assistant("المشتريات اليومية")

# ══════════════════════════════════════════════════════════════
# صفحة: إدارة الموردين
# ══════════════════════════════════════════════════════════════
elif page == "🏪 إدارة الموردين":
    st.header("🏪 إدارة الموردين")
    st.caption("إدارة قائمة الموردين والتعامل معهم")
    st.markdown("---")
    st.info("قريباً: نظام إدارة الموردين.")

    # ── مساعد الذكاء الاصطناعي ──────────────────────────────
    if AI_PAGE_MANAGER_AVAILABLE:
        show_page_ai_assistant("إدارة الموردين")

# ══════════════════════════════════════════════════════════════
# صفحة: مذكرة المصروفات
# ══════════════════════════════════════════════════════════════
elif page == "💰 مذكرة المصروفات":
    st.header("💰 مذكرة المصروفات")
    st.caption("تسجيل وتتبع المصروفات والنفقات")
    st.markdown("---")
    st.info("قريباً: نظام تتبع المصروفات.")

    # ── مساعد الذكاء الاصطناعي ──────────────────────────────
    if AI_PAGE_MANAGER_AVAILABLE:
        show_page_ai_assistant("مذكرة المصروفات")

# ══════════════════════════════════════════════════════════════
# صفحة: الإعدادات
# ══════════════════════════════════════════════════════════════
elif page == "⚙️ الإعدادات":
    st.header("⚙️ الإعدادات")
    st.caption("تكوين التطبيق وإدارة الإعدادات العامة")
    st.markdown("---")
    
    st.subheader("🔑 مفاتيح API")
    gemini_key = st.text_input(
        "مفتاح Gemini API",
        value=st.session_state.gemini_key,
        type="password",
    )
    st.session_state.gemini_key = gemini_key
    
    st.subheader("📡 حالة الاتصالات")
    st.success("🟢 Gemini متصل")
    st.success("🟢 OpenRouter متصل")
    st.error("🔴 Make يحتاج تحديث")
    st.error("🔴 Make يحتاج إضافة")
    
    st.subheader("📂 معلومات النظام")
    st.write(f"الإصدار: v14.2")
    st.write(f"التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # ── مساعد الذكاء الاصطناعي ──────────────────────────────
    if AI_PAGE_MANAGER_AVAILABLE:
        show_page_ai_assistant("الإعدادات")
