"""
🎨 التحسينات البصرية الراقية
نظام التسعير الذكي v8.0
"""

import streamlit as st

def apply_custom_styles():
    """
    تطبيق CSS مخصص راقي على التطبيق
    """
    st.markdown("""
    <style>
    /* ============================================
       1. الألوان الراقية حسب الحالة
       ============================================ */
    
    /* رفع السعر - أحمر ناعم */
    .status-raise {
        background-color: #FFF5F5 !important;
        color: #C53030 !important;
        border-left: 4px solid #C53030 !important;
        padding: 12px !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    
    .status-raise:hover {
        background-color: #FED7D7 !important;
        transform: translateX(-5px) !important;
        box-shadow: 0 4px 12px rgba(197, 48, 48, 0.15) !important;
    }
    
    /* خفض السعر - برتقالي ناعم */
    .status-lower {
        background-color: #FFFBEB !important;
        color: #92400E !important;
        border-left: 4px solid #D97706 !important;
        padding: 12px !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    
    .status-lower:hover {
        background-color: #FEF3C7 !important;
        transform: translateX(-5px) !important;
        box-shadow: 0 4px 12px rgba(217, 119, 6, 0.15) !important;
    }
    
    /* موافق - أخضر ناعم */
    .status-ok {
        background-color: #F0FDF4 !important;
        color: #166534 !important;
        border-left: 4px solid #16A34A !important;
        padding: 12px !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    
    .status-ok:hover {
        background-color: #DCFCE7 !important;
        transform: translateX(-5px) !important;
        box-shadow: 0 4px 12px rgba(22, 163, 74, 0.15) !important;
    }
    
    /* مفقود - أزرق ناعم */
    .status-missing {
        background-color: #EFF6FF !important;
        color: #1E40AF !important;
        border-left: 4px solid #3B82F6 !important;
        padding: 12px !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    
    .status-missing:hover {
        background-color: #DBEAFE !important;
        transform: translateX(-5px) !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15) !important;
    }
    
    /* ============================================
       2. الجداول - أكبر وأوضح
       ============================================ */
    
    /* حجم خط أكبر للجداول */
    .dataframe {
        font-size: 1.1rem !important;
        width: 100% !important;
    }
    
    .dataframe th {
        background-color: #2D3748 !important;
        color: white !important;
        font-size: 1.2rem !important;
        font-weight: 700 !important;
        padding: 16px !important;
        text-align: center !important;
        border-bottom: 3px solid #4A5568 !important;
    }
    
    .dataframe td {
        font-size: 1.1rem !important;
        padding: 14px !important;
        border-bottom: 1px solid #E2E8F0 !important;
        transition: background-color 0.2s ease !important;
    }
    
    .dataframe tr:hover td {
        background-color: #F7FAFC !important;
    }
    
    /* عرض كامل للجداول */
    .stDataFrame {
        width: 100% !important;
    }
    
    /* ============================================
       3. البطاقات والعناصر
       ============================================ */
    
    /* بطاقات راقية */
    .card {
        background: white;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border: 1px solid #E2E8F0;
        transition: all 0.3s ease;
    }
    
    .card:hover {
        box-shadow: 0 8px 24px rgba(0,0,0,0.12);
        transform: translateY(-4px);
    }
    
    /* عناوين راقية */
    .section-title {
        font-size: 2rem;
        font-weight: 700;
        color: #1A202C;
        margin-bottom: 24px;
        padding-bottom: 12px;
        border-bottom: 3px solid #4299E1;
    }
    
    .subsection-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #2D3748;
        margin-top: 32px;
        margin-bottom: 16px;
    }
    
    /* ============================================
       4. الأزرار
       ============================================ */
    
    .stButton > button {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        padding: 12px 24px !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
    }
    
    /* ============================================
       5. المقاييس (Metrics)
       ============================================ */
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 24px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 12px 0;
    }
    
    .metric-label {
        font-size: 1rem;
        opacity: 0.9;
    }
    
    /* ============================================
       6. التنبيهات
       ============================================ */
    
    .alert-success {
        background-color: #F0FDF4;
        border-left: 4px solid #16A34A;
        color: #166534;
        padding: 16px;
        border-radius: 8px;
        margin: 16px 0;
    }
    
    .alert-warning {
        background-color: #FFFBEB;
        border-left: 4px solid #D97706;
        color: #92400E;
        padding: 16px;
        border-radius: 8px;
        margin: 16px 0;
    }
    
    .alert-error {
        background-color: #FFF5F5;
        border-left: 4px solid #C53030;
        color: #C53030;
        padding: 16px;
        border-radius: 8px;
        margin: 16px 0;
    }
    
    .alert-info {
        background-color: #EFF6FF;
        border-left: 4px solid #3B82F6;
        color: #1E40AF;
        padding: 16px;
        border-radius: 8px;
        margin: 16px 0;
    }
    
    /* ============================================
       7. الشريط الجانبي
       ============================================ */
    
    .css-1d391kg {
        background-color: #F7FAFC;
    }
    
    .sidebar-section {
        background: white;
        padding: 16px;
        border-radius: 8px;
        margin-bottom: 16px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* ============================================
       8. حالة الاتصال
       ============================================ */
    
    .connection-status {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
    }
    
    .connection-connected {
        background-color: #F0FDF4;
        color: #166534;
    }
    
    .connection-disconnected {
        background-color: #FFF5F5;
        color: #C53030;
    }
    
    .connection-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        animation: pulse 2s infinite;
    }
    
    .connection-dot.connected {
        background-color: #16A34A;
    }
    
    .connection-dot.disconnected {
        background-color: #DC2626;
    }
    
    @keyframes pulse {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.5;
        }
    }
    
    /* ============================================
       9. التقدم والعدادات
       ============================================ */
    
    .progress-container {
        background-color: #E2E8F0;
        border-radius: 10px;
        height: 24px;
        overflow: hidden;
        position: relative;
    }
    
    .progress-bar {
        background: linear-gradient(90deg, #4299E1 0%, #667eea 100%);
        height: 100%;
        transition: width 0.5s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    /* ============================================
       10. تحسينات عامة
       ============================================ */
    
    /* إزالة الحواف الحادة */
    * {
        border-radius: inherit;
    }
    
    /* تحسين القراءة */
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        line-height: 1.6;
        color: #2D3748;
    }
    
    /* تحسين التباعد */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* تحسين العناصر المدخلة */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select {
        font-size: 1.1rem !important;
        padding: 12px !important;
        border-radius: 8px !important;
        border: 2px solid #E2E8F0 !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #4299E1 !important;
        box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.1) !important;
    }
    
    /* تحسين الـ Expander */
    .streamlit-expanderHeader {
        font-size: 1.2rem !important;
        font-weight: 600 !important;
        color: #2D3748 !important;
        background-color: #F7FAFC !important;
        border-radius: 8px !important;
        padding: 16px !important;
    }
    
    /* تحسين الـ Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        font-size: 1.1rem;
        font-weight: 600;
        padding: 12px 24px;
        border-radius: 8px 8px 0 0;
    }
    
    /* إخفاء العناصر غير الضرورية */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* تحسين الـ Spinner */
    .stSpinner > div {
        border-top-color: #4299E1 !important;
    }
    
    </style>
    """, unsafe_allow_html=True)

def render_status_badge(status: str, text: str = None) -> str:
    """
    إنشاء شارة حالة ملونة
    
    Args:
        status: نوع الحالة ('raise', 'lower', 'ok', 'missing')
        text: النص المعروض (اختياري)
    
    Returns:
        HTML للشارة
    """
    status_classes = {
        'raise': 'status-raise',
        'lower': 'status-lower',
        'ok': 'status-ok',
        'missing': 'status-missing'
    }
    
    status_icons = {
        'raise': '🔴',
        'lower': '🟡',
        'ok': '🟢',
        'missing': '🔵'
    }
    
    status_texts = {
        'raise': 'رفع السعر',
        'lower': 'خفض السعر',
        'ok': 'موافق',
        'missing': 'مفقود'
    }
    
    css_class = status_classes.get(status, 'status-ok')
    icon = status_icons.get(status, '⚪')
    display_text = text or status_texts.get(status, status)
    
    return f'<div class="{css_class}">{icon} {display_text}</div>'

def render_connection_status(connected: bool, service_name: str) -> str:
    """
    إنشاء مؤشر حالة الاتصال
    
    Args:
        connected: True إذا كان متصل
        service_name: اسم الخدمة
    
    Returns:
        HTML لمؤشر الاتصال
    """
    if connected:
        return f'''
        <div class="connection-status connection-connected">
            <span class="connection-dot connected"></span>
            <span>{service_name} متصل</span>
        </div>
        '''
    else:
        return f'''
        <div class="connection-status connection-disconnected">
            <span class="connection-dot disconnected"></span>
            <span>{service_name} غير متصل</span>
        </div>
        '''

def render_metric_card(value: str, label: str, icon: str = "📊") -> str:
    """
    إنشاء بطاقة مقياس
    
    Args:
        value: القيمة
        label: التسمية
        icon: الأيقونة
    
    Returns:
        HTML للبطاقة
    """
    return f'''
    <div class="metric-card">
        <div style="font-size: 2rem;">{icon}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
    </div>
    '''

def render_progress_bar(percentage: float, label: str = "") -> str:
    """
    إنشاء شريط تقدم
    
    Args:
        percentage: النسبة المئوية (0-100)
        label: التسمية
    
    Returns:
        HTML لشريط التقدم
    """
    return f'''
    <div class="progress-container">
        <div class="progress-bar" style="width: {percentage}%;">
            {label} {percentage:.1f}%
        </div>
    </div>
    '''
