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
            "📤 رفع الملفات",
            "🔴 رفع سعر",
            "🟡 خفض سعر",
            "🟢 موافق عليها",
            "🆕 منتجات مفقودة",
            "🤖 تحقق Gemini",
            "⚡ أتمتة Make",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.caption("الإصدار 3.0 | نظام التسعير الذكي")

# ══════════════════════════════════════════════════════════════
# صفحة: رفع الملفات
# ══════════════════════════════════════════════════════════════
if page == "📤 رفع الملفات":
    st.header("📤 رفع ملفات البيانات والمعالجة")
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏪 ملف متجرك")
        up_my = st.file_uploader(
            "ارفع ملف Excel أو CSV",
            type=["xlsx", "csv"],
            key="upload_my",
        )
        if up_my is not None:
            st.session_state.my_file = {
                "name": up_my.name,
                "data": up_my.getvalue(),
            }
            st.success(f"✅ {up_my.name}")

    with col2:
        st.subheader("🏢 ملفات المنافسين")
        up_comp = st.file_uploader(
            "ارفع ملفات المنافسين",
            type=["xlsx", "csv"],
            accept_multiple_files=True,
            key="upload_comp",
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

# ══════════════════════════════════════════════════════════════
# صفحة: لوحة القيادة
# ══════════════════════════════════════════════════════════════
elif page == "🏠 لوحة القيادة":
    st.header("🏠 لوحة القيادة الرئيسية")
    st.markdown("---")

    r = st.session_state.results
    if r is None:
        st.info("📋 ارفع الملفات وابدأ المعالجة أولاً من صفحة **رفع الملفات**.")
    else:
        stats = r.get("stats", {})

        # صف المقاييس الرئيسية
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("📊 إجمالي المقارنات", stats.get("total", 0))
        c2.metric("🔴 رفع سعر", stats.get("raise_count", 0))
        c3.metric("🟡 خفض سعر", stats.get("lower_count", 0))
        c4.metric("🟢 موافق", stats.get("approved_count", 0))
        c5.metric("🆕 مفقودة", stats.get("missing_count", 0))

        st.markdown("---")

        # صف ثانوي
        c6, c7, c8 = st.columns(3)
        c6.metric("⚠️ حالات حرجة", stats.get("critical", 0))
        c7.metric("📈 متوسط الفرق", f"{stats.get('avg_diff', 0)} ر.س")
        c8.metric("🏢 عدد المنافسين", stats.get("competitors", 0))

        st.markdown("---")
        st.caption(f"آخر تحديث: {stats.get('timestamp', '-')}")

        # ملخص سريع
        df_all = r.get("all", pd.DataFrame())
        if not df_all.empty:
            st.subheader("📋 ملخص سريع - أهم 10 مقارنات")
            top10 = df_all.sort_values(
                "الفرق", key=abs, ascending=False
            ).head(10)
            show_table(top10, height=350)

# ══════════════════════════════════════════════════════════════
# صفحة: رفع سعر
# ══════════════════════════════════════════════════════════════
elif page == "🔴 رفع سعر":
    st.header("🔴 منتجات تحتاج رفع سعر")
    st.caption("سعرك أقل من المنافس - فرصة لزيادة الأرباح")
    st.markdown("---")

    r = st.session_state.results
    if r is None:
        st.info("📋 ابدأ المعالجة أولاً.")
    else:
        df = r.get("raise", pd.DataFrame())
        if df.empty:
            st.success("🎉 لا توجد منتجات تحتاج رفع سعر!")
        else:
            # فلتر الخطورة
            sev = st.multiselect(
                "تصفية حسب الخطورة:",
                ["حرج", "متوسط", "عادي"],
                default=["حرج", "متوسط", "عادي"],
            )
            filtered = df[df["الخطورة"].isin(sev)]

            c1, c2 = st.columns([1, 4])
            with c1:
                st.metric("عدد المنتجات", len(filtered))
            with c2:
                if not filtered.empty:
                    avg = round(filtered["الفرق"].mean(), 2)
                    st.metric("متوسط الفرق", f"{avg} ر.س")

            show_table(filtered)
            download_btn(
                filtered,
                "📥 تحميل قائمة رفع السعر",
                f"raise_price_{datetime.now():%Y%m%d}.xlsx",
            )

# ══════════════════════════════════════════════════════════════
# صفحة: خفض سعر
# ══════════════════════════════════════════════════════════════
elif page == "🟡 خفض سعر":
    st.header("🟡 منتجات تحتاج خفض سعر")
    st.caption("سعرك أعلى من المنافس - خطر خسارة عملاء")
    st.markdown("---")

    r = st.session_state.results
    if r is None:
        st.info("📋 ابدأ المعالجة أولاً.")
    else:
        df = r.get("lower", pd.DataFrame())
        if df.empty:
            st.success("🎉 لا توجد منتجات تحتاج خفض سعر!")
        else:
            sev = st.multiselect(
                "تصفية حسب الخطورة:",
                ["حرج", "متوسط", "عادي"],
                default=["حرج", "متوسط", "عادي"],
                key="lower_sev",
            )
            filtered = df[df["الخطورة"].isin(sev)]

            c1, c2 = st.columns([1, 4])
            with c1:
                st.metric("عدد المنتجات", len(filtered))
            with c2:
                if not filtered.empty:
                    avg = round(filtered["الفرق"].mean(), 2)
                    st.metric("متوسط الفرق", f"{avg} ر.س")

            show_table(filtered)
            download_btn(
                filtered,
                "📥 تحميل قائمة خفض السعر",
                f"lower_price_{datetime.now():%Y%m%d}.xlsx",
            )

# ══════════════════════════════════════════════════════════════
# صفحة: موافق عليها
# ══════════════════════════════════════════════════════════════
elif page == "🟢 موافق عليها":
    st.header("🟢 أسعار موافق عليها")
    st.caption("أسعارك متوازنة مع السوق")
    st.markdown("---")

    r = st.session_state.results
    if r is None:
        st.info("📋 ابدأ المعالجة أولاً.")
    else:
        df = r.get("approved", pd.DataFrame())
        if df.empty:
            st.info("لا توجد منتجات متطابقة السعر.")
        else:
            st.metric("عدد المنتجات الموافق عليها", len(df))
            show_table(df)
            download_btn(
                df,
                "📥 تحميل القائمة الموافق عليها",
                f"approved_{datetime.now():%Y%m%d}.xlsx",
            )

# ══════════════════════════════════════════════════════════════
# صفحة: منتجات مفقودة
# ══════════════════════════════════════════════════════════════
elif page == "🆕 منتجات مفقودة":
    st.header("🆕 منتجات مفقودة - موجودة عند المنافسين فقط")
    st.caption("فرص جديدة لتوسيع تشكيلتك")
    st.markdown("---")

    r = st.session_state.results
    if r is None:
        st.info("📋 ابدأ المعالجة أولاً.")
    else:
        df = r.get("missing", pd.DataFrame())
        if df.empty:
            st.success("🎉 تشكيلتك شاملة! لا توجد منتجات مفقودة.")
        else:
            # فلتر حسب المنافس
            comps = df["المنافس"].unique().tolist()
            sel = st.multiselect(
                "تصفية حسب المنافس:",
                comps, default=comps,
                key="missing_comp",
            )
            filtered = df[df["المنافس"].isin(sel)]

            c1, c2 = st.columns([1, 4])
            with c1:
                st.metric("منتجات مفقودة", len(filtered))
            with c2:
                types = filtered["نوع_المنتج"].value_counts()
                st.write("التوزيع حسب النوع:", types.to_dict())

            show_table(filtered)
            download_btn(
                filtered,
                "📥 تحميل المنتجات المفقودة",
                f"missing_{datetime.now():%Y%m%d}.xlsx",
            )

# ══════════════════════════════════════════════════════════════
# صفحة: تحقق Gemini
# ══════════════════════════════════════════════════════════════
elif page == "🤖 تحقق Gemini":
    st.header("🤖 التحقق الذكي بـ Gemini AI")
    st.caption("اضغط على أي منتج للحصول على تحليل وتوصية ذكية")
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
            st.subheader("اختر منتج للتحقق:")

            # عرض المنتجات كأزرار
            for idx, row in df_all.iterrows():
                icon = row.get("الأيقونة", "")
                name = row.get("اسم_منتجي", "")
                price = row.get("سعري", 0)
                comp_price = row.get("سعر_المنافس", 0)
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
                    with st.spinner("🤖 Gemini يحلل..."):
                        result = gemini_verify(
                            name, price, comp_price, api_key
                        )
                    st.markdown(
                        f'<div class="severity-medium">'
                        f"🤖 <b>تحليل Gemini:</b><br>{result}"
                        f"</div>",
                        unsafe_allow_html=True,
                    )

# ══════════════════════════════════════════════════════════════
# صفحة: أتمتة Make
# ══════════════════════════════════════════════════════════════
elif page == "⚡ أتمتة Make":
    st.header("⚡ أتمتة Make.com")
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
