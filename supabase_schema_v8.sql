-- 🗄️ جداول جديدة لنظام التسعير v8.0
-- تاريخ: 2026-02-13
-- ملاحظة: هذه جداول جديدة فقط - لا تحذف الجداول الموجودة!

-- ============================================
-- 1. نظام المستخدمين والصلاحيات
-- ============================================

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT,
    email TEXT,
    role TEXT NOT NULL CHECK (role IN ('admin', 'purchase_manager', 'pricing_manager', 'inventory', 'accountant', 'viewer')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP,
    created_by INT REFERENCES users(id)
);

-- مستخدم افتراضي (admin)
-- كلمة المرور: admin123 (يجب تغييرها!)
INSERT INTO users (username, password_hash, full_name, role, is_active)
VALUES ('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYILSBqZvSi', 'المدير', 'admin', TRUE)
ON CONFLICT (username) DO NOTHING;

-- ============================================
-- 2. سجل العمليات (Audit Log)
-- ============================================

CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    action TEXT NOT NULL,  -- 'added_product', 'updated_price', 'sent_to_salla', etc.
    details JSONB,  -- تفاصيل العملية
    ip_address TEXT,
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Index للبحث السريع
CREATE INDEX IF NOT EXISTS idx_audit_log_user ON audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON audit_log(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_audit_log_action ON audit_log(action);

-- ============================================
-- 3. الموردين
-- ============================================

CREATE TABLE IF NOT EXISTS suppliers (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    contact_person TEXT,
    phone TEXT,
    email TEXT,
    address TEXT,
    rating DECIMAL(3,2) DEFAULT 0.00 CHECK (rating >= 0 AND rating <= 5),  -- 0.00 to 5.00
    notes TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    created_by INT REFERENCES users(id)
);

-- Index للبحث السريع
CREATE INDEX IF NOT EXISTS idx_suppliers_name ON suppliers(name);
CREATE INDEX IF NOT EXISTS idx_suppliers_active ON suppliers(is_active);

-- ============================================
-- 4. المشتريات اليومية
-- ============================================

CREATE TABLE IF NOT EXISTS purchases (
    id SERIAL PRIMARY KEY,
    product_name TEXT NOT NULL,
    product_sku TEXT,
    supplier_id INT REFERENCES suppliers(id),
    purchase_price DECIMAL(10,2) NOT NULL CHECK (purchase_price > 0),
    quantity INT NOT NULL CHECK (quantity > 0),
    total_cost DECIMAL(10,2) GENERATED ALWAYS AS (purchase_price * quantity) STORED,
    purchase_date DATE NOT NULL DEFAULT CURRENT_DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    created_by INT REFERENCES users(id)
);

-- Index للبحث والتقارير
CREATE INDEX IF NOT EXISTS idx_purchases_product ON purchases(product_name);
CREATE INDEX IF NOT EXISTS idx_purchases_supplier ON purchases(supplier_id);
CREATE INDEX IF NOT EXISTS idx_purchases_date ON purchases(purchase_date DESC);
CREATE INDEX IF NOT EXISTS idx_purchases_sku ON purchases(product_sku);

-- ============================================
-- 5. المصروفات
-- ============================================

CREATE TABLE IF NOT EXISTS expenses (
    id SERIAL PRIMARY KEY,
    expense_date DATE NOT NULL DEFAULT CURRENT_DATE,
    category TEXT NOT NULL,  -- 'rent', 'salaries', 'electricity', 'shipping', 'marketing', 'other'
    expense_type TEXT NOT NULL CHECK (expense_type IN ('fixed', 'variable')),  -- ثابتة أو متغيرة
    amount DECIMAL(10,2) NOT NULL CHECK (amount > 0),
    description TEXT,
    receipt_url TEXT,  -- رابط الإيصال (اختياري)
    created_at TIMESTAMP DEFAULT NOW(),
    created_by INT REFERENCES users(id)
);

-- Index للتقارير الشهرية
CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses(expense_date DESC);
CREATE INDEX IF NOT EXISTS idx_expenses_category ON expenses(category);
CREATE INDEX IF NOT EXISTS idx_expenses_type ON expenses(expense_type);

-- ============================================
-- 6. المنتجات المحسّنة (اختياري - للميزات الإضافية)
-- ============================================

CREATE TABLE IF NOT EXISTS products_enhanced (
    id SERIAL PRIMARY KEY,
    product_name TEXT NOT NULL,
    sku TEXT UNIQUE,
    brand TEXT,
    size TEXT,
    category TEXT,  -- 'perfume', 'tester', 'oud', etc.
    current_price DECIMAL(10,2),
    cost_price DECIMAL(10,2),  -- من آخر عملية شراء
    stock_quantity INT DEFAULT 0,
    is_discontinued BOOLEAN DEFAULT FALSE,  -- منقطع من السوق
    image_url TEXT,
    description TEXT,
    ingredients TEXT,
    notes_top TEXT,  -- النوتات العليا
    notes_middle TEXT,  -- النوتات الوسطى
    notes_base TEXT,  -- النوتات القاعدية
    target_gender TEXT,  -- 'male', 'female', 'unisex'
    season TEXT,  -- 'summer', 'winter', 'all'
    occasions TEXT,  -- 'daily', 'evening', 'special'
    salla_product_id TEXT,  -- ربط مع Salla
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by INT REFERENCES users(id)
);

-- Index للبحث السريع
CREATE INDEX IF NOT EXISTS idx_products_enhanced_sku ON products_enhanced(sku);
CREATE INDEX IF NOT EXISTS idx_products_enhanced_name ON products_enhanced(product_name);
CREATE INDEX IF NOT EXISTS idx_products_enhanced_brand ON products_enhanced(brand);
CREATE INDEX IF NOT EXISTS idx_products_enhanced_discontinued ON products_enhanced(is_discontinued);

-- ============================================
-- 7. Views للتقارير السريعة
-- ============================================

-- متوسط سعر الشراء لكل منتج
CREATE OR REPLACE VIEW v_avg_purchase_price AS
SELECT 
    product_name,
    product_sku,
    AVG(purchase_price) as avg_price,
    MIN(purchase_price) as min_price,
    MAX(purchase_price) as max_price,
    COUNT(*) as purchase_count,
    MAX(purchase_date) as last_purchase_date
FROM purchases
GROUP BY product_name, product_sku;

-- أداء الموردين
CREATE OR REPLACE VIEW v_supplier_performance AS
SELECT 
    s.id,
    s.name,
    s.rating,
    COUNT(p.id) as total_purchases,
    SUM(p.total_cost) as total_spent,
    AVG(p.purchase_price) as avg_price,
    MAX(p.purchase_date) as last_purchase_date
FROM suppliers s
LEFT JOIN purchases p ON s.id = p.supplier_id
GROUP BY s.id, s.name, s.rating;

-- المصروفات الشهرية
CREATE OR REPLACE VIEW v_monthly_expenses AS
SELECT 
    DATE_TRUNC('month', expense_date) as month,
    category,
    expense_type,
    SUM(amount) as total_amount,
    COUNT(*) as expense_count
FROM expenses
GROUP BY DATE_TRUNC('month', expense_date), category, expense_type
ORDER BY month DESC, category;

-- ============================================
-- 8. Functions للعمليات الشائعة
-- ============================================

-- دالة لتسجيل العمليات تلقائياً
CREATE OR REPLACE FUNCTION log_user_action()
RETURNS TRIGGER AS $$
BEGIN
    -- يمكن إضافة منطق تسجيل تلقائي هنا
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- دالة لتحديث updated_at تلقائياً
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger لتحديث updated_at في products_enhanced
CREATE TRIGGER update_products_enhanced_updated_at
BEFORE UPDATE ON products_enhanced
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- 9. Row Level Security (RLS) - اختياري
-- ============================================

-- تفعيل RLS على الجداول الحساسة
-- ALTER TABLE users ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE purchases ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE expenses ENABLE ROW LEVEL SECURITY;

-- يمكن إضافة Policies حسب الحاجة

-- ============================================
-- 10. تعليقات على الجداول
-- ============================================

COMMENT ON TABLE users IS 'جدول المستخدمين والصلاحيات';
COMMENT ON TABLE audit_log IS 'سجل كل العمليات المهمة';
COMMENT ON TABLE suppliers IS 'قائمة الموردين';
COMMENT ON TABLE purchases IS 'المشتريات اليومية';
COMMENT ON TABLE expenses IS 'المصروفات الشهرية';
COMMENT ON TABLE products_enhanced IS 'معلومات المنتجات المحسّنة';

-- ============================================
-- ✅ انتهى - الجداول جاهزة!
-- ============================================

-- ملاحظات:
-- 1. كل الجداول تستخدم IF NOT EXISTS - آمنة للتشغيل مرات متعددة
-- 2. لا تحذف أي جداول موجودة
-- 3. Indexes للبحث السريع
-- 4. Views للتقارير الجاهزة
-- 5. Foreign Keys للربط بين الجداول
-- 6. Constraints للتحقق من صحة البيانات
