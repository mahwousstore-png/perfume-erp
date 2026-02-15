# -*- coding: utf-8 -*-
"""
Salla Formatter - تحويل النتائج إلى تنسيق سلة المطلوب
"""

import pandas as pd
from io import BytesIO
from datetime import datetime


def convert_to_salla_price_update(results):
    """
    تحويل نتائج التحليل إلى تنسيق ملف تحديث الأسعار في سلة.
    
    المعاملات:
    - results: قائمة من نتائج Gemini
    
    الإرجاع:
    - DataFrame: جدول جاهز للرفع إلى سلة
    """
    data = []
    for result in results:
        data.append({
            'No.': result.get('product_id', ''),
            'النوع': 'منتج',
            'أسم المنتج': result.get('product_name', ''),
            'رمز المنتج sku': result.get('sku', ''),
            'سعر المنتج': result.get('current_price', 0),
            'سعر التكلفة': result.get('cost', 0),
            'السعر المخفض': result.get('recommended_price', 0),
            'تاريخ بداية التخفيض': '',
            'تاريخ نهاية التخفيض': '',
        })
    
    return pd.DataFrame(data)


def convert_to_salla_new_product(product):
    """
    تحويل منتج جديد إلى تنسيق سلة.
    
    المعاملات:
    - product: بيانات المنتج الجديد
    
    الإرجاع:
    - dict: صف جاهز للإضافة إلى الجدول
    """
    return {
        'النوع': 'منتج',
        'أسم المنتج': product.get('name', ''),
        'تصنيف المنتج': product.get('category', ''),
        'صورة المنتج': product.get('image_url', ''),
        'وصف صورة المنتج': '',
        'نوع المنتج': 'منتج جاهز',
        'سعر المنتج': product.get('price', 0),
        'الوصف': product.get('description', ''),
        'هل يتطلب شحن؟': 'نعم',
        'رمز المنتج sku': product.get('sku', ''),
        'سعر التكلفة': product.get('cost', 0),
        'السعر المخفض': product.get('sale_price', 0),
        'تاريخ بداية التخفيض': '',
        'تاريخ نهاية التخفيض': '',
        'اقصي كمية لكل عميل': 0,
        'إخفاء خيار تحديد الكمية': 'لا',
        'اضافة صورة عند الطلب': 'لا',
        'الوزن': product.get('weight', 0.1),
        'وحدة الوزن': 'kg',
        'الماركة': product.get('brand', ''),
        'العنوان الترويجي': '',
        'تثبيت المنتج': 'لا',
        'الباركود': product.get('barcode', ''),
        'السعرات الحرارية': '',
        'MPN': '',
        'GTIN': '',
        'خاضع للضريبة ؟': 'نعم',
        'سبب عدم الخضوع للضريبة': '',
    }


def create_salla_files(gemini_results, new_products=None):
    """
    إنشاء ملفات سلة جاهزة للرفع.
    
    المعاملات:
    - gemini_results: نتائج Gemini (للأسعار المحدثة)
    - new_products: منتجات جديدة (اختياري)
    
    الإرجاع:
    - dict: {'price_update': BytesIO, 'new_products': BytesIO}
    """
    files = {}
    
    # 1. ملف تحديث الأسعار
    if gemini_results:
        df_prices = convert_to_salla_price_update(gemini_results)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_prices.to_excel(writer, sheet_name='تحديث الأسعار', index=False)
        output.seek(0)
        files['price_update'] = output
        files['price_update_df'] = df_prices
    
    # 2. ملف المنتجات الجديدة
    if new_products:
        new_products_list = [convert_to_salla_new_product(p) for p in new_products]
        df_new = pd.DataFrame(new_products_list)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_new.to_excel(writer, sheet_name='منتجات جديدة', index=False)
        output.seek(0)
        files['new_products'] = output
        files['new_products_df'] = df_new
    
    return files


def prepare_for_make_webhook(results, operation_type='price_update'):
    """
    تحضير البيانات لإرسالها إلى Make.com webhook.
    
    المعاملات:
    - results: نتائج التحليل
    - operation_type: نوع العملية (price_update أو new_products)
    
    الإرجاع:
    - dict: بيانات جاهزة للإرسال
    """
    if operation_type == 'price_update':
        df = convert_to_salla_price_update(results)
        return {
            'type': 'price_update',
            'timestamp': datetime.now().isoformat(),
            'total_items': len(df),
            'data': df.to_dict('records')
        }
    elif operation_type == 'new_products':
        data_list = [convert_to_salla_new_product(p) for p in results]
        return {
            'type': 'new_products',
            'timestamp': datetime.now().isoformat(),
            'total_items': len(data_list),
            'data': data_list
        }


def export_to_csv(df, _filename):
    """
    تصدير DataFrame إلى ملف CSV.
    
    المعاملات:
    - df: DataFrame للتصدير
    - filename: اسم الملف
    
    الإرجاع:
    - BytesIO: محتوى الملف
    """
    output = BytesIO()
    df.to_csv(output, index=False, encoding='utf-8-sig')
    output.seek(0)
    return output
