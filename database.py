"""
💾 نظام قاعدة البيانات - Database System
====================================
نظام متكامل لتخزين البيانات ومنع التكرارات وتتبع العمليات
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional

# ══════════════════════════════════════════════════════════════
# إعدادات قاعدة البيانات
# ══════════════════════════════════════════════════════════════

DB_PATH = "perfume_erp.db"

# ══════════════════════════════════════════════════════════════
# إنشاء الجداول
# ══════════════════════════════════════════════════════════════

def init_database():
    """إنشاء قاعدة البيانات والجداول"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # جدول العمليات (سجل كل عملية)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS operations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            operation_type TEXT NOT NULL,
            product_name TEXT,
            old_price REAL,
            new_price REAL,
            status TEXT NOT NULL,
            details TEXT,
            user_action TEXT
        )
    """)
    
    # جدول المنتجات المعدلة (لمنع التكرار)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS modified_products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT UNIQUE NOT NULL,
            last_modified TEXT NOT NULL,
            modification_count INTEGER DEFAULT 1,
            last_operation TEXT
        )
    """)
    
    # جدول المنتجات المضافة (لمنع التكرار)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS added_products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT UNIQUE NOT NULL,
            added_date TEXT NOT NULL,
            source TEXT,
            status TEXT DEFAULT 'pending'
        )
    """)
    
    # جدول قرارات المنتجات المفقودة (إضافة/تأجيل/تجاهل)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS missing_decisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            decision TEXT NOT NULL,
            decision_date TEXT NOT NULL,
            competitor_name TEXT,
            competitor_price REAL,
            suggested_price REAL,
            notes TEXT,
            UNIQUE(product_name, competitor_name)
        )
    """)
    
    conn.commit()
    conn.close()

# ══════════════════════════════════════════════════════════════
# تسجيل العمليات
# ══════════════════════════════════════════════════════════════

def log_operation(
    operation_type: str,
    product_name: str = None,
    old_price: float = None,
    new_price: float = None,
    status: str = "success",
    details: Dict = None,
    user_action: str = None
) -> int:
    """
    تسجيل عملية جديدة
    
    Args:
        operation_type: نوع العملية (price_update, product_add, ai_check, etc.)
        product_name: اسم المنتج
        old_price: السعر القديم
        new_price: السعر الجديد
        status: حالة العملية (success, failed, pending)
        details: تفاصيل إضافية (JSON)
        user_action: الإجراء الذي اتخذه المستخدم
    
    Returns:
        int: معرف العملية
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    details_json = json.dumps(details, ensure_ascii=False) if details else None
    
    cursor.execute("""
        INSERT INTO operations 
        (timestamp, operation_type, product_name, old_price, new_price, status, details, user_action)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (timestamp, operation_type, product_name, old_price, new_price, status, details_json, user_action))
    
    operation_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return operation_id

# ══════════════════════════════════════════════════════════════
# منع التكرارات
# ══════════════════════════════════════════════════════════════

def is_product_modified(product_name: str) -> bool:
    """التحقق من أن المنتج تم تعديله مسبقاً"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id FROM modified_products WHERE product_name = ?
    """, (product_name,))
    
    result = cursor.fetchone()
    conn.close()
    
    return result is not None

def mark_product_modified(product_name: str, operation: str):
    """تسجيل المنتج كمعدل"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("""
        INSERT OR REPLACE INTO modified_products 
        (product_name, last_modified, modification_count, last_operation)
        VALUES (
            ?,
            ?,
            COALESCE((SELECT modification_count + 1 FROM modified_products WHERE product_name = ?), 1),
            ?
        )
    """, (product_name, timestamp, product_name, operation))
    
    conn.commit()
    conn.close()

def is_product_added(product_name: str) -> bool:
    """التحقق من أن المنتج تم إضافته مسبقاً"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id FROM added_products WHERE product_name = ?
    """, (product_name,))
    
    result = cursor.fetchone()
    conn.close()
    
    return result is not None

def mark_product_added(product_name: str, source: str = "manual"):
    """تسجيل المنتج كمضاف"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        cursor.execute("""
            INSERT INTO added_products (product_name, added_date, source)
            VALUES (?, ?, ?)
        """, (product_name, timestamp, source))
        
        conn.commit()
    except sqlite3.IntegrityError:
        # المنتج موجود بالفعل
        pass
    
    conn.close()

# ══════════════════════════════════════════════════════════════
# استرجاع البيانات
# ══════════════════════════════════════════════════════════════

def get_operations(
    limit: int = 100,
    operation_type: str = None,
    status: str = None
) -> List[Dict]:
    """
    استرجاع سجل العمليات
    
    Args:
        limit: عدد العمليات المطلوبة
        operation_type: تصفية حسب نوع العملية
        status: تصفية حسب الحالة
    
    Returns:
        List[Dict]: قائمة العمليات
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    query = "SELECT * FROM operations WHERE 1=1"
    params = []
    
    if operation_type:
        query += " AND operation_type = ?"
        params.append(operation_type)
    
    if status:
        query += " AND status = ?"
        params.append(status)
    
    query += " ORDER BY id DESC LIMIT ?"
    params.append(limit)
    
    cursor.execute(query, params)
    
    columns = [desc[0] for desc in cursor.description]
    operations = []
    
    for row in cursor.fetchall():
        op = dict(zip(columns, row))
        if op['details']:
            try:
                op['details'] = json.loads(op['details'])
            except:
                pass
        operations.append(op)
    
    conn.close()
    return operations

def get_modified_products() -> List[Dict]:
    """استرجاع قائمة المنتجات المعدلة"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM modified_products ORDER BY last_modified DESC
    """)
    
    columns = [desc[0] for desc in cursor.description]
    products = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    conn.close()
    return products

def get_added_products() -> List[Dict]:
    """استرجاع قائمة المنتجات المضافة"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM added_products ORDER BY added_date DESC
    """)
    
    columns = [desc[0] for desc in cursor.description]
    products = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    conn.close()
    return products

# ══════════════════════════════════════════════════════════════
# إحصائيات
# ══════════════════════════════════════════════════════════════

def get_statistics() -> Dict:
    """الحصول على إحصائيات قاعدة البيانات"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # عدد العمليات
    cursor.execute("SELECT COUNT(*) FROM operations")
    total_operations = cursor.fetchone()[0]
    
    # عدد العمليات الناجحة
    cursor.execute("SELECT COUNT(*) FROM operations WHERE status = 'success'")
    successful_operations = cursor.fetchone()[0]
    
    # عدد المنتجات المعدلة
    cursor.execute("SELECT COUNT(*) FROM modified_products")
    modified_count = cursor.fetchone()[0]
    
    # عدد المنتجات المضافة
    cursor.execute("SELECT COUNT(*) FROM added_products")
    added_count = cursor.fetchone()[0]
    
    # آخر عملية
    cursor.execute("SELECT timestamp, operation_type FROM operations ORDER BY id DESC LIMIT 1")
    last_op = cursor.fetchone()
    
    conn.close()
    
    return {
        "total_operations": total_operations,
        "successful_operations": successful_operations,
        "modified_products": modified_count,
        "added_products": added_count,
        "last_operation": {
            "timestamp": last_op[0] if last_op else None,
            "type": last_op[1] if last_op else None
        }
    }

# ══════════════════════════════════════════════════════════════
# تنظيف البيانات
# ══════════════════════════════════════════════════════════════

def clear_old_operations(days: int = 30):
    """حذف العمليات القديمة"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        DELETE FROM operations 
        WHERE datetime(timestamp) < datetime('now', '-' || ? || ' days')
    """, (days,))
    
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    
    return deleted

# ══════════════════════════════════════════════════════════════
# تهيئة عند الاستيراد
# ══════════════════════════════════════════════════════════════

# إنشاء قاعدة البيانات تلقائياً
init_database()
