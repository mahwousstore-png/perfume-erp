"""
🔐 نظام المستخدمين والصلاحيات
نظام التسعير الذكي v8.0
"""

import streamlit as st
import hashlib
from typing import Optional, Dict, List

# ============================================
# الأدوار والصلاحيات
# ============================================

ROLES = {
    'admin': {
        'name': 'المدير',
        'permissions': ['all']  # كل الصلاحيات
    },
    'purchase_manager': {
        'name': 'مدير المشتريات',
        'permissions': ['view_products', 'add_purchase', 'manage_suppliers', 'view_purchase_reports']
    },
    'pricing_manager': {
        'name': 'مدير التسعير',
        'permissions': ['view_products', 'upload_files', 'view_results', 'suggest_prices']
    },
    'inventory': {
        'name': 'موظف المخزون',
        'permissions': ['view_products', 'update_stock', 'add_products']
    },
    'accountant': {
        'name': 'المحاسب',
        'permissions': ['view_reports', 'add_expenses', 'view_costs']
    }
    },
    'viewer': {
        'name': 'مشاهد',
        'permissions': ['view_products', 'view_reports']
    }
}

# ============================================
# دوال المصادقة
# ============================================

def hash_password(password: str) -> str:
    """
    تشفير كلمة المرور باستخدام SHA256
    """
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """
    التحقق من كلمة المرور
    """
    return hash_password(password) == hashed

def authenticate(username: str, password: str) -> Optional[Dict]:
    """
    مصادقة المستخدم
    
    Returns:
        Dict مع معلومات المستخدم إذا نجحت المصادقة، None إذا فشلت
    """
    try:
        # للتطوير فقط - مستخدم افتراضي
        # في الإنتاج، يجب الاستعلام من Supabase
        if username == "admin" and password == "admin123":
            return {
                'id': 1,
                'username': 'admin',
                'full_name': 'المدير',
                'role': 'admin',
                'email': 'admin@mahwoos.com'
            }
        
        # TODO: الاستعلام من Supabase
        # من supabase import get_supabase
        # supabase = get_supabase()
        # result = supabase.table('users').select('*').eq('username', username).eq('is_active', True).execute()
        # if result.data:
        #     user = result.data[0]
        #     if verify_password(password, user['password_hash']):
        #         return user
        
        return None
    except Exception as e:
        st.error(f"خطأ في المصادقة: {str(e)}")
        return None

def check_permission(permission: str) -> bool:
    """
    التحقق من صلاحية المستخدم الحالي
    
    Args:
        permission: اسم الصلاحية المطلوبة
    
    Returns:
        True إذا كان المستخدم لديه الصلاحية
    """
    if not st.session_state.get('logged_in', False):
        return False
    
    role = st.session_state.get('role', 'viewer')
    
    # المدير لديه كل الصلاحيات
    if role == 'admin':
        return True
    
    # التحقق من صلاحيات الدور
    role_permissions = ROLES.get(role, {}).get('permissions', [])
    return permission in role_permissions or 'all' in role_permissions

def require_permission(permission: str):
    """
    Decorator للتحقق من الصلاحية قبل تنفيذ الدالة
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not check_permission(permission):
                st.error("⛔ ليس لديك صلاحية للوصول إلى هذه الميزة")
                st.stop()
            return func(*args, **kwargs)
        return wrapper
    return decorator

def log_action(action: str, details: Dict = None):
    """
    تسجيل عملية في Audit Log
    
    Args:
        action: نوع العملية (مثل 'updated_price', 'sent_to_salla')
        details: تفاصيل إضافية (Dict)
    """
    if not st.session_state.get('logged_in', False):
        return
    
    try:
        user_id = st.session_state.get('user', {}).get('id')
        
        # TODO: حفظ في Supabase
        # من supabase import get_supabase
        # supabase = get_supabase()
        # supabase.table('audit_log').insert({
        #     'user_id': user_id,
        #     'action': action,
        #     'details': details,
        #     'ip_address': get_client_ip(),
        #     'timestamp': datetime.now().isoformat()
        # }).execute()
        
        # للتطوير: طباعة في Console
        print(f"[AUDIT] User {user_id} - {action}: {details}")
        
    except Exception as e:
        print(f"خطأ في تسجيل العملية: {str(e)}")

# ============================================
# واجهة تسجيل الدخول
# ============================================

def show_login_page():
    """
    عرض صفحة تسجيل الدخول
    """
    st.markdown("""
    <style>
    .login-container {
        max-width: 400px;
        margin: 100px auto;
        padding: 40px;
        background: white;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .login-title {
        text-align: center;
        color: #2D3748;
        font-size: 28px;
        font-weight: bold;
        margin-bottom: 30px;
    }
    .login-subtitle {
        text-align: center;
        color: #718096;
        font-size: 14px;
        margin-bottom: 30px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<div class="login-title">🔐 تسجيل الدخول</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-subtitle">نظام التسعير الذكي v8.0</div>', unsafe_allow_html=True)
        
        username = st.text_input("اسم المستخدم", key="login_username")
        password = st.text_input("كلمة المرور", type="password", key="login_password")
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("🔓 دخول", use_container_width=True, type="primary"):
                if username and password:
                    user = authenticate(username, password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user = user
                        st.session_state.role = user['role']
                        st.session_state.username = user['username']
                        
                        # تسجيل عملية الدخول
                        log_action('login', {'username': username})
                        
                        st.success(f"مرحباً {user['full_name']}! 👋")
                        st.rerun()
                    else:
                        st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة")
                else:
                    st.warning("⚠️ الرجاء إدخال اسم المستخدم وكلمة المرور")
        
        with col_btn2:
            if st.button("❓ نسيت كلمة المرور", use_container_width=True):
                st.info("📧 الرجاء التواصل مع المدير")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # معلومات للتطوير
        with st.expander("ℹ️ معلومات تسجيل الدخول (للتطوير)"):
            st.code("""
اسم المستخدم: admin
كلمة المرور: admin123
الدور: المدير (كل الصلاحيات)
            """)

def show_logout_button():
    """
    عرض زر تسجيل الخروج في الشريط الجانبي
    """
    if st.session_state.get('logged_in', False):
        user = st.session_state.get('user', {})
        role_name = ROLES.get(st.session_state.get('role', 'viewer'), {}).get('name', 'مستخدم')
        
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"**👤 {user.get('full_name', 'مستخدم')}**")
        st.sidebar.markdown(f"*{role_name}*")
        
        if st.sidebar.button("🚪 تسجيل خروج", use_container_width=True):
            # تسجيل عملية الخروج
            log_action('logout', {'username': st.session_state.get('username')})
            
            # مسح الجلسة
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            
            st.rerun()

def init_session():
    """
    تهيئة الجلسة
    """
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user' not in st.session_state:
        st.session_state.user = {}
    if 'role' not in st.session_state:
        st.session_state.role = 'viewer'

# ============================================
# دوال مساعدة
# ============================================

def get_user_role_name() -> str:
    """
    الحصول على اسم دور المستخدم الحالي
    """
    role = st.session_state.get('role', 'viewer')
    return ROLES.get(role, {}).get('name', 'مستخدم')

def is_admin() -> bool:
    """
    التحقق من أن المستخدم الحالي مدير
    """
    return st.session_state.get('role') == 'admin'

def get_available_sections() -> List[str]:
    """
    الحصول على الأقسام المتاحة للمستخدم الحالي
    """
    role = st.session_state.get('role', 'viewer')
    permissions = ROLES.get(role, {}).get('permissions', [])
    
    sections = []
    
    if 'all' in permissions or 'upload_files' in permissions:
        sections.append('رفع الملفات')
    
    if 'all' in permissions or 'view_results' in permissions:
        sections.append('النتائج')
    
    if 'all' in permissions or 'add_purchase' in permissions:
        sections.append('المشتريات')
    
    if 'all' in permissions or 'manage_suppliers' in permissions:
        sections.append('الموردين')
    
    if 'all' in permissions or 'add_expenses' in permissions:
        sections.append('المصروفات')
    
    if 'all' in permissions or 'view_reports' in permissions:
        sections.append('التقارير')
    
    if 'all' in permissions:
        sections.append('الإعدادات')
        sections.append('المستخدمين')
    
    return sections
