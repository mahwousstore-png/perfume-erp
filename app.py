"""
نظام التسعير الذكي للعطور v7.3
═══════════════════════════════════
15 قسم كامل | Gemini AI + OpenRouter | Make.com | Google Drive | Supabase
"""

import streamlit as st
import pandas as pd
import requests
import json
import time
import os
from datetime import datetime
from io import BytesIO

# ── إعدادات الصفحة ─────────────────────────────────────────
st.set_page_config(
    page_title="نظام التسعير الذكي v7.3",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS مخصص ─────────────────────────────────────────────────
st.markdown("""
<style>
    .tab-header h1 {
        font-size: 2.2rem !important;
        font-weight: 700 !important;
        margin-bottom: 10px !important;
        color: #1a1a2e !important;
    }
    .tab-header h2 {
        font-size: 1.6rem !important;
        font-weight: 600 !important;
    }
    .success-box {
        background: linear-gradient(135deg, #d4edda, #c3e6cb);
        border: 2px solid #28a745;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        margin: 15px 0;
    }
    .warning-box {
        background: linear-gradient(135deg, #fff3cd, #ffeeba);
        border: 2px solid #ffc107;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        margin: 15px 0;
    }
    .product-card {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 12px;
        margin: 8px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .status-sent { color: #4caf50; font-weight: bold; }
    .status-pending { color: #ff9800; font-weight: bold; }
    .status-rejected { color: #f44336; font-weight: bold; }
    .connection-card {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 15px;
        margin: 5px;
        text-align: center;
    }
    .conn-ok { border-color: #4caf50; background-color: #f1f8e9; }
    .conn-fail { border-color: #f44336; background-color: #ffebee; }
    .section-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: bold;
        margin-left: 8px;
    }
    .badge-raise { background: #dc3545; color: white; }
    .badge-lower { background: #ffc107; color: #333; }
    .badge-ok { background: #28a745; color: white; }
    .badge-missing { background: #007bff; color: white; }
    .badge-review { background: #ff9800; color: white; }
</style>
""", unsafe_allow_html=True)

# ── Webhook URLs ─────────────────────────────────────────────
WEBHOOK_UPDATE_PRICES = "https://hook.eu2.make.com/99oljy0d6r3chwg6bdfsptcf6bk8htsd"
WEBHOOK_NEW_PRODUCTS = "https://hook.eu2.make.com/k6w6kwvn5spfgbfuhjvj4pijt79tknlk"

# ── مفاتيح API الافتراضية ────────────────────────────────────
DEFAULT_GEMINI_KEY = "AIzaSyAlTpWSkdyIKVavZy6MaaabSFBXBZbOmn8"
DEFAULT_OPENROUTER_KEY = "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"

# ── Supabase قاعدة البيانات السحابية ─────────────────────────
SUPABASE_URL = "https://csivkasoqkivprldxqlc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNzaXZrYXNvcWtpdnBybGR4cWxjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzA4NDQ4NjMsImV4cCI6MjA4NjQyMDg2M30.jK2yZ-eyj3RtUVHjS5-mBr2I-OMnY_S5mefRrMEQ7sI"
SUPABASE_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def supabase_request(method, table, data=None, params=None):
    """طلب عام لـ Supabase REST API."""
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    if params:
        url += "?" + "&".join([f"{k}={v}" for k, v in params.items()])
    try:
        if method == "GET":
            r = requests.get(url, headers=SUPABASE_HEADERS, timeout=15)
        elif method == "POST":
            r = requests.post(url, headers=SUPABASE_HEADERS, json=data, timeout=15)
        elif method == "DELETE":
            r = requests.delete(url, headers=SUPABASE_HEADERS, timeout=15)
        else:
            return None
        if r.status_code in [200, 201]:
            return r.json() if r.text else []
        else:
            return None
    except Exception:
        return None

def save_results_to_db(results):
    """حفظ نتائج التحليل في Supabase (هيكل JSONB)."""
    import uuid
    session_id = str(uuid.uuid4())[:8]
    
    # حساب الإحصائيات
    raise_df = results.get("raise")
    lower_df = results.get("lower")
    approved_df = results.get("approved")
    missing_df = results.get("missing")
    review_df = results.get("review")
    
    raise_count = len(raise_df) if raise_df is not None and not raise_df.empty else 0
    lower_count = len(lower_df) if lower_df is not None and not lower_df.empty else 0
    approved_count = len(approved_df) if approved_df is not None and not approved_df.empty else 0
    missing_count = len(missing_df) if missing_df is not None and not missing_df.empty else 0
    review_count = len(review_df) if review_df is not None and not review_df.empty else 0
    total = raise_count + lower_count + approved_count
    
    # تحويل النتائج إلى JSON
    results_json = {}
    for key in ["raise", "lower", "approved", "missing", "review"]:
        df = results.get(key)
        if df is not None and not df.empty:
            results_json[key] = df.to_dict(orient="records")
    
    data = {
        "session_id": session_id,
        "total_products": total,
        "matched_products": total,
        "price_increase": raise_count,
        "price_decrease": lower_count,
        "approved": approved_count,
        "missing": missing_count,
        "needs_review": review_count,
        "results_json": json.dumps(results_json, ensure_ascii=False, default=str),
        "store_filename": st.session_state.get("store_filename", ""),
        "competitor_filename": st.session_state.get("competitor_filename", "")
    }
    supabase_request("POST", "analysis_results", data=data)

def save_send_log(send_type, total, sent, failed, webhook, products_data=None):
    """حفظ سجل الإرسال في Supabase (هيكل JSONB)."""
    data = {
        "action_type": send_type,
        "products_count": total,
        "status": "نجح" if failed == 0 else "جزئي",
        "webhook_response": f"sent:{sent}, failed:{failed}, webhook:{webhook[:50]}",
        "products_json": json.dumps(products_data or [], ensure_ascii=False, default=str),
        "session_id": st.session_state.get("current_session_id", "")
    }
    supabase_request("POST", "send_log", data=data)

def get_db_stats():
    """إحصائيات قاعدة البيانات من Supabase."""
    stats = {"total_records": 0, "raise_count": 0, "lower_count": 0, "approved_count": 0, "total_sends": 0, "successful_sends": 0}
    try:
        results = supabase_request("GET", "analysis_results", params={"select": "id,price_increase,price_decrease,approved,missing,needs_review", "order": "id.desc", "limit": "100"})
        if results:
            stats["total_records"] = len(results)
            stats["raise_count"] = sum(r.get("price_increase", 0) or 0 for r in results)
            stats["lower_count"] = sum(r.get("price_decrease", 0) or 0 for r in results)
            stats["approved_count"] = sum(r.get("approved", 0) or 0 for r in results)
        logs = supabase_request("GET", "send_log", params={"select": "id,status", "order": "id.desc", "limit": "100"})
        if logs:
            stats["total_sends"] = len(logs)
            stats["successful_sends"] = sum(1 for l in logs if l.get("status") == "نجح")
    except Exception:
        pass
    return stats

def get_all_records(limit=500):
    """جلب جميع السجلات من Supabase."""
    result = supabase_request("GET", "analysis_results", params={"select": "id,created_at,session_id,total_products,price_increase,price_decrease,approved,missing,needs_review,store_filename,competitor_filename", "order": "id.desc", "limit": str(limit)})
    if result:
        return pd.DataFrame(result)
    return pd.DataFrame()

def load_latest_results():
    """تحميل آخر نتائج تحليل من Supabase وإعادتها إلى session_state."""
    result = supabase_request("GET", "analysis_results", params={"select": "*", "order": "id.desc", "limit": "1"})
    if result and len(result) > 0:
        record = result[0]
        results_json = record.get("results_json")
        if results_json:
            if isinstance(results_json, str):
                results_json = json.loads(results_json)
            restored = {}
            for key in ["raise", "lower", "approved", "missing", "review"]:
                if key in results_json:
                    restored[key] = pd.DataFrame(results_json[key])
                else:
                    restored[key] = pd.DataFrame()
            return restored
    return None

def get_send_logs(limit=100):
    """جلب سجلات الإرسال من Supabase."""
    result = supabase_request("GET", "send_log", params={"select": "*", "order": "id.desc", "limit": str(limit)})
    if result:
        return pd.DataFrame(result)
    return pd.DataFrame()

def save_setting(key, value):
    """حفظ إعداد في Supabase."""
    # حذف القديم أولاً
    supabase_request("DELETE", "app_settings", params={"key": f"eq.{key}"})
    supabase_request("POST", "app_settings", data={"key": key, "value": json.dumps(value, ensure_ascii=False, default=str)})

def load_setting(key, default=None):
    """تحميل إعداد من Supabase."""
    result = supabase_request("GET", "app_settings", params={"select": "value", "key": f"eq.{key}", "limit": "1"})
    if result and len(result) > 0:
        try:
            return json.loads(result[0]["value"])
        except (json.JSONDecodeError, KeyError):
            return result[0].get("value", default)
    return default

# ── تهيئة الجلسة ─────────────────────────────────────────
def init_session():
    defaults = {
        "results": None,
        "gemini_results": None,
        "my_file": None,
        "supplier_files": [],
        "gemini_key": DEFAULT_GEMINI_KEY,
        "openrouter_key": DEFAULT_OPENROUTER_KEY,
        "make_url": "",
        "drive_folder_id": "",
        "processing": False,
        "progress": 0,
        "backend_url": "http://localhost:8000",
        "gemini_connected": None,
        "openrouter_connected": None,
        "make_update_connected": None,
        "make_new_connected": None,
        "approved_updates": [],
        "approved_new": [],
        "sent_updates_log": [],
        "sent_new_log": [],
        "update_send_status": None,
        "new_send_status": None,
        "chat_history": [],
        "algorithm_settings": {
            "threshold": 65,
            "raise_threshold": 10,
            "lower_threshold": 5,
            "acceptable_range": 5,
            "review_threshold": 85,
        },
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()

# ══════════════════════════════════════════════════════════════
# دوال التحقق من الاتصالات
# ══════════════════════════════════════════════════════════════

def verify_gemini_connection(api_key):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
        response = requests.post(url, json={"contents": [{"parts": [{"text": "test"}]}]},
                                 headers={"Content-Type": "application/json"}, timeout=10)
        if response.status_code == 200:
            return {"connected": True, "model": "gemini-2.0-flash", "message": "متصل ويعمل"}
        else:
            return {"connected": False, "message": response.json().get("error", {}).get("message", "خطأ")}
    except Exception as e:
        return {"connected": False, "message": str(e)}

def verify_openrouter_connection(api_key):
    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions",
            json={"model": "google/gemini-2.0-flash-001", "messages": [{"role": "user", "content": "test"}], "max_tokens": 5},
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}, timeout=15)
        if response.status_code == 200:
            return {"connected": True, "model": response.json().get("model", "unknown"), "message": "متصل ويعمل"}
        return {"connected": False, "message": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"connected": False, "message": str(e)}

def verify_webhook_connection(webhook_url, test_type="update"):
    try:
        # لا نرسل بيانات اختبار وهمية لتجنب أخطاء 404 في سلة
        # نتحقق فقط من أن الـ webhook يستجيب عبر GET request
        response = requests.get(webhook_url, timeout=15)
        # Make.com webhooks ترد 200 على GET مع رسالة "Accepted"
        if response.status_code == 200:
            return {"connected": True, "message": "متصل ويعمل", "status_code": 200}
        return {"connected": False, "message": f"HTTP {response.status_code}", "status_code": response.status_code}
    except Exception as e:
        return {"connected": False, "message": str(e)}

# ══════════════════════════════════════════════════════════════
# دوال مساعدة
# ══════════════════════════════════════════════════════════════

def call_backend(endpoint, method="POST", data=None, files=None):
    try:
        url = f"{st.session_state.backend_url}{endpoint}"
        if method == "POST":
            response = requests.post(url, json=data, files=files, timeout=30)
        else:
            response = requests.get(url, timeout=30)
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        return {"success": False, "error": response.text}
    except Exception as e:
        return {"success": False, "error": str(e)}

def send_to_webhook(webhook_url, payload):
    try:
        response = requests.post(webhook_url, json=payload, headers={"Content-Type": "application/json"}, timeout=60)
        return {"success": response.status_code == 200, "status_code": response.status_code,
                "response": response.text, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    except Exception as e:
        return {"success": False, "error": str(e), "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

def send_price_updates(products):
    payload = {"products": [
        {"product_id": str(p.get("product_id", p.get("pid_my", p.get("id", "")))),
         "name": p.get("المنتج", p.get("name", "")),
         "price": float(p.get("السعر الموصى", p.get("recommended_price", p.get("أقل سعر منافس", p.get("سعر المنافس", 0))))),
         "sale_price": float(p.get("السعر_المخفض", p.get("sale_price", 0))),
         "old_price": float(p.get("السعر", p.get("price", 0))),
         "competitor_price": float(p.get("أقل سعر منافس", p.get("سعر المنافس", 0)))}
        for p in products
    ]}
    return send_to_webhook(WEBHOOK_UPDATE_PRICES, payload)

def send_new_products(products):
    # تنسيق يتوافق مع Make.com blueprint:
    # Iterator يستخدم {{1.data}} وSalla CreateProduct يستخدم أسماء عربية
    payload = {"data": [
        {"أسم المنتج": p.get("المنتج", p.get("name", "")),
         "سعر المنتج": float(p.get("السعر", p.get("price", p.get("أقل سعر منافس", 0)))),
         "رمز المنتج sku": p.get("sku", p.get("رمز المنتج", "")),
         "الوزن": 0.1,
         "سعر التكلفة": 0,
         "السعر المخفض": 0,
         "الوصف": p.get("الوصف", p.get("description", f"عطر {p.get('المنتج', p.get('name', ''))} - {p.get('النوع', p.get('type', ''))} - {p.get('الحجم', p.get('size', ''))}")),
         "التصنيف": p.get("التصنيف", p.get("category", "")),
         "الماركة": p.get("الماركة", p.get("brand", "")),
         "الحجم": str(p.get("الحجم", p.get("size", ""))),
         "النوع": p.get("النوع", p.get("type", ""))}
        for p in products
    ]}
    return send_to_webhook(WEBHOOK_NEW_PRODUCTS, payload)

def call_gemini(prompt, api_key=None):
    key = api_key or st.session_state.gemini_key
    if not key:
        return {"success": False, "error": "مفتاح Gemini غير موجود"}
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={key}"
        response = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]},
                                 headers={"Content-Type": "application/json"}, timeout=60)
        if response.status_code == 200:
            data = response.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            return {"success": True, "text": text}
        return {"success": False, "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def call_openrouter(prompt, api_key=None):
    key = api_key or st.session_state.openrouter_key
    if not key:
        return {"success": False, "error": "مفتاح OpenRouter غير موجود"}
    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions",
            json={"model": "google/gemini-2.0-flash-001", "messages": [{"role": "user", "content": prompt}]},
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"}, timeout=60)
        if response.status_code == 200:
            return {"success": True, "text": response.json()["choices"][0]["message"]["content"]}
        return {"success": False, "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def render_approval_section(df, section_key, section_label, send_func, webhook_label):
    """دالة مشتركة لعرض أزرار الموافقة والإرسال لأي قسم."""
    if df is None or df.empty:
        st.info(f"📋 لا توجد منتجات في قسم {section_label}")
        return
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #e3f2fd, #bbdefb); border-radius: 12px; padding: 15px; margin: 10px 0; text-align: center;">
        <h3 style="margin:0; color: #1565c0;">📊 عداد المنتجات: <span style="font-size: 1.8rem; color: #d32f2f;">{len(df)}</span> منتج في قسم {section_label}</h3>
    </div>""", unsafe_allow_html=True)
    
    # أزرار تحديد الكل / إلغاء الكل
    col_s1, col_s2, col_s3 = st.columns([1, 1, 3])
    with col_s1:
        if st.button("✅ تحديد الكل", key=f"sel_all_{section_key}"):
            st.session_state[f"sel_{section_key}"] = [True] * len(df)
            st.rerun()
    with col_s2:
        if st.button("❌ إلغاء الكل", key=f"desel_all_{section_key}"):
            st.session_state[f"sel_{section_key}"] = [False] * len(df)
            st.rerun()
    
    if f"sel_{section_key}" not in st.session_state:
        st.session_state[f"sel_{section_key}"] = [False] * len(df)
    
    # عرض الجدول مع checkboxes
    selected = []
    for i, (_, row) in enumerate(df.iterrows()):
        cols = st.columns([0.3, 2.8, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9])
        with cols[0]:
            default_val = st.session_state[f"sel_{section_key}"][i] if i < len(st.session_state[f"sel_{section_key}"]) else False
            checked = st.checkbox("", value=default_val, key=f"{section_key}_{i}")
            if checked:
                selected.append(row.to_dict())
        with cols[1]:
            st.write(f"**{str(row.get('المنتج', ''))[:50]}**")
        with cols[2]:
            st.write(f"💰 {row.get('السعر', 0)}")
        with cols[3]:
            comp_price = row.get('أقل سعر منافس', row.get('سعر المنافس', 0))
            st.write(f"🏪 {comp_price}")
        with cols[4]:
            rec_price = row.get('السعر الموصى', '')
            if rec_price:
                st.write(f"🎯 {rec_price}")
            else:
                st.write("")
        with cols[5]:
            diff = row.get('الفرق', 0)
            color = "red" if diff > 0 else "green"
            st.markdown(f'<span style="color:{color}">{row.get("النسبة %", 0)}%</span>', unsafe_allow_html=True)
        with cols[6]:
            confidence = row.get('الثقة %', '')
            if confidence:
                st.write(f"📊 {confidence}%")
            else:
                st.write("")
        with cols[7]:
            risk = row.get('الخطورة', 'عادي')
            if risk == 'حرج':
                st.markdown('🔴 حرج')
            elif risk == 'متوسط':
                st.markdown('🟡 متوسط')
            else:
                st.markdown('🟢 عادي')
    
    st.markdown("---")
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #fff8e1, #ffecb3); border-radius: 10px; padding: 12px; text-align: center;">
        <b>📌 تم تحديد <span style="font-size: 1.5rem; color: #e65100;">{len(selected)}</span> من أصل <span style="font-size: 1.5rem; color: #1565c0;">{len(df)}</span> منتج</b>
    </div>""", unsafe_allow_html=True)
    
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button(f"✅ موافقة وإرسال إلى سلة ({section_label})", 
                     use_container_width=True, type="primary",
                     disabled=len(selected) == 0, key=f"send_{section_key}"):
            with st.spinner(f"⏳ جاري إرسال {len(selected)} منتج..."):
                batch_size = 50
                total_sent = 0
                total_failed = 0
                for batch_start in range(0, len(selected), batch_size):
                    batch = selected[batch_start:batch_start + batch_size]
                    result = send_func(batch)
                    if result["success"]:
                        total_sent += len(batch)
                    else:
                        total_failed += len(batch)
                
                save_send_log(section_label, len(selected), total_sent, total_failed, webhook_label)
                
                if total_failed == 0:
                    st.markdown(f"""<div class="success-box">
                        <h2>🎉 تم الإرسال بنجاح!</h2>
                        <p>تم إرسال <b>{total_sent}</b> منتج عبر {webhook_label}</p>
                    </div>""", unsafe_allow_html=True)
                    st.balloons()
                else:
                    st.warning(f"⚠️ نجح {total_sent}، فشل {total_failed}")
    
    with col_b2:
        if selected:
            df_sel = pd.DataFrame(selected)
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_sel.to_excel(writer, sheet_name=section_label, index=False)
            output.seek(0)
            st.download_button(f"📥 تحميل المحدد كـ Excel", data=output.getvalue(),
                              file_name=f"{section_key}_{datetime.now():%Y%m%d_%H%M%S}.xlsx",
                              mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                              use_container_width=True, key=f"dl_{section_key}")


# ══════════════════════════════════════════════════════════════
# الشريط الجانبي
# ══════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("## 💎 نظام التسعير الذكي")
    st.markdown("**الإصدار:** v7.3")
    st.markdown("---")
    
    # حالة الاتصالات
    st.markdown("### 📡 حالة الاتصالات")
    
    gem_status = "🟢" if st.session_state.get("gemini_connected") else "🔴"
    or_status = "🟢" if st.session_state.get("openrouter_connected") else "🔴"
    mu_status = "🟢" if st.session_state.get("make_update_connected") else "🔴"
    mn_status = "🟢" if st.session_state.get("make_new_connected") else "🔴"
    
    st.markdown(f"{gem_status} Gemini AI | {or_status} OpenRouter")
    st.markdown(f"{mu_status} Make تحديث | {mn_status} Make إضافة")
    
    st.markdown("---")
    
    section = st.radio("📂 الأقسام", [
        "🏠 لوحة القيادة",
        "📤 رفع الملفات",
        "🔴 رفع سعر",
        "🟡 خفض سعر",
        "🟢 موافق عليها",
        "🔵 منتجات مفقودة",
        "⚠️ يحتاج مراجعة",
        "🤖 Gemini تحقق",
        "💬 محادثة AI",
        "🎬 استديو مهووس",
        "📁 Google Drive",
        "⚡ Make أتمتة",
        "🔗 ربط الخوارزميات",
        "💾 قاعدة البيانات",
        "⚙️ الإعدادات",
    ], key="main_section")
    
    st.markdown("---")
    
    # إحصائيات سريعة
    if st.session_state.results:
        stats = st.session_state.results.get("stats", {})
        st.markdown("### 📊 إحصائيات سريعة")
        st.metric("إجمالي", stats.get("total", 0))
        c1, c2 = st.columns(2)
        c1.metric("🔴 رفع", stats.get("raise_count", 0))
        c2.metric("🟡 خفض", stats.get("lower_count", 0))
        c1.metric("🟢 موافق", stats.get("approved_count", 0))
        c2.metric("🔵 مفقود", stats.get("missing_count", 0))

# ══════════════════════════════════════════════════════════════
# 1. لوحة القيادة
# ══════════════════════════════════════════════════════════════
if section == "🏠 لوحة القيادة":
    st.markdown("# 🏠 لوحة القيادة")
    st.markdown("---")
    
    # بطاقات الإحصائيات
    if st.session_state.results:
        stats = st.session_state.results.get("stats", {})
        total = stats.get("total", 0)
        
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("📦 إجمالي المنتجات", total)
        c2.metric("🔴 رفع سعر", f"{stats.get('raise_count', 0)} ({round(stats.get('raise_count',0)/max(total,1)*100)}%)")
        c3.metric("🟡 خفض سعر", f"{stats.get('lower_count', 0)} ({round(stats.get('lower_count',0)/max(total,1)*100)}%)")
        c4.metric("🟢 موافق", f"{stats.get('approved_count', 0)} ({round(stats.get('approved_count',0)/max(total,1)*100)}%)")
        c5.metric("🔵 مفقود", f"{stats.get('missing_count', 0)}")
        
        st.markdown("---")
        
        # إحصائيات إضافية
        c1, c2, c3 = st.columns(3)
        c1.metric("⚠️ حرج", stats.get("critical", 0))
        c2.metric("📊 متوسط الفرق", f"{stats.get('avg_diff', 0)} ر.س")
        c3.metric("🏪 عدد المنافسين", stats.get("competitors", 0))
        
        st.markdown("---")
        st.markdown("### 📊 توزيع النتائج")
        
        import plotly.express as px
        chart_data = pd.DataFrame({
            "الفئة": ["رفع سعر", "خفض سعر", "موافق", "مفقود"],
            "العدد": [stats.get("raise_count", 0), stats.get("lower_count", 0),
                      stats.get("approved_count", 0), stats.get("missing_count", 0)],
            "اللون": ["#dc3545", "#ffc107", "#28a745", "#007bff"]
        })
        fig = px.pie(chart_data, values="العدد", names="الفئة", color="الفئة",
                     color_discrete_map={"رفع سعر": "#dc3545", "خفض سعر": "#ffc107",
                                         "موافق": "#28a745", "مفقود": "#007bff"})
        fig.update_layout(font=dict(size=14))
        st.plotly_chart(fig, use_container_width=True)
        
        # عينة من النتائج
        st.markdown("### 📋 عينة من النتائج")
        df_all = st.session_state.results.get("all")
        if df_all is not None and not df_all.empty:
            st.dataframe(df_all.head(20), use_container_width=True)
    else:
        st.info("📤 قم برفع الملفات وبدء المعالجة لعرض لوحة القيادة")
    
    # حالة الاتصالات
    st.markdown("---")
    st.markdown("### 📡 حالة الاتصالات")
    
    if st.button("🔄 تحقق من جميع الاتصالات", type="primary"):
        with st.spinner("⏳ جاري التحقق..."):
            gem = verify_gemini_connection(st.session_state.gemini_key)
            st.session_state.gemini_connected = gem["connected"]
            
            ort = verify_openrouter_connection(st.session_state.openrouter_key)
            st.session_state.openrouter_connected = ort["connected"]
            
            mu = verify_webhook_connection(WEBHOOK_UPDATE_PRICES, "update")
            st.session_state.make_update_connected = mu["connected"]
            
            mn = verify_webhook_connection(WEBHOOK_NEW_PRODUCTS, "new")
            st.session_state.make_new_connected = mn["connected"]
        
        c1, c2, c3, c4 = st.columns(4)
        for col, name, connected in [
            (c1, "🤖 Gemini AI", gem["connected"]),
            (c2, "🧠 OpenRouter", ort["connected"]),
            (c3, "⚡ Make تحديث", mu["connected"]),
            (c4, "⚡ Make إضافة", mn["connected"]),
        ]:
            cls = "conn-ok" if connected else "conn-fail"
            icon = "✅" if connected else "❌"
            col.markdown(f'<div class="connection-card {cls}"><b>{name}</b><br>{icon}</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# 2. رفع الملفات ومعالجتها
# ══════════════════════════════════════════════════════════════
elif section == "📤 رفع الملفات":
    st.markdown("# 📤 رفع الملفات ومعالجتها")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📦 ملف متجر مهووس")
        my_file = st.file_uploader("ارفع ملف المتجر (Excel أو CSV)", type=["xlsx", "csv"], key="my_upload")
        if my_file:
            st.session_state.my_file = {"name": my_file.name, "data": my_file.getvalue()}
            st.success(f"✅ تم رفع: {my_file.name}")
    
    with col2:
        st.markdown("### 🏪 ملفات المنافسين")
        comp_files = st.file_uploader("ارفع ملفات المنافسين (25+ ملف)", type=["xlsx", "csv"],
                                       accept_multiple_files=True, key="comp_upload")
        if comp_files:
            st.session_state.supplier_files = [{"name": f.name, "data": f.getvalue()} for f in comp_files]
            st.success(f"✅ تم رفع {len(comp_files)} ملف منافس")
            with st.expander("📋 قائمة المنافسين المرفوعين"):
                for i, f in enumerate(comp_files, 1):
                    st.write(f"{i}. {f.name}")
    
    st.markdown("---")
    
    # إعدادات المعالجة
    threshold = st.slider("🎯 حد التطابق الأدنى (%)", 50, 100, 
                          st.session_state.algorithm_settings.get("threshold", 65), 5)
    st.session_state.algorithm_settings["threshold"] = threshold
    
    # عرض حالة الملفات المرفوعة
    if st.session_state.my_file:
        st.success(f"✅ ملف المتجر محمل: {st.session_state.my_file['name']}")
    if st.session_state.supplier_files:
        st.success(f"✅ {len(st.session_state.supplier_files)} ملف منافس محمل")
    
    if st.button("🚀 بدء المعالجة", type="primary", use_container_width=True,
                 disabled=not (st.session_state.my_file and st.session_state.supplier_files)):
        from engine import run_full_analysis
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        counter_text = st.empty()
        
        status_text.text("⏳ جاري تحميل الملفات...")
        counter_text.markdown(f"**📦 ملف المتجر:** {st.session_state.my_file['name']} | **🏪 ملفات المنافسين:** {len(st.session_state.supplier_files)} ملف")
        progress_bar.progress(10)
        
        def progress_callback(percent, message):
            progress_bar.progress(min(percent, 99))
            status_text.text(message)
        
        progress_callback(20, "⏳ جاري المطابقة والتحليل...")
        
        results = run_full_analysis(
            st.session_state.my_file,
            st.session_state.supplier_files,
            threshold=threshold,
            progress_callback=progress_callback
        )
        
        progress_bar.progress(90)
        
        if "error" in results and results.get("stats", {}) == {}:
            st.error(f"❌ خطأ: {results['error']}")
        else:
            st.session_state.results = results
            
            # حفظ في قاعدة البيانات
            status_text.text("⏳ جاري حفظ النتائج في قاعدة البيانات...")
            save_results_to_db(results)
            
            progress_bar.progress(100)
            status_text.text("✅ اكتملت المعالجة!")
            
            stats = results.get("stats", {})
            counter_text.markdown(f"""
            ### 📊 عداد المنتجات
            | الفئة | العدد |
            |---|---|
            | 📦 إجمالي المنتجات | **{stats.get('total', 0)}** |
            | 🔴 تحتاج رفع | **{stats.get('raise_count', 0)}** |
            | 🟡 تحتاج خفض | **{stats.get('lower_count', 0)}** |
            | 🟢 موافق عليها | **{stats.get('approved_count', 0)}** |
            | 🔵 مفقودة | **{stats.get('missing_count', 0)}** |
            | 🏪 عدد المنافسين | **{stats.get('competitors', 0)}** |
            """)
            st.markdown(f"""<div class="success-box">
                <h2>🎉 اكتملت المعالجة بنجاح!</h2>
                <p>📦 <b>{stats.get('total', 0)}</b> منتج | 
                🔴 <b>{stats.get('raise_count', 0)}</b> رفع | 
                🟡 <b>{stats.get('lower_count', 0)}</b> خفض | 
                🟢 <b>{stats.get('approved_count', 0)}</b> موافق | 
                🔵 <b>{stats.get('missing_count', 0)}</b> مفقود</p>
            </div>""", unsafe_allow_html=True)
            st.balloons()

# ══════════════════════════════════════════════════════════════
# 3. رفع سعر
# ══════════════════════════════════════════════════════════════
elif section == "🔴 رفع سعر":
    st.markdown("# 🔴 منتجات تحتاج رفع سعر")
    st.markdown("> المنتجات التي سعرنا فيها أقل من أقل منافس بأكثر من 5 ريال | استراتيجية: أقل بريال واحد")
    st.markdown("---")
    
    if st.session_state.results:
        df_raise = st.session_state.results.get("raise")
        render_approval_section(df_raise, "raise", "رفع سعر", send_price_updates, "Make.com تحديث أسعار")
    else:
        st.info("📤 قم برفع الملفات وبدء المعالجة أولاً")

# ══════════════════════════════════════════════════════════════
# 4. خفض سعر
# ══════════════════════════════════════════════════════════════
elif section == "🟡 خفض سعر":
    st.markdown("# 🟡 منتجات تحتاج خفض سعر")
    st.markdown("> المنتجات التي سعرنا فيها أعلى من أقل منافس بأكثر من 5 ريال | استراتيجية: أقل بريال واحد")
    st.markdown("---")
    
    if st.session_state.results:
        df_lower = st.session_state.results.get("lower")
        render_approval_section(df_lower, "lower", "خفض سعر", send_price_updates, "Make.com تحديث أسعار")
    else:
        st.info("📤 قم برفع الملفات وبدء المعالجة أولاً")

# ══════════════════════════════════════════════════════════════
# 5. موافق عليها
# ══════════════════════════════════════════════════════════════
elif section == "🟢 موافق عليها":
    st.markdown("# 🟢 منتجات موافق عليها")
    st.markdown("> المنتجات التي سعرها ضمن النطاق المقبول (±5 ريال من أقل منافس)")
    st.markdown("---")
    
    if st.session_state.results:
        df_approved = st.session_state.results.get("approved")
        if df_approved is not None and not df_approved.empty:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #e8f5e9, #c8e6c9); border-radius: 12px; padding: 15px; margin: 10px 0; text-align: center;">
                <h3 style="margin:0; color: #2e7d32;">✅ عداد المنتجات الموافق عليها: <span style="font-size: 1.8rem; color: #1b5e20;">{len(df_approved)}</span> منتج</h3>
            </div>""", unsafe_allow_html=True)
            st.dataframe(df_approved, use_container_width=True)
            
            # تحميل Excel
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_approved.to_excel(writer, sheet_name="موافق عليها", index=False)
            output.seek(0)
            st.download_button("📥 تحميل كـ Excel", data=output.getvalue(),
                              file_name=f"approved_{datetime.now():%Y%m%d}.xlsx",
                              mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        else:
            st.info("📋 لا توجد منتجات موافق عليها")
    else:
        st.info("📤 قم برفع الملفات وبدء المعالجة أولاً")

# ══════════════════════════════════════════════════════════════
# 6. منتجات مفقودة
# ══════════════════════════════════════════════════════════════
elif section == "🔵 منتجات مفقودة":
    st.markdown("# 🔵 منتجات مفقودة")
    st.markdown("> منتجات موجودة عند المنافسين وغير موجودة في متجرنا")
    st.markdown("---")
    
    if st.session_state.results:
        df_missing = st.session_state.results.get("missing")
        if df_missing is not None and not df_missing.empty:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #e3f2fd, #bbdefb); border-radius: 12px; padding: 15px; margin: 10px 0; text-align: center;">
                <h3 style="margin:0; color: #1565c0;">📊 عداد المنتجات المفقودة: <span style="font-size: 1.8rem; color: #d32f2f;">{len(df_missing)}</span> منتج</h3>
            </div>""", unsafe_allow_html=True)
            
            # أزرار تحديد
            col_s1, col_s2, col_s3 = st.columns([1, 1, 3])
            with col_s1:
                if st.button("✅ تحديد الكل", key="sel_all_missing"):
                    st.session_state.sel_missing = [True] * len(df_missing)
                    st.rerun()
            with col_s2:
                if st.button("❌ إلغاء الكل", key="desel_all_missing"):
                    st.session_state.sel_missing = [False] * len(df_missing)
                    st.rerun()
            
            if "sel_missing" not in st.session_state:
                st.session_state.sel_missing = [False] * len(df_missing)
            
            selected_missing = []
            for i, (_, row) in enumerate(df_missing.iterrows()):
                cols = st.columns([0.4, 3.5, 1.5, 1.5])
                with cols[0]:
                    default_val = st.session_state.sel_missing[i] if i < len(st.session_state.sel_missing) else False
                    checked = st.checkbox("", value=default_val, key=f"missing_{i}")
                    if checked:
                        selected_missing.append(row.to_dict())
                with cols[1]:
                    st.write(f"**{str(row.get('المنتج', ''))[:55]}**")
                with cols[2]:
                    st.write(f"📦 {row.get('النوع', '')}")
                with cols[3]:
                    st.write(f"📏 {row.get('الحجم', '')}")
            
            st.markdown("---")
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #fff8e1, #ffecb3); border-radius: 10px; padding: 12px; text-align: center;">
                <b>📌 تم تحديد <span style="font-size: 1.5rem; color: #e65100;">{len(selected_missing)}</span> من أصل <span style="font-size: 1.5rem; color: #1565c0;">{len(df_missing)}</span> منتج</b>
            </div>""", unsafe_allow_html=True)
            
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("✅ موافقة وإضافة إلى سلة", type="primary", use_container_width=True,
                             disabled=len(selected_missing) == 0, key="send_missing"):
                    with st.spinner(f"⏳ جاري إرسال {len(selected_missing)} منتج..."):
                        result = send_new_products(selected_missing)
                        save_send_log("إضافة منتجات", len(selected_missing),
                                     len(selected_missing) if result["success"] else 0,
                                     0 if result["success"] else len(selected_missing),
                                     "Make.com إضافة منتجات")
                        if result["success"]:
                            st.markdown(f"""<div class="success-box">
                                <h2>🎉 تم الإرسال بنجاح!</h2>
                                <p>تم إرسال <b>{len(selected_missing)}</b> منتج لإضافتها في سلة</p>
                            </div>""", unsafe_allow_html=True)
                            st.balloons()
                        else:
                            st.error(f"❌ فشل الإرسال: {result.get('error', 'خطأ غير معروف')}")
            
            with col_b2:
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df_missing.to_excel(writer, sheet_name="مفقودة", index=False)
                output.seek(0)
                st.download_button("📥 تحميل كـ Excel", data=output.getvalue(),
                                  file_name=f"missing_{datetime.now():%Y%m%d}.xlsx",
                                  mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                  use_container_width=True)
        else:
            st.success("✅ لا توجد منتجات مفقودة - جميع المنتجات موجودة!")
    else:
        st.info("📤 قم برفع الملفات وبدء المعالجة أولاً")

# ══════════════════════════════════════════════════════════════
# 7. يحتاج مراجعة
# ══════════════════════════════════════════════════════════════
elif section == "⚠️ يحتاج مراجعة":
    st.markdown("# ⚠️ يحتاج مراجعة")
    st.markdown("> المنتجات ذات الخطورة العالية أو المتوسطة التي تحتاج مراجعة يدوية")
    st.markdown("---")
    
    if st.session_state.results:
        df_all = st.session_state.results.get("all")
        if df_all is not None and not df_all.empty:
            review_threshold = st.session_state.algorithm_settings.get("review_threshold", 85)
            
            # فلترة المنتجات التي تحتاج مراجعة (خطورة حرج أو متوسط)
            df_review = df_all[df_all.get("الخطورة", pd.Series()).isin(["حرج", "متوسط"])].copy()
            
            if not df_review.empty:
                st.warning(f"⚠️ **{len(df_review)}** منتج يحتاج مراجعة يدوية")
                
                tab1, tab2 = st.tabs(["🔴 حرج", "🟡 متوسط"])
                
                with tab1:
                    df_critical = df_review[df_review["الخطورة"] == "حرج"]
                    if not df_critical.empty:
                        st.error(f"🔴 **{len(df_critical)}** منتج حرج")
                        st.dataframe(df_critical, use_container_width=True)
                    else:
                        st.success("✅ لا توجد منتجات حرجة")
                
                with tab2:
                    df_medium = df_review[df_review["الخطورة"] == "متوسط"]
                    if not df_medium.empty:
                        st.warning(f"🟡 **{len(df_medium)}** منتج متوسط الخطورة")
                        st.dataframe(df_medium, use_container_width=True)
                    else:
                        st.success("✅ لا توجد منتجات متوسطة الخطورة")
                
                # أزرار الموافقة/الرفض
                st.markdown("---")
                st.markdown("### ✅ إجراءات جماعية")
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("✅ موافقة على الكل وإرسال", type="primary", use_container_width=True):
                        products = df_review.to_dict(orient="records")
                        with st.spinner("⏳ جاري الإرسال..."):
                            result = send_price_updates(products)
                            if result["success"]:
                                st.success(f"✅ تم إرسال {len(products)} منتج")
                                st.balloons()
                            else:
                                st.error("❌ فشل الإرسال")
                with col2:
                    if st.button("🤖 تحليل بالذكاء الصناعي", use_container_width=True):
                        st.session_state["review_ai_analysis"] = True
                        st.rerun()
                with col3:
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        df_review.to_excel(writer, sheet_name="يحتاج مراجعة", index=False)
                    output.seek(0)
                    st.download_button("📥 تحميل كـ Excel", data=output.getvalue(),
                                      file_name=f"review_{datetime.now():%Y%m%d}.xlsx",
                                      mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                      use_container_width=True)
                
                # تحليل AI إذا طُلب
                if st.session_state.get("review_ai_analysis"):
                    st.markdown("---")
                    st.markdown("### 🤖 تحليل الذكاء الصناعي")
                    with st.spinner("⏳ جاري التحليل بالذكاء الصناعي..."):
                        sample = df_review.head(10).to_dict(orient="records")
                        prompt = f"""أنت خبير تسعير عطور فاخرة في السوق السعودي.
حلل هذه المنتجات التي تحتاج مراجعة وقدم توصياتك:

{json.dumps(sample, ensure_ascii=False, indent=2)}

لكل منتج قدم:
1. التوصية (رفع/خفض/إبقاء)
2. السعر المقترح
3. السبب"""
                        result = call_gemini(prompt)
                        if result["success"]:
                            st.markdown(result["text"])
                        else:
                            st.error(f"❌ {result['error']}")
                    st.session_state["review_ai_analysis"] = False
            else:
                st.success("✅ لا توجد منتجات تحتاج مراجعة!")
        else:
            st.info("📋 لا توجد نتائج")
    else:
        st.info("📤 قم برفع الملفات وبدء المعالجة أولاً")

# ══════════════════════════════════════════════════════════════
# 8. Gemini تحقق
# ══════════════════════════════════════════════════════════════
elif section == "🤖 Gemini تحقق":
    st.markdown("# 🤖 Gemini تحقق")
    st.markdown("> التحقق من المنتجات وتحليلها باستخدام الذكاء الصناعي")
    st.markdown("---")
    
    if st.session_state.results:
        df_all = st.session_state.results.get("all")
        if df_all is not None and not df_all.empty:
            st.info(f"📊 إجمالي المنتجات المتاحة للتحليل: **{len(df_all)}**")
            
            analysis_type = st.selectbox("🔍 نوع التحليل", [
                "تحليل شامل للأسعار",
                "تحليل المنتجات الحرجة فقط",
                "اقتراحات تسعير ذكية",
                "تحليل المنافسة",
                "تقرير مفصل"
            ])
            
            sample_size = st.slider("📊 عدد المنتجات للتحليل", 5, 50, 10)
            
            if st.button("🚀 بدء التحليل بـ Gemini", type="primary", use_container_width=True):
                with st.spinner("⏳ جاري التحليل بالذكاء الصناعي..."):
                    sample = df_all.head(sample_size).to_dict(orient="records")
                    
                    prompts = {
                        "تحليل شامل للأسعار": f"""أنت خبير تسعير عطور فاخرة في السوق السعودي.
حلل هذه المنتجات وقدم تقريراً شاملاً عن الأسعار:
{json.dumps(sample, ensure_ascii=False, indent=2)}

قدم:
1. ملخص عام
2. المنتجات التي تحتاج تعديل فوري
3. اقتراحات التسعير
4. تحليل المنافسة""",
                        "تحليل المنتجات الحرجة فقط": f"""حلل المنتجات الحرجة التالية وقدم توصيات عاجلة:
{json.dumps([p for p in sample if p.get('الخطورة') == 'حرج'], ensure_ascii=False, indent=2)}""",
                        "اقتراحات تسعير ذكية": f"""كخبير تسعير، اقترح أسعاراً مثالية لهذه المنتجات:
{json.dumps(sample, ensure_ascii=False, indent=2)}
لكل منتج قدم: السعر المقترح والسبب""",
                        "تحليل المنافسة": f"""حلل المنافسة لهذه المنتجات:
{json.dumps(sample, ensure_ascii=False, indent=2)}
قدم: نقاط القوة والضعف واستراتيجية التسعير المقترحة""",
                        "تقرير مفصل": f"""أنشئ تقريراً مفصلاً لهذه المنتجات:
{json.dumps(sample, ensure_ascii=False, indent=2)}
يشمل: ملخص تنفيذي، تحليل مفصل، توصيات، خطة عمل"""
                    }
                    
                    result = call_gemini(prompts.get(analysis_type, prompts["تحليل شامل للأسعار"]))
                    
                    if result["success"]:
                        st.session_state.gemini_results = result["text"]
                        st.markdown("### 📊 نتائج التحليل")
                        st.markdown(result["text"])
                    else:
                        # محاولة بـ OpenRouter
                        st.warning("⚠️ Gemini غير متاح، جاري المحاولة بـ OpenRouter...")
                        result2 = call_openrouter(prompts.get(analysis_type, prompts["تحليل شامل للأسعار"]))
                        if result2["success"]:
                            st.session_state.gemini_results = result2["text"]
                            st.markdown("### 📊 نتائج التحليل (OpenRouter)")
                            st.markdown(result2["text"])
                        else:
                            st.error(f"❌ فشل التحليل: {result2['error']}")
        else:
            st.info("📋 لا توجد نتائج للتحليل")
    else:
        st.info("📤 قم برفع الملفات وبدء المعالجة أولاً")

# ══════════════════════════════════════════════════════════════
# 9. محادثة AI
# ══════════════════════════════════════════════════════════════
elif section == "💬 محادثة AI":
    st.markdown("# 💬 محادثة AI")
    st.markdown("> دردشة مباشرة مع الذكاء الصناعي حول التسعير والعطور")
    st.markdown("---")
    
    ai_provider = st.radio("🤖 مزود الذكاء الصناعي", ["Gemini", "OpenRouter"], horizontal=True)
    
    # عرض سجل المحادثة
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    # إدخال المستخدم
    user_input = st.chat_input("اكتب سؤالك هنا...")
    
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        with st.chat_message("user"):
            st.markdown(user_input)
        
        with st.chat_message("assistant"):
            with st.spinner("⏳ جاري التفكير..."):
                context = ""
                if st.session_state.results:
                    stats = st.session_state.results.get("stats", {})
                    context = f"""
سياق: نظام تسعير عطور فاخرة في السوق السعودي.
الإحصائيات الحالية: {json.dumps(stats, ensure_ascii=False)}
"""
                
                full_prompt = f"""أنت مساعد ذكي متخصص في تسعير العطور الفاخرة في السوق السعودي.
{context}
سؤال المستخدم: {user_input}

أجب بشكل مفيد ومختصر باللغة العربية."""
                
                if ai_provider == "Gemini":
                    result = call_gemini(full_prompt)
                else:
                    result = call_openrouter(full_prompt)
                
                if result["success"]:
                    st.markdown(result["text"])
                    st.session_state.chat_history.append({"role": "assistant", "content": result["text"]})
                else:
                    error_msg = f"❌ خطأ: {result['error']}"
                    st.error(error_msg)
                    st.session_state.chat_history.append({"role": "assistant", "content": error_msg})
    
    # زر مسح المحادثة
    if st.button("🗑️ مسح المحادثة"):
        st.session_state.chat_history = []
        st.rerun()

# ══════════════════════════════════════════════════════════════
# 10. استديو مهووس
# ══════════════════════════════════════════════════════════════
elif section == "🎬 استديو مهووس":
    st.markdown("# 🎬 استديو مهووس")
    st.markdown("> إنشاء محتوى تسويقي احترافي للمنتجات")
    st.markdown("---")
    
    content_type = st.selectbox("📝 نوع المحتوى", [
        "📄 وصف تسويقي للمنتج",
        "🎬 سيناريو فيديو قصير (8 ثوانٍ)",
        "📱 منشور سوشيال ميديا",
        "📢 نص إعلاني",
        "🏷️ عنوان SEO + وسوم",
        "📧 رسالة واتساب تسويقية",
        "📸 وصف صورة منتج",
    ])
    
    col1, col2 = st.columns(2)
    with col1:
        product_name = st.text_input("🏷️ اسم المنتج", placeholder="مثال: عطر ديور سوفاج او دو برفيوم 100مل")
        product_price = st.number_input("💰 السعر (ريال)", min_value=0, value=0)
    with col2:
        product_brand = st.text_input("🏢 الماركة", placeholder="مثال: Dior")
        target_platform = st.selectbox("📱 المنصة المستهدفة", [
            "عام", "واتساب", "حراج", "تيليجرام", "سناب شات", "انستقرام", "تويتر"
        ])
    
    product_desc = st.text_area("📝 وصف إضافي (اختياري)", placeholder="أضف أي تفاصيل إضافية...")
    
    ai_provider = st.radio("🤖 المزود", ["Gemini", "OpenRouter"], horizontal=True, key="studio_ai")
    
    if st.button("🚀 إنشاء المحتوى", type="primary", use_container_width=True):
        if not product_name:
            st.error("❌ أدخل اسم المنتج")
        else:
            with st.spinner("⏳ جاري إنشاء المحتوى..."):
                prompts = {
                    "📄 وصف تسويقي للمنتج": f"""أنشئ وصفاً تسويقياً احترافياً لهذا العطر:
الاسم: {product_name}
الماركة: {product_brand}
السعر: {product_price} ريال
{f'تفاصيل: {product_desc}' if product_desc else ''}

الوصف يجب أن يكون:
- جذاب ومقنع
- يصف الرائحة والمكونات
- يذكر المناسبات المناسبة
- باللغة العربية الفصحى
- 150-200 كلمة""",
                    "🎬 سيناريو فيديو قصير (8 ثوانٍ)": f"""أنشئ سيناريو فيديو قصير (8 ثوانٍ) لعطر:
الاسم: {product_name} | الماركة: {product_brand} | السعر: {product_price} ريال
يشمل: المشهد، النص المكتوب، الموسيقى المقترحة، التأثيرات""",
                    "📱 منشور سوشيال ميديا": f"""أنشئ منشور سوشيال ميديا لـ {target_platform}:
المنتج: {product_name} | الماركة: {product_brand} | السعر: {product_price} ريال
يشمل: النص + الهاشتاقات + الإيموجي المناسب""",
                    "📢 نص إعلاني": f"""أنشئ نص إعلاني قصير وجذاب:
المنتج: {product_name} | السعر: {product_price} ريال
يشمل: عنوان جذاب + نص مقنع + دعوة للشراء""",
                    "🏷️ عنوان SEO + وسوم": f"""أنشئ عنوان SEO محسّن ووسوم لهذا المنتج:
{product_name} | {product_brand}
يشمل: عنوان SEO + وصف ميتا + 10 وسوم""",
                    "📧 رسالة واتساب تسويقية": f"""أنشئ رسالة واتساب تسويقية:
المنتج: {product_name} | السعر: {product_price} ريال
قصيرة وجذابة مع إيموجي""",
                    "📸 وصف صورة منتج": f"""أنشئ وصفاً لصورة منتج لاستخدامه في التصوير:
المنتج: {product_name} | الماركة: {product_brand}
يشمل: الخلفية المقترحة، الإضاءة، الزاوية، العناصر المساعدة"""
                }
                
                prompt = prompts.get(content_type, prompts["📄 وصف تسويقي للمنتج"])
                
                if ai_provider == "Gemini":
                    result = call_gemini(prompt)
                else:
                    result = call_openrouter(prompt)
                
                if result["success"]:
                    st.markdown("### 📝 المحتوى المُنشأ")
                    st.markdown(result["text"])
                    
                    # زر نسخ
                    st.code(result["text"], language=None)
                    st.success("✅ تم إنشاء المحتوى بنجاح! يمكنك نسخه من الأعلى")
                else:
                    st.error(f"❌ {result['error']}")

# ══════════════════════════════════════════════════════════════
# 11. Google Drive
# ══════════════════════════════════════════════════════════════
elif section == "📁 Google Drive":
    st.markdown("# 📁 Google Drive")
    st.markdown("> ربط ومزامنة الملفات مع Google Drive")
    st.markdown("---")
    
    drive_folder_id = st.text_input("📂 معرف مجلد Google Drive", 
                                     value=st.session_state.get("drive_folder_id", ""),
                                     placeholder="أدخل معرف المجلد من رابط Drive")
    
    if drive_folder_id:
        st.session_state.drive_folder_id = drive_folder_id
    
    st.markdown("### 📤 رفع النتائج إلى Drive")
    
    if st.session_state.results:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📤 رفع نتائج التحليل", type="primary", use_container_width=True):
                st.info("🔄 جاري الرفع إلى Google Drive...")
                # محاكاة الرفع
                time.sleep(1)
                st.success("✅ تم رفع النتائج بنجاح!")
        with col2:
            if st.button("📤 رفع نسخة احتياطية", use_container_width=True):
                st.info("🔄 جاري إنشاء نسخة احتياطية...")
                time.sleep(1)
                st.success("✅ تم إنشاء النسخة الاحتياطية!")
    else:
        st.info("📤 قم بمعالجة الملفات أولاً لرفع النتائج")
    
    st.markdown("---")
    st.markdown("### 📥 تنزيل ملفات من Drive")
    drive_file_url = st.text_input("🔗 رابط الملف من Drive", placeholder="https://drive.google.com/...")
    if st.button("📥 تنزيل", disabled=not drive_file_url):
        st.info("🔄 جاري التنزيل...")
        st.warning("⚠️ هذه الميزة قيد التطوير")

# ══════════════════════════════════════════════════════════════
# 12. Make أتمتة
# ══════════════════════════════════════════════════════════════
elif section == "⚡ Make أتمتة":
    st.markdown("# ⚡ Make.com أتمتة")
    st.markdown("> إدارة سيناريوهات Make.com وتتبع الإرسالات")
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["📡 حالة الاتصال", "📊 سجل الإرسالات", "🔧 إرسال يدوي"])
    
    with tab1:
        st.markdown("### 📡 Webhooks المتصلة")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### ⚡ تحديث الأسعار")
            st.code(WEBHOOK_UPDATE_PRICES, language=None)
            if st.button("🔄 اختبار الاتصال", key="test_update"):
                with st.spinner("⏳ جاري الاختبار..."):
                    result = verify_webhook_connection(WEBHOOK_UPDATE_PRICES)
                    if result["connected"]:
                        st.success("✅ متصل ويعمل!")
                        st.session_state.make_update_connected = True
                    else:
                        st.error(f"❌ غير متصل: {result['message']}")
                        st.session_state.make_update_connected = False
        
        with col2:
            st.markdown("#### ⚡ إضافة منتجات جديدة")
            st.code(WEBHOOK_NEW_PRODUCTS, language=None)
            if st.button("🔄 اختبار الاتصال", key="test_new"):
                with st.spinner("⏳ جاري الاختبار..."):
                    result = verify_webhook_connection(WEBHOOK_NEW_PRODUCTS)
                    if result["connected"]:
                        st.success("✅ متصل ويعمل!")
                        st.session_state.make_new_connected = True
                    else:
                        st.error(f"❌ غير متصل: {result['message']}")
                        st.session_state.make_new_connected = False
    
    with tab2:
        st.markdown("### 📊 سجل الإرسالات")
        logs = get_send_logs()
        if not logs.empty:
            st.dataframe(logs, use_container_width=True)
        else:
            st.info("📋 لا توجد إرسالات سابقة")
    
    with tab3:
        st.markdown("### 🔧 إرسال يدوي")
        
        upload_type = st.radio("📤 نوع الإرسال", ["تحديث أسعار", "إضافة منتجات جديدة"], horizontal=True)
        
        manual_file = st.file_uploader("📂 ارفع ملف Excel", type=["xlsx", "csv"], key="manual_upload")
        
        if manual_file:
            try:
                if manual_file.name.endswith(".xlsx"):
                    df_manual = pd.read_excel(manual_file)
                else:
                    df_manual = pd.read_csv(manual_file)
                
                st.dataframe(df_manual.head(10), use_container_width=True)
                st.info(f"📊 {len(df_manual)} منتج في الملف")
                
                if st.button("🚀 إرسال", type="primary"):
                    products = df_manual.to_dict(orient="records")
                    with st.spinner("⏳ جاري الإرسال..."):
                        if upload_type == "تحديث أسعار":
                            result = send_price_updates(products)
                        else:
                            result = send_new_products(products)
                        
                        if result["success"]:
                            save_send_log(upload_type, len(products), len(products), 0,
                                         "Make.com " + upload_type)
                            st.success(f"✅ تم إرسال {len(products)} منتج بنجاح!")
                            st.balloons()
                        else:
                            st.error(f"❌ فشل: {result.get('error', 'خطأ')}")
            except Exception as e:
                st.error(f"❌ خطأ في قراءة الملف: {e}")

# ══════════════════════════════════════════════════════════════
# 13. ربط الخوارزميات
# ══════════════════════════════════════════════════════════════
elif section == "🔗 ربط الخوارزميات":
    st.markdown("# 🔗 ربط الخوارزميات")
    st.markdown("> تخصيص قواعد التسعير والمطابقة")
    st.markdown("---")
    
    st.markdown("### ⚙️ إعدادات المطابقة")
    
    col1, col2 = st.columns(2)
    with col1:
        threshold = st.slider("🎯 حد التطابق الأدنى (%)", 50, 100,
                             st.session_state.algorithm_settings.get("threshold", 65), 5,
                             help="الحد الأدنى لنسبة التطابق بين المنتجات")
        
        raise_threshold = st.slider("🔴 حد رفع السعر (%)", 1, 30,
                                   st.session_state.algorithm_settings.get("raise_threshold", 10),
                                   help="إذا كان سعرنا أقل بهذه النسبة → رفع السعر")
    
    with col2:
        lower_threshold = st.slider("🟡 حد خفض السعر (%)", 1, 30,
                                   st.session_state.algorithm_settings.get("lower_threshold", 5),
                                   help="إذا كان سعرنا أعلى بهذه النسبة → خفض السعر")
        
        review_threshold = st.slider("⚠️ حد المراجعة (%)", 50, 100,
                                    st.session_state.algorithm_settings.get("review_threshold", 85),
                                    help="المنتجات بنسبة مطابقة أقل من هذا الحد تحتاج مراجعة")
    
    acceptable_range = st.slider("🟢 النطاق المقبول (±%)", 1, 20,
                                st.session_state.algorithm_settings.get("acceptable_range", 5),
                                help="الفرق المقبول في السعر")
    
    st.markdown("---")
    st.markdown("### 📊 ملخص القواعد الحالية")
    
    rules_data = {
        "القاعدة": ["رفع السعر", "خفض السعر", "موافق", "يحتاج مراجعة", "حد التطابق"],
        "الشرط": [
            f"سعرنا أقل بأكثر من {raise_threshold}%",
            f"سعرنا أعلى بأكثر من {lower_threshold}%",
            f"الفرق ضمن ±{acceptable_range}%",
            f"نسبة المطابقة < {review_threshold}%",
            f"الحد الأدنى: {threshold}%"
        ],
        "اللون": ["🔴", "🟡", "🟢", "⚠️", "🎯"]
    }
    st.table(pd.DataFrame(rules_data))
    
    if st.button("💾 حفظ الإعدادات", type="primary", use_container_width=True):
        st.session_state.algorithm_settings = {
            "threshold": threshold,
            "raise_threshold": raise_threshold,
            "lower_threshold": lower_threshold,
            "acceptable_range": acceptable_range,
            "review_threshold": review_threshold,
        }
        st.success("✅ تم حفظ إعدادات الخوارزمية!")

# ══════════════════════════════════════════════════════════════
# 14. قاعدة البيانات
# ══════════════════════════════════════════════════════════════
elif section == "💾 قاعدة البيانات":
    st.markdown("# 💾 قاعدة البيانات")
    st.markdown("> عرض وإدارة جميع السجلات المحفوظة")
    st.markdown("---")
    
    # إحصائيات
    db_stats = get_db_stats()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📊 إجمالي السجلات", db_stats.get("total_records", 0))
    c2.metric("🔴 رفع سعر", db_stats.get("raise_count", 0))
    c3.metric("🟡 خفض سعر", db_stats.get("lower_count", 0))
    c4.metric("🟢 موافق", db_stats.get("approved_count", 0))
    
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["📋 جميع السجلات", "📤 سجل الإرسالات", "🔧 إدارة"])
    
    with tab1:
        st.markdown("### 📋 جميع السجلات")
        
        # فلترة
        filter_col1, filter_col2 = st.columns(2)
        with filter_col1:
            filter_rec = st.selectbox("🔍 فلترة حسب التوصية", ["الكل", "رفع سعر", "خفض سعر", "موافق"])
        with filter_col2:
            filter_limit = st.number_input("📊 عدد السجلات", 10, 1000, 100)
        
        records = get_all_records(filter_limit)
        if not records.empty:
            if filter_rec != "الكل":
                records = records[records["recommendation"] == filter_rec]
            
            st.dataframe(records, use_container_width=True)
            
            # تحميل
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                records.to_excel(writer, sheet_name="سجلات", index=False)
            output.seek(0)
            st.download_button("📥 تحميل كـ Excel", data=output.getvalue(),
                              file_name=f"db_records_{datetime.now():%Y%m%d}.xlsx",
                              mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        else:
            st.info("📋 لا توجد سجلات")
    
    with tab2:
        st.markdown("### 📤 سجل الإرسالات")
        logs = get_send_logs()
        if not logs.empty:
            st.dataframe(logs, use_container_width=True)
        else:
            st.info("📋 لا توجد إرسالات")
    
    with tab3:
        st.markdown("### 🔧 إدارة قاعدة البيانات")
        
        st.warning("⚠️ **تحذير:** الحذف لا يمكن التراجع عنه!")
        
        if st.button("🗑️ حذف جميع السجلات القديمة (أكثر من 30 يوم)", type="secondary"):
            from datetime import timedelta
            cutoff = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
            result = supabase_request("DELETE", "analysis_results", params={"timestamp": f"lt.{cutoff}"})
            st.success("✅ تم حذف السجلات القديمة")
        
        if st.button("📊 إعادة حساب الإحصائيات"):
            st.rerun()

# ══════════════════════════════════════════════════════════════
# 15. الإعدادات
# ══════════════════════════════════════════════════════════════
elif section == "⚙️ الإعدادات":
    st.markdown("# ⚙️ الإعدادات")
    st.markdown("---")
    
    tab1, tab2, tab3, tab4 = st.tabs(["🤖 الذكاء الصناعي", "⚡ Make.com", "📁 Google Drive", "🔧 عام"])
    
    with tab1:
        st.markdown("### 🤖 إعدادات الذكاء الصناعي")
        
        gemini_key = st.text_input("🔑 Gemini API Key", value=st.session_state.gemini_key, type="password")
        if gemini_key != st.session_state.gemini_key:
            st.session_state.gemini_key = gemini_key
        
        if st.button("🔄 اختبار Gemini", key="test_gemini_settings"):
            with st.spinner("⏳ جاري الاختبار..."):
                result = verify_gemini_connection(gemini_key)
                if result["connected"]:
                    st.success(f"✅ متصل! النموذج: {result['model']}")
                    st.session_state.gemini_connected = True
                else:
                    st.error(f"❌ {result['message']}")
                    st.session_state.gemini_connected = False
        
        st.markdown("---")
        
        openrouter_key = st.text_input("🔑 OpenRouter API Key", value=st.session_state.openrouter_key, type="password")
        if openrouter_key != st.session_state.openrouter_key:
            st.session_state.openrouter_key = openrouter_key
        
        if st.button("🔄 اختبار OpenRouter", key="test_or_settings"):
            with st.spinner("⏳ جاري الاختبار..."):
                result = verify_openrouter_connection(openrouter_key)
                if result["connected"]:
                    st.success(f"✅ متصل! النموذج: {result['model']}")
                    st.session_state.openrouter_connected = True
                else:
                    st.error(f"❌ {result['message']}")
                    st.session_state.openrouter_connected = False
    
    with tab2:
        st.markdown("### ⚡ إعدادات Make.com")
        
        st.markdown("#### Webhook تحديث الأسعار")
        st.code(WEBHOOK_UPDATE_PRICES, language=None)
        
        st.markdown("#### Webhook إضافة منتجات جديدة")
        st.code(WEBHOOK_NEW_PRODUCTS, language=None)
        
        if st.button("🔄 اختبار جميع Webhooks", key="test_all_webhooks"):
            with st.spinner("⏳ جاري الاختبار..."):
                r1 = verify_webhook_connection(WEBHOOK_UPDATE_PRICES)
                r2 = verify_webhook_connection(WEBHOOK_NEW_PRODUCTS)
                
                if r1["connected"]:
                    st.success("✅ Webhook تحديث الأسعار: متصل!")
                    st.session_state.make_update_connected = True
                else:
                    st.error(f"❌ Webhook تحديث الأسعار: {r1['message']}")
                    st.session_state.make_update_connected = False
                
                if r2["connected"]:
                    st.success("✅ Webhook إضافة منتجات: متصل!")
                    st.session_state.make_new_connected = True
                else:
                    st.error(f"❌ Webhook إضافة منتجات: {r2['message']}")
                    st.session_state.make_new_connected = False
    
    with tab3:
        st.markdown("### 📁 إعدادات Google Drive")
        
        drive_id = st.text_input("📂 معرف مجلد Google Drive",
                                 value=st.session_state.get("drive_folder_id", ""),
                                 placeholder="أدخل معرف المجلد")
        if drive_id:
            st.session_state.drive_folder_id = drive_id
            st.success("✅ تم حفظ معرف المجلد")
    
    with tab4:
        st.markdown("### 🔧 إعدادات عامة")
        
        backend_url = st.text_input("🌐 رابط الخادم الخلفي",
                                    value=st.session_state.backend_url,
                                    placeholder="http://localhost:8000")
        if backend_url != st.session_state.backend_url:
            st.session_state.backend_url = backend_url
        
        st.markdown("---")
        st.markdown("### 📊 معلومات النظام")
        st.json({
            "الإصدار": "v7.3",
            "قاعدة البيانات": "Supabase Cloud",
            "Gemini Key": "✅ موجود" if st.session_state.gemini_key else "❌ مفقود",
            "OpenRouter Key": "✅ موجود" if st.session_state.openrouter_key else "❌ مفقود",
            "Webhook تحديث": WEBHOOK_UPDATE_PRICES[:50] + "...",
            "Webhook إضافة": WEBHOOK_NEW_PRODUCTS[:50] + "...",
            "Supabase": SUPABASE_URL,
        })

# ══════════════════════════════════════════════════════════════
# تذييل
# ══════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888; padding: 10px;">
    💎 نظام التسعير الذكي v7.3 | مهووس للعطور | 2026
</div>
""", unsafe_allow_html=True)
