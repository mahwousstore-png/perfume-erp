"""
database.py - قاعدة البيانات المركزية للنظام
SQLite مع إدارة كاملة للمنتجات والمنافسين والمحاسبة
"""
import sqlite3
import os
from datetime import datetime, date


DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "perfume_erp.db"
)


def get_connection():
    """إنشاء اتصال بقاعدة البيانات."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_database():
    """تهيئة جميع الجداول."""
    conn = get_connection()
    c = conn.cursor()

    # جدول المنتجات الرئيسي
    c.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            brand TEXT DEFAULT '',
            category TEXT DEFAULT '',
            size_ml REAL DEFAULT 0,
            product_type TEXT DEFAULT 'retail',
            cost_price REAL DEFAULT 0,
            sell_price REAL DEFAULT 0,
            sku TEXT DEFAULT '',
            description TEXT DEFAULT '',
            image_url TEXT DEFAULT '',
            status TEXT DEFAULT 'active',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # جدول المنافسين
    c.execute("""
        CREATE TABLE IF NOT EXISTS competitors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            website TEXT DEFAULT '',
            notes TEXT DEFAULT '',
            risk_level TEXT DEFAULT 'medium',
            last_updated TEXT DEFAULT CURRENT_TIMESTAMP,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # جدول منتجات المنافسين
    c.execute("""
        CREATE TABLE IF NOT EXISTS competitor_products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            competitor_id INTEGER NOT NULL,
            product_name TEXT NOT NULL,
            brand TEXT DEFAULT '',
            category TEXT DEFAULT '',
            size_ml REAL DEFAULT 0,
            product_type TEXT DEFAULT 'retail',
            price REAL DEFAULT 0,
            original_name TEXT DEFAULT '',
            source_url TEXT DEFAULT '',
            last_updated TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (competitor_id) REFERENCES competitors(id)
                ON DELETE CASCADE
        )
    """)

    # جدول سجل الأسعار
    c.execute("""
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            competitor_product_id INTEGER,
            old_price REAL DEFAULT 0,
            new_price REAL DEFAULT 0,
            change_type TEXT DEFAULT '',
            recorded_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # جدول المقارنات
    c.execute("""
        CREATE TABLE IF NOT EXISTS comparisons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            competitor_product_id INTEGER NOT NULL,
            my_price REAL DEFAULT 0,
            competitor_price REAL DEFAULT 0,
            price_diff REAL DEFAULT 0,
            diff_percent REAL DEFAULT 0,
            recommendation TEXT DEFAULT '',
            risk_level TEXT DEFAULT 'low',
            gemini_note TEXT DEFAULT '',
            compared_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id),
            FOREIGN KEY (competitor_product_id)
                REFERENCES competitor_products(id)
        )
    """)

    # جدول المحاسبة والمصروفات
    c.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            amount REAL DEFAULT 0,
            expense_type TEXT DEFAULT 'general',
            expense_date TEXT DEFAULT CURRENT_TIMESTAMP,
            notes TEXT DEFAULT '',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # جدول المحتوى المنتج
    c.execute("""
        CREATE TABLE IF NOT EXISTS content_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            content_type TEXT DEFAULT '',
            content_text TEXT DEFAULT '',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)

    # جدول سجل الأتمتة
    c.execute("""
        CREATE TABLE IF NOT EXISTS automation_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action_type TEXT DEFAULT '',
            details TEXT DEFAULT '',
            status TEXT DEFAULT 'success',
            executed_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # جدول الإعدادات
    c.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT DEFAULT ''
        )
    """)

    conn.commit()
    conn.close()


# ===== عمليات المنتجات =====

def add_product(name, brand="", category="", size_ml=0,
                product_type="retail", cost_price=0,
                sell_price=0, sku="", description="",
                image_url=""):
    """إضافة منتج جديد."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO products
        (name, brand, category, size_ml, product_type,
         cost_price, sell_price, sku, description, image_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, brand, category, size_ml, product_type,
          cost_price, sell_price, sku, description, image_url))
    pid = c.lastrowid
    conn.commit()
    conn.close()
    return pid


def update_product(pid, **kwargs):
    """تحديث منتج."""
    conn = get_connection()
    allowed = [
        "name", "brand", "category", "size_ml",
        "product_type", "cost_price", "sell_price",
        "sku", "description", "image_url", "status"
    ]
    sets = []
    vals = []
    for k, v in kwargs.items():
        if k in allowed:
            sets.append(f"{k} = ?")
            vals.append(v)
    if sets:
        sets.append("updated_at = ?")
        vals.append(datetime.now().isoformat())
        vals.append(pid)
        query = f"UPDATE products SET {', '.join(sets)} WHERE id = ?"
        conn.execute(query, vals)
        conn.commit()
    conn.close()


def get_products(status=None, brand=None, category=None,
                 search=None):
    """جلب المنتجات مع فلترة."""
    conn = get_connection()
    query = "SELECT * FROM products WHERE 1=1"
    params = []
    if status:
        query += " AND status = ?"
        params.append(status)
    if brand:
        query += " AND brand = ?"
        params.append(brand)
    if category:
        query += " AND category = ?"
        params.append(category)
    if search:
        query += " AND (name LIKE ? OR brand LIKE ? OR sku LIKE ?)"
        s = f"%{search}%"
        params.extend([s, s, s])
    query += " ORDER BY name"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_product_by_id(pid):
    """جلب منتج واحد."""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM products WHERE id = ?", (pid,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def delete_product(pid):
    """حذف منتج."""
    conn = get_connection()
    conn.execute("DELETE FROM products WHERE id = ?", (pid,))
    conn.commit()
    conn.close()


def get_unique_brands():
    """جلب الماركات الفريدة."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT DISTINCT brand FROM products "
        "WHERE brand != '' ORDER BY brand"
    ).fetchall()
    conn.close()
    return [r["brand"] for r in rows]


def get_unique_categories():
    """جلب الأقسام الفريدة."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT DISTINCT category FROM products "
        "WHERE category != '' ORDER BY category"
    ).fetchall()
    conn.close()
    return [r["category"] for r in rows]


# ===== عمليات المنافسين =====

def add_competitor(name, website="", notes=""):
    """إضافة منافس جديد."""
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO competitors (name, website, notes) "
            "VALUES (?, ?, ?)",
            (name, website, notes)
        )
        cid = c.lastrowid
        conn.commit()
    except sqlite3.IntegrityError:
        row = conn.execute(
            "SELECT id FROM competitors WHERE name = ?", (name,)
        ).fetchone()
        cid = row["id"] if row else None
    conn.close()
    return cid


def get_competitors():
    """جلب جميع المنافسين."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT c.*, "
        "(SELECT COUNT(*) FROM competitor_products "
        " WHERE competitor_id = c.id) as product_count "
        "FROM competitors c ORDER BY c.name"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_competitor_by_id(cid):
    """جلب منافس واحد."""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM competitors WHERE id = ?", (cid,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def delete_competitor(cid):
    """حذف منافس ومنتجاته."""
    conn = get_connection()
    conn.execute("DELETE FROM competitors WHERE id = ?", (cid,))
    conn.commit()
    conn.close()


def add_competitor_product(competitor_id, product_name,
                           brand="", category="", size_ml=0,
                           product_type="retail", price=0,
                           original_name=""):
    """إضافة منتج منافس."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO competitor_products
        (competitor_id, product_name, brand, category,
         size_ml, product_type, price, original_name)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (competitor_id, product_name, brand, category,
          size_ml, product_type, price, original_name))
    cpid = c.lastrowid
    conn.commit()
    conn.close()
    return cpid


def get_competitor_products(competitor_id=None, search=None):
    """جلب منتجات المنافسين."""
    conn = get_connection()
    query = (
        "SELECT cp.*, c.name as competitor_name "
        "FROM competitor_products cp "
        "JOIN competitors c ON cp.competitor_id = c.id "
        "WHERE 1=1"
    )
    params = []
    if competitor_id:
        query += " AND cp.competitor_id = ?"
        params.append(competitor_id)
    if search:
        query += " AND (cp.product_name LIKE ? OR cp.brand LIKE ?)"
        s = f"%{search}%"
        params.extend([s, s])
    query += " ORDER BY cp.product_name"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def clear_competitor_products(competitor_id):
    """حذف جميع منتجات منافس معين."""
    conn = get_connection()
    conn.execute(
        "DELETE FROM competitor_products WHERE competitor_id = ?",
        (competitor_id,)
    )
    conn.commit()
    conn.close()


def update_competitor_timestamp(competitor_id):
    """تحديث وقت آخر تحديث للمنافس."""
    conn = get_connection()
    conn.execute(
        "UPDATE competitors SET last_updated = ? WHERE id = ?",
        (datetime.now().isoformat(), competitor_id)
    )
    conn.commit()
    conn.close()


# ===== عمليات المقارنات =====

def save_comparison(product_id, comp_product_id,
                    my_price, comp_price, price_diff,
                    diff_percent, recommendation,
                    risk_level, gemini_note=""):
    """حفظ مقارنة."""
    conn = get_connection()
    conn.execute("""
        INSERT INTO comparisons
        (product_id, competitor_product_id, my_price,
         competitor_price, price_diff, diff_percent,
         recommendation, risk_level, gemini_note)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (product_id, comp_product_id, my_price,
          comp_price, price_diff, diff_percent,
          recommendation, risk_level, gemini_note))
    conn.commit()
    conn.close()


def get_comparisons(recommendation=None):
    """جلب المقارنات."""
    conn = get_connection()
    query = """
        SELECT cmp.*,
               p.name as my_product_name,
               p.brand as my_brand,
               p.size_ml as my_size,
               p.cost_price,
               cp.product_name as comp_product_name,
               cp.brand as comp_brand,
               c.name as competitor_name
        FROM comparisons cmp
        JOIN products p ON cmp.product_id = p.id
        JOIN competitor_products cp
            ON cmp.competitor_product_id = cp.id
        JOIN competitors c ON cp.competitor_id = c.id
        WHERE 1=1
    """
    params = []
    if recommendation:
        query += " AND cmp.recommendation = ?"
        params.append(recommendation)
    query += " ORDER BY ABS(cmp.diff_percent) DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def clear_comparisons():
    """حذف جميع المقارنات."""
    conn = get_connection()
    conn.execute("DELETE FROM comparisons")
    conn.commit()
    conn.close()


# ===== عمليات المحاسبة =====

def add_expense(title, amount, expense_type="general",
                expense_date=None, notes=""):
    """إضافة مصروف."""
    if not expense_date:
        expense_date = date.today().isoformat()
    conn = get_connection()
    conn.execute(
        "INSERT INTO expenses "
        "(title, amount, expense_type, expense_date, notes) "
        "VALUES (?, ?, ?, ?, ?)",
        (title, amount, expense_type, expense_date, notes)
    )
    conn.commit()
    conn.close()


def get_expenses(expense_type=None, month=None):
    """جلب المصروفات."""
    conn = get_connection()
    query = "SELECT * FROM expenses WHERE 1=1"
    params = []
    if expense_type:
        query += " AND expense_type = ?"
        params.append(expense_type)
    if month:
        query += " AND expense_date LIKE ?"
        params.append(f"{month}%")
    query += " ORDER BY expense_date DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_expense(eid):
    """حذف مصروف."""
    conn = get_connection()
    conn.execute("DELETE FROM expenses WHERE id = ?", (eid,))
    conn.commit()
    conn.close()


# ===== عمليات المحتوى =====

def save_content(product_id, content_type, content_text):
    """حفظ محتوى منتج."""
    conn = get_connection()
    conn.execute(
        "INSERT INTO content_log "
        "(product_id, content_type, content_text) "
        "VALUES (?, ?, ?)",
        (product_id, content_type, content_text)
    )
    conn.commit()
    conn.close()


def get_content_log(product_id=None, content_type=None):
    """جلب سجل المحتوى."""
    conn = get_connection()
    query = (
        "SELECT cl.*, p.name as product_name "
        "FROM content_log cl "
        "LEFT JOIN products p ON cl.product_id = p.id "
        "WHERE 1=1"
    )
    params = []
    if product_id:
        query += " AND cl.product_id = ?"
        params.append(product_id)
    if content_type:
        query += " AND cl.content_type = ?"
        params.append(content_type)
    query += " ORDER BY cl.created_at DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ===== عمليات الأتمتة =====

def log_automation(action_type, details, status="success"):
    """تسجيل عملية أتمتة."""
    conn = get_connection()
    conn.execute(
        "INSERT INTO automation_log "
        "(action_type, details, status) "
        "VALUES (?, ?, ?)",
        (action_type, details, status)
    )
    conn.commit()
    conn.close()


def get_automation_log(limit=50):
    """جلب سجل الأتمتة."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM automation_log "
        "ORDER BY executed_at DESC LIMIT ?",
        (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ===== عمليات الإعدادات =====

def get_setting(key, default=""):
    """جلب إعداد."""
    conn = get_connection()
    row = conn.execute(
        "SELECT value FROM settings WHERE key = ?", (key,)
    ).fetchone()
    conn.close()
    return row["value"] if row else default


def set_setting(key, value):
    """حفظ إعداد."""
    conn = get_connection()
    conn.execute(
        "INSERT OR REPLACE INTO settings (key, value) "
        "VALUES (?, ?)",
        (key, str(value))
    )
    conn.commit()
    conn.close()


# ===== إحصائيات =====

def get_dashboard_stats():
    """جلب إحصائيات لوحة القيادة."""
    conn = get_connection()
    stats = {}

    row = conn.execute(
        "SELECT COUNT(*) as c FROM products WHERE status='active'"
    ).fetchone()
    stats["total_products"] = row["c"]

    row = conn.execute(
        "SELECT COUNT(*) as c FROM competitors"
    ).fetchone()
    stats["total_competitors"] = row["c"]

    row = conn.execute(
        "SELECT COUNT(*) as c FROM competitor_products"
    ).fetchone()
    stats["total_comp_products"] = row["c"]

    row = conn.execute(
        "SELECT COUNT(*) as c FROM comparisons"
    ).fetchone()
    stats["total_comparisons"] = row["c"]

    row = conn.execute(
        "SELECT COUNT(*) as c FROM comparisons "
        "WHERE recommendation = 'raise'"
    ).fetchone()
    stats["raise_count"] = row["c"]

    row = conn.execute(
        "SELECT COUNT(*) as c FROM comparisons "
        "WHERE recommendation = 'lower'"
    ).fetchone()
    stats["lower_count"] = row["c"]

    row = conn.execute(
        "SELECT COUNT(*) as c FROM comparisons "
        "WHERE recommendation = 'ok'"
    ).fetchone()
    stats["ok_count"] = row["c"]

    row = conn.execute(
        "SELECT COALESCE(SUM(sell_price - cost_price), 0) as p "
        "FROM products WHERE status='active' AND cost_price > 0"
    ).fetchone()
    stats["total_profit_margin"] = row["p"]

    row = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) as e FROM expenses"
    ).fetchone()
    stats["total_expenses"] = row["e"]

    conn.close()
    return stats


def import_products_from_df(df):
    """استيراد منتجات من DataFrame."""
    conn = get_connection()
    count = 0
    for _, row in df.iterrows():
        name = str(row.get("name", row.get("الاسم", ""))).strip()
        if not name:
            continue
        brand = str(row.get("brand", row.get("الماركة", ""))).strip()
        category = str(
            row.get("category", row.get("القسم", ""))
        ).strip()
        size_ml = float(row.get(
            "size_ml", row.get("الحجم", 0)
        ) or 0)
        cost_price = float(row.get(
            "cost_price", row.get("التكلفة", 0)
        ) or 0)
        sell_price = float(row.get(
            "sell_price", row.get("السعر", row.get("سعر البيع", 0))
        ) or 0)
        product_type = str(row.get(
            "product_type", row.get("النوع", "retail")
        )).strip().lower()
        sku = str(row.get("sku", row.get("SKU", ""))).strip()

        conn.execute("""
            INSERT INTO products
            (name, brand, category, size_ml, product_type,
             cost_price, sell_price, sku)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, brand, category, size_ml, product_type,
              cost_price, sell_price, sku))
        count += 1
    conn.commit()
    conn.close()
    return count


def import_competitor_products_from_df(df, competitor_id):
    """استيراد منتجات منافس من DataFrame."""
    conn = get_connection()
    count = 0
    for _, row in df.iterrows():
        name = str(row.get(
            "product_name", row.get("name", row.get("الاسم", ""))
        )).strip()
        if not name:
            continue
        brand = str(row.get("brand", row.get("الماركة", ""))).strip()
        category = str(
            row.get("category", row.get("القسم", ""))
        ).strip()
        size_ml = float(row.get(
            "size_ml", row.get("الحجم", 0)
        ) or 0)
        price = float(row.get(
            "price", row.get("السعر", 0)
        ) or 0)
        product_type = str(row.get(
            "product_type", row.get("النوع", "retail")
        )).strip().lower()

        conn.execute("""
            INSERT INTO competitor_products
            (competitor_id, product_name, brand, category,
             size_ml, product_type, price, original_name)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (competitor_id, name, brand, category,
              size_ml, product_type, price, name))
        count += 1
    conn.commit()
    conn.close()
    return count


# تهيئة قاعدة البيانات عند الاستيراد
init_database()
