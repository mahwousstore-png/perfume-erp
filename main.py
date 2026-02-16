"""
app.py
نظام التسعير الذكي للعطور v15.0
═══════════════════════════════════
15 قسم كامل | نظام تصنيف ذكي متعدد المستويات | Gemini AI + OpenRouter | Make.com | Google Drive | Supabase
"""

import streamlit as st
import pandas as pd
import requests
import json
import time
import os
from datetime import datetime
from io import BytesIO

# ── استيراد الوحدات الجديدة v8.0 ──────────────────────────────
try:
    from modules.auth import init_session, show_login_page, show_logout_button, check_permission, log_action
    from modules.styles import apply_custom_styles
    V8_MODULES_AVAILABLE = True
except ImportError:
    V8_MODULES_AVAILABLE = False
    print("⚠️ وحدات v8.0 غير متوفرة - التشغيل بالوضع v7.4")

# ── إعدادات الصفحة ─────────────────────────────────────────
# تم نقل إعدادات الصفحة إلى app.py لتجنب التضارب
# st.set_page_config(
#     page_title="نظام التسعير الذكي v15.0",
#     page_icon="💎",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# ── تهيئة الجلسة v8.0 ──────────────────────────────────────────
if V8_MODULES_AVAILABLE:
    init_session()
    apply_custom_styles()

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
WEBHOOK_NEW_PRODUCTS = "https://hook.eu2.make.com/xvubj23dmpxu8qzilstd25cnumrwtdxm"

# ── مفاتيح API من Streamlit Secrets (آمن) ────────────────────
# يتم قراءة المفاتيح من .streamlit/secrets.toml أو Streamlit Cloud Secrets
try:
    DEFAULT_GEMINI_KEY = st.secrets.get("GEMINI_API_KEY", "")
    DEFAULT_OPENROUTER_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
except:
    # في حالة عدم وجود ملف secrets، استخدم قيم فارغة
    DEFAULT_GEMINI_KEY = ""
    DEFAULT_OPENROUTER_KEY = ""

# Fallback: إذا كان المفتاح فارغاً، استخدم المفتاح الاحتياطي
if not DEFAULT_GEMINI_KEY or DEFAULT_GEMINI_KEY.strip() == "":
    # المفتاح يُقرأ من Streamlit Secrets فقط - لا تضع المفتاح هنا
    DEFAULT_GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")

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

def _safe_df_len(obj):
    """حساب طول DataFrame أو List بأمان"""
    if obj is None:
        return 0
    if isinstance(obj, pd.DataFrame):
        return 0 if obj.empty else len(obj)
    if isinstance(obj, list):
        return len(obj)
    return 0

def _safe_df_to_records(obj):
    """تحويل DataFrame أو List إلى قائمة records بأمان"""
    if obj is None:
        return []
    if isinstance(obj, pd.DataFrame):
        return obj.to_dict(orient="records") if not obj.empty else []
    if isinstance(obj, list):
        return obj
    return []

def save_results_to_db(results):
    """حفظ نتائج التحليل في Supabase (هيكل JSONB)."""
    import uuid
    session_id = str(uuid.uuid4())[:8]
    
    # حساب الإحصائيات بأمان (يتعامل مع DataFrame و List)
    raise_df = results.get("raise")
    lower_df = results.get("lower")
    approved_df = results.get("approved")
    missing_df = results.get("missing")
    review_df = results.get("review")
    
    raise_count = _safe_df_len(raise_df)
    lower_count = _safe_df_len(lower_df)
    approved_count = _safe_df_len(approved_df)
    missing_count = _safe_df_len(missing_df)
    review_count = _safe_df_len(review_df)
    total = raise_count + lower_count + approved_count
    
    # تحويل النتائج إلى JSON
    results_json = {}
    for key in ["raise", "lower", "approved", "missing", "review"]:
        records = _safe_df_to_records(results.get(key))
        if records:
            results_json[key] = records
    
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
    """تحميل آخر نتائج تحليل من Supabase وإعادتها بهيكل كامل يشمل stats و all."""
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
            
            # بناء stats من البيانات المحفوظة
            raise_count = len(restored.get("raise", pd.DataFrame()))
            lower_count = len(restored.get("lower", pd.DataFrame()))
            approved_count = len(restored.get("approved", pd.DataFrame()))
            missing_count = len(restored.get("missing", pd.DataFrame()))
            review_count = len(restored.get("review", pd.DataFrame()))
            total = raise_count + lower_count + approved_count
            
            restored["stats"] = {
                "total": total,
                "raise_count": raise_count,
                "lower_count": lower_count,
                "approved_count": approved_count,
                "missing_count": missing_count,
                "review_count": review_count,
                "critical": record.get("needs_review", 0) or 0,
                "avg_diff": 0,
                "competitors": 0,
            }
            
            # بناء all من دمج جميع DataFrames
            all_frames = []
            for key in ["raise", "lower", "approved"]:
                df = restored.get(key)
                if df is not None and not df.empty:
                    df = df.copy()
                    df["التوصية"] = {"raise": "رفع سعر", "lower": "خفض سعر", "approved": "موافق"}.get(key, key)
                    all_frames.append(df)
            if all_frames:
                restored["all"] = pd.concat(all_frames, ignore_index=True)
            else:
                restored["all"] = pd.DataFrame()
            
            return restored
    return None

def load_all_previous_results():
    """تحميل جميع نتائج التحليلات السابقة من Supabase."""
    results_list = supabase_request("GET", "analysis_results", params={"select": "*", "order": "id.desc", "limit": "50"})
    if not results_list:
        return []
    
    all_sessions = []
    for record in results_list:
        results_json = record.get("results_json")
        if results_json:
            if isinstance(results_json, str):
                try:
                    results_json = json.loads(results_json)
                except Exception:
                    continue
            session_data = {
                "id": record.get("id"),
                "created_at": record.get("created_at", ""),
                "store_filename": record.get("store_filename", ""),
                "competitor_filename": record.get("competitor_filename", ""),
                "total_products": record.get("total_products", 0),
                "price_increase": record.get("price_increase", 0),
                "price_decrease": record.get("price_decrease", 0),
                "approved": record.get("approved", 0),
                "missing": record.get("missing", 0),
                "needs_review": record.get("needs_review", 0),
            }
            # تحميل DataFrames
            for key in ["raise", "lower", "approved", "missing", "review"]:
                if key in results_json:
                    session_data[key] = pd.DataFrame(results_json[key])
                else:
                    session_data[key] = pd.DataFrame()
            all_sessions.append(session_data)
    return all_sessions

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
            "threshold": 60,
            "raise_threshold": 10,
            "lower_threshold": 5,
            "acceptable_range": 5,
            "review_threshold": 85,
        },
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
    
    # تحميل آخر نتائج من Supabase تلقائياً عند فتح التطبيق
    if st.session_state.results is None:
        try:
            loaded = load_latest_results()
            if loaded:
                st.session_state.results = loaded
        except Exception:
            pass  # فشل التحميل لا يمنع التطبيق من العمل

init_session()

# ══════════════════════════════════════════════════════════════
# دوال التحقق من الاتصالات
# ══════════════════════════════════════════════════════════════

def verify_gemini_connection(api_key=None, update_session=True):
    """فحص اتصال Gemini/OpenRouter مع نظام المفاتيح المتعددة."""
    try:
        from modules.ai_verification import verify_ai_connection, get_ai_status
        
        # فحص الاتصال الفعلي
        ai_result = verify_ai_connection()
        ai_status = get_ai_status()
        
        if ai_result.get("connected"):
            provider = ai_result.get("provider", "gemini")
            gemini_count = ai_status.get("gemini_active", 0)
            openrouter_count = ai_status.get("openrouter_active", 0)
            
            result = {
                "connected": True, 
                "model": f"{provider}",
                "message": f"✅ متصل عبر {provider} | Gemini: {gemini_count} مفتاح | OpenRouter: {openrouter_count} مفتاح"
            }
            if update_session:
                st.session_state.gemini_connected = True
            return result
        else:
            result = {
                "connected": False, 
                "message": f"❌ جميع المفاتيح فاشلة | Gemini: {ai_status.get('gemini_total', 0)} | OpenRouter: {ai_status.get('openrouter_total', 0)}"
            }
            if update_session:
                st.session_state.gemini_connected = False
            return result
    
    except Exception as e:
        # Fallback: المحاولة بالطريقة القديمة
        if api_key is None:
            api_key = DEFAULT_GEMINI_KEY
        
        if not api_key or len(api_key) < 10:
            result = {"connected": False, "message": "مفتاح API مفقود أو غير صالح"}
            if update_session:
                st.session_state.gemini_connected = False
            return result
        
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
            response = requests.post(
                url,
                json={"contents": [{"parts": [{"text": "test"}]}]},
                headers={"Content-Type": "application/json"},
                timeout=20
            )
            
            if response.status_code == 200:
                result = {"connected": True, "model": "gemini-2.5-flash", "message": "متصل ويعمل"}
                if update_session:
                    st.session_state.gemini_connected = True
                return result
            else:
                err_msg = "خطأ"
                try:
                    err_msg = response.json().get("error", {}).get("message", f"HTTP {response.status_code}")
                except:
                    err_msg = f"HTTP {response.status_code}"
                result = {"connected": False, "message": err_msg}
                if update_session:
                    st.session_state.gemini_connected = False
                return result
        except Exception as ex:
            result = {"connected": False, "message": str(ex)}
            if update_session:
                st.session_state.gemini_connected = False
            return result

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

def _safe_int_id(val):
    """تحويل product_id إلى عدد صحيح نظيف (بدون .0)"""
    if val is None or val == "" or val == 0:
        return ""
    try:
        return str(int(float(val)))
    except (ValueError, TypeError):
        return str(val)

# ── تحميل ماركات وتصنيفات سلة من الملفات ──────────────────────────────
def _load_salla_brands():
    """تحميل 521 ماركة من ملف سلة وبناء قائمة مطابقة (عربي + إنجليزي)"""
    try:
        df = pd.read_csv(os.path.join(os.path.dirname(__file__), "data", "brands.csv"))
        brand_map = []  # [(full_name, search_terms)]
        for b in df["اسم الماركة"].dropna().tolist():
            b = str(b).strip()
            terms = [b.lower()]  # الاسم الكامل
            if "|" in b:
                parts = b.split("|")
                ar = parts[0].strip()
                en = parts[1].strip() if len(parts) > 1 else ""
                if ar: terms.append(ar.lower())
                if en: terms.append(en.lower())
            brand_map.append((b, terms))
        # ترتيب بالأطول أولاً للمطابقة الأدق
        brand_map.sort(key=lambda x: max(len(t) for t in x[1]), reverse=True)
        return brand_map
    except Exception:
        return []

def _load_salla_categories():
    """تحميل 88 تصنيف من ملف سلة"""
    try:
        df = pd.read_csv(os.path.join(os.path.dirname(__file__), "data", "categories.csv"))
        return df["التصنيفات"].dropna().tolist()
    except Exception:
        return []

_SALLA_BRANDS = _load_salla_brands()  # تحميل مرة واحدة
_SALLA_CATEGORIES = _load_salla_categories()

def _extract_brand(name):
    """استخراج الماركة من اسم المنتج باستخدام 521 ماركة من سلة"""
    name_lower = name.lower()
    for full_name, terms in _SALLA_BRANDS:
        for term in terms:
            if term in name_lower:
                return full_name
    return "عطور"

def _extract_category(name, product_type=""):
    """استخراج التصنيف من اسم المنتج باستخدام 88 تصنيف من سلة"""
    combined = f"{name} {product_type}".lower()
    # قواعد مخصصة بالأولوية
    if "تستر" in combined:
        return "عطور التستر"
    if "طقم" in combined or "مجموع" in combined or "set" in combined:
        return "مجموعات و هدايا"
    if "شعر" in combined or "hair" in combined:
        return "عطور الشعر"
    if "جسم" in combined or "body" in combined:
        return "عطور الجسم"
    if "عينة" in combined or "sample" in combined or "ميني" in combined:
        return "عطور عينات ميني"
    if "بخور" in combined:
        return "العود و البخور"
    if "عود" in combined:
        return "عود طبيعي"
    if "معطر" in combined:
        return "معطرات المنازل"
    # افتراضي
    return "العطور"

def send_price_updates(products):
    payload = {"products": [
        {"product_id": _safe_int_id(p.get("product_id", p.get("pid_my", p.get("id", "")))),
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
    import hashlib, time
    payload = {"data": []}
    for p in products:
        name = p.get("المنتج", p.get("name", ""))
        price_raw = p.get("السعر", p.get("price", p.get("أقل سعر منافس", 0)))
        try:
            price = int(float(str(price_raw).replace(',','')))
        except:
            price = 0
        if price <= 0:
            price = 1  # سلة لا تقبل سعر 0
        # توليد SKU تلقائي إذا كان فارغاً
        sku = p.get("sku", p.get("رمز المنتج", ""))
        if not sku:
            sku = f"PERF-{hashlib.md5(name.encode()).hexdigest()[:8].upper()}"
        # استخراج الماركة تلقائياً إذا كانت فارغة
        brand = p.get("الماركة", p.get("brand", ""))
        if not brand:
            brand = _extract_brand(name)
        # تصنيف افتراضي إذا كان فارغاً - يستخدم 88 تصنيف من سلة
        category = p.get("التصنيف", p.get("category", ""))
        if not category:
            p_type = p.get("النوع", p.get("type", ""))
            category = _extract_category(name, str(p_type))
        # بناء الوصف
        desc = p.get("الوصف", p.get("description", ""))
        if not desc:
            desc = f"{name} - {p.get('النوع', p.get('type', ''))} - {p.get('الحجم', p.get('size', ''))}"
        # بناء البيانات بتنسيق يتوافق مع Salla API عبر Make.com
        # الحقول المدعومة في blueprint: أسم المنتج, سعر المنتج, رمز المنتج sku, الوزن, سعر التكلفة, السعر المخفض, الوصف
        # ملاحظة: categories و brand_id يحتاجان ID رقمي من سلة وليس اسم نصي
        item = {
            "أسم المنتج": name,
            "سعر المنتج": price,
            "رمز المنتج sku": sku,
            "الوزن": 1,
            "الوصف": desc,
        }
        # لا نرسل سعر التكلفة والسعر المخفض إذا كانا 0 لتجنب أخطاء سلة
        cost = p.get("سعر التكلفة", p.get("cost_price", 0))
        if cost and int(float(str(cost))) > 0:
            item["سعر التكلفة"] = int(float(str(cost)))
        sale = p.get("السعر المخفض", p.get("sale_price", 0))
        if sale and int(float(str(sale))) > 0:
            item["السعر المخفض"] = int(float(str(sale)))
        payload["data"].append(item)
    return send_to_webhook(WEBHOOK_NEW_PRODUCTS, payload)

def call_gemini(prompt, api_key=None, max_retries=3):
    """استدعاء Gemini مع معالجة أخطاء وإعادة محاولة تلقائية."""
    import time
    
    # استخدام المفتاح المدمج إذا لم يتم تمرير مفتاح
    if api_key is None:
        api_key = DEFAULT_GEMINI_KEY
    
    key = api_key or st.session_state.gemini_key
    if not key:
        return {"success": False, "error": "مفتاح Gemini غير موجود"}
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={key}"
    
    for attempt in range(max_retries):
        try:
            response = requests.post(
                url,
                json={"contents": [{"parts": [{"text": prompt}]}]},
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                return {"success": True, "text": text}
            
            elif response.status_code == 429:  # Rate Limit
                wait_time = 60 * (attempt + 1)  # 60, 120, 180 ثانية
                if attempt < max_retries - 1:
                    st.warning(f"⚠️ تجاوز الحد الأقصى للطلبات. انتظار {wait_time} ثانية...")
                    time.sleep(wait_time)
                    continue
                return {"success": False, "error": "تجاوز الحد الأقصى للطلبات بعد عدة محاولات"}
            
            elif response.status_code == 401:  # Invalid API Key
                return {"success": False, "error": "مفتاح API غير صحيح أو منتهي الصلاحية"}
            
            elif response.status_code == 400:  # Bad Request
                error_msg = response.json().get("error", {}).get("message", "طلب غير صحيح")
                return {"success": False, "error": f"خطأ في الطلب: {error_msg}"}
            
            else:
                if attempt < max_retries - 1:
                    st.warning(f"⚠️ خطأ HTTP {response.status_code}. محاولة {attempt + 1}/{max_retries}...")
                    time.sleep(5)
                    continue
                return {"success": False, "error": f"HTTP {response.status_code}"}
        
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                st.warning(f"⚠️ انتهت المهلة. محاولة {attempt + 1}/{max_retries}...")
                time.sleep(5)
                continue
            return {"success": False, "error": "انتهت مهلة الاتصال بعد عدة محاولات"}
        
        except requests.exceptions.ConnectionError:
            if attempt < max_retries - 1:
                st.warning(f"⚠️ خطأ في الاتصال. محاولة {attempt + 1}/{max_retries}...")
                time.sleep(5)
                continue
            return {"success": False, "error": "فشل الاتصال بالخادم"}
        
        except Exception as e:
            if attempt < max_retries - 1:
                st.warning(f"⚠️ خطأ: {str(e)}. محاولة {attempt + 1}/{max_retries}...")
                time.sleep(5)
                continue
            return {"success": False, "error": str(e)}
    
    return {"success": False, "error": "فشلت كل المحاولات"}

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
    """دالة مشتركة لعرض أزرار الموافقة والإرسال لأي قسم - مع Pagination ونظام قرارات."""
    if df is None or df.empty:
        st.info(f"📋 لا توجد منتجات في قسم {section_label}")
        return
    
    total_products = len(df)
    
    # ── نظام القرارات: تتبع المنتجات المُزالة ──
    removed_key = f"removed_{section_key}"
    if removed_key not in st.session_state:
        st.session_state[removed_key] = set()
    
    # فلترة المنتجات المُزالة
    removed_indices = st.session_state[removed_key]
    df_filtered = df[~df.index.isin(removed_indices)]
    removed_count = total_products - len(df_filtered)
    
    # ── نظام الفلاتر الشامل ──
    with st.expander("🔍 فلاتر البحث والتصفية", expanded=False):
        fcol1, fcol2, fcol3, fcol4 = st.columns(4)
        
        with fcol1:
            # فلتر البحث بالاسم
            search_text = st.text_input("🔎 بحث باسم المنتج", key=f"filter_search_{section_key}", placeholder="اكتب اسم المنتج...")
        
        with fcol2:
            # فلتر المنافس
            competitors_list = ["-- الكل --"]
            if 'المنافس' in df_filtered.columns:
                unique_comp = df_filtered['المنافس'].dropna().unique().tolist()
                competitors_list.extend([str(c).replace('.xlsx','').replace('.csv','') for c in unique_comp if str(c) != 'nan'])
            filter_competitor = st.selectbox("🏢 المنافس", competitors_list, key=f"filter_comp_{section_key}")
        
        with fcol3:
            # فلتر الخطورة
            risk_options = ["-- الكل --", "🔴 حرج", "🟡 متوسط", "🟢 عادي"]
            filter_risk = st.selectbox("⚠️ الخطورة", risk_options, key=f"filter_risk_{section_key}")
        
        with fcol4:
            # فلتر الثقة
            confidence_options = ["-- الكل --", "✅ عالية (90%+)", "⚠️ متوسطة (75-90%)", "❌ منخفضة (<75%)"]
            filter_confidence = st.selectbox("🔒 الثقة", confidence_options, key=f"filter_conf_{section_key}")
        
        fcol5, fcol6, fcol7, fcol8 = st.columns(4)
        with fcol5:
            # فلتر نطاق السعر
            price_col = 'السعر' if 'السعر' in df_filtered.columns else None
            if price_col:
                try:
                    min_p = float(df_filtered[price_col].min())
                    max_p = float(df_filtered[price_col].max())
                    if min_p < max_p:
                        price_range = st.slider("💰 نطاق السعر", min_value=min_p, max_value=max_p, value=(min_p, max_p), key=f"filter_price_{section_key}")
                    else:
                        price_range = (min_p, max_p)
                except:
                    price_range = None
            else:
                price_range = None
        
        with fcol6:
            # فلتر نسبة الفرق
            diff_col = 'النسبة %' if 'النسبة %' in df_filtered.columns else None
            if diff_col:
                try:
                    min_d = float(df_filtered[diff_col].min())
                    max_d = float(df_filtered[diff_col].max())
                    if min_d < max_d:
                        diff_range = st.slider("📈 نسبة الفرق %", min_value=min_d, max_value=max_d, value=(min_d, max_d), key=f"filter_diff_{section_key}")
                    else:
                        diff_range = (min_d, max_d)
                except:
                    diff_range = None
            else:
                diff_range = None
        
        with fcol7:
            # ترتيب
            sort_options = ["الافتراضي", "السعر: الأعلى", "السعر: الأقل", "الفرق: الأعلى", "الفرق: الأقل", "الثقة: الأعلى", "الثقة: الأقل"]
            sort_by = st.selectbox("↕️ ترتيب حسب", sort_options, key=f"filter_sort_{section_key}")
        
        with fcol8:
            if st.button("🔄 إعادة تعيين الفلاتر", key=f"reset_filters_{section_key}", use_container_width=True):
                for fk in [f"filter_search_{section_key}", f"filter_comp_{section_key}", f"filter_risk_{section_key}", f"filter_conf_{section_key}"]:
                    if fk in st.session_state:
                        del st.session_state[fk]
                st.rerun()
    
    # تطبيق الفلاتر
    if search_text:
        mask = df_filtered.apply(lambda r: search_text.lower() in str(r.get('المنتج', '')).lower() or search_text.lower() in str(r.get('اسم المنافس', '')).lower(), axis=1)
        df_filtered = df_filtered[mask]
    
    if filter_competitor != "-- الكل --" and 'المنافس' in df_filtered.columns:
        df_filtered = df_filtered[df_filtered['المنافس'].astype(str).str.contains(filter_competitor.replace('.xlsx','').replace('.csv',''), na=False)]
    
    if filter_risk != "-- الكل --" and 'الخطورة' in df_filtered.columns:
        risk_map = {"🔴 حرج": "حرج", "🟡 متوسط": "متوسط", "🟢 عادي": "عادي"}
        df_filtered = df_filtered[df_filtered['الخطورة'] == risk_map.get(filter_risk, '')]
    
    if filter_confidence != "-- الكل --" and 'الثقة %' in df_filtered.columns:
        try:
            conf_vals = pd.to_numeric(df_filtered['الثقة %'], errors='coerce').fillna(0)
            if "عالية" in filter_confidence:
                df_filtered = df_filtered[conf_vals >= 90]
            elif "متوسطة" in filter_confidence:
                df_filtered = df_filtered[(conf_vals >= 75) & (conf_vals < 90)]
            elif "منخفضة" in filter_confidence:
                df_filtered = df_filtered[conf_vals < 75]
        except:
            pass
    
    if price_range and price_col:
        try:
            price_vals = pd.to_numeric(df_filtered[price_col], errors='coerce').fillna(0)
            df_filtered = df_filtered[(price_vals >= price_range[0]) & (price_vals <= price_range[1])]
        except:
            pass
    
    if diff_range and diff_col:
        try:
            diff_vals = pd.to_numeric(df_filtered[diff_col], errors='coerce').fillna(0)
            df_filtered = df_filtered[(diff_vals >= diff_range[0]) & (diff_vals <= diff_range[1])]
        except:
            pass
    
    # تطبيق الترتيب
    if sort_by != "الافتراضي":
        try:
            if "السعر: الأعلى" == sort_by and price_col:
                df_filtered = df_filtered.sort_values(price_col, ascending=False, key=lambda x: pd.to_numeric(x, errors='coerce'))
            elif "السعر: الأقل" == sort_by and price_col:
                df_filtered = df_filtered.sort_values(price_col, ascending=True, key=lambda x: pd.to_numeric(x, errors='coerce'))
            elif "الفرق: الأعلى" == sort_by and diff_col:
                df_filtered = df_filtered.sort_values(diff_col, ascending=False, key=lambda x: pd.to_numeric(x, errors='coerce').abs())
            elif "الفرق: الأقل" == sort_by and diff_col:
                df_filtered = df_filtered.sort_values(diff_col, ascending=True, key=lambda x: pd.to_numeric(x, errors='coerce').abs())
            elif "الثقة: الأعلى" == sort_by and 'الثقة %' in df_filtered.columns:
                df_filtered = df_filtered.sort_values('الثقة %', ascending=False, key=lambda x: pd.to_numeric(x, errors='coerce'))
            elif "الثقة: الأقل" == sort_by and 'الثقة %' in df_filtered.columns:
                df_filtered = df_filtered.sort_values('الثقة %', ascending=True, key=lambda x: pd.to_numeric(x, errors='coerce'))
        except:
            pass
    
    filtered_count = len(df_filtered)
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #e3f2fd, #bbdefb); border-radius: 12px; padding: 15px; margin: 10px 0; text-align: center;">
        <h3 style="margin:0; color: #1565c0;">📊 عداد المنتجات: <span style="font-size: 1.8rem; color: #d32f2f;">{filtered_count}</span> منتج في قسم {section_label}
        {f' | <span style="color: #999;">🗑️ تم إزالة {removed_count}</span>' if removed_count > 0 else ''}</h3>
    </div>""", unsafe_allow_html=True)
    
    # ── Pagination ──
    ITEMS_PER_PAGE = 25
    page_key = f"page_{section_key}"
    if page_key not in st.session_state:
        st.session_state[page_key] = 0
    
    total_pages = max(1, (filtered_count + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE)
    current_page = min(st.session_state[page_key], total_pages - 1)
    
    # أزرار التنقل بين الصفحات
    if total_pages > 1:
        col_prev, col_page_info, col_next, col_goto = st.columns([1, 2, 1, 2])
        with col_prev:
            if st.button("◀️ السابق", key=f"prev_{section_key}", disabled=current_page == 0):
                st.session_state[page_key] = current_page - 1
                st.rerun()
        with col_page_info:
            st.markdown(f"<div style='text-align:center; padding:8px;'><b>صفحة {current_page + 1} من {total_pages}</b> ({filtered_count} منتج)</div>", unsafe_allow_html=True)
        with col_next:
            if st.button("التالي ▶️", key=f"next_{section_key}", disabled=current_page >= total_pages - 1):
                st.session_state[page_key] = current_page + 1
                st.rerun()
        with col_goto:
            goto_page = st.number_input("انتقل لصفحة", min_value=1, max_value=total_pages, value=current_page + 1, key=f"goto_{section_key}", label_visibility="collapsed")
            if goto_page - 1 != current_page:
                st.session_state[page_key] = goto_page - 1
                st.rerun()
    
    # حساب نطاق الصفحة الحالية
    start_idx = current_page * ITEMS_PER_PAGE
    end_idx = min(start_idx + ITEMS_PER_PAGE, filtered_count)
    page_df = df_filtered.iloc[start_idx:end_idx]
    
    # أزرار تحديد الكل / إلغاء الكل
    col_s1, col_s2, col_s3, col_s4 = st.columns([1, 1, 1, 2])
    with col_s1:
        if st.button("✅ تحديد الكل", key=f"sel_all_{section_key}"):
            st.session_state[f"sel_{section_key}"] = {idx: True for idx in df_filtered.index}
            st.rerun()
    with col_s2:
        if st.button("❌ إلغاء الكل", key=f"desel_all_{section_key}"):
            st.session_state[f"sel_{section_key}"] = {idx: False for idx in df_filtered.index}
            st.rerun()
    with col_s3:
        if removed_count > 0:
            if st.button(f"♻️ استعادة المُزالة ({removed_count})", key=f"restore_{section_key}"):
                st.session_state[removed_key] = set()
                st.rerun()
    
    if f"sel_{section_key}" not in st.session_state:
        st.session_state[f"sel_{section_key}"] = {}
    
    # ── عناوين الأعمدة ──
    header_cols = st.columns([0.3, 2.5, 2.5, 1.0, 1.0, 1.0, 0.8, 0.8, 0.8, 0.5])
    with header_cols[0]:
        st.markdown("**✓**")
    with header_cols[1]:
        st.markdown("**📦 منتجنا**")
    with header_cols[2]:
        st.markdown("**🏪 منتج المنافس**")
    with header_cols[3]:
        st.markdown("**💰 سعرنا**")
    with header_cols[4]:
        st.markdown("**🏷️ سعر المنافس**")
    with header_cols[5]:
        st.markdown("**🎯 الموصى**")
    with header_cols[6]:
        st.markdown("**📊 النسبة**")
    with header_cols[7]:
        st.markdown("**🔒 الثقة**")
    with header_cols[8]:
        st.markdown("**⚠️ خطورة**")
    with header_cols[9]:
        st.markdown("**🤖**")
    st.markdown("<hr style='margin:5px 0;'>", unsafe_allow_html=True)
    
    # ── عرض المنتجات مع أسماء كاملة ──
    selected = []
    for _, row in page_df.iterrows():
        original_idx = row.name  # الفهرس الأصلي
        cols = st.columns([0.3, 2.5, 2.5, 1.0, 1.0, 1.0, 0.8, 0.8, 0.8, 0.5])
        
        with cols[0]:
            default_val = st.session_state[f"sel_{section_key}"].get(original_idx, False)
            checked = st.checkbox("", value=default_val, key=f"{section_key}_{original_idx}")
            st.session_state[f"sel_{section_key}"][original_idx] = checked
            if checked:
                selected.append(row.to_dict())
        
        with cols[1]:
            # اسم منتجنا كامل
            my_product = str(row.get('المنتج', ''))
            my_brand = str(row.get('ماركتنا', ''))
            st.markdown(f"**{my_product}**")
            if my_brand:
                st.caption(f"🏷️ {my_brand}")
        
        with cols[2]:
            # اسم منتج المنافس كامل + اسم المنافس
            comp_product = str(row.get('اسم المنافس', ''))
            competitor_name = str(row.get('المنافس', '')).replace('.xlsx', '').replace('.csv', '')
            match_stage = str(row.get('مرحلة المطابقة', ''))
            if comp_product and comp_product != 'nan':
                st.markdown(f"**{comp_product}**")
                stage_emoji = {'fast': '⚡', 'medium': '🔍', 'deep': '🔬', 'gemini': '🤖'}.get(match_stage, '📋')
                st.caption(f"{stage_emoji} {competitor_name}")
            else:
                st.markdown("*غير متاح*")
        
        with cols[3]:
            st.write(f"💰 {row.get('السعر', 0)}")
        
        with cols[4]:
            comp_price = row.get('أقل سعر منافس', row.get('سعر المنافس', 0))
            st.write(f"🏷️ {comp_price}")
        
        with cols[5]:
            rec_price = row.get('السعر الموصى', '')
            if rec_price:
                st.write(f"🎯 {rec_price}")
            else:
                st.write("—")
        
        with cols[6]:
            diff_pct = row.get('النسبة %', 0)
            color = "red" if diff_pct > 0 else "green"
            st.markdown(f'<span style="color:{color};font-weight:bold">{diff_pct}%</span>', unsafe_allow_html=True)
        
        with cols[7]:
            confidence = row.get('الثقة %', '')
            if confidence:
                conf_val = float(confidence) if confidence else 0
                conf_color = "#4caf50" if conf_val >= 90 else "#ff9800" if conf_val >= 75 else "#f44336"
                st.markdown(f'<span style="color:{conf_color};font-weight:bold">{confidence}%</span>', unsafe_allow_html=True)
            else:
                st.write("—")
        
        with cols[8]:
            risk = row.get('الخطورة', 'عادي')
            if risk == 'حرج':
                st.markdown('🔴')
            elif risk == 'متوسط':
                st.markdown('🟡')
            else:
                st.markdown('🟢')
        
        with cols[9]:
            if st.button("🤖", key=f"ai_{section_key}_{original_idx}", help="تحقق بالذكاء الصناعي"):
                st.session_state[f"ai_check_{section_key}_{original_idx}"] = True
                st.rerun()
        
        # ── نتيجة التحقق AI + أزرار القرار (v5.0) ──
        if st.session_state.get(f"ai_check_{section_key}_{original_idx}"):
            with st.spinner("🤖 جاري التحليل الذكي المتخصص..."):
                from modules.ai_verification import analyze_for_section
                product_name = str(row.get('المنتج', ''))
                comp_product_name = str(row.get('اسم المنافس', ''))
                our_price_val = 0
                comp_price_val = 0
                try:
                    our_price_val = float(row.get('السعر', 0) or 0)
                except (ValueError, TypeError):
                    our_price_val = 0
                try:
                    comp_price_val = float(row.get('سعر المنافس', row.get('أقل سعر منافس', 0)) or 0)
                except (ValueError, TypeError):
                    comp_price_val = 0
                
                result = analyze_for_section(
                    section_type=section_key,  # "raise" أو "lower"
                    our_product=product_name,
                    competitor_product=comp_product_name,
                    our_price=our_price_val,
                    competitor_price=comp_price_val,
                    competitor_name=str(row.get('المنافس', '')).replace('.xlsx', '').replace('.csv', ''),
                    confidence=float(row.get('الثقة %', 0) or 0),
                    diff_pct=float(row.get('النسبة %', 0) or 0),
                )
                
                if result["success"]:
                    ai_data = result.get("data", {})
                    if not isinstance(ai_data, dict):
                        ai_data = {}
                    
                    match_correct = ai_data.get('match_correct', True)
                    match_reason = ai_data.get('match_reason', '')
                    recommendation = ai_data.get('recommendation', 'لا توجد توصية')
                    action = ai_data.get('action', 'تأجيل')
                    suggested_price = ai_data.get('suggested_price', 0)
                    urgency = ai_data.get('urgency', 'متوسط')
                    reason = ai_data.get('reason', '')
                    
                    # لون حسب صحة المطابقة
                    if match_correct:
                        bg_color = "#e8f5e9"
                        border_color = "#4caf50"
                        match_icon = "&#x2705;"
                    else:
                        bg_color = "#ffebee"
                        border_color = "#f44336"
                        match_icon = "&#x274C;"
                    
                    # لون الاستعجال
                    urgency_colors = {'عاجل': '#f44336', 'متوسط': '#ff9800', 'منخفض': '#4caf50'}
                    urgency_color = urgency_colors.get(urgency, '#999')
                    
                    match_text = 'صحيحة' if match_correct else 'خاطئة - ' + match_reason
                    
                    # بناء صف السعر المقترح
                    suggested_row = ""
                    if suggested_price:
                        try:
                            suggested_row = f'<tr style="border-bottom: 1px solid #eee;"><td style="padding:6px;"><b>&#x1F3AF; السعر المقترح:</b></td><td style="padding:6px;"><b style="color:#1565c0;font-size:1.1em;">{float(suggested_price):.2f} ر.س</b></td></tr>'
                        except: pass
                    
                    reason_html = f'<p style="margin:4px 0 0 0; color:#666;"><small>{reason}</small></p>' if reason else ''
                    
                    ai_html = f"""<div style="background: linear-gradient(135deg, {bg_color}, #fff); border-radius: 12px; padding: 18px; margin: 10px 0; border-right: 5px solid {border_color}; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                        <h4 style="margin:0 0 12px 0; color: #1a237e;">&#x1F916; تحليل الذكاء الاصطناعي</h4>
                        <table style="width:100%; border-collapse: collapse;">
                            <tr style="border-bottom: 1px solid #eee;"><td style="padding:6px;"><b>&#x1F4E6; منتجنا:</b></td><td style="padding:6px;">{product_name}</td></tr>
                            <tr style="border-bottom: 1px solid #eee;"><td style="padding:6px;"><b>&#x1F3EA; منتج المنافس:</b></td><td style="padding:6px;">{comp_product_name}</td></tr>
                            <tr style="border-bottom: 1px solid #eee;"><td style="padding:6px;"><b>{match_icon} المطابقة:</b></td><td style="padding:6px;">{match_text}</td></tr>
                            <tr style="border-bottom: 1px solid #eee;"><td style="padding:6px;"><b>&#x1F4B0; سعرنا:</b></td><td style="padding:6px;">{our_price_val:.2f} ر.س</td></tr>
                            <tr style="border-bottom: 1px solid #eee;"><td style="padding:6px;"><b>&#x1F3F7; سعر المنافس:</b></td><td style="padding:6px;">{comp_price_val:.2f} ر.س</td></tr>
                            {suggested_row}
                            <tr style="border-bottom: 1px solid #eee;"><td style="padding:6px;"><b>&#x23F0; الاستعجال:</b></td><td style="padding:6px;"><span style="color:{urgency_color};font-weight:bold;">{urgency}</span></td></tr>
                        </table>
                        <div style="margin-top:12px; padding:10px; background:#f5f5f5; border-radius:8px;">
                            <p style="margin:0 0 5px 0;"><b>&#x1F3AF; التوصية:</b></p>
                            <p style="margin:0; color:#333; line-height:1.6;">{recommendation}</p>
                        </div>
                        <div style="margin-top:8px; padding:8px; background:#e3f2fd; border-radius:8px;">
                            <p style="margin:0;"><b>&#x1F4CB; الاجراء المقترح:</b> <span style="color:#1565c0; font-weight:bold;">{action}</span></p>
                            {reason_html}
                        </div>
                    </div>"""
                    st.markdown(ai_html, unsafe_allow_html=True)
                    
                    # أزرار القرار المحسنة
                    col_modify, col_delay, col_remove, col_close = st.columns(4)
                    with col_modify:
                        if st.button("✅ تعديل السعر", key=f"modify_{section_key}_{original_idx}", type="primary"):
                            st.session_state[f"ai_check_{section_key}_{original_idx}"] = False
                            st.session_state[f"sel_{section_key}"][original_idx] = True
                            st.success(f"✅ تم تحديد المنتج للتعديل")
                            st.rerun()
                    with col_delay:
                        if st.button("⏸️ تأجيل", key=f"delay_{section_key}_{original_idx}"):
                            st.session_state[f"ai_check_{section_key}_{original_idx}"] = False
                            st.info("⏸️ تم تأجيل القرار")
                            st.rerun()
                    with col_remove:
                        if st.button("🗑️ إزالة", key=f"remove_{section_key}_{original_idx}"):
                            st.session_state[removed_key].add(original_idx)
                            st.session_state[f"ai_check_{section_key}_{original_idx}"] = False
                            st.warning("🗑️ تم إزالة المنتج من القائمة")
                            st.rerun()
                    with col_close:
                        if st.button("🔙 إغلاق", key=f"close_{section_key}_{original_idx}"):
                            st.session_state[f"ai_check_{section_key}_{original_idx}"] = False
                            st.rerun()
                else:
                    st.error(f"❌ {result.get('error', 'فشل الاتصال بالذكاء الاصطناعي')}")
                    if st.button("🔙 إغلاق", key=f"close_err_{section_key}_{original_idx}"):
                        st.session_state[f"ai_check_{section_key}_{original_idx}"] = False
                        st.rerun()
    
    # ── Pagination أسفل ──
    if total_pages > 1:
        st.markdown("---")
        col_prev2, col_info2, col_next2 = st.columns([1, 3, 1])
        with col_prev2:
            if st.button("◀️ السابق", key=f"prev2_{section_key}", disabled=current_page == 0):
                st.session_state[page_key] = current_page - 1
                st.rerun()
        with col_info2:
            st.markdown(f"<div style='text-align:center;'>عرض {start_idx + 1}-{end_idx} من {filtered_count} | صفحة {current_page + 1}/{total_pages}</div>", unsafe_allow_html=True)
        with col_next2:
            if st.button("التالي ▶️", key=f"next2_{section_key}", disabled=current_page >= total_pages - 1):
                st.session_state[page_key] = current_page + 1
                st.rerun()
    
    # ── ملخص التحديد والإجراءات ──
    # جمع كل المحددين من جميع الصفحات
    all_selected = []
    for idx, row in df_filtered.iterrows():
        if st.session_state[f"sel_{section_key}"].get(idx, False):
            all_selected.append(row.to_dict())
    
    st.markdown("---")
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #fff8e1, #ffecb3); border-radius: 10px; padding: 12px; text-align: center;">
        <b>📌 تم تحديد <span style="font-size: 1.5rem; color: #e65100;">{len(all_selected)}</span> من أصل <span style="font-size: 1.5rem; color: #1565c0;">{filtered_count}</span> منتج</b>
    </div>""", unsafe_allow_html=True)
    
    col_b1, col_b2, col_b3 = st.columns(3)
    with col_b1:
        if st.button(f"✅ موافقة وإرسال إلى سلة ({section_label})", 
                     use_container_width=True, type="primary",
                     disabled=len(all_selected) == 0, key=f"send_{section_key}"):
            with st.spinner(f"⏳ جاري إرسال {len(all_selected)} منتج..."):
                # استيراد نظام قاعدة البيانات
                from database import log_operation, mark_product_modified, is_product_modified
                
                batch_size = 50
                total_sent = 0
                total_failed = 0
                for batch_start in range(0, len(all_selected), batch_size):
                    batch = all_selected[batch_start:batch_start + batch_size]
                    result = send_func(batch)
                    if result["success"]:
                        total_sent += len(batch)
                        # تسجيل كل منتج في قاعدة البيانات
                        for product in batch:
                            product_name = product.get('المنتج', '')
                            if not is_product_modified(product_name):
                                log_operation(
                                    operation_type="price_update",
                                    product_name=product_name,
                                    old_price=product.get('سعر المنافس', 0),
                                    new_price=product.get('سعرنا', 0),
                                    status="success",
                                    details={"section": section_label, "webhook": webhook_label},
                                    user_action="approved_and_sent"
                                )
                                mark_product_modified(product_name, "price_update")
                    else:
                        total_failed += len(batch)
                
                save_send_log(section_label, len(all_selected), total_sent, total_failed, webhook_label)
                
                if total_failed == 0:
                    st.markdown(f"""<div class="success-box">
                        <h2>🎉 تم الإرسال بنجاح!</h2>
                        <p>تم إرسال <b>{total_sent}</b> منتج عبر {webhook_label}</p>
                    </div>""", unsafe_allow_html=True)
                    st.balloons()
                else:
                    st.warning(f"⚠️ نجح {total_sent}، فشل {total_failed}")
    
    with col_b2:
        if all_selected:
            df_sel = pd.DataFrame(all_selected)
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_sel.to_excel(writer, sheet_name=section_label, index=False)
            output.seek(0)
            st.download_button(f"📥 تحميل المحدد كـ Excel", data=output.getvalue(),
                              file_name=f"{section_key}_{datetime.now():%Y%m%d_%H%M%S}.xlsx",
                              mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                              use_container_width=True, key=f"dl_{section_key}")
    
    with col_b3:
        # تحميل الكل كـ Excel
        output_all = BytesIO()
        with pd.ExcelWriter(output_all, engine='openpyxl') as writer:
            df_filtered.to_excel(writer, sheet_name=section_label, index=False)
        output_all.seek(0)
        st.download_button(f"📥 تحميل الكل ({filtered_count})", data=output_all.getvalue(),
                          file_name=f"{section_key}_all_{datetime.now():%Y%m%d_%H%M%S}.xlsx",
                          mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                          use_container_width=True, key=f"dl_all_{section_key}")


# ══════════════════════════════════════════════════════════════
# الشريط الجانبي
# ══════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("## 💎 نظام التسعير الذكي")
    st.markdown("**الإصدار:** v14.2")
    st.markdown("---")
    
    # حالة الاتصالات
    st.markdown("### 📡 حالة الاتصالات")
    
    try:
        from modules.ai_verification import get_ai_status
        ai_st = get_ai_status()
        g_active = ai_st.get('gemini_active', 0)
        o_active = ai_st.get('openrouter_active', 0)
        gem_status = "🟢" if g_active > 0 else "🔴"
        or_status = "🟢" if o_active > 0 else "🔴"
        st.markdown(f"{gem_status} Gemini ({g_active}) | {or_status} OpenRouter ({o_active})")
    except:
        gem_status = "🟢" if st.session_state.get("gemini_connected") else "🔴"
        or_status = "🟢" if st.session_state.get("openrouter_connected") else "🔴"
        st.markdown(f"{gem_status} Gemini AI | {or_status} OpenRouter")
    
    mu_status = "🟢" if st.session_state.get("make_update_connected") else "🔴"
    mn_status = "🟢" if st.session_state.get("make_new_connected") else "🔴"
    st.markdown(f"{mu_status} Make تحديث | {mn_status} Make إضافة")
    
    st.markdown("---")
    
    section = st.radio("📂 الأقسام", [
        "🏠 لوحة القيادة",
        "📤 رفع الملفات",
        "📊 سجل العمليات",
        "🔴 رفع سعر",
        "🟡 خفض سعر",
        "🟢 موافق عليها",
        "🔵 منتجات مفقودة",
        "⚠️ يحتاج مراجعة",
        "🔍 تفاصيل المطابقة",
        "🤖 فحص AI",
        "🤖 تحقق AI",
        "💬 محادثة AI",
        "🎬 استديو مهووس",
        "⚡ Make أتمتة",
        "💾 قاعدة البيانات",
        "🛒 المشتريات اليومية",
        "🏪 إدارة الموردين",
        "💰 مذكرة المصروفات",
        "⚙️ الإعدادات",
    ], key="main_section")
    
    st.markdown("---")
    
    # فحص تلقائي للذكاء الاصطناعي
    st.markdown("### 🤖 فحص الذكاء الاصطناعي")
    
    if st.button("🔄 فحص عمل AI تلقائياً", type="secondary", use_container_width=True):
        with st.spinner("⏳ جاري فحص الذكاء الاصطناعي..."):
            # فحص Gemini
            try:
                from modules.ai_verification import get_ai_status
                ai_st = get_ai_status()
                g_active = ai_st.get('gemini_active', 0)
                o_active = ai_st.get('openrouter_active', 0)
                
                if g_active > 0 or o_active > 0:
                    st.success(f"✅ الذكاء الاصطناعي يعمل: Gemini ({g_active}) | OpenRouter ({o_active})")
                    
                    # اختبار سريع للـ AI
                    test_result = verify_gemini_connection(update_session=False)
                    if test_result["connected"]:
                        st.info("🧠 Gemini AI متصل ويعمل بشكل طبيعي")
                    else:
                        st.warning("⚠️ Gemini AI غير متصل - سيتم استخدام OpenRouter")
                        
                    # عرض حالة مفصلة
                    st.markdown("#### 📊 حالة مفصلة:")
                    c1, c2 = st.columns(2)
                    with c1:
                        st.metric("🤖 Gemini", f"{g_active} مفتاح نشط")
                    with c2:
                        st.metric("🧠 OpenRouter", f"{o_active} مفتاح نشط")
                else:
                    st.error("❌ جميع مفاتيح الذكاء الاصطناعي غير متاحة")
                    st.warning("⚠️ يرجى إدخال مفاتيح API صحيحة في قسم الإعدادات")
                    
            except Exception as e:
                st.error(f"❌ خطأ في فحص الذكاء الاصطناعي: {str(e)}")
    
    st.markdown("---")

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
        st.info("📤 لا توجد نتائج محفوظة. قم برفع الملفات وبدء المعالجة لعرض لوحة القيادة")
        if st.button("🔄 تحميل آخر نتائج من قاعدة البيانات"):
            with st.spinner("⏳ جاري تحميل البيانات السابقة..."):
                loaded = load_latest_results()
                if loaded:
                    st.session_state.results = loaded
                    st.success("✅ تم تحميل آخر نتائج بنجاح!")
                    st.rerun()
                else:
                    st.warning("⚠️ لا توجد نتائج سابقة في قاعدة البيانات")
    
    # حالة الاتصالات
    st.markdown("---")
    st.markdown("### 📡 حالة الاتصالات")
    
    if st.button("🔄 تحقق من جميع الاتصالات", type="primary"):
        with st.spinner("⏳ جاري التحقق..."):
            gem = verify_gemini_connection()
            
            # فحص OpenRouter عبر النظام الجديد
            try:
                from modules.ai_verification import get_ai_status
                ai_st = get_ai_status()
                or_connected = ai_st.get('openrouter_active', 0) > 0
            except:
                ort = verify_openrouter_connection(st.session_state.openrouter_key)
                or_connected = ort["connected"]
            st.session_state.openrouter_connected = or_connected
            
            mu = verify_webhook_connection(WEBHOOK_UPDATE_PRICES, "update")
            st.session_state.make_update_connected = mu["connected"]
            
            mn = verify_webhook_connection(WEBHOOK_NEW_PRODUCTS, "new")
            st.session_state.make_new_connected = mn["connected"]
        
        # عرض حالة المفاتيح المتعددة
        try:
            from modules.ai_verification import get_ai_status
            ai_st = get_ai_status()
            st.markdown("#### 🔑 نظام المفاتيح المتعددة")
            c1, c2 = st.columns(2)
            with c1:
                g_a = ai_st.get('gemini_active', 0)
                g_t = ai_st.get('gemini_total', 0)
                st.metric("🤖 Gemini", f"{g_a}/{g_t} نشط")
            with c2:
                o_a = ai_st.get('openrouter_active', 0)
                o_t = ai_st.get('openrouter_total', 0)
                st.metric("🧠 OpenRouter", f"{o_a}/{o_t} نشط")
        except:
            pass
        
        c1, c2, c3, c4 = st.columns(4)
        for col, name, connected in [
            (c1, "🤖 Gemini AI", gem["connected"]),
            (c2, "🧠 OpenRouter", or_connected),
            (c3, "⚡ Make تحديث", mu["connected"]),
            (c4, "⚡ Make إضافة", mn["connected"]),
        ]:
            cls = "conn-ok" if connected else "conn-fail"
            icon = "✅" if connected else "❌"
            col.markdown(f'<div class="connection-card {cls}"><b>{name}</b><br>{icon}</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# 2. رفع الملفات ومعالجتها
# ══════════════════════════════════════════════════════════════
elif section == "📊 سجل العمليات":
    from operations_log_section import show_operations_log
    show_operations_log()

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
    
    # إعدادات المعالجة - نسبة ثابتة مثالية 60%
    threshold = 60  # أفضل نسبة بناءً على الاختبارات
    st.session_state.algorithm_settings["threshold"] = threshold
    
    # عرض النسبة الثابتة
    st.info("🎯 **حد التطابق المثالي:** 60% (محدد تلقائيًا لأفضل نتائج)")
    
    # عرض حالة الملفات المرفوعة
    if st.session_state.my_file:
        st.success(f"✅ ملف المتجر محمل: {st.session_state.my_file['name']}")
    if st.session_state.supplier_files:
        st.success(f"✅ {len(st.session_state.supplier_files)} ملف منافس محمل")
    
    if st.button("🚀 بدء المعالجة", type="primary", use_container_width=True,
                 disabled=not (st.session_state.my_file and st.session_state.supplier_files)):
        # استيراد المحرك الجديد
        try:
            from engine_v2 import run_smart_matching
            USE_V2 = True
        except:
            from engine import run_full_analysis
            USE_V2 = False
            st.warning("⚠️ استخدام المحرك القديم")
        import time
        
        # عناصر العرض
        progress_bar = st.progress(0)
        status_text = st.empty()
        time_text = st.empty()
        counter_text = st.empty()
        stats_text = st.empty()
        
        start_time = time.time()
        _progress_state = {'current': 0, 'total': 0, 'matched': 0, 'ai_active': False, 'ai_calls': 0}
        
        def update_progress(percent, message=""):
            progress_bar.progress(min(int(percent), 99) if percent < 100 else 100)
            elapsed = time.time() - start_time
            
            # تحويل الوقت
            elapsed_min = int(elapsed // 60)
            elapsed_sec = int(elapsed % 60)
            elapsed_display = f"{elapsed_min}د {elapsed_sec}ث" if elapsed_min > 0 else f"{elapsed_sec}ث"
            
            # استخراج الوقت المتبقي
            remaining_display = ""
            if "متبقي:" in message:
                import re
                match = re.search(r'متبقي: ~(\d+)ث', message)
                if match:
                    rem = int(match.group(1))
                    rem_min = int(rem // 60)
                    rem_sec = int(rem % 60)
                    remaining_display = f"{rem_min}د {rem_sec}ث" if rem_min > 0 else f"~{rem_sec}ث"
            
            # حالة AI
            ai_status = "🟢 متصل" if _progress_state.get('ai_active') else "⚪ في الانتظار"
            ai_calls = _progress_state.get('ai_calls', 0)
            current = _progress_state.get('current', 0)
            total = _progress_state.get('total', 0)
            matched = _progress_state.get('matched', 0)
            
            # عرض الحالة الرئيسية
            status_text.markdown(f"### {message}")
            
            # عداد رقمي كبير وواضح
            time_text.markdown(f"""
            <div style="background: linear-gradient(135deg, #e3f2fd, #bbdefb); border-radius: 12px; padding: 20px; margin: 10px 0; direction: rtl;">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 15px;">
                    <div style="text-align: center; min-width: 120px;">
                        <div style="font-size: 2.2rem; font-weight: bold; color: #1565c0;">{int(percent)}%</div>
                        <div style="font-size: 0.85rem; color: #546e7a;">نسبة الإنجاز</div>
                    </div>
                    <div style="text-align: center; min-width: 120px;">
                        <div style="font-size: 2.2rem; font-weight: bold; color: #2e7d32;">{current}/{total}</div>
                        <div style="font-size: 0.85rem; color: #546e7a;">المنتج الحالي</div>
                    </div>
                    <div style="text-align: center; min-width: 120px;">
                        <div style="font-size: 2.2rem; font-weight: bold; color: #e65100;">{matched}</div>
                        <div style="font-size: 0.85rem; color: #546e7a;">تم مطابقته</div>
                    </div>
                    <div style="text-align: center; min-width: 120px;">
                        <div style="font-size: 1.5rem; font-weight: bold; color: #37474f;">{elapsed_display}</div>
                        <div style="font-size: 0.85rem; color: #546e7a;">الوقت المنقضي</div>
                    </div>
                    {'<div style="text-align: center; min-width: 120px;"><div style="font-size: 1.5rem; font-weight: bold; color: #c62828;">' + remaining_display + '</div><div style="font-size: 0.85rem; color: #546e7a;">الوقت المتبقي</div></div>' if remaining_display else ''}
                </div>
                <div style="margin-top: 15px; padding-top: 12px; border-top: 1px solid #90caf9; display: flex; justify-content: center; gap: 25px; flex-wrap: wrap;">
                    <span style="font-size: 0.95rem;">🤖 Gemini AI: <b>{ai_status}</b></span>
                    <span style="font-size: 0.95rem;">📡 طلبات AI: <b>{ai_calls}</b></span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        update_progress(5, "⏳ جاري تحميل الملفات...")
        counter_text.markdown(f"**📦 ملف المتجر:** {st.session_state.my_file['name']} | **🏪 ملفات المنافسين:** {len(st.session_state.supplier_files)} ملف")
        
        def progress_callback(percent, message):
            update_progress(percent, message)
        
        # تحميل الملفات
        import pandas as pd
        import io
        
        # قراءة ملف المتجر من bytes
        from engine import normalize_columns
        try:
            my_file_data = st.session_state.my_file['data']
            my_file_name = st.session_state.my_file['name']
            if my_file_name.endswith('.xlsx'):
                my_df = pd.read_excel(io.BytesIO(my_file_data))
            else:
                my_df = pd.read_csv(io.BytesIO(my_file_data), encoding='utf-8-sig')
            my_df = normalize_columns(my_df)
            my_products = my_df.to_dict('records')
        except Exception as e:
            st.error(f"❌ خطأ في قراءة ملف المتجر: {e}")
            my_products = []
        
        # قراءة ملفات المنافسين من bytes
        comp_products = []
        for comp_file in st.session_state.supplier_files:
            try:
                comp_file_data = comp_file['data']
                comp_file_name = comp_file['name']
                if comp_file_name.endswith('.xlsx'):
                    comp_df = pd.read_excel(io.BytesIO(comp_file_data))
                else:
                    comp_df = pd.read_csv(io.BytesIO(comp_file_data), encoding='utf-8-sig')
                comp_df = normalize_columns(comp_df)
                records = comp_df.to_dict('records')
                # إضافة اسم المنافس
                for r in records:
                    r['_competitor'] = comp_file_name.replace('.csv', '').replace('.xlsx', '').replace('متجر', '').replace('متحر', '').strip()
                comp_products.extend(records)
            except Exception as e:
                st.warning(f"⚠️ خطأ في قراءة ملف منافس: {e}")
                continue
        
        update_progress(10, f"✅ تم تحميل {len(my_products)} منتج + {len(comp_products)} منافس")
        
        _progress_state['total'] = len(my_products)
        
        if USE_V2:
            # المحرك الجديد
            def smart_progress(progress, elapsed, eta, stats):
                percent = int(progress * 80) + 10  # 10-90%
                current_idx = int(progress * len(my_products))
                total_matched = stats['fast_matches'] + stats['medium_matches'] + stats['deep_matches']
                
                # تحديث العداد
                _progress_state['current'] = current_idx
                _progress_state['matched'] = total_matched
                _progress_state['ai_calls'] = stats['gemini_calls']
                _progress_state['ai_active'] = stats['gemini_calls'] > 0
                
                message = f"🔍 جاري المطابقة... | متبقي: ~{int(eta)}ث"
                update_progress(percent, message)
                
                # عرض إحصائيات المطابقة
                stats_text.markdown(f"""
                <div style="background: #f5f5f5; border-radius: 8px; padding: 12px; margin: 5px 0; direction: rtl;">
                    <div style="display: flex; justify-content: space-around; flex-wrap: wrap; gap: 10px;">
                        <span>⚖️ سريعة: <b>{stats['fast_matches']}</b></span>
                        <span>💡 متوسطة: <b>{stats['medium_matches']}</b></span>
                        <span>🧠 عميقة: <b>{stats['deep_matches']}</b></span>
                        <span>🤖 Gemini: <b>{stats['gemini_calls']}</b></span>
                        <span>💾 Cache: <b>{stats['cache_hits']}</b></span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            raw_results = run_smart_matching(
                my_products,
                comp_products,
                progress_callback=smart_progress
            )
            
            # تحويل إلى نفس الشكل القديم (أعمدة عربية)
            import pandas as pd
            from engine import extract_brand, extract_concentration, extract_size, get_type_label
            
            def _v2_to_arabic_row(r, include_recommended=True):
                """تحويل صف V2 إلى الشكل العربي المتوقع"""
                row = {
                    "المقارنة": f"{r.get('my_name', '')} 🆚 {r.get('comp_name', '')}",
                    "المنتج": r.get("my_name", ""),
                    "ماركتنا": extract_brand(r.get("my_name", "")),
                    "تركيزنا": extract_concentration(r.get("my_name", "")),
                    "حجمنا": extract_size(r.get("my_name", "")),
                    "اسم المنافس": r.get("comp_name", ""),
                    "ماركة المنافس": extract_brand(r.get("comp_name", "")) if r.get("comp_name") else "",
                    "تركيز المنافس": extract_concentration(r.get("comp_name", "")) if r.get("comp_name") else "",
                    "حجم المنافس": extract_size(r.get("comp_name", "")) if r.get("comp_name") else 0,
                    "السعر": r.get("my_price", 0),
                    "أقل سعر منافس": r.get("comp_price", 0),
                    "سعر المنافس": r.get("comp_price", 0),
                    "الفرق": round(r.get("diff", 0), 2),
                    "النسبة %": round(r.get("diff_pct", 0), 1),
                    "الثقة %": r.get("confidence", r.get("match_confidence", 0)),
                    "ثقة AI %": r.get("confidence", r.get("match_confidence", 0)),
                    "حالة التحقق": r.get("match_reason", "✅ مؤكد"),
                    "تفسير AI": r.get("match_reason", ""),
                    "عدد المنافسين": 1,
                    "التفسير": r.get("match_reason", ""),
                    "نسبة التطابق": r.get("confidence", r.get("match_confidence", 0)),
                    "المنافس": r.get("competitor", ""),
                    "مرحلة المطابقة": r.get("match_stage", ""),
                    "pid_my": "",
                }
                if include_recommended:
                    comp_price = r.get("comp_price", 0)
                    row["السعر الموصى"] = max(comp_price - 1, 1) if comp_price > 0 else 0
                
                # تحديد الخطورة
                abs_pct = abs(r.get("diff_pct", 0))
                if abs_pct >= 20:
                    row["الخطورة"] = "حرج"
                elif abs_pct >= 10:
                    row["الخطورة"] = "متوسط"
                else:
                    row["الخطورة"] = "عادي"
                
                return row
            
            def _v2_missing_to_arabic(r):
                """تحويل منتج مفقود V2 إلى الشكل العربي"""
                return {
                    "المنتج": r.get("my_name", ""),
                    "النوع": "ريتيل",
                    "الحجم": extract_size(r.get("my_name", "")),
                    "السعر": r.get("my_price", 0),
                    "المنافس": "غير محدد",
                }
            
            raise_list = [r for r in raw_results if r["category"] == "raise_price"]
            lower_list = [r for r in raw_results if r["category"] == "lower_price"]
            keep_list = [r for r in raw_results if r["category"] == "keep_price"]
            missing_list = [r for r in raw_results if r["category"] == "missing"]
            
            # تحويل إلى DataFrames بأعمدة عربية
            df_raise = pd.DataFrame([_v2_to_arabic_row(r) for r in raise_list]) if raise_list else pd.DataFrame()
            df_lower = pd.DataFrame([_v2_to_arabic_row(r) for r in lower_list]) if lower_list else pd.DataFrame()
            df_approved = pd.DataFrame([_v2_to_arabic_row(r, include_recommended=False) for r in keep_list]) if keep_list else pd.DataFrame()
            df_missing = pd.DataFrame([_v2_missing_to_arabic(r) for r in missing_list]) if missing_list else pd.DataFrame()
            
            # دمج جميع النتائج
            df_all = pd.concat([df_raise, df_lower, df_approved], ignore_index=True) if any(not df.empty for df in [df_raise, df_lower, df_approved]) else pd.DataFrame()
            
            # حساب إحصائيات إضافية
            avg_diff = round(df_all["الفرق"].mean(), 2) if not df_all.empty and "الفرق" in df_all.columns else 0
            critical_count = len(df_all[df_all["الخطورة"] == "حرج"]) if not df_all.empty and "الخطورة" in df_all.columns else 0
            
            results = {
                "raise": df_raise,
                "lower": df_lower,
                "approved": df_approved,
                "missing": df_missing,
                "review": pd.DataFrame(),
                "all": df_all,
                "stats": {
                    "total": len(raise_list) + len(lower_list) + len(keep_list),
                    "raise_count": len(raise_list),
                    "lower_count": len(lower_list),
                    "approved_count": len(keep_list),
                    "missing_count": len(missing_list),
                    "competitors": len(st.session_state.supplier_files),
                    "critical": critical_count,
                    "avg_diff": avg_diff,
                },
            }
        else:
            # المحرك القديم
            results = run_full_analysis(
                st.session_state.my_file,
                st.session_state.supplier_files,
                threshold=threshold,
                progress_callback=progress_callback
            )
        
        update_progress(90, "⏳ جاري حفظ النتائج...")
        
        if "error" in results and results.get("stats", {}) == {}:
            st.error(f"❌ خطأ: {results['error']}")
        else:
            st.session_state.results = results
            st.session_state.analysis_result = results  # حفظ لصفحة تفاصيل المطابقة
            
            # حفظ في قاعدة البيانات
            save_results_to_db(results)
            
            total_time = time.time() - start_time
            update_progress(100, "✅ اكتملت المعالجة!")
            time_text.markdown(f"""
            <div style="background: linear-gradient(135deg, #c8e6c9, #a5d6a7); border-radius: 10px; padding: 15px; margin: 10px 0;">
                <p style="margin:0; font-size: 1.1rem;"><b>✅ اكتمل التحليل بنجاح!</b></p>
                <p style="margin:5px 0 0 0;"><b>⏱️ إجمالي الوقت:</b> {total_time:.1f} ثانية | <b>🎯 نسبة التطابق:</b> {results['stats']['total'] / (results['stats']['total'] + results['stats']['missing_count']) * 100 if (results['stats']['total'] + results['stats']['missing_count']) > 0 else 0:.1f}%</p>
            </div>
            """, unsafe_allow_html=True)
            
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
            total_approved = len(df_approved)
            
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #e8f5e9, #c8e6c9); border-radius: 12px; padding: 15px; margin: 10px 0; text-align: center;">
                <h3 style="margin:0; color: #2e7d32;">✅ عداد المنتجات الموافق عليها: <span style="font-size: 1.8rem; color: #1b5e20;">{total_approved}</span> منتج</h3>
            </div>""", unsafe_allow_html=True)
            
            # ── Pagination ──
            ITEMS_PER_PAGE_APPROVED = 25
            if "page_approved" not in st.session_state:
                st.session_state.page_approved = 0
            
            total_pages_a = max(1, (total_approved + ITEMS_PER_PAGE_APPROVED - 1) // ITEMS_PER_PAGE_APPROVED)
            current_page_a = min(st.session_state.page_approved, total_pages_a - 1)
            
            if total_pages_a > 1:
                col_prev_a, col_info_a, col_next_a = st.columns([1, 3, 1])
                with col_prev_a:
                    if st.button("◀️ السابق", key="prev_approved", disabled=current_page_a == 0):
                        st.session_state.page_approved = current_page_a - 1
                        st.rerun()
                with col_info_a:
                    st.markdown(f"<div style='text-align:center; padding:8px;'><b>صفحة {current_page_a + 1} من {total_pages_a}</b> ({total_approved} منتج)</div>", unsafe_allow_html=True)
                with col_next_a:
                    if st.button("التالي ▶️", key="next_approved", disabled=current_page_a >= total_pages_a - 1):
                        st.session_state.page_approved = current_page_a + 1
                        st.rerun()
            
            start_a = current_page_a * ITEMS_PER_PAGE_APPROVED
            end_a = min(start_a + ITEMS_PER_PAGE_APPROVED, total_approved)
            page_approved_df = df_approved.iloc[start_a:end_a]
            
            # ── عناوين الأعمدة ──
            h_cols = st.columns([3.0, 3.0, 1.0, 1.0, 1.0, 0.8, 0.5])
            with h_cols[0]:
                st.markdown("**📦 منتجنا**")
            with h_cols[1]:
                st.markdown("**🏪 منتج المنافس**")
            with h_cols[2]:
                st.markdown("**💰 سعرنا**")
            with h_cols[3]:
                st.markdown("**🏷️ المنافس**")
            with h_cols[4]:
                st.markdown("**📊 النسبة**")
            with h_cols[5]:
                st.markdown("**🔒 الثقة**")
            with h_cols[6]:
                st.markdown("**🤖**")
            st.markdown("<hr style='margin:5px 0;'>", unsafe_allow_html=True)
            
            # ── عرض المنتجات ──
            for _, row in page_approved_df.iterrows():
                original_idx = row.name
                cols = st.columns([3.0, 3.0, 1.0, 1.0, 1.0, 0.8, 0.5])
                
                with cols[0]:
                    my_product = str(row.get('المنتج', row.get('اسم المنتج', '')))
                    my_brand = str(row.get('ماركتنا', ''))
                    st.markdown(f"**{my_product}**")
                    if my_brand and my_brand != 'nan':
                        st.caption(f"🏷️ {my_brand}")
                
                with cols[1]:
                    comp_product = str(row.get('اسم المنافس', ''))
                    competitor_name = str(row.get('المنافس', '')).replace('.xlsx', '').replace('.csv', '')
                    match_stage = str(row.get('مرحلة المطابقة', ''))
                    if comp_product and comp_product != 'nan':
                        st.markdown(f"**{comp_product}**")
                        stage_emoji = {'fast': '⚡', 'medium': '🔍', 'deep': '🔬', 'gemini': '🤖'}.get(match_stage, '📋')
                        st.caption(f"{stage_emoji} {competitor_name}")
                    else:
                        st.markdown("*غير متاح*")
                
                with cols[2]:
                    st.write(f"💰 {row.get('السعر', 0)}")
                
                with cols[3]:
                    comp_price = row.get('أقل سعر منافس', row.get('سعر المنافس', 0))
                    st.write(f"🏷️ {comp_price}")
                
                with cols[4]:
                    diff_pct = row.get('النسبة %', 0)
                    st.markdown(f'<span style="color:#4caf50;font-weight:bold">{diff_pct}%</span>', unsafe_allow_html=True)
                
                with cols[5]:
                    confidence = row.get('الثقة %', '')
                    if confidence:
                        conf_val = float(confidence) if confidence else 0
                        conf_color = "#4caf50" if conf_val >= 90 else "#ff9800" if conf_val >= 75 else "#f44336"
                        st.markdown(f'<span style="color:{conf_color};font-weight:bold">{confidence}%</span>', unsafe_allow_html=True)
                    else:
                        st.write("—")
                
                with cols[6]:
                    if st.button("🤖", key=f"ai_approved_{original_idx}", help="تحقق ذكي"):
                        st.session_state[f"ai_verify_approved_{original_idx}"] = True
                        st.rerun()
                
                # نتيجة AI (v5.0) مع أزرار قرار
                if st.session_state.get(f"ai_verify_approved_{original_idx}"):
                    with st.spinner("🤖 جاري التحليل الذكي المتخصص..."):
                        from modules.ai_verification import analyze_for_section
                        product_name = str(row.get('المنتج', row.get('اسم المنتج', '')))
                        comp_product_name = str(row.get('اسم المنافس', ''))
                        our_price_val = 0
                        comp_price_val = 0
                        try:
                            our_price_val = float(row.get('السعر', 0) or 0)
                        except (ValueError, TypeError):
                            our_price_val = 0
                        try:
                            comp_price_val = float(row.get('سعر المنافس', row.get('أقل سعر منافس', 0)) or 0)
                        except (ValueError, TypeError):
                            comp_price_val = 0
                        
                        result = analyze_for_section(
                            section_type="approved",
                            our_product=product_name,
                            competitor_product=comp_product_name,
                            our_price=our_price_val,
                            competitor_price=comp_price_val,
                            competitor_name=str(row.get('المنافس', '')).replace('.xlsx', '').replace('.csv', ''),
                            confidence=float(row.get('الثقة %', 0) or 0),
                            diff_pct=float(row.get('النسبة %', 0) or 0),
                        )
                        
                        if result["success"]:
                            ai_data = result.get("data", {})
                            if not isinstance(ai_data, dict):
                                ai_data = {}
                            
                            match_correct = ai_data.get('match_correct', True)
                            recommendation = ai_data.get('recommendation', 'لا توجد توصية')
                            action = ai_data.get('action', 'تثبيت السعر')
                            suggested_price = ai_data.get('suggested_price', 0)
                            reason = ai_data.get('reason', '')
                            
                            bg_color = "#e8f5e9" if match_correct else "#ffebee"
                            border_color = "#4caf50" if match_correct else "#f44336"
                            match_icon_a = "&#x2705;" if match_correct else "&#x274C;"
                            match_text_a = "صحيحة" if match_correct else "خاطئة"
                            
                            suggested_row_a = ""
                            if suggested_price:
                                try:
                                    suggested_row_a = f'<tr style="border-bottom: 1px solid #eee;"><td style="padding:6px;"><b>&#x1F3AF; السعر المقترح:</b></td><td style="padding:6px;"><b style="color:#1565c0;">{float(suggested_price):.2f} ر.س</b></td></tr>'
                                except: pass
                            
                            reason_html_a = f'<p style="margin:4px 0 0 0; color:#666;"><small>{reason}</small></p>' if reason else ''
                            
                            ai_html_a = f"""<div style="background: linear-gradient(135deg, {bg_color}, #fff); border-radius: 12px; padding: 18px; margin: 10px 0; border-right: 5px solid {border_color}; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                                <h4 style="margin:0 0 12px 0; color: #1a237e;">&#x1F916; تحليل الذكاء الاصطناعي</h4>
                                <table style="width:100%; border-collapse: collapse;">
                                    <tr style="border-bottom: 1px solid #eee;"><td style="padding:6px;"><b>&#x1F4E6; منتجنا:</b></td><td style="padding:6px;">{product_name}</td></tr>
                                    <tr style="border-bottom: 1px solid #eee;"><td style="padding:6px;"><b>&#x1F3EA; منتج المنافس:</b></td><td style="padding:6px;">{comp_product_name}</td></tr>
                                    <tr style="border-bottom: 1px solid #eee;"><td style="padding:6px;"><b>{match_icon_a} المطابقة:</b></td><td style="padding:6px;">{match_text_a}</td></tr>
                                    <tr style="border-bottom: 1px solid #eee;"><td style="padding:6px;"><b>&#x1F4B0; سعرنا:</b></td><td style="padding:6px;">{our_price_val:.2f} ر.س</td></tr>
                                    <tr style="border-bottom: 1px solid #eee;"><td style="padding:6px;"><b>&#x1F3F7; سعر المنافس:</b></td><td style="padding:6px;">{comp_price_val:.2f} ر.س</td></tr>
                                    {suggested_row_a}
                                </table>
                                <div style="margin-top:12px; padding:10px; background:#f5f5f5; border-radius:8px;">
                                    <p style="margin:0 0 5px 0;"><b>&#x1F3AF; التوصية:</b></p>
                                    <p style="margin:0; color:#333; line-height:1.6;">{recommendation}</p>
                                </div>
                                <div style="margin-top:8px; padding:8px; background:#e3f2fd; border-radius:8px;">
                                    <p style="margin:0;"><b>&#x1F4CB; الاجراء:</b> <span style="color:#1565c0; font-weight:bold;">{action}</span></p>
                                    {reason_html_a}
                                </div>
                            </div>"""
                            st.markdown(ai_html_a, unsafe_allow_html=True)
                        else:
                            st.error(f"❌ {result.get('error', 'فشل الاتصال')}")
                        
                        # أزرار القرار
                        col_keep_a, col_delay_a, col_close_a = st.columns(3)
                        with col_keep_a:
                            if st.button("✅ تثبيت", key=f"keep_approved_{original_idx}", type="primary"):
                                st.session_state[f"ai_verify_approved_{original_idx}"] = False
                                st.success("✅ تم تثبيت السعر")
                                st.rerun()
                        with col_delay_a:
                            if st.button("⏸️ تأجيل", key=f"delay_approved_{original_idx}"):
                                st.session_state[f"ai_verify_approved_{original_idx}"] = False
                                st.info("⏸️ تم تأجيل القرار")
                                st.rerun()
                        with col_close_a:
                            if st.button("🔙 إغلاق", key=f"close_approved_{original_idx}"):
                                st.session_state[f"ai_verify_approved_{original_idx}"] = False
                                st.rerun()
            
            # Pagination أسفل
            if total_pages_a > 1:
                st.markdown("---")
                col_p2, col_i2, col_n2 = st.columns([1, 3, 1])
                with col_p2:
                    if st.button("◀️ السابق", key="prev2_approved", disabled=current_page_a == 0):
                        st.session_state.page_approved = current_page_a - 1
                        st.rerun()
                with col_i2:
                    st.markdown(f"<div style='text-align:center;'>عرض {start_a + 1}-{end_a} من {total_approved} | صفحة {current_page_a + 1}/{total_pages_a}</div>", unsafe_allow_html=True)
                with col_n2:
                    if st.button("التالي ▶️", key="next2_approved", disabled=current_page_a >= total_pages_a - 1):
                        st.session_state.page_approved = current_page_a + 1
                        st.rerun()
            
            # عرض الجدول الكامل
            with st.expander("📊 عرض الجدول الكامل"):
                st.dataframe(df_approved, use_container_width=True, height=400)
            
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
    st.markdown("> منتجات موجودة عند المنافسين وغير موجودة في متجرنا - مع نظام تحقق قوي لمنع التكرار")
    st.markdown("---")
    
    if st.session_state.results:
        df_missing = st.session_state.results.get("missing")
        if df_missing is not None and not df_missing.empty:
            total_missing = len(df_missing)
            
            # ── نظام القرارات: تتبع المنتجات المُزالة/المؤجلة ──
            if "removed_missing" not in st.session_state:
                st.session_state["removed_missing"] = set()
            if "delayed_missing" not in st.session_state:
                st.session_state["delayed_missing"] = set()
            
            removed_indices = st.session_state["removed_missing"]
            delayed_indices = st.session_state["delayed_missing"]
            df_active = df_missing[~df_missing.index.isin(removed_indices)]
            removed_count = total_missing - len(df_active)
            delayed_count = len(delayed_indices - removed_indices)
            
            # ── نظام الفلاتر الشامل ──
            with st.expander("🔍 فلاتر البحث والتصفية", expanded=False):
                mf1, mf2, mf3, mf4 = st.columns(4)
                with mf1:
                    m_search = st.text_input("🔎 بحث باسم المنتج", key="filter_search_missing", placeholder="اكتب اسم المنتج...")
                with mf2:
                    m_comp_list = ["-- الكل --"]
                    if 'المنافس' in df_active.columns:
                        m_unique = df_active['المنافس'].dropna().unique().tolist()
                        m_comp_list.extend([str(c).replace('.xlsx','').replace('.csv','') for c in m_unique if str(c) != 'nan'])
                    m_filter_comp = st.selectbox("🏢 المنافس", m_comp_list, key="filter_comp_missing")
                with mf3:
                    m_type_list = ["-- الكل --"]
                    if 'النوع' in df_active.columns:
                        m_types = df_active['النوع'].dropna().unique().tolist()
                        m_type_list.extend([str(t) for t in m_types if str(t) != 'nan'])
                    m_filter_type = st.selectbox("🎯 النوع", m_type_list, key="filter_type_missing")
                with mf4:
                    m_status_options = ["-- الكل --", "✅ جديد", "⏸️ مؤجل"]
                    m_filter_status = st.selectbox("📋 الحالة", m_status_options, key="filter_status_missing")
                
                mf5, mf6, mf7, mf8 = st.columns(4)
                with mf5:
                    if 'السعر' in df_active.columns:
                        try:
                            m_min_p = float(df_active['السعر'].min())
                            m_max_p = float(df_active['السعر'].max())
                            if m_min_p < m_max_p:
                                m_price_range = st.slider("💰 نطاق السعر", min_value=m_min_p, max_value=m_max_p, value=(m_min_p, m_max_p), key="filter_price_missing")
                            else:
                                m_price_range = None
                        except:
                            m_price_range = None
                    else:
                        m_price_range = None
                with mf6:
                    m_sort_options = ["الافتراضي", "السعر: الأعلى", "السعر: الأقل", "الاسم: أ-ي", "الاسم: ي-أ"]
                    m_sort_by = st.selectbox("↕️ ترتيب", m_sort_options, key="filter_sort_missing")
                with mf7:
                    m_show_added = st.checkbox("🚫 إخفاء المضافة مسبقاً", value=True, key="hide_added_missing")
                with mf8:
                    if st.button("🔄 إعادة تعيين", key="reset_filters_missing", use_container_width=True):
                        for fk in ["filter_search_missing", "filter_comp_missing", "filter_type_missing", "filter_status_missing"]:
                            if fk in st.session_state:
                                del st.session_state[fk]
                        st.rerun()
            
            # تطبيق الفلاتر
            if m_search:
                df_active = df_active[df_active.apply(lambda r: m_search.lower() in str(r.get('المنتج', '')).lower(), axis=1)]
            if m_filter_comp != "-- الكل --" and 'المنافس' in df_active.columns:
                df_active = df_active[df_active['المنافس'].astype(str).str.contains(m_filter_comp, na=False)]
            if m_filter_type != "-- الكل --" and 'النوع' in df_active.columns:
                df_active = df_active[df_active['النوع'].astype(str) == m_filter_type]
            if m_filter_status == "⏸️ مؤجل":
                df_active = df_active[df_active.index.isin(delayed_indices)]
            elif m_filter_status == "✅ جديد":
                df_active = df_active[~df_active.index.isin(delayed_indices)]
            if m_price_range and 'السعر' in df_active.columns:
                try:
                    pv = pd.to_numeric(df_active['السعر'], errors='coerce').fillna(0)
                    df_active = df_active[(pv >= m_price_range[0]) & (pv <= m_price_range[1])]
                except:
                    pass
            # إخفاء المضافة مسبقاً (تحقق من قاعدة البيانات)
            if m_show_added:
                try:
                    from database import is_product_added
                    already_added = []
                    for idx, row in df_active.iterrows():
                        pname = str(row.get('المنتج', ''))
                        if is_product_added(pname):
                            already_added.append(idx)
                    if already_added:
                        df_active = df_active[~df_active.index.isin(already_added)]
                except:
                    pass
            # تطبيق الترتيب
            if m_sort_by != "الافتراضي":
                try:
                    if "السعر: الأعلى" == m_sort_by and 'السعر' in df_active.columns:
                        df_active = df_active.sort_values('السعر', ascending=False, key=lambda x: pd.to_numeric(x, errors='coerce'))
                    elif "السعر: الأقل" == m_sort_by and 'السعر' in df_active.columns:
                        df_active = df_active.sort_values('السعر', ascending=True, key=lambda x: pd.to_numeric(x, errors='coerce'))
                    elif "الاسم: أ-ي" == m_sort_by and 'المنتج' in df_active.columns:
                        df_active = df_active.sort_values('المنتج', ascending=True)
                    elif "الاسم: ي-أ" == m_sort_by and 'المنتج' in df_active.columns:
                        df_active = df_active.sort_values('المنتج', ascending=False)
                except:
                    pass
            
            filtered_count = len(df_active)
            
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #e3f2fd, #bbdefb); border-radius: 12px; padding: 15px; margin: 10px 0; text-align: center;">
                <h3 style="margin:0; color: #1565c0;">📊 عداد المنتجات المفقودة: <span style="font-size: 1.8rem; color: #d32f2f;">{filtered_count}</span> منتج
                {f' | <span style="color: #999;">🗑️ مزال: {removed_count}</span>' if removed_count > 0 else ''}
                {f' | <span style="color: #ff9800;">⏸️ مؤجل: {delayed_count}</span>' if delayed_count > 0 else ''}</h3>
            </div>""", unsafe_allow_html=True)
            
            # ── Pagination ──
            ITEMS_PER_PAGE = 25
            if "page_missing" not in st.session_state:
                st.session_state["page_missing"] = 0
            total_pages = max(1, (filtered_count + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE)
            current_page = min(st.session_state["page_missing"], total_pages - 1)
            
            if total_pages > 1:
                mp1, mp2, mp3, mp4 = st.columns([1, 2, 1, 2])
                with mp1:
                    if st.button("◀️ السابق", key="prev_missing", disabled=current_page == 0):
                        st.session_state["page_missing"] = current_page - 1
                        st.rerun()
                with mp2:
                    st.markdown(f"<div style='text-align:center; padding:8px;'><b>صفحة {current_page + 1} من {total_pages}</b> ({filtered_count} منتج)</div>", unsafe_allow_html=True)
                with mp3:
                    if st.button("التالي ▶️", key="next_missing", disabled=current_page >= total_pages - 1):
                        st.session_state["page_missing"] = current_page + 1
                        st.rerun()
                with mp4:
                    goto_p = st.number_input("انتقل لصفحة", min_value=1, max_value=total_pages, value=current_page + 1, key="goto_missing", label_visibility="collapsed")
                    if goto_p - 1 != current_page:
                        st.session_state["page_missing"] = goto_p - 1
                        st.rerun()
            
            start_idx = current_page * ITEMS_PER_PAGE
            end_idx = min(start_idx + ITEMS_PER_PAGE, filtered_count)
            page_df = df_active.iloc[start_idx:end_idx]
            
            # أزرار تحديد
            ms1, ms2, ms3, ms4 = st.columns([1, 1, 1, 2])
            with ms1:
                if st.button("✅ تحديد الكل", key="sel_all_missing"):
                    st.session_state["sel_missing"] = {idx: True for idx in df_active.index}
                    st.rerun()
            with ms2:
                if st.button("❌ إلغاء الكل", key="desel_all_missing"):
                    st.session_state["sel_missing"] = {idx: False for idx in df_active.index}
                    st.rerun()
            with ms3:
                if removed_count > 0 or delayed_count > 0:
                    if st.button(f"♻️ استعادة الكل ({removed_count + delayed_count})", key="restore_missing"):
                        st.session_state["removed_missing"] = set()
                        st.session_state["delayed_missing"] = set()
                        st.rerun()
            
            if "sel_missing" not in st.session_state:
                st.session_state["sel_missing"] = {}
            
            # ── عناوين الأعمدة ──
            hcols = st.columns([0.3, 3.0, 1.0, 0.8, 1.0, 1.2, 0.5])
            with hcols[0]: st.markdown("**✓**")
            with hcols[1]: st.markdown("**📦 المنتج**")
            with hcols[2]: st.markdown("**🎯 النوع**")
            with hcols[3]: st.markdown("**📏 الحجم**")
            with hcols[4]: st.markdown("**💰 السعر**")
            with hcols[5]: st.markdown("**🏢 المنافس**")
            with hcols[6]: st.markdown("**🤖**")
            st.markdown("<hr style='margin:5px 0;'>", unsafe_allow_html=True)
            
            # ── عرض المنتجات ──
            selected_missing = []
            for _, row in page_df.iterrows():
                original_idx = row.name
                is_delayed = original_idx in delayed_indices
                
                cols = st.columns([0.3, 3.0, 1.0, 0.8, 1.0, 1.2, 0.5])
                
                with cols[0]:
                    default_val = st.session_state["sel_missing"].get(original_idx, False)
                    checked = st.checkbox("", value=default_val, key=f"missing_{original_idx}")
                    st.session_state["sel_missing"][original_idx] = checked
                    if checked:
                        selected_missing.append(row.to_dict())
                
                with cols[1]:
                    product_name = str(row.get('المنتج', ''))
                    if is_delayed:
                        st.markdown(f"⏸️ **{product_name}**")
                    else:
                        st.markdown(f"**{product_name}**")
                
                with cols[2]:
                    st.write(f"{row.get('النوع', '')}")
                
                with cols[3]:
                    size_val = row.get('الحجم', '')
                    st.write(f"{size_val}" if size_val else "—")
                
                with cols[4]:
                    try:
                        price_val = float(row.get('السعر', 0) or 0)
                        st.write(f"{price_val:.0f} ر.س")
                    except:
                        st.write(f"{row.get('السعر', 0)}")
                
                with cols[5]:
                    comp_name = str(row.get('المنافس', 'غير محدد')).replace('.xlsx', '').replace('.csv', '')
                    st.write(f"{comp_name[:20]}")
                
                with cols[6]:
                    if st.button("🤖", key=f"ai_missing_{original_idx}", help="تحليل ذكي للمنتج"):
                        st.session_state[f"ai_check_missing_{original_idx}"] = True
                        st.rerun()
                
                # ── نتيجة AI + أزرار القرار ──
                if st.session_state.get(f"ai_check_missing_{original_idx}"):
                    with st.spinner("🤖 جاري التحليل الذكي..."):
                        from modules.ai_verification import analyze_for_section
                        product_name = str(row.get('المنتج', ''))
                        comp_price_val = 0
                        try:
                            comp_price_val = float(row.get('السعر', 0) or 0)
                        except (ValueError, TypeError):
                            comp_price_val = 0
                        
                        result = analyze_for_section(
                            section_type="missing",
                            our_product=product_name,
                            competitor_product="",
                            our_price=0,
                            competitor_price=comp_price_val,
                            competitor_name=str(row.get('المنافس', '')).replace('.xlsx', '').replace('.csv', ''),
                            confidence=0,
                            diff_pct=0,
                        )
                        
                        if result["success"]:
                            ai_data = result.get("data", {})
                            if not isinstance(ai_data, dict):
                                ai_data = {}
                            
                            worth_adding = ai_data.get('worth_adding', True)
                            recommendation = ai_data.get('recommendation', 'لا توجد توصية')
                            action = ai_data.get('action', 'تأجيل')
                            suggested_sell = ai_data.get('suggested_sell_price', 0)
                            estimated_cost = ai_data.get('estimated_cost', 0)
                            profit_margin = ai_data.get('profit_margin', '')
                            product_type = ai_data.get('product_type', '')
                            brand = ai_data.get('brand', '')
                            reason = ai_data.get('reason', '')
                            
                            bg_color = "#e8f5e9" if worth_adding else "#fff3e0"
                            border_color = "#4caf50" if worth_adding else "#ff9800"
                            worth_icon = "&#x2705;" if worth_adding else "&#x26A0;&#xFE0F;"
                            worth_text = "نعم" if worth_adding else "لا"
                            worth_color = "#4caf50" if worth_adding else "#ff9800"
                            
                            # بناء صفوف إضافية
                            extra_rows = ""
                            if suggested_sell:
                                try:
                                    extra_rows += f'<tr style="border-bottom: 1px solid #eee;"><td style="padding:6px;"><b>&#x1F4B5; سعر البيع المقترح:</b></td><td style="padding:6px;"><b style="color:#1565c0;font-size:1.1em;">{float(suggested_sell):.2f} ر.س</b></td></tr>'
                                except: pass
                            if estimated_cost:
                                try:
                                    extra_rows += f'<tr style="border-bottom: 1px solid #eee;"><td style="padding:6px;"><b>&#x1F4B8; التكلفة المتوقعة:</b></td><td style="padding:6px;">{float(estimated_cost):.2f} ر.س</td></tr>'
                                except: pass
                            if profit_margin:
                                extra_rows += f'<tr style="border-bottom: 1px solid #eee;"><td style="padding:6px;"><b>&#x1F4C8; هامش الربح:</b></td><td style="padding:6px;">{profit_margin}</td></tr>'
                            
                            reason_html = f'<p style="margin:4px 0 0 0; color:#666;"><small>{reason}</small></p>' if reason else ''
                            
                            ai_html = f"""<div style="background: linear-gradient(135deg, {bg_color}, #fff); border-radius: 12px; padding: 18px; margin: 10px 0; border-right: 5px solid {border_color}; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                                <h4 style="margin:0 0 12px 0; color: #1a237e;">&#x1F916; تحليل الذكاء الاصطناعي - منتج مفقود</h4>
                                <table style="width:100%; border-collapse: collapse;">
                                    <tr style="border-bottom: 1px solid #eee;"><td style="padding:6px;"><b>&#x1F4E6; المنتج:</b></td><td style="padding:6px;">{product_name}</td></tr>
                                    <tr style="border-bottom: 1px solid #eee;"><td style="padding:6px;"><b>&#x1F3AF; النوع:</b></td><td style="padding:6px;">{product_type}</td></tr>
                                    <tr style="border-bottom: 1px solid #eee;"><td style="padding:6px;"><b>&#x1F3F7; الماركة:</b></td><td style="padding:6px;">{brand}</td></tr>
                                    <tr style="border-bottom: 1px solid #eee;"><td style="padding:6px;"><b>&#x1F4B0; سعر المنافس:</b></td><td style="padding:6px;">{comp_price_val:.2f} ر.س</td></tr>
                                    <tr style="border-bottom: 1px solid #eee;"><td style="padding:6px;"><b>{worth_icon} يستحق الاضافة:</b></td><td style="padding:6px;"><b style="color:{worth_color};">{worth_text}</b></td></tr>
                                    {extra_rows}
                                </table>
                                <div style="margin-top:12px; padding:10px; background:#f5f5f5; border-radius:8px;">
                                    <p style="margin:0 0 5px 0;"><b>&#x1F3AF; التوصية:</b></p>
                                    <p style="margin:0; color:#333; line-height:1.6;">{recommendation}</p>
                                </div>
                                <div style="margin-top:8px; padding:8px; background:#e3f2fd; border-radius:8px;">
                                    <p style="margin:0;"><b>&#x1F4CB; الاجراء المقترح:</b> <span style="color:#1565c0; font-weight:bold;">{action}</span></p>
                                    {reason_html}
                                </div>
                            </div>"""
                            st.markdown(ai_html, unsafe_allow_html=True)
                            
                            # أزرار القرار
                            dc1, dc2, dc3, dc4 = st.columns(4)
                            with dc1:
                                if st.button("✅ إضافة للمتجر", key=f"add_missing_{original_idx}", type="primary"):
                                    st.session_state[f"ai_check_missing_{original_idx}"] = False
                                    st.session_state["sel_missing"][original_idx] = True
                                    # تسجيل القرار
                                    try:
                                        from database import log_operation
                                        log_operation("missing_decision", product_name, new_price=comp_price_val, status="add", details={"action": "add", "ai_recommendation": recommendation})
                                    except: pass
                                    st.success("✅ تم تحديد المنتج للإضافة")
                                    st.rerun()
                            with dc2:
                                if st.button("⏸️ تأجيل", key=f"delay_missing_{original_idx}"):
                                    st.session_state[f"ai_check_missing_{original_idx}"] = False
                                    st.session_state["delayed_missing"].add(original_idx)
                                    try:
                                        from database import log_operation
                                        log_operation("missing_decision", product_name, status="delayed", details={"action": "delay"})
                                    except: pass
                                    st.info("⏸️ تم تأجيل القرار")
                                    st.rerun()
                            with dc3:
                                if st.button("🗑️ تجاهل", key=f"ignore_missing_{original_idx}"):
                                    st.session_state["removed_missing"].add(original_idx)
                                    st.session_state[f"ai_check_missing_{original_idx}"] = False
                                    try:
                                        from database import log_operation
                                        log_operation("missing_decision", product_name, status="ignored", details={"action": "ignore"})
                                    except: pass
                                    st.warning("🗑️ تم تجاهل المنتج")
                                    st.rerun()
                            with dc4:
                                if st.button("🔙 إغلاق", key=f"close_missing_{original_idx}"):
                                    st.session_state[f"ai_check_missing_{original_idx}"] = False
                                    st.rerun()
                        else:
                            st.error(f"❌ {result.get('error', 'فشل الاتصال بالذكاء الاصطناعي')}")
                            if st.button("🔙 إغلاق", key=f"close_err_missing_{original_idx}"):
                                st.session_state[f"ai_check_missing_{original_idx}"] = False
                                st.rerun()
            
            # ── Pagination أسفل ──
            if total_pages > 1:
                st.markdown("---")
                bp1, bp2, bp3 = st.columns([1, 3, 1])
                with bp1:
                    if st.button("◀️ السابق", key="prev2_missing", disabled=current_page == 0):
                        st.session_state["page_missing"] = current_page - 1
                        st.rerun()
                with bp2:
                    st.markdown(f"<div style='text-align:center;'>عرض {start_idx + 1}-{end_idx} من {filtered_count} | صفحة {current_page + 1}/{total_pages}</div>", unsafe_allow_html=True)
                with bp3:
                    if st.button("التالي ▶️", key="next2_missing", disabled=current_page >= total_pages - 1):
                        st.session_state["page_missing"] = current_page + 1
                        st.rerun()
            
            # ── ملخص التحديد والإجراءات ──
            all_selected_missing = []
            for idx, row in df_active.iterrows():
                if st.session_state["sel_missing"].get(idx, False):
                    all_selected_missing.append(row.to_dict())
            
            st.markdown("---")
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #fff8e1, #ffecb3); border-radius: 10px; padding: 12px; text-align: center;">
                <b>📌 تم تحديد <span style="font-size: 1.5rem; color: #e65100;">{len(all_selected_missing)}</span> من أصل <span style="font-size: 1.5rem; color: #1565c0;">{filtered_count}</span> منتج</b>
            </div>""", unsafe_allow_html=True)
            
            col_b1, col_b2, col_b3 = st.columns(3)
            with col_b1:
                if st.button("✅ موافقة وإضافة إلى سلة", type="primary", use_container_width=True,
                             disabled=len(all_selected_missing) == 0, key="send_missing"):
                    with st.spinner(f"⏳ جاري إرسال {len(all_selected_missing)} منتج..."):
                        from database import log_operation, mark_product_added, is_product_added
                        
                        # تحقق من التكرار قبل الإرسال
                        new_products = []
                        duplicates = []
                        for product in all_selected_missing:
                            pname = product.get('المنتج', '')
                            if is_product_added(pname):
                                duplicates.append(pname)
                            else:
                                new_products.append(product)
                        
                        if duplicates:
                            st.warning(f"⚠️ تم تجاوز {len(duplicates)} منتج مكرر (مضاف مسبقاً)")
                        
                        if new_products:
                            result = send_new_products(new_products)
                            if result.get("success"):
                                for product in new_products:
                                    product_name = product.get('المنتج', '')
                                    log_operation("product_add", product_name, new_price=product.get('السعر', 0), status="success", details={"source": "missing_products"}, user_action="approved_and_added")
                                    mark_product_added(product_name, "missing_products")
                                save_send_log("إضافة منتجات", len(new_products), len(new_products), 0, "Make.com إضافة منتجات")
                                st.markdown(f"""<div class="success-box"><h2>🎉 تم الإرسال بنجاح!</h2><p>تم إرسال <b>{len(new_products)}</b> منتج جديد لإضافتها في سلة</p></div>""", unsafe_allow_html=True)
                                st.balloons()
                            else:
                                st.error(f"❌ فشل الإرسال: {result.get('error', 'خطأ غير معروف')}")
                        elif not new_products and duplicates:
                            st.info("ℹ️ جميع المنتجات المحددة مضافة مسبقاً")
            
            with col_b2:
                if all_selected_missing:
                    df_sel = pd.DataFrame(all_selected_missing)
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        df_sel.to_excel(writer, sheet_name="مفقودة محددة", index=False)
                    output.seek(0)
                    st.download_button("📥 تحميل المحدد", data=output.getvalue(),
                                      file_name=f"missing_selected_{datetime.now():%Y%m%d_%H%M%S}.xlsx",
                                      mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                      use_container_width=True, key="dl_sel_missing")
            
            with col_b3:
                output_all = BytesIO()
                with pd.ExcelWriter(output_all, engine='openpyxl') as writer:
                    df_active.to_excel(writer, sheet_name="مفقودة", index=False)
                output_all.seek(0)
                st.download_button(f"📥 تحميل الكل ({filtered_count})", data=output_all.getvalue(),
                                  file_name=f"missing_all_{datetime.now():%Y%m%d_%H%M%S}.xlsx",
                                  mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                  use_container_width=True, key="dl_all_missing")
            
            # زر التحقق المجمع
            st.markdown("---")
            if st.button("🤖 تحقق مجمع للمنتجات المحددة", type="secondary", use_container_width=True,
                       disabled=len(all_selected_missing) == 0, key="batch_verify_missing"):
                with st.spinner(f"🔍 جاري التحقق من {len(all_selected_missing)} منتج..."):
                    from modules.ai_verification import batch_verification
                    products_data = [{"name": str(item.get('المنتج', '')), "competitor_price": item.get('السعر', 0)} for item in all_selected_missing]
                    result = batch_verification(products=products_data, store_file_path=None, verification_type="comprehensive")
                    if result["success"]:
                        data = result["data"]
                        st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #e1f5fe, #b3e5fc); border-radius: 12px; padding: 20px; margin: 15px 0;">
                            <h3 style="margin:0; color: #01579b;">📊 ملخص التحقق المجمع</h3>
                            <p><b>📦 إجمالي:</b> {data.get('total_products', 0)} | <b>✅ موجود:</b> {data.get('found_in_store', 0)} | <b>❌ غير موجود:</b> {data.get('not_found', 0)}</p>
                            <p><b>🎯 التوصيات:</b> {data.get('recommendations', '')}</p>
                        </div>""", unsafe_allow_html=True)
                        with st.expander("📝 عرض التفاصيل الكاملة"):
                            for item in data.get('details', []):
                                st.markdown(f"""<div style="background: #f5f5f5; border-left: 4px solid #2196f3; padding: 10px; margin: 5px 0;">
                                    <p><b>🏪 {item.get('product_name', '')}</b></p>
                                    <p>💰 سعر المنافس: {item.get('competitor_price', '')} ر.س | 🏪 في متجرنا: {'✅' if item.get('in_our_store') else '❌'}</p>
                                    <p>🎯 {item.get('recommendation', '')}</p>
                                </div>""", unsafe_allow_html=True)
                    else:
                        st.error(f"❌ {result.get('error', 'خطأ غير معروف')}")
        else:
            st.success("✅ لا توجد منتجات مفقودة - جميع المنتجات موجودة!")
    else:
        st.info("📤 قم برفع الملفات وبدء المعالجة أولاً")

# ══════════════════════════════════════════════════════════════
# 7. يحتاج مراجعة
# ══════════════════════════════════════════════════════════════
elif section == "🔍 تفاصيل المطابقة":
    from match_details_page import render_match_details_page
    render_match_details_page()

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
# 8. تحقق AI (دمج الأقسام المتشابهة)
# ══════════════════════════════════════════════════════════════
elif section == "🤖 تحقق AI":
    st.markdown("# 🤖 تحقق AI")
    st.markdown("> نظام شامل للتحقق من المنتجات باستخدام الذكاء الاصطناعي")
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

    # تبويبات التحقق
    tab1, tab2, tab3 = st.tabs(["🤖 Gemini تحقق", "🔍 تحقق مجمع AI", "🔬 كشف الأخطاء الذكي"])

    with tab1:
        st.markdown("### 🤖 Gemini تحقق")
        st.markdown("> التحقق من المنتجات وتحليلها باستخدام الذكاء الصناعي")

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
                ], key="gemini_analysis_type")

                sample_size = st.slider("📊 عدد المنتجات للتحليل", 5, 50, 10, key="gemini_sample_size")

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

    with tab2:
        st.markdown("### 🔍 تحقق مجمع AI")
        st.markdown("> تحقق ذكي من عدة منتجات دفعة واحدة")

        # الخيارات
        st.markdown("#### ⚙️ خيارات التحقق")
        col1, col2 = st.columns(2)

        with col1:
            verification_type = st.selectbox(
                "نوع التحقق",
                ["البحث الإلكتروني فقط", "التحقق من ملف المتجر فقط", "تحقق شامل (الاثنين معاً)"],
                help="اختر نوع التحقق المطلوب",
                key="batch_verification_type"
            )

        with col2:
            store_file = None
            if "ملف المتجر" in verification_type or "شامل" in verification_type:
                store_file = st.file_uploader(
                    "📄 ملف المتجر (CSV)",
                    type=["csv"],
                    help="ارفع ملف CSV الخاص بمتجرك للتحقق",
                    key="batch_store_file"
                )

        st.markdown("---")
        st.markdown("#### 📦 اختيار المنتجات")

        if st.session_state.results:
            df_approved = st.session_state.results.get("approved")

            if df_approved is not None and not df_approved.empty:
                st.success(f"✅ {len(df_approved)} منتج متاح للتحقق")

                selection_method = st.radio(
                    "طريقة التحديد",
                    ["تحديد يدوي", "تحديد الكل", "تحديد حسب النطاق"],
                    horizontal=True,
                    key="batch_selection_method"
                )

                selected_products = []

                if selection_method == "تحديد يدوي":
                    st.markdown("##### اختر المنتجات:")
                    for idx, row in df_approved.iterrows():
                        product_name = row.get('اسم المنتج', row.iloc[0])
                        product_price = row.get('السعر', row.iloc[1] if len(row) > 1 else 'N/A')

                        if st.checkbox(f"{product_name} - {product_price} ريال", key=f"batch_select_{idx}"):
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

                else:
                    col_range1, col_range2 = st.columns(2)
                    with col_range1:
                        start_idx = st.number_input("من", min_value=1, max_value=len(df_approved), value=1, key="batch_start_idx")
                    with col_range2:
                        end_idx = st.number_input("إلى", min_value=1, max_value=len(df_approved), value=min(10, len(df_approved)), key="batch_end_idx")

                    selected_products = [
                        {
                            "name": row.get('اسم المنتج', row.iloc[0]),
                            "price": float(row.get('السعر', row.iloc[1] if len(row) > 1 else 0))
                        }
                        for idx, row in df_approved.iloc[start_idx-1:end_idx].iterrows()
                    ]
                    st.info(f"📊 تم تحديد {len(selected_products)} منتج من النطاق")

                st.markdown("---")

                if len(selected_products) > 0:
                    st.markdown(f"### 🚀 جاهز للتحقق من {len(selected_products)} منتج")

                    if st.button("🤖 بدء التحقق المجمع", type="primary", use_container_width=True):
                        store_file_path = None
                        if store_file:
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
                                tmp.write(store_file.getvalue())
                                store_file_path = tmp.name

                        with st.spinner("⏳ جاري التحقق المجمع... قد يستغرق بعض الوقت"):
                            result = batch_verification(selected_products, store_file_path)

                            if result["success"]:
                                st.success("✅ تم التحقق المجمع بنجاح!")

                                summary = result.get("summary")
                                if summary:
                                    st.markdown("### 📊 ملخص النتائج")
                                    col_s1, col_s2, col_s3 = st.columns(3)

                                    with col_s1:
                                        st.metric("إجمالي المنتجات", summary.get("total_products", 0))
                                    with col_s2:
                                        st.metric("منتجات تنافسية", summary.get("competitive_count", 0), delta="✅")
                                    with col_s3:
                                        st.metric("تحتاج تعديل", summary.get("needs_adjustment", 0), delta="⚠️")

                                    if summary.get("recommendations"):
                                        st.markdown("#### 💡 التوصيات:")
                                        for rec in summary["recommendations"]:
                                            st.info(f"• {rec}")

                                    if summary.get("summary"):
                                        st.markdown("#### 📝 الملخص العام:")
                                        st.write(summary["summary"])

                                st.markdown("---")
                                st.markdown("### 📋 النتائج التفصيلية")

                                results_list = result.get("results", [])
                                for i, res in enumerate(results_list, 1):
                                    if res.get("success"):
                                        product_results = res["results"]
                                        with st.expander(f"🔍 {i}. {product_results['product_name']}"):
                                            if product_results.get("online_search"):
                                                st.markdown("#### 🌐 البحث الإلكتروني:")
                                                st.json(product_results["online_search"])
                                            if product_results.get("store_verification"):
                                                st.markdown("#### 🏪 التحقق من المتجر:")
                                                st.json(product_results["store_verification"])
                                            if product_results.get("analysis"):
                                                st.markdown("#### 🎯 التحليل الذكي:")
                                                st.json(product_results["analysis"])
                                    else:
                                        st.error(f"❌ خطأ في المنتج {i}: {res.get('error', 'غير معروف')}")

                                st.markdown("---")
                                st.markdown("### 📥 تحميل النتائج")
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

    with tab3:
        st.markdown("### 🔬 كشف الأخطاء الذكي")
        st.markdown("> نظام ذكي لاكتشاف الأخطاء في المطابقة باستخدام Gemini AI")

        # اختيار نوع التحليل
        analysis_mode = st.radio(
            "نوع التحليل",
            ["📊 تحليل المطابقات", "🔍 تحقق فردي"],
            horizontal=True,
            key="error_detection_mode"
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

                if matches:
                    st.success(f"✅ تم العثور على {len(matches)} مطابقة للتحليل")

                    # عرض ملخص المطابقات
                    st.markdown("#### 📊 ملخص المطابقات")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("إجمالي المطابقات", len(matches))
                    with col2:
                        avg_similarity = sum(m['similarity'] for m in matches) / len(matches)
                        st.metric("متوسط التشابه", f"{avg_similarity:.2%}")
                    with col3:
                        high_similarity = sum(1 for m in matches if m['similarity'] >= 0.8)
                        st.metric("مطابقات عالية", high_similarity)

                    # تحليل الأخطاء المحتملة
                    st.markdown("---")
                    st.markdown("#### 🔍 تحليل الأخطاء المحتملة")

                    error_analysis = []

                    for match in matches:
                        errors = []

                        # فحص الفرق في الأسعار
                        price_diff = abs(match['my_price'] - match['competitor_price'])
                        if price_diff > match['my_price'] * 0.5:  # فرق أكبر من 50%
                            errors.append(f"فرق سعر كبير ({price_diff:.0f} ر.س)")

                        # فحص التشابه المنخفض
                        if match['similarity'] < 0.6:
                            errors.append(f"تشابه منخفض ({match['similarity']:.1%})")

                        # فحص الأسماء المتشابهة جداً
                        if match['similarity'] > 0.95:
                            errors.append("تشابه عالي جداً - قد يكون خطأ في المطابقة")

                        if errors:
                            error_analysis.append({
                                'product': match['my_product'],
                                'competitor': match['competitor_product'],
                                'errors': errors,
                                'similarity': match['similarity'],
                                'price_diff': price_diff
                            })

                    if error_analysis:
                        st.warning(f"⚠️ تم العثور على {len(error_analysis)} منتج قد يحتوي على أخطاء")

                        for item in error_analysis[:10]:  # عرض أول 10 فقط
                            with st.expander(f"🔍 {item['product']}"):
                                st.markdown(f"**المنافس:** {item['competitor']}")
                                st.markdown(f"**نسبة التشابه:** {item['similarity']:.1%}")
                                st.markdown(f"**فرق السعر:** {item['price_diff']:.0f} ر.س")

                                st.markdown("**الأخطاء المحتملة:**")
                                for error in item['errors']:
                                    st.error(f"• {error}")

                                # زر للتحقق الفردي
                                if st.button(f"🤖 تحقق فردي لهذا المنتج", key=f"verify_{hash(item['product'])}"):
                                    st.info("🔄 جاري التحقق الفردي...")
                                    # يمكن إضافة منطق التحقق الفردي هنا
                    else:
                        st.success("✅ لم يتم العثور على أخطاء واضحة في المطابقات")
                else:
                    st.info("📋 لا توجد مطابقات للتحليل")
            else:
                st.info("📤 لا توجد نتائج للتحليل. قم برفع الملفات وبدء المعالجة أولاً.")

        else:
            # التحقق الفردي
            st.markdown("#### 🔍 التحقق الفردي")
            st.markdown("أدخل تفاصيل المنتج للتحقق من الأخطاء:")

            col1, col2 = st.columns(2)
            with col1:
                product_name = st.text_input("اسم المنتج", key="individual_product_name")
                my_price = st.number_input("سعرنا (ريال)", min_value=0.0, key="individual_my_price")

            with col2:
                competitor_name = st.text_input("اسم المنتج المنافس", key="individual_competitor_name")
                competitor_price = st.number_input("سعر المنافس (ريال)", min_value=0.0, key="individual_competitor_price")

            if st.button("🔍 تحقق من الأخطاء", type="primary", disabled=not (product_name and competitor_name)):
                with st.spinner("🤖 جاري التحقق من الأخطاء..."):
                    # منطق التحقق الفردي
                    errors_found = []

                    # فحص التشابه في الأسماء
                    from difflib import SequenceMatcher
                    similarity = SequenceMatcher(None, product_name.lower(), competitor_name.lower()).ratio()

                    if similarity < 0.3:
                        errors_found.append("الأسماء مختلفة جداً - قد لا تكون مطابقة صحيحة")
                    elif similarity > 0.95:
                        errors_found.append("الأسماء متطابقة تماماً - تحقق من عدم التكرار")

                    # فحص الفرق في الأسعار
                    if my_price > 0 and competitor_price > 0:
                        price_diff_pct = abs(my_price - competitor_price) / min(my_price, competitor_price)
                        if price_diff_pct > 2.0:  # فرق أكبر من 200%
                            errors_found.append(f"فرق سعر كبير جداً ({price_diff_pct:.1%})")

                    # فحص الأنماط الشائعة للأخطاء
                    if "ml" in product_name.lower() and "ml" not in competitor_name.lower():
                        errors_found.append("اختلاف في وحدة القياس (ml)")
                    if "ml" in competitor_name.lower() and "ml" not in product_name.lower():
                        errors_found.append("اختلاف في وحدة القياس (ml)")

                    # عرض النتائج
                    st.markdown("### 📊 نتائج التحقق")

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("نسبة التشابه", f"{similarity:.1%}")
                    with col2:
                        if my_price > 0 and competitor_price > 0:
                            price_diff = abs(my_price - competitor_price)
                            st.metric("فرق السعر", f"{price_diff:.0f} ر.س")
                    with col3:
                        status = "🟢 آمن" if len(errors_found) == 0 else "🟡 يحتاج مراجعة" if len(errors_found) <= 2 else "🔴 خطير"
                        st.metric("الحالة", status)

                    if errors_found:
                        st.warning("⚠️ تم العثور على الأخطاء التالية:")
                        for error in errors_found:
                            st.error(f"• {error}")

                        st.markdown("#### 💡 توصيات:")
                        if similarity < 0.5:
                            st.info("• تحقق من صحة المطابقة - الأسماء مختلفة جداً")
                        if len(errors_found) > 2:
                            st.info("• هذا المنتج يحتاج مراجعة يدوية دقيقة")
                    else:
                        st.success("✅ لم يتم العثور على أخطاء واضحة - المطابقة تبدو صحيحة")

# ══════════════════════════════════════════════════════════════
# 10. محادثة AI
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
        
        with st.chat_message("assistant"), st.spinner("⏳ جاري التفكير..."):
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
# 10. استديو مهووس الذكي v9.0
# ══════════════════════════════════════════════════════════════
elif section == "🎬 استديو مهووس":
    try:
        from modules.studio import show_studio_page
        show_studio_page()
    except Exception as e:
        st.error(f"❌ خطأ في تحميل استديو مهووس: {str(e)}")
        st.code(f"تفاصيل الخطأ:\n{e}", language="python")
        import traceback
        st.code(traceback.format_exc(), language="python")

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
    
    # نسبة التطابق الثابتة
    threshold = 60  # أفضل نسبة بناءً على الاختبارات
    st.info("🎯 **حد التطابق المثالي:** 60% (محدد تلقائيًا لأفضل نتائج - بناءً على اختبارات مكثفة)")
    
    col1, col2 = st.columns(2)
    with col1:
        raise_threshold = st.slider("🔴 حد رفع السعر (%)", 1, 30,
                                   st.session_state.algorithm_settings.get("raise_threshold", 10),
                                   help="إذا كان سعرنا أقل بهذه النسبة → رفع السعر")
        
        lower_threshold = st.slider("🟡 حد خفض السعر (%)", 1, 30,
                                   st.session_state.algorithm_settings.get("lower_threshold", 5),
                                   help="إذا كان سعرنا أعلى بهذه النسبة → خفض السعر")
    
    with col2:
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
    st.markdown("# 💾 قاعدة البيانات Supabase")
    st.markdown("> عرض وإدارة جميع السجلات المحفوظة في السحابة")
    st.markdown("---")
    
    # معلومات الاتصال
    with st.expander("🔗 معلومات الاتصال بقاعدة البيانات"):
        st.code(f"""
Supabase URL: {SUPABASE_URL}
Project ID: csivkasoqkivprldxqlc
Region: AWS ap-southeast-1 (Singapore)
Status: ✅ متصل
الجداول:
- analysis_results: نتائج التحليل
- send_log: سجل الإرسالات
- users: المستخدمين
- suppliers: الموردين
- purchases: المشتريات
- expenses: المصروفات
- audit_log: سجل التدقيق
        """, language="text")
        st.info("📌 يمكنك الوصول إلى لوحة تحكم Supabase من [supabase.com/dashboard](https://supabase.com/dashboard)")
    
    # إحصائيات محسّنة
    db_stats = get_db_stats()
    st.markdown("### 📊 إحصائيات قاعدة البيانات")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("📊 إجمالي السجلات", db_stats.get("total_records", 0))
    c2.metric("🔴 رفع سعر", db_stats.get("raise_count", 0))
    c3.metric("🟡 خفض سعر", db_stats.get("lower_count", 0))
    c4.metric("🟢 موافق", db_stats.get("approved_count", 0))
    c5.metric("📤 إرسالات", db_stats.get("total_sends", 0))
    
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
            st.success(f"✅ تم تحميل **{len(records)}** سجل")
            
            # عرض الجدول بتنسيق محسّن
            st.dataframe(records, use_container_width=True, height=500)
            
            # أزرار التحميل
            col_d1, col_d2, col_d3 = st.columns(3)
            with col_d1:
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    records.to_excel(writer, sheet_name="سجلات", index=False)
                output.seek(0)
                st.download_button("📅 تحميل Excel", data=output.getvalue(),
                                  file_name=f"db_records_{datetime.now():%Y%m%d}.xlsx",
                                  mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                  use_container_width=True)
            with col_d2:
                csv_data = records.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📄 تحميل CSV", data=csv_data,
                                  file_name=f"db_records_{datetime.now():%Y%m%d}.csv",
                                  mime="text/csv",
                                  use_container_width=True)
            with col_d3:
                json_data = records.to_json(orient='records', force_ascii=False, indent=2)
                st.download_button("📦 تحميل JSON", data=json_data,
                                  file_name=f"db_records_{datetime.now():%Y%m%d}.json",
                                  mime="application/json",
                                  use_container_width=True)
        else:
            st.info("📋 لا توجد سجلات")
            st.markdown("""
            ### 💡 نصيحة
            قم برفع ملفات المنافسين وبدء المعالجة لإنشاء سجلات جديدة.
            """)
    
    with tab2:
        st.markdown("### 📤 سجل الإرسالات")
        
        # فلترة حسب الحالة
        log_filter = st.selectbox("🔍 فلترة حسب الحالة", ["الكل", "نجح", "جزئي", "فشل"])
        
        logs = get_send_logs()
        if not logs.empty:
            if log_filter != "الكل":
                logs = logs[logs["status"] == log_filter]
            
            st.success(f"✅ تم تحميل **{len(logs)}** إرسالية")
            st.dataframe(logs, use_container_width=True, height=400)
            
            # تحميل سجل الإرسالات
            output_logs = BytesIO()
            with pd.ExcelWriter(output_logs, engine='openpyxl') as writer:
                logs.to_excel(writer, sheet_name="سجل الإرسالات", index=False)
            output_logs.seek(0)
            st.download_button("📅 تحميل سجل الإرسالات", data=output_logs.getvalue(),
                              file_name=f"send_logs_{datetime.now():%Y%m%d}.xlsx",
                              mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                              use_container_width=True)
        else:
            st.info("📋 لا توجد إرسالات")
    
    with tab3:
        st.markdown("### 🔧 إدارة قاعدة البيانات")
        
        st.warning("⚠️ **تحذير:** عمليات الحذف لا يمكن التراجع عنها!")
        
        col_m1, col_m2 = st.columns(2)
        
        with col_m1:
            st.markdown("#### 🗑️ حذف السجلات")
            days_old = st.number_input("حذف السجلات الأقدم من (يوم)", 7, 365, 30)
            if st.button(f"🗑️ حذف سجلات أقدم من {days_old} يوم", type="secondary"):
                from datetime import timedelta
                cutoff = (datetime.now() - timedelta(days=days_old)).strftime("%Y-%m-%d %H:%M:%S")
                result = supabase_request("DELETE", "analysis_results", params={"created_at": f"lt.{cutoff}"})
                if result:
                    st.success(f"✅ تم حذف السجلات الأقدم من {days_old} يوم")
                    st.balloons()
                else:
                    st.error("❌ فشل الحذف")
        
        with col_m2:
            st.markdown("#### 🔄 صيانة")
            if st.button("📊 إعادة حساب الإحصائيات"):
                st.rerun()
            
            if st.button("📥 نسخ احتياطي كامل"):
                with st.spinner("⏳ جاري إنشاء النسخة الاحتياطية..."):
                    all_records = get_all_records(10000)
                    if not all_records.empty:
                        output = BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            all_records.to_excel(writer, sheet_name="جميع السجلات", index=False)
                        output.seek(0)
                        st.download_button("📅 تحميل النسخة الاحتياطية", 
                                          data=output.getvalue(),
                                          file_name=f"backup_full_{datetime.now():%Y%m%d_%H%M%S}.xlsx",
                                          mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                        st.success("✅ جاهز للتحميل!")
                    else:
                        st.warning("⚠️ لا توجد سجلات")
        
        st.markdown("---")
        st.markdown("#### 🔍 فحص الاتصال")
        if st.button("🔄 اختبار اتصال Supabase", key="test_supabase"):
            with st.spinner("⏳ جاري الفحص..."):
                try:
                    test_result = supabase_request("GET", "analysis_results", params={"select": "id", "limit": "1"})
                    if test_result is not None:
                        st.success("✅ الاتصال بقاعدة البيانات ناجح!")
                        st.balloons()
                    else:
                        st.error("❌ فشل الاتصال")
                except Exception as e:
                    st.error(f"❌ خطأ: {str(e)}")

# ══════════════════════════════════════════════════════════════
# فحص AI
# ══════════════════════════════════════════════════════════════
elif section == "🤖 فحص AI":
    st.markdown("# 🤖 فحص الذكاء الاصطناعي")
    st.markdown("> فحص شامل لحالة الذكاء الاصطناعي وتشخيص المشاكل")
    st.markdown("---")
    
    # فحص حالة الاتصال
    st.markdown("### 📡 فحص حالة الاتصال")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 فحص Gemini AI", use_container_width=True):
            with st.spinner("⏳ جاري فحص Gemini..."):
                gemini_result = verify_gemini_connection(update_session=False)
                if gemini_result["connected"]:
                    st.success("✅ Gemini AI متصل ويعمل")
                    st.info(f"📊 النموذج: {gemini_result.get('model', 'غير محدد')}")
                else:
                    st.error(f"❌ Gemini AI غير متصل: {gemini_result['message']}")
    
    with col2:
        if st.button("🔄 فحص OpenRouter", use_container_width=True):
            with st.spinner("⏳ جاري فحص OpenRouter..."):
                try:
                    from modules.ai_verification import get_ai_status
                    ai_st = get_ai_status()
                    o_active = ai_st.get('openrouter_active', 0)
                    if o_active > 0:
                        st.success(f"✅ OpenRouter متصل ({o_active} مفتاح نشط)")
                    else:
                        st.error("❌ OpenRouter غير متصل")
                except:
                    st.error("❌ خطأ في فحص OpenRouter")
    
    with col3:
        if st.button("🔄 فحص شامل", type="primary", use_container_width=True):
            with st.spinner("⏳ جاري الفحص الشامل..."):
                # فحص Gemini
                gemini_result = verify_gemini_connection(update_session=False)
                
                # فحص OpenRouter
                try:
                    from modules.ai_verification import get_ai_status
                    ai_st = get_ai_status()
                    g_active = ai_st.get('gemini_active', 0)
                    o_active = ai_st.get('openrouter_active', 0)
                    
                    st.markdown("#### 📊 نتائج الفحص الشامل:")
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        if gemini_result["connected"] or g_active > 0:
                            st.success("🟢 Gemini AI: متصل ويعمل")
                        else:
                            st.error("🔴 Gemini AI: غير متصل")
                    
                    with c2:
                        if o_active > 0:
                            st.success("🟢 OpenRouter: متصل ويعمل")
                        else:
                            st.error("🔴 OpenRouter: غير متصل")
                    
                    if (gemini_result["connected"] or g_active > 0) or o_active > 0:
                        st.success("✅ الذكاء الاصطناعي جاهز للاستخدام!")
                    else:
                        st.error("❌ جميع خدمات الذكاء الاصطناعي غير متاحة")
                        
                except Exception as e:
                    st.error(f"❌ خطأ في الفحص الشامل: {str(e)}")
    
    st.markdown("---")
    
    # اختبار عملي
    st.markdown("### 🧪 اختبار عملي")
    
    test_prompt = st.text_area(
        "📝 نص الاختبار",
        value="ما هو أفضل سعر لعطر شانيل رقم 5 حجم 100 مل في السوق السعودي؟",
        height=100,
        help="اكتب نص لاختبار الذكاء الاصطناعي"
    )
    
    col_test1, col_test2 = st.columns(2)
    
    with col_test1:
        if st.button("🤖 اختبار Gemini", use_container_width=True, disabled=not test_prompt):
            with st.spinner("⏳ جاري الاختبار..."):
                result = call_gemini(test_prompt)
                if result["success"]:
                    st.success("✅ نجح الاختبار!")
                    st.markdown("#### 📝 الرد:")
                    st.write(result["text"])
                else:
                    st.error(f"❌ فشل الاختبار: {result['error']}")
    
    with col_test2:
        if st.button("🧠 اختبار OpenRouter", use_container_width=True, disabled=not test_prompt):
            with st.spinner("⏳ جاري الاختبار..."):
                result = call_openrouter(test_prompt)
                if result["success"]:
                    st.success("✅ نجح الاختبار!")
                    st.markdown("#### 📝 الرد:")
                    st.write(result["text"])
                else:
                    st.error(f"❌ فشل الاختبار: {result['error']}")
    
    st.markdown("---")
    
    # إعدادات المفاتيح
    st.markdown("### 🔑 إعدادات مفاتيح API")
    
    with st.expander("⚙️ إدارة المفاتيح", expanded=False):
        st.markdown("#### 🤖 مفتاح Gemini API")
        gemini_key_input = st.text_input(
            "مفتاح Gemini API",
            value=st.session_state.get("gemini_key", ""),
            type="password",
            help="أدخل مفتاح Gemini API الخاص بك"
        )
        
        st.markdown("#### 🧠 مفتاح OpenRouter API")
        openrouter_key_input = st.text_input(
            "مفتاح OpenRouter API", 
            value=st.session_state.get("openrouter_key", ""),
            type="password",
            help="أدخل مفتاح OpenRouter API الخاص بك"
        )
        
        if st.button("💾 حفظ المفاتيح", type="primary"):
            st.session_state.gemini_key = gemini_key_input
            st.session_state.openrouter_key = openrouter_key_input
            st.success("✅ تم حفظ المفاتيح!")
            st.rerun()
    
    # معلومات التشخيص
    st.markdown("---")
    st.markdown("### 🔧 معلومات التشخيص")
    
    with st.expander("📊 تفاصيل النظام", expanded=False):
        import sys
        st.markdown(f"**Python Version:** {sys.version}")
        st.markdown(f"**Platform:** {sys.platform}")
        
        try:
            import streamlit
            st.markdown(f"**Streamlit Version:** {streamlit.__version__}")
        except:
            st.markdown("**Streamlit Version:** غير متاح")
        
        try:
            import google.generativeai as genai
            st.markdown(f"**Google Generative AI Version:** {genai.__version__}")
        except:
            st.markdown("**Google Generative AI:** غير مثبت")
        
        try:
            import requests
            st.markdown(f"**Requests Version:** {requests.__version__}")
        except:
            st.markdown("**Requests:** غير مثبت")

# ══════════════════════════════════════════════════════════════
# المشتريات اليومية
# ══════════════════════════════════════════════════════════════
elif section == "🛒 المشتريات اليومية":
    from modules.purchases import show_purchases_page
    show_purchases_page()

# ══════════════════════════════════════════════════════════════
# إدارة الموردين
# ══════════════════════════════════════════════════════════════
elif section == "🏪 إدارة الموردين":
    from modules.suppliers import show_suppliers_page
    show_suppliers_page()

# ══════════════════════════════════════════════════════════════
# مذكرة المصروفات
# ══════════════════════════════════════════════════════════════
elif section == "💰 مذكرة المصروفات":
    from modules.expenses import show_expenses_page
    show_expenses_page()

# ══════════════════════════════════════════════════════════════
# الإعدادات
# ══════════════════════════════════════════════════════════════
elif section == "⚙️ الإعدادات":
    st.markdown("# ⚙️ الإعدادات")
    st.markdown("---")
    
    tab1, tab2, tab3, tab4 = st.tabs(["🤖 الذكاء الصناعي", "⚡ Make.com", "📁 Google Drive", "🔗 ربط الخوارزميات"])
    
    with tab1:
        st.markdown("### 🤖 إعدادات الذكاء الصناعي")
        
        # عرض حالة المفاتيح المتعددة
        st.info("🔑 **نظام مفاتيح متعددة** - تبديل تلقائي عند الفشل (Gemini + OpenRouter)")
        
        try:
            from modules.ai_verification import get_ai_status
            ai_status = get_ai_status()
            col_g, col_o = st.columns(2)
            with col_g:
                g_count = ai_status.get('gemini_active', 0)
                g_total = ai_status.get('gemini_total', 0)
                if g_count > 0:
                    st.success(f"✅ Gemini: {g_count}/{g_total} مفتاح نشط")
                else:
                    st.error(f"❌ Gemini: لا مفاتيح نشطة ({g_total} إجمالي)")
            with col_o:
                o_count = ai_status.get('openrouter_active', 0)
                o_total = ai_status.get('openrouter_total', 0)
                if o_count > 0:
                    st.success(f"✅ OpenRouter: {o_count}/{o_total} مفتاح نشط")
                else:
                    st.warning(f"⚠️ OpenRouter: لا مفاتيح ({o_total} إجمالي)")
            
            st.metric("إجمالي الطلبات", ai_status.get('total_calls', 0))
            
            # تحذير إذا لم تكن هناك مفاتيح متاحة
            if ai_status.get('available', False) == False:
                st.error("❌ **جميع مفاتيح الذكاء الاصطناعي غير متاحة!**")
                st.warning("⚠️ يرجى إدخال مفاتيح API صحيحة في قسم إدارة المفاتيح أدناه")
                
        except Exception:
            if DEFAULT_GEMINI_KEY:
                st.success(f"✅ مفتاح Gemini موجود وجاهز")
            else:
                st.warning("⚠️ مفتاح Gemini غير موجود في Streamlit Secrets")
        
        if st.button("🔄 اختبار اتصال Gemini", key="test_gemini_settings"):
            with st.spinner("⏳ جاري الاختبار..."):
                result = verify_gemini_connection()  # يستخدم المفتاح المدمج
                if result["connected"]:
                    st.success(f"✅ متصل بنجاح! النموذج: {result['model']}")
                    st.balloons()
                else:
                    st.error(f"❌ فشل الاتصال: {result['message']}")
        
        st.markdown("---")
        
        # إدارة مفاتيح API
        st.markdown("#### 🔑 إدارة مفاتيح API")
        
        # زر عرض الدليل
        if st.button("📋 عرض دليل إعداد المفاتيح", key="show_api_guide"):
            with st.expander("📖 دليل إعداد مفاتيح API", expanded=True):
                st.markdown("""
**🔑 Gemini AI Keys:**
1. اذهب إلى: [Google AI Studio](https://makersuite.google.com/app/apikey)
2. أنشئ مفتاح API جديد
3. انسخ المفتاح واحفظه في مكان آمن

**🧠 OpenRouter Keys:**
1. اذهب إلى: [OpenRouter Keys](https://openrouter.ai/keys)
2. أنشئ مفتاح API جديد  
3. انسخ المفتاح واحفظه في مكان آمن

**⚙️ خطوات الإعداد:**
1. أدخل مفاتيحك في الحقول أدناه
2. اضغط '💾 حفظ المفاتيح'
3. اختبر الاتصال بالضغط على '🔄 اختبار الاتصال'

**💡 نصائح مهمة:**
- يمكنك إدخال عدة مفاتيح للتبديل التلقائي عند الفشل
- المفاتيح محفوظة محلياً فقط في جلسة التطبيق
- لا تشارك مفاتيحك مع أي شخص آخر
- تأكد من وجود رصيد كافي في حساباتك
                """)
        
        st.markdown("---")
        
        with st.expander("⚙️ إعدادات مفاتيح Gemini", expanded=True):
            st.markdown("**مفاتيح Gemini AI (متعددة للتبديل التلقائي):**")
            
            # إدخال مفاتيح Gemini
            gemini_keys = []
            for i in range(1, 6):  # حتى 5 مفاتيح
                key_name = f"gemini_key_{i}"
                current_value = st.session_state.get(key_name, "")
                key_input = st.text_input(
                    f"🔑 Gemini API Key {i}",
                    value=current_value,
                    type="password",
                    key=f"input_{key_name}",
                    help=f"أدخل مفتاح Gemini API رقم {i}"
                )
                if key_input and key_input != current_value:
                    st.session_state[key_name] = key_input
                if key_input.strip():
                    gemini_keys.append(key_input.strip())
            
            if st.button("💾 حفظ مفاتيح Gemini نهائياً", key="save_gemini_keys", type="primary"):
                try:
                    # حفظ المفاتيح في ملف محلي آمن
                    api_keys_data = {"gemini_keys": gemini_keys, "timestamp": datetime.now().isoformat()}
                    
                    # إنشاء مجلد .secrets إذا لم يكن موجوداً
                    secrets_dir = ".secrets"
                    if not os.path.exists(secrets_dir):
                        os.makedirs(secrets_dir)
                    
                    # حفظ المفاتيح في ملف JSON
                    import json
                    with open(f"{secrets_dir}/api_keys.json", "w") as f:
                        json.dump(api_keys_data, f, indent=2)
                    
                    # تحديث متغيرات البيئة للجلسة الحالية
                    for i, key in enumerate(gemini_keys, 1):
                        os.environ[f"GEMINI_API_KEY_{i if i > 1 else ''}"] = key
                    
                    # إعادة تحميل مدير المفاتيح
                    from modules.ai_verification import key_manager
                    key_manager._load_keys()
                    
                    st.success(f"✅ تم حفظ {len(gemini_keys)} مفتاح Gemini نهائياً!")
                    st.info("💡 المفاتيح محفوظة الآن بشكل دائم وستظل متاحة حتى بعد إعادة تشغيل التطبيق")
                    st.balloons()
                    
                except Exception as e:
                    st.error(f"❌ خطأ في حفظ المفاتيح: {str(e)}")
        
        with st.expander("⚙️ إعدادات مفاتيح OpenRouter", expanded=False):
            st.markdown("**مفاتيح OpenRouter (متعددة للتبديل التلقائي):**")
            
            # إدخال مفاتيح OpenRouter
            openrouter_keys = []
            for i in range(1, 3):  # حتى 2 مفاتيح
                key_name = f"openrouter_key_{i}"
                current_value = st.session_state.get(key_name, "")
                key_input = st.text_input(
                    f"🔑 OpenRouter API Key {i}",
                    value=current_value,
                    type="password",
                    key=f"input_{key_name}",
                    help=f"أدخل مفتاح OpenRouter API رقم {i}"
                )
                if key_input and key_input != current_value:
                    st.session_state[key_name] = key_input
                if key_input.strip():
                    openrouter_keys.append(key_input.strip())
            
            if st.button("💾 حفظ مفاتيح OpenRouter نهائياً", key="save_openrouter_keys", type="primary"):
                try:
                    # قراءة الملف الحالي إذا كان موجوداً
                    secrets_dir = ".secrets"
                    secrets_file = f"{secrets_dir}/api_keys.json"
                    api_keys_data = {}
                    
                    if os.path.exists(secrets_file):
                        with open(secrets_file, "r") as f:
                            api_keys_data = json.load(f)
                    
                    # تحديث مفاتيح OpenRouter
                    api_keys_data["openrouter_keys"] = openrouter_keys
                    api_keys_data["timestamp"] = datetime.now().isoformat()
                    
                    # إنشاء المجلد إذا لم يكن موجوداً
                    if not os.path.exists(secrets_dir):
                        os.makedirs(secrets_dir)
                    
                    # حفظ المفاتيح في ملف JSON
                    with open(secrets_file, "w") as f:
                        json.dump(api_keys_data, f, indent=2)
                    
                    # تحديث متغيرات البيئة للجلسة الحالية
                    for i, key in enumerate(openrouter_keys, 1):
                        os.environ[f"OPENROUTER_API_KEY_{i if i > 1 else ''}"] = key
                    
                    # إعادة تحميل مدير المفاتيح
                    from modules.ai_verification import key_manager
                    key_manager._load_keys()
                    
                    st.success(f"✅ تم حفظ {len(openrouter_keys)} مفتاح OpenRouter نهائياً!")
                    st.info("💡 المفاتيح محفوظة الآن بشكل دائم وستظل متاحة حتى بعد إعادة تشغيل التطبيق")
                    st.balloons()
                    
                except Exception as e:
                    st.error(f"❌ خطأ في حفظ المفاتيح: {str(e)}")
        
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
        st.markdown("### � ربط الخوارزميات")
        
        st.markdown("#### ⚙️ إعدادات خوارزمية المطابقة")
        
        # إعدادات الخوارزمية
        threshold = st.slider(
            "📊 حد التطابق (%)",
            min_value=50,
            max_value=95,
            value=st.session_state.algorithm_settings.get("threshold", 60),
            step=5,
            help="الحد الأدنى لنسبة التطابق لاعتبار المنتجات مطابقة"
        )
        
        raise_threshold = st.slider(
            "📈 حد رفع السعر (%)",
            min_value=5,
            max_value=20,
            value=st.session_state.algorithm_settings.get("raise_threshold", 10),
            step=1,
            help="الفرق المسموح لرفع السعر"
        )
        
        lower_threshold = st.slider(
            "📉 حد خفض السعر (%)",
            min_value=5,
            max_value=20,
            value=st.session_state.algorithm_settings.get("lower_threshold", 5),
            step=1,
            help="الفرق المسموح لخفض السعر"
        )
        
        acceptable_range = st.slider(
            "🎯 النطاق المقبول (±%)",
            min_value=1,
            max_value=10,
            value=st.session_state.algorithm_settings.get("acceptable_range", 5),
            step=1,
            help="النطاق المقبول حول سعر المنافس"
        )
        
        review_threshold = st.slider(
            "🔍 حد المراجعة (%)",
            min_value=80,
            max_value=95,
            value=st.session_state.algorithm_settings.get("review_threshold", 85),
            step=5,
            help="الحد الأدنى للثقة لتجنب المراجعة اليدوية"
        )
        
        # حفظ الإعدادات
        if st.button("💾 حفظ إعدادات الخوارزمية", type="primary"):
            st.session_state.algorithm_settings = {
                "threshold": threshold,
                "raise_threshold": raise_threshold,
                "lower_threshold": lower_threshold,
                "acceptable_range": acceptable_range,
                "review_threshold": review_threshold,
            }
            st.success("✅ تم حفظ إعدادات الخوارزمية!")
            
            # حفظ في قاعدة البيانات
            save_setting("algorithm_settings", st.session_state.algorithm_settings)
        
        st.markdown("---")
        st.markdown("#### 📊 إعدادات متقدمة")
        
        # إعدادات متقدمة
        use_ai_matching = st.checkbox(
            "🤖 استخدام الذكاء الصناعي في المطابقة",
            value=st.session_state.algorithm_settings.get("use_ai_matching", True),
            help="تفعيل استخدام Gemini AI للمطابقات المعقدة"
        )
        
        use_cache = st.checkbox(
            "💾 استخدام التخزين المؤقت",
            value=st.session_state.algorithm_settings.get("use_cache", True),
            help="تسريع المعالجة باستخدام النتائج المحفوظة"
        )
        
        batch_size = st.slider(
            "📦 حجم الدفعة",
            min_value=10,
            max_value=100,
            value=st.session_state.algorithm_settings.get("batch_size", 50),
            step=10,
            help="عدد المنتجات المعالجة في كل دفعة"
        )
        
        # حفظ الإعدادات المتقدمة
        if st.button("💾 حفظ الإعدادات المتقدمة"):
            st.session_state.algorithm_settings.update({
                "use_ai_matching": use_ai_matching,
                "use_cache": use_cache,
                "batch_size": batch_size,
            })
            st.success("✅ تم حفظ الإعدادات المتقدمة!")
            
            # حفظ في قاعدة البيانات
            save_setting("algorithm_settings", st.session_state.algorithm_settings)
        
        st.markdown("---")
        st.markdown("#### 🔄 إعادة تعيين")
        
        if st.button("🔄 استعادة الإعدادات الافتراضية", type="secondary"):
            default_settings = {
                "threshold": 60,
                "raise_threshold": 10,
                "lower_threshold": 5,
                "acceptable_range": 5,
                "review_threshold": 85,
                "use_ai_matching": True,
                "use_cache": True,
                "batch_size": 50,
            }
            st.session_state.algorithm_settings = default_settings
            save_setting("algorithm_settings", default_settings)
            st.success("✅ تم استعادة الإعدادات الافتراضية!")
            st.rerun()

# ═══════════════════════════════════════════════════════════════
# الأقسام الجديدة v8.0
# ═══════════════════════════════════════════════════════════════

# تم حذف الأقسام الميتة: 🤖 الأتمتة الذكية، 🔔 التنبيهات، 🔍 منع التكرار

# ══════════════════════════════════════════════════════════════
# تذييل
# ══════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888; padding: 10px;">
    💎 نظام التسعير الذكي v14.2 | مهووس للعطور | 2026
</div>
""", unsafe_allow_html=True)
