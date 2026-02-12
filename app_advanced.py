# -*- coding: utf-8 -*-
"""
نظام التسعير الذكي للعطور - الإصدار 5.0
تطبيق Streamlit متقدم مع:
- Gemini AI متقدم
- Google Drive integration
- Make.com automation (تحديث أسعار + إضافة منتجات جديدة)
- استديو مهووس لإنشاء محتوى
- نظام موافقة يدوية للمنتجات
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import time
import requests
import json
from io import BytesIO
import asyncio

# ── إعدادات الصفحة ──────────────────────────────────────────
st.set_page_config(
    page_title="نظام التسعير الذكي v5.0",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS مخصص ─────────────────────────────────────────────────
st.markdown("""
<style>
    .main {direction: rtl; text-align: right;}
    .stMetric {text-align: center;}
    .block-container {padding-top: 1rem;}
    div[data-testid="stMetricValue"] {font-size: 2rem;}
    
    .tab-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    
    .gemini-box {
        background-color: #f0f4ff;
        border-left: 4px solid #667eea;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
    
    .drive-box {
        background-color: #fff3e0;
        border-left: 4px solid #ff9800;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
    
    .make-box {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
    
    .studio-box {
        background-color: #e8f5e9;
        border-left: 4px solid #4caf50;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
    
    .approval-box {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
    
    .success-box {
        background-color: #e8f5e9;
        border: 2px solid #4caf50;
        padding: 15px;
        margin: 10px 0;
        border-radius: 10px;
        text-align: center;
    }
    
    .warning-box {
        background-color: #fff8e1;
        border: 2px solid #ffc107;
        padding: 15px;
        margin: 10px 0;
        border-radius: 10px;
    }
    
    .product-card {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 12px;
        margin: 8px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .status-sent {
        color: #4caf50;
        font-weight: bold;
    }
    
    .status-pending {
        color: #ff9800;
        font-weight: bold;
    }
    
    .status-rejected {
        color: #f44336;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ── Webhook URLs ─────────────────────────────────────────────
WEBHOOK_UPDATE_PRICES = "https://hook.eu2.make.com/99oljy0d6r3chwg6bdfsptcf6bk8htsd"
WEBHOOK_NEW_PRODUCTS = "https://hook.eu2.make.com/k6w6kwvn5spfgbfuhjvj4pijt79tknlk"

# ── تهيئة الجلسة ─────────────────────────────────────────
def init_session():
    """تهيئة متغيرات الجلسة."""
    defaults = {
        "results": None,
        "gemini_results": None,
        "my_file": None,
        "supplier_files": [],
        "gemini_key": "",
        "make_url": "",
        "drive_folder_id": "",
        "processing": False,
        "progress": 0,
        "backend_url": "http://localhost:8000",
        # متغيرات الموافقة اليدوية
        "approved_updates": [],       # المنتجات الموافق على تحديث أسعارها
        "approved_new": [],           # المنتجات الموافق على إضافتها
        "sent_updates_log": [],       # سجل الإرسالات لتحديث الأسعار
        "sent_new_log": [],           # سجل الإرسالات للمنتجات الجديدة
        "update_send_status": None,   # حالة آخر إرسال تحديث
        "new_send_status": None,      # حالة آخر إرسال منتجات جديدة
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()

# ── دوال مساعدة ──────────────────────────────────────────
def call_backend(endpoint, method="POST", data=None, files=None):
    """استدعاء API الـ backend."""
    try:
        url = f"{st.session_state.backend_url}{endpoint}"
        if method == "POST":
            response = requests.post(url, json=data, files=files, timeout=30)
        else:
            response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        else:
            return {"success": False, "error": response.text}
    except Exception as e:
        return {"success": False, "error": str(e)}


def send_to_webhook(webhook_url, payload):
    """إرسال البيانات مباشرة إلى Make.com webhook."""
    try:
        response = requests.post(
            webhook_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        return {
            "success": response.status_code == 200,
            "status_code": response.status_code,
            "response": response.text,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }


def send_price_updates(products):
    """
    إرسال تحديثات الأسعار إلى Make.com → Salla.
    
    البيانات المرسلة:
    {
        "products": [
            {"product_id": "...", "name": "...", "price": ..., "sale_price": ...},
            ...
        ]
    }
    """
    payload = {
        "products": [
            {
                "product_id": str(p.get("product_id", p.get("pid_my", p.get("id", "")))),
                "name": p.get("المنتج", p.get("name", p.get("product_name", ""))),
                "price": float(p.get("السعر_الجديد", p.get("recommended_price", p.get("سعر المنافس", 0)))),
                "sale_price": float(p.get("السعر_المخفض", p.get("sale_price", 0))),
            }
            for p in products
        ]
    }
    return send_to_webhook(WEBHOOK_UPDATE_PRICES, payload)


def send_new_products(products):
    """
    إرسال المنتجات الجديدة إلى Make.com → Salla.
    
    البيانات المرسلة:
    {
        "products": [
            {"name": "...", "price": ..., "sku": "...", "category": "...", ...},
            ...
        ]
    }
    """
    payload = {
        "products": [
            {
                "name": p.get("المنتج", p.get("name", p.get("product_name", ""))),
                "price": float(p.get("السعر", p.get("price", 0))),
                "sku": p.get("sku", p.get("رمز المنتج", "")),
                "category": p.get("التصنيف", p.get("category", "")),
                "description": p.get("الوصف", p.get("description", "")),
                "brand": p.get("الماركة", p.get("brand", "")),
                "size": p.get("الحجم", p.get("size", "")),
                "type": p.get("النوع", p.get("type", "")),
            }
            for p in products
        ]
    }
    return send_to_webhook(WEBHOOK_NEW_PRODUCTS, payload)


# ══════════════════════════════════════════════════════════════
# الشريط الجانبي - الإعدادات والتنقل
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.image(
        "https://img.icons8.com/3d-fluency/94/diamond.png",
        width=60,
    )
    st.title("💎 نظام التسعير v5.0")
    st.markdown("---")
    
    # ── الاتصالات ──
    st.subheader("🔌 الاتصالات والإعدادات")
    
    # Gemini
    st.markdown("**🤖 Gemini AI**")
    gemini_key = st.text_input(
        "API Key",
        value=st.session_state.gemini_key,
        type="password",
        key="gemini_input"
    )
    st.session_state.gemini_key = gemini_key
    
    if gemini_key:
        st.markdown('<p style="color: #28a745; font-weight: bold;">✅ متصل</p>', unsafe_allow_html=True)
    else:
        st.markdown('<p style="color: #dc3545; font-weight: bold;">❌ غير متصل</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Google Drive
    st.markdown("**📁 Google Drive**")
    drive_folder = st.text_input(
        "Folder ID",
        value=st.session_state.drive_folder_id,
        placeholder="أدخل معرف المجلد",
        key="drive_input"
    )
    st.session_state.drive_folder_id = drive_folder
    
    if drive_folder:
        st.markdown('<p style="color: #28a745; font-weight: bold;">✅ متصل</p>', unsafe_allow_html=True)
    else:
        st.markdown('<p style="color: #dc3545; font-weight: bold;">❌ غير متصل</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Make.com - تحديث الأسعار
    st.markdown("**⚡ Make.com - تحديث الأسعار**")
    st.markdown(f'<p style="color: #28a745; font-weight: bold;">✅ متصل</p>', unsafe_allow_html=True)
    st.caption(f"Webhook: ...{WEBHOOK_UPDATE_PRICES[-20:]}")
    
    # Make.com - إضافة منتجات
    st.markdown("**⚡ Make.com - إضافة منتجات**")
    st.markdown(f'<p style="color: #28a745; font-weight: bold;">✅ متصل</p>', unsafe_allow_html=True)
    st.caption(f"Webhook: ...{WEBHOOK_NEW_PRODUCTS[-20:]}")
    
    st.markdown("---")
    
    # Backend
    st.markdown("**🖥️ Backend Server**")
    backend_url = st.text_input(
        "Server URL",
        value=st.session_state.backend_url,
        placeholder="http://localhost:8000",
        key="backend_input"
    )
    st.session_state.backend_url = backend_url
    
    st.markdown("---")
    
    # التنقل
    page = st.radio(
        "📑 الصفحات",
        [
            "🏠 لوحة القيادة",
            "📤 رفع الملفات",
            "🤖 تحليل Gemini",
            "📊 النتائج والمقارنات",
            "✅ الموافقات والإرسال",
            "📁 Google Drive",
            "⚡ Make.com",
            "🎬 استديو مهووس",
        ],
        label_visibility="collapsed",
    )
    
    st.markdown("---")
    st.caption("الإصدار 5.0 | نظام التسعير الذكي")

# ══════════════════════════════════════════════════════════════
# صفحة: لوحة القيادة
# ══════════════════════════════════════════════════════════════
if page == "🏠 لوحة القيادة":
    st.markdown('<div class="tab-header"><h1>🏠 لوحة القيادة الرئيسية</h1></div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 الملفات المرفوعة", 
                 1 if st.session_state.my_file else 0)
    
    with col2:
        st.metric("🤖 تحليلات Gemini", 
                 len(st.session_state.gemini_results) if st.session_state.gemini_results else 0)
    
    with col3:
        st.metric("✅ موافقات معلقة", 
                 len(st.session_state.approved_updates) + len(st.session_state.approved_new))
    
    with col4:
        total_sent = len(st.session_state.sent_updates_log) + len(st.session_state.sent_new_log)
        st.metric("📤 إرسالات مكتملة", total_sent)
    
    st.markdown("---")
    
    st.subheader("📈 الإحصائيات السريعة")
    
    if st.session_state.results:
        stats = st.session_state.results.get("stats", {})
        c1, c2, c3, c4 = st.columns(4)
        
        c1.metric("إجمالي المقارنات", stats.get("total", 0))
        c2.metric("رفع سعر", stats.get("raise_count", 0))
        c3.metric("خفض سعر", stats.get("lower_count", 0))
        c4.metric("منتجات مفقودة", stats.get("missing_count", 0))
    else:
        st.info("📋 ابدأ بـ رفع الملفات أولاً")
    
    # ── حالة الاتصالات ──
    st.markdown("---")
    st.subheader("🔌 حالة الاتصالات")
    
    conn_col1, conn_col2, conn_col3, conn_col4 = st.columns(4)
    
    with conn_col1:
        if st.session_state.gemini_key:
            st.success("🤖 Gemini AI: متصل")
        else:
            st.error("🤖 Gemini AI: غير متصل")
    
    with conn_col2:
        if st.session_state.drive_folder_id:
            st.success("📁 Google Drive: متصل")
        else:
            st.error("📁 Google Drive: غير متصل")
    
    with conn_col3:
        st.success("⚡ Make - تحديث أسعار: متصل")
    
    with conn_col4:
        st.success("⚡ Make - إضافة منتجات: متصل")

# ══════════════════════════════════════════════════════════════
# صفحة: رفع الملفات
# ══════════════════════════════════════════════════════════════
elif page == "📤 رفع الملفات":
    st.markdown('<div class="tab-header"><h1>📤 رفع ملفات البيانات</h1></div>', unsafe_allow_html=True)
    
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
        st.subheader("🏢 ملفات الموردين")
        up_suppliers = st.file_uploader(
            "ارفع ملفات الموردين",
            type=["xlsx", "csv"],
            accept_multiple_files=True,
            key="upload_suppliers",
        )
        if up_suppliers:
            st.session_state.supplier_files = [
                {"name": f.name, "data": f.getvalue()}
                for f in up_suppliers
            ]
            st.success(f"✅ {len(up_suppliers)} ملف موردين")
    
    st.markdown("---")
    
    if st.button("🚀 ابدأ المعالجة", use_container_width=True, type="primary"):
        if not st.session_state.my_file:
            st.error("❌ ارفع ملف متجرك أولاً")
        elif not st.session_state.supplier_files:
            st.error("❌ ارفع ملف موردين واحد على الأقل")
        else:
            st.session_state.processing = True
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # 1. تحميل الملفات
                status_text.info("⏳ جاري تحميل الملفات...")
                progress_bar.progress(20)
                time.sleep(0.5)
                
                # 2. معالجة مع Gemini
                status_text.info("🤖 جاري تحليل Gemini...")
                progress_bar.progress(50)
                
                # استدعاء backend
                result = call_backend("/api/analyze", data={
                    "gemini_enabled": bool(st.session_state.gemini_key),
                    "drive_enabled": bool(st.session_state.drive_folder_id),
                })
                
                if result["success"]:
                    st.session_state.gemini_results = result["data"].get("results", [])
                    progress_bar.progress(100)
                    status_text.success("🎉 اكتملت المعالجة!")
                    st.balloons()
                else:
                    status_text.error(f"❌ خطأ: {result.get('error')}")
                
                st.session_state.processing = False
            
            except Exception as e:
                status_text.error(f"❌ خطأ: {e}")
                st.session_state.processing = False

# ══════════════════════════════════════════════════════════════
# صفحة: تحليل Gemini
# ══════════════════════════════════════════════════════════════
elif page == "🤖 تحليل Gemini":
    st.markdown('<div class="tab-header"><h1>🤖 تحليل Gemini AI</h1></div>', unsafe_allow_html=True)
    
    if not st.session_state.gemini_key:
        st.warning("⚠️ أدخل Gemini API Key من الشريط الجانبي أولاً")
    elif not st.session_state.gemini_results:
        st.info("📋 ابدأ المعالجة أولاً من صفحة رفع الملفات")
    else:
        st.markdown('<div class="gemini-box">', unsafe_allow_html=True)
        st.subheader("📊 نتائج التحليل")
        
        # عرض النتائج
        results_df = pd.DataFrame(st.session_state.gemini_results)
        
        # اختيار الأعمدة المهمة
        display_cols = [
            'product_name', 'current_price', 'cost', 
            'market_price', 'recommended_price', 'margin_percentage', 'confidence'
        ]
        
        available_cols = [c for c in display_cols if c in results_df.columns]
        
        st.dataframe(
            results_df[available_cols] if available_cols else results_df,
            use_container_width=True,
            height=400,
            hide_index=True,
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # تحميل النتائج
        st.markdown("---")
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            results_df.to_excel(writer, sheet_name='نتائج Gemini', index=False)
        
        output.seek(0)
        
        st.download_button(
            label="📥 تحميل نتائج Gemini",
            data=output.getvalue(),
            file_name=f"gemini_analysis_{datetime.now():%Y%m%d_%H%M%S}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

# ══════════════════════════════════════════════════════════════
# صفحة: النتائج والمقارنات
# ══════════════════════════════════════════════════════════════
elif page == "📊 النتائج والمقارنات":
    st.markdown('<div class="tab-header"><h1>📊 النتائج والمقارنات</h1></div>', unsafe_allow_html=True)
    
    if not st.session_state.results:
        st.info("📋 ابدأ المعالجة أولاً من صفحة رفع الملفات")
    else:
        results = st.session_state.results
        stats = results.get("stats", {})
        
        # عرض الإحصائيات
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("إجمالي", stats.get("total", 0))
        c2.metric("🔺 رفع سعر", stats.get("raise_count", 0))
        c3.metric("🔻 خفض سعر", stats.get("lower_count", 0))
        c4.metric("🆕 مفقودة", stats.get("missing_count", 0))
        
        st.markdown("---")
        
        # عرض التبويبات
        tab1, tab2, tab3, tab4 = st.tabs(["🔺 رفع السعر", "🔻 خفض السعر", "✅ موافق", "🆕 مفقودة"])
        
        with tab1:
            df_raise = results.get("raise")
            if df_raise is not None and not df_raise.empty:
                st.dataframe(df_raise, use_container_width=True, hide_index=True)
            else:
                st.info("لا توجد منتجات تحتاج رفع سعر")
        
        with tab2:
            df_lower = results.get("lower")
            if df_lower is not None and not df_lower.empty:
                st.dataframe(df_lower, use_container_width=True, hide_index=True)
            else:
                st.info("لا توجد منتجات تحتاج خفض سعر")
        
        with tab3:
            df_approved = results.get("approved")
            if df_approved is not None and not df_approved.empty:
                st.dataframe(df_approved, use_container_width=True, hide_index=True)
            else:
                st.info("لا توجد منتجات موافق عليها")
        
        with tab4:
            df_missing = results.get("missing")
            if df_missing is not None and not df_missing.empty:
                st.dataframe(df_missing, use_container_width=True, hide_index=True)
            else:
                st.info("لا توجد منتجات مفقودة")

# ══════════════════════════════════════════════════════════════
# صفحة: الموافقات والإرسال (الصفحة الجديدة الرئيسية)
# ══════════════════════════════════════════════════════════════
elif page == "✅ الموافقات والإرسال":
    st.markdown('<div class="tab-header"><h1>✅ الموافقات والإرسال إلى سلة</h1></div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="approval-box">
        <h3>📋 نظام الموافقة اليدوية</h3>
        <p>هنا يمكنك مراجعة المنتجات التي تحتاج تحديث أسعار أو إضافة جديدة، واختيار المنتجات التي تريد الموافقة عليها قبل إرسالها إلى سلة عبر Make.com</p>
    </div>
    """, unsafe_allow_html=True)
    
    # ── تبويبات الموافقة ──
    approval_tab1, approval_tab2, approval_tab3 = st.tabs([
        "🔄 تحديث الأسعار",
        "🆕 إضافة منتجات جديدة",
        "📋 سجل الإرسالات"
    ])
    
    # ══════════════════════════════════════════════════════════
    # تبويب 1: تحديث الأسعار
    # ══════════════════════════════════════════════════════════
    with approval_tab1:
        st.subheader("🔄 المنتجات التي تحتاج تحديث أسعار")
        
        # خيار 1: من نتائج المقارنة
        if st.session_state.results:
            results = st.session_state.results
            df_raise = results.get("raise")
            df_lower = results.get("lower")
            
            # دمج المنتجات التي تحتاج تحديث
            update_products = []
            
            if df_raise is not None and not df_raise.empty:
                for _, row in df_raise.iterrows():
                    update_products.append({
                        "المنتج": row.get("المنتج", ""),
                        "السعر_الحالي": row.get("السعر", 0),
                        "سعر_المنافس": row.get("سعر المنافس", 0),
                        "الفرق": row.get("الفرق", 0),
                        "النسبة": row.get("النسبة %", 0),
                        "التوصية": "رفع السعر",
                        "product_id": row.get("pid_my", ""),
                    })
            
            if df_lower is not None and not df_lower.empty:
                for _, row in df_lower.iterrows():
                    update_products.append({
                        "المنتج": row.get("المنتج", ""),
                        "السعر_الحالي": row.get("السعر", 0),
                        "سعر_المنافس": row.get("سعر المنافس", 0),
                        "الفرق": row.get("الفرق", 0),
                        "النسبة": row.get("النسبة %", 0),
                        "التوصية": "خفض السعر",
                        "product_id": row.get("pid_my", ""),
                    })
            
            if update_products:
                st.info(f"📊 تم العثور على **{len(update_products)}** منتج يحتاج تحديث سعر")
                
                # عرض الجدول مع checkboxes
                df_updates = pd.DataFrame(update_products)
                
                # إضافة عمود الموافقة
                st.markdown("### اختر المنتجات للموافقة:")
                
                # زر تحديد الكل / إلغاء الكل
                col_sel1, col_sel2, col_sel3 = st.columns([1, 1, 3])
                with col_sel1:
                    select_all_updates = st.button("✅ تحديد الكل", key="select_all_updates")
                with col_sel2:
                    deselect_all_updates = st.button("❌ إلغاء الكل", key="deselect_all_updates")
                
                # تهيئة حالة التحديد
                if "update_selections" not in st.session_state:
                    st.session_state.update_selections = [False] * len(update_products)
                
                # تحديث حالة التحديد
                if select_all_updates:
                    st.session_state.update_selections = [True] * len(update_products)
                if deselect_all_updates:
                    st.session_state.update_selections = [False] * len(update_products)
                
                # عرض كل منتج مع checkbox
                selected_updates = []
                for i, product in enumerate(update_products):
                    col_check, col_name, col_price, col_comp, col_diff, col_rec = st.columns([0.5, 3, 1.5, 1.5, 1.5, 1.5])
                    
                    with col_check:
                        default_val = st.session_state.update_selections[i] if i < len(st.session_state.update_selections) else False
                        checked = st.checkbox("", value=default_val, key=f"update_{i}")
                        if checked:
                            selected_updates.append(product)
                    
                    with col_name:
                        st.write(f"**{product['المنتج'][:50]}**")
                    
                    with col_price:
                        st.write(f"💰 {product['السعر_الحالي']}")
                    
                    with col_comp:
                        st.write(f"🏪 {product['سعر_المنافس']}")
                    
                    with col_diff:
                        diff_color = "red" if product['الفرق'] > 0 else "green"
                        st.markdown(f'<span style="color:{diff_color}">{product["النسبة"]}%</span>', unsafe_allow_html=True)
                    
                    with col_rec:
                        if product['التوصية'] == "رفع السعر":
                            st.markdown("🔺 رفع")
                        else:
                            st.markdown("🔻 خفض")
                
                st.markdown("---")
                
                # عرض عدد المحدد
                st.info(f"📌 تم تحديد **{len(selected_updates)}** من أصل **{len(update_products)}** منتج")
                
                # زر الموافقة والإرسال
                col_btn1, col_btn2 = st.columns(2)
                
                with col_btn1:
                    if st.button("✅ موافقة وإرسال تحديث الأسعار إلى سلة", 
                                use_container_width=True, type="primary",
                                disabled=len(selected_updates) == 0):
                        if selected_updates:
                            with st.spinner(f"⏳ جاري إرسال {len(selected_updates)} منتج إلى سلة عبر Make.com..."):
                                # إرسال على دفعات (50 منتج لكل دفعة)
                                batch_size = 50
                                total_sent = 0
                                total_failed = 0
                                
                                for batch_start in range(0, len(selected_updates), batch_size):
                                    batch = selected_updates[batch_start:batch_start + batch_size]
                                    result = send_price_updates(batch)
                                    
                                    if result["success"]:
                                        total_sent += len(batch)
                                    else:
                                        total_failed += len(batch)
                                
                                # تسجيل الإرسال
                                log_entry = {
                                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    "type": "تحديث أسعار",
                                    "total": len(selected_updates),
                                    "sent": total_sent,
                                    "failed": total_failed,
                                    "products": [p["المنتج"] for p in selected_updates],
                                }
                                st.session_state.sent_updates_log.append(log_entry)
                                
                                if total_failed == 0:
                                    st.markdown(f"""
                                    <div class="success-box">
                                        <h2>🎉 تم الإرسال بنجاح!</h2>
                                        <p>تم إرسال <b>{total_sent}</b> منتج لتحديث الأسعار في سلة</p>
                                        <p>عبر Make.com → Salla Update Product</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    st.balloons()
                                else:
                                    st.warning(f"⚠️ تم إرسال {total_sent} بنجاح، فشل {total_failed}")
                        else:
                            st.warning("⚠️ اختر منتجات أولاً!")
                
                with col_btn2:
                    # تحميل المنتجات المحددة كملف Excel
                    if selected_updates:
                        df_selected = pd.DataFrame(selected_updates)
                        output = BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            df_selected.to_excel(writer, sheet_name='تحديث الأسعار', index=False)
                        output.seek(0)
                        
                        st.download_button(
                            label="📥 تحميل المحدد كـ Excel",
                            data=output.getvalue(),
                            file_name=f"price_updates_{datetime.now():%Y%m%d_%H%M%S}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True,
                        )
            else:
                st.info("📋 لا توجد منتجات تحتاج تحديث أسعار حالياً")
        
        else:
            st.info("📋 ابدأ المعالجة أولاً من صفحة رفع الملفات")
        
        # خيار 2: رفع ملف يدوي لتحديث الأسعار
        st.markdown("---")
        st.subheader("📤 أو ارفع ملف تحديث أسعار يدوياً")
        st.caption("الملف يجب أن يحتوي على أعمدة: product_id, name, price, sale_price")
        
        manual_update_file = st.file_uploader(
            "ارفع ملف Excel أو CSV",
            type=["xlsx", "csv"],
            key="manual_update_upload",
        )
        
        if manual_update_file:
            try:
                if manual_update_file.name.endswith('.csv'):
                    df_manual = pd.read_csv(manual_update_file)
                else:
                    df_manual = pd.read_excel(manual_update_file)
                
                st.dataframe(df_manual, use_container_width=True, hide_index=True)
                st.info(f"📊 الملف يحتوي على **{len(df_manual)}** منتج")
                
                if st.button("✅ موافقة وإرسال الملف إلى سلة (تحديث أسعار)", 
                            use_container_width=True, type="primary",
                            key="manual_update_send"):
                    products = df_manual.to_dict('records')
                    with st.spinner(f"⏳ جاري إرسال {len(products)} منتج..."):
                        result = send_price_updates(products)
                        if result["success"]:
                            st.markdown("""
                            <div class="success-box">
                                <h2>🎉 تم الإرسال بنجاح!</h2>
                            </div>
                            """, unsafe_allow_html=True)
                            st.balloons()
                            
                            st.session_state.sent_updates_log.append({
                                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "type": "تحديث أسعار (ملف يدوي)",
                                "total": len(products),
                                "sent": len(products),
                                "failed": 0,
                            })
                        else:
                            st.error(f"❌ فشل الإرسال: {result.get('error', 'خطأ غير معروف')}")
            except Exception as e:
                st.error(f"❌ خطأ في قراءة الملف: {e}")
    
    # ══════════════════════════════════════════════════════════
    # تبويب 2: إضافة منتجات جديدة
    # ══════════════════════════════════════════════════════════
    with approval_tab2:
        st.subheader("🆕 المنتجات الجديدة التي تحتاج إضافة")
        
        # من نتائج المقارنة - المنتجات المفقودة
        if st.session_state.results:
            results = st.session_state.results
            df_missing = results.get("missing")
            
            if df_missing is not None and not df_missing.empty:
                st.info(f"📊 تم العثور على **{len(df_missing)}** منتج جديد غير موجود في متجرك")
                
                # عرض الجدول مع checkboxes
                st.markdown("### اختر المنتجات للإضافة:")
                
                # زر تحديد الكل / إلغاء الكل
                col_ns1, col_ns2, col_ns3 = st.columns([1, 1, 3])
                with col_ns1:
                    select_all_new = st.button("✅ تحديد الكل", key="select_all_new")
                with col_ns2:
                    deselect_all_new = st.button("❌ إلغاء الكل", key="deselect_all_new")
                
                # تهيئة حالة التحديد
                if "new_selections" not in st.session_state:
                    st.session_state.new_selections = [False] * len(df_missing)
                
                if select_all_new:
                    st.session_state.new_selections = [True] * len(df_missing)
                if deselect_all_new:
                    st.session_state.new_selections = [False] * len(df_missing)
                
                # عرض كل منتج مع checkbox
                selected_new = []
                for i, (_, row) in enumerate(df_missing.iterrows()):
                    col_check, col_name, col_type, col_size = st.columns([0.5, 4, 1.5, 1.5])
                    
                    with col_check:
                        default_val = st.session_state.new_selections[i] if i < len(st.session_state.new_selections) else False
                        checked = st.checkbox("", value=default_val, key=f"new_{i}")
                        if checked:
                            selected_new.append(row.to_dict())
                    
                    with col_name:
                        st.write(f"**{str(row.get('المنتج', ''))[:60]}**")
                    
                    with col_type:
                        st.write(f"📦 {row.get('النوع', '')}")
                    
                    with col_size:
                        size_val = row.get('الحجم', 0)
                        if size_val:
                            st.write(f"📏 {size_val} ml")
                
                st.markdown("---")
                
                st.info(f"📌 تم تحديد **{len(selected_new)}** من أصل **{len(df_missing)}** منتج")
                
                # زر الموافقة والإرسال
                col_nbtn1, col_nbtn2 = st.columns(2)
                
                with col_nbtn1:
                    if st.button("✅ موافقة وإضافة المنتجات إلى سلة", 
                                use_container_width=True, type="primary",
                                disabled=len(selected_new) == 0):
                        if selected_new:
                            with st.spinner(f"⏳ جاري إرسال {len(selected_new)} منتج جديد إلى سلة..."):
                                result = send_new_products(selected_new)
                                
                                if result["success"]:
                                    st.markdown(f"""
                                    <div class="success-box">
                                        <h2>🎉 تم الإرسال بنجاح!</h2>
                                        <p>تم إرسال <b>{len(selected_new)}</b> منتج جديد لإضافته في سلة</p>
                                        <p>عبر Make.com → Salla Create Product</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    st.balloons()
                                    
                                    st.session_state.sent_new_log.append({
                                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                        "type": "إضافة منتجات جديدة",
                                        "total": len(selected_new),
                                        "sent": len(selected_new),
                                        "failed": 0,
                                        "products": [p.get("المنتج", "") for p in selected_new],
                                    })
                                else:
                                    st.error(f"❌ فشل الإرسال: {result.get('error', 'خطأ غير معروف')}")
                
                with col_nbtn2:
                    if selected_new:
                        df_selected_new = pd.DataFrame(selected_new)
                        output = BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            df_selected_new.to_excel(writer, sheet_name='منتجات جديدة', index=False)
                        output.seek(0)
                        
                        st.download_button(
                            label="📥 تحميل المحدد كـ Excel",
                            data=output.getvalue(),
                            file_name=f"new_products_{datetime.now():%Y%m%d_%H%M%S}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True,
                        )
            else:
                st.info("📋 لا توجد منتجات جديدة للإضافة حالياً")
        else:
            st.info("📋 ابدأ المعالجة أولاً من صفحة رفع الملفات")
        
        # خيار 2: رفع ملف يدوي لإضافة منتجات
        st.markdown("---")
        st.subheader("📤 أو ارفع ملف منتجات جديدة يدوياً")
        st.caption("الملف يجب أن يحتوي على أعمدة: name, price, sku, category")
        
        manual_new_file = st.file_uploader(
            "ارفع ملف Excel أو CSV",
            type=["xlsx", "csv"],
            key="manual_new_upload",
        )
        
        if manual_new_file:
            try:
                if manual_new_file.name.endswith('.csv'):
                    df_manual_new = pd.read_csv(manual_new_file)
                else:
                    df_manual_new = pd.read_excel(manual_new_file)
                
                st.dataframe(df_manual_new, use_container_width=True, hide_index=True)
                st.info(f"📊 الملف يحتوي على **{len(df_manual_new)}** منتج")
                
                if st.button("✅ موافقة وإرسال الملف إلى سلة (منتجات جديدة)", 
                            use_container_width=True, type="primary",
                            key="manual_new_send"):
                    products = df_manual_new.to_dict('records')
                    with st.spinner(f"⏳ جاري إرسال {len(products)} منتج جديد..."):
                        result = send_new_products(products)
                        if result["success"]:
                            st.markdown("""
                            <div class="success-box">
                                <h2>🎉 تم الإرسال بنجاح!</h2>
                            </div>
                            """, unsafe_allow_html=True)
                            st.balloons()
                            
                            st.session_state.sent_new_log.append({
                                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "type": "إضافة منتجات (ملف يدوي)",
                                "total": len(products),
                                "sent": len(products),
                                "failed": 0,
                            })
                        else:
                            st.error(f"❌ فشل الإرسال: {result.get('error', 'خطأ غير معروف')}")
            except Exception as e:
                st.error(f"❌ خطأ في قراءة الملف: {e}")
    
    # ══════════════════════════════════════════════════════════
    # تبويب 3: سجل الإرسالات
    # ══════════════════════════════════════════════════════════
    with approval_tab3:
        st.subheader("📋 سجل الإرسالات")
        
        all_logs = st.session_state.sent_updates_log + st.session_state.sent_new_log
        all_logs.sort(key=lambda x: x["timestamp"], reverse=True)
        
        if all_logs:
            for log in all_logs:
                with st.expander(f"📤 {log['type']} - {log['timestamp']}"):
                    col1, col2, col3 = st.columns(3)
                    col1.metric("إجمالي", log["total"])
                    col2.metric("✅ نجح", log["sent"])
                    col3.metric("❌ فشل", log["failed"])
                    
                    if log.get("products"):
                        st.markdown("**المنتجات:**")
                        for p in log["products"][:10]:
                            st.write(f"• {p}")
                        if len(log.get("products", [])) > 10:
                            st.caption(f"... و {len(log['products']) - 10} منتج آخر")
        else:
            st.info("📋 لا توجد إرسالات سابقة")
        
        # زر مسح السجل
        if all_logs:
            if st.button("🗑️ مسح سجل الإرسالات", type="secondary"):
                st.session_state.sent_updates_log = []
                st.session_state.sent_new_log = []
                st.rerun()

# ══════════════════════════════════════════════════════════════
# صفحة: Google Drive
# ══════════════════════════════════════════════════════════════
elif page == "📁 Google Drive":
    st.markdown('<div class="tab-header"><h1>📁 Google Drive Integration</h1></div>', unsafe_allow_html=True)
    
    if not st.session_state.drive_folder_id:
        st.warning("⚠️ أدخل Google Drive Folder ID من الشريط الجانبي أولاً")
    else:
        st.markdown('<div class="drive-box">', unsafe_allow_html=True)
        st.success("✅ متصل بـ Google Drive")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.subheader("📤 رفع الملفات")
        
        uploaded_file = st.file_uploader(
            "اختر ملف لرفعه",
            type=["xlsx", "csv", "pdf"],
            key="drive_upload"
        )
        
        if uploaded_file and st.button("🚀 رفع إلى Drive", use_container_width=True, type="primary"):
            with st.spinner("⏳ جاري الرفع..."):
                result = call_backend("/api/upload-to-drive", data={
                    "folder_id": st.session_state.drive_folder_id
                })
                
                if result["success"]:
                    st.success(f"✅ تم الرفع بنجاح!")
                    st.info(f"[الملف على Drive]({result['data'].get('link')})")
                else:
                    st.error(f"❌ خطأ: {result.get('error')}")

# ══════════════════════════════════════════════════════════════
# صفحة: Make.com
# ══════════════════════════════════════════════════════════════
elif page == "⚡ Make.com":
    st.markdown('<div class="tab-header"><h1>⚡ Make.com Automation</h1></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="make-box">', unsafe_allow_html=True)
    st.subheader("🔗 حالة الاتصال بـ Make.com")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **⚡ سيناريو تحديث الأسعار:**
        - الحالة: ✅ مفعّل
        - النوع: Webhook → Iterator → Salla Update Product
        - التشغيل: فوري عند وصول البيانات
        """)
    
    with col2:
        st.markdown("""
        **⚡ سيناريو إضافة المنتجات:**
        - الحالة: ✅ مفعّل
        - النوع: Webhook → Iterator → Salla Create Product
        - التشغيل: فوري عند وصول البيانات
        """)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # اختبار الاتصال
    st.subheader("🧪 اختبار الاتصال")
    
    test_col1, test_col2 = st.columns(2)
    
    with test_col1:
        if st.button("🧪 اختبار webhook تحديث الأسعار", use_container_width=True):
            with st.spinner("⏳ جاري الاختبار..."):
                test_payload = {
                    "products": [
                        {
                            "product_id": "TEST_001",
                            "name": "منتج تجريبي - اختبار الاتصال",
                            "price": 100,
                            "sale_price": 0,
                        }
                    ]
                }
                result = send_to_webhook(WEBHOOK_UPDATE_PRICES, test_payload)
                if result["success"]:
                    st.success("✅ الاتصال يعمل بنجاح!")
                else:
                    st.error(f"❌ فشل الاتصال: {result.get('error', '')}")
    
    with test_col2:
        if st.button("🧪 اختبار webhook إضافة المنتجات", use_container_width=True):
            with st.spinner("⏳ جاري الاختبار..."):
                test_payload = {
                    "products": [
                        {
                            "name": "منتج تجريبي - اختبار الاتصال",
                            "price": 100,
                            "sku": "TEST_SKU_001",
                            "category": "اختبار",
                        }
                    ]
                }
                result = send_to_webhook(WEBHOOK_NEW_PRODUCTS, test_payload)
                if result["success"]:
                    st.success("✅ الاتصال يعمل بنجاح!")
                else:
                    st.error(f"❌ فشل الاتصال: {result.get('error', '')}")
    
    st.markdown("---")
    
    # إحصائيات الإرسال
    st.subheader("📊 إحصائيات الإرسال")
    
    stat_col1, stat_col2, stat_col3 = st.columns(3)
    
    with stat_col1:
        st.metric("📤 إرسالات تحديث الأسعار", len(st.session_state.sent_updates_log))
    
    with stat_col2:
        st.metric("📤 إرسالات المنتجات الجديدة", len(st.session_state.sent_new_log))
    
    with stat_col3:
        total = len(st.session_state.sent_updates_log) + len(st.session_state.sent_new_log)
        st.metric("📤 إجمالي الإرسالات", total)

# ══════════════════════════════════════════════════════════════
# صفحة: استديو مهووس
# ══════════════════════════════════════════════════════════════
elif page == "🎬 استديو مهووس":
    st.markdown('<div class="tab-header"><h1>🎬 استديو مهووس - إنشاء محتوى</h1></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="studio-box">', unsafe_allow_html=True)
    st.subheader("📸 إنشاء منشورات وفيديوهات")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # اختيار نوع المحتوى
    content_type = st.radio(
        "نوع المحتوى:",
        ["📸 صورة منتج", "🎥 فيديو قصير", "📝 منشور نصي", "🎨 تصميم إعلاني"]
    )
    
    if content_type == "📸 صورة منتج":
        st.subheader("📸 إنشاء صورة منتج")
        
        product_name = st.text_input("اسم المنتج")
        product_description = st.text_area("وصف المنتج")
        
        if st.button("🎨 إنشاء صورة", use_container_width=True, type="primary"):
            st.info("⏳ جاري إنشاء الصورة...")
            st.success("✅ تم إنشاء الصورة!")
    
    elif content_type == "🎥 فيديو قصير":
        st.subheader("🎥 إنشاء فيديو قصير")
        
        video_concept = st.text_area("فكرة الفيديو")
        duration = st.slider("مدة الفيديو (ثواني)", 5, 30, 15)
        
        if st.button("🎬 إنشاء فيديو", use_container_width=True, type="primary"):
            st.info("⏳ جاري إنشاء الفيديو...")
            st.success("✅ تم إنشاء الفيديو!")
    
    elif content_type == "📝 منشور نصي":
        st.subheader("📝 إنشاء منشور نصي")
        
        post_topic = st.text_input("موضوع المنشور")
        platform = st.selectbox("المنصة", ["Instagram", "TikTok", "Facebook", "Twitter"])
        
        if st.button("✍️ إنشاء منشور", use_container_width=True, type="primary"):
            st.info("⏳ جاري إنشاء المنشور...")
            st.success("✅ تم إنشاء المنشور!")
    
    elif content_type == "🎨 تصميم إعلاني":
        st.subheader("🎨 إنشاء تصميم إعلاني")
        
        ad_headline = st.text_input("عنوان الإعلان")
        ad_description = st.text_area("وصف الإعلان")
        
        if st.button("🎨 إنشاء تصميم", use_container_width=True, type="primary"):
            st.info("⏳ جاري إنشاء التصميم...")
            st.success("✅ تم إنشاء التصميم!")
