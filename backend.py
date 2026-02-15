# -*- coding: utf-8 -*-
"""
Backend FastAPI - نظام التسعير الذكي للعطور
يتعامل مع:
- Google Drive API
- Gemini AI
- Make.com Webhooks
- تحليل المنتجات والأسعار
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import pandas as pd
import os
from io import BytesIO
import json
from datetime import datetime
import httpx
import asyncio

# Google Drive API
from google.colab import auth
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload

# Gemini AI
import google.generativeai as genai

# إعدادات
app = FastAPI(title="نظام التسعير الذكي للعطور")

# متغيرات عامة
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
MAKE_WEBHOOK_URL = os.getenv("MAKE_WEBHOOK_URL", "")
GOOGLE_DRIVE_FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID", "")

# Fallback: إذا كان المفتاح فارغاً، استخدم المفتاح الاحتياطي
if not GEMINI_API_KEY or GEMINI_API_KEY.strip() == "":
    GEMINI_API_KEY = "AIzaSyBLgjwRh_t0gHqgN-V2NsDzdL5kro4lXVE"

# تهيئة Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# ── دوال مساعدة ──────────────────────────────────────────

def setup_google_drive():
    """تهيئة Google Drive API."""
    try:
        auth.authenticate_user()
        drive_service = build('drive', 'v3')
        return drive_service
    except Exception as e:
        print(f"خطأ في تهيئة Google Drive: {e}")
        return None

def upload_to_drive(drive_service, file_name, file_content, folder_id=None):
    """رفع ملف إلى Google Drive."""
    try:
        file_metadata = {
            'name': file_name,
            'parents': [folder_id] if folder_id else []
        }
        
        media = MediaIoBaseUpload(
            BytesIO(file_content),
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink'
        ).execute()
        
        return {
            "success": True,
            "file_id": file.get('id'),
            "link": file.get('webViewLink')
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

async def analyze_with_gemini(product_name, supplier_data, market_price=None):
    """
    تحليل المنتج باستخدام Gemini AI.
    
    المعاملات:
    - product_name: اسم المنتج
    - supplier_data: بيانات الموردين
    - market_price: سعر السوق (اختياري)
    
    الإرجاع:
    - dict: نتائج التحليل (التكلفة، الملاحظات، التوصيات)
    """
    try:
        prompt = f"""
        أنت خبير تسعير العطور. قم بتحليل المنتج التالي:
        
        اسم المنتج: {product_name}
        بيانات الموردين: {json.dumps(supplier_data, ensure_ascii=False)}
        سعر السوق: {market_price if market_price else 'غير محدد'}
        
        المطلوب:
        1. استخراج التكلفة من بيانات الموردين
        2. البحث عن سعر السوق المناسب
        3. حساب الهامش الربحي المناسب
        4. التحقق من المقارنة مع المنافسين
        5. إعطاء توصيات التسعير
        
        الرجاء إرجاع الإجابة بصيغة JSON:
        {{
            "cost": رقم,
            "market_price": رقم,
            "recommended_price": رقم,
            "margin_percentage": رقم,
            "notes": "ملاحظات",
            "confidence": رقم من 0 إلى 1
        }}
        """
        
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        
        # محاولة استخراج JSON من الإجابة
        try:
            result = json.loads(response.text)
            return result
        except:
            return {
                "cost": 0,
                "market_price": market_price or 0,
                "recommended_price": 0,
                "margin_percentage": 0,
                "notes": response.text,
                "confidence": 0.5
            }
    except Exception as e:
        return {
            "error": str(e),
            "cost": 0,
            "market_price": 0,
            "recommended_price": 0,
            "margin_percentage": 0,
            "notes": f"خطأ في التحليل: {e}",
            "confidence": 0
        }

async def send_to_make(data, webhook_url=None):
    """إرسال البيانات إلى Make.com."""
    try:
        url = webhook_url or MAKE_WEBHOOK_URL
        if not url:
            return {"success": False, "error": "لم يتم تحديد webhook URL"}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data)
            return {
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "response": response.text
            }
    except Exception as e:
        return {"success": False, "error": str(e)}

# ── API Endpoints ────────────────────────────────────────

@app.post("/api/analyze")
async def analyze_products(
    my_file: UploadFile = File(...),
    supplier_files: list = File(...),
    gemini_enabled: bool = True,
    drive_enabled: bool = True
):
    """
    تحليل المنتجات مع Gemini و Google Drive.
    """
    try:
        # 1. قراءة ملف المتجر
        my_content = await my_file.read()
        my_df = pd.read_csv(BytesIO(my_content)) if my_file.filename.endswith('.csv') else pd.read_excel(BytesIO(my_content))
        
        # 2. قراءة ملفات الموردين
        supplier_dfs = []
        for supplier_file in supplier_files:
            content = await supplier_file.read()
            df = pd.read_csv(BytesIO(content)) if supplier_file.filename.endswith('.csv') else pd.read_excel(BytesIO(content))
            supplier_dfs.append(df)
        
        # 3. تحليل مع Gemini
        results = []
        if gemini_enabled:
            for _, row in my_df.iterrows():
                product_name = row.get('اسم المنتج') or row.get('name') or row.get('styles_productCard__name__pakbB')
                
                # جمع بيانات الموردين
                supplier_data = []
                for sup_df in supplier_dfs:
                    matching = sup_df[sup_df.apply(lambda x: product_name in str(x.values), axis=1)]
                    if not matching.empty:
                        supplier_data.append(matching.to_dict('records')[0])
                
                # تحليل مع Gemini
                analysis = await analyze_with_gemini(product_name, supplier_data)
                
                result = {
                    "product_name": product_name,
                    "current_price": row.get('السعر') or row.get('price') or row.get('text-sm-2'),
                    "cost": analysis.get("cost"),
                    "market_price": analysis.get("market_price"),
                    "recommended_price": analysis.get("recommended_price"),
                    "margin_percentage": analysis.get("margin_percentage"),
                    "confidence": analysis.get("confidence"),
                    "notes": analysis.get("notes"),
                    "timestamp": datetime.now().isoformat()
                }
                results.append(result)
        # 4. حفظ في Google Drive
        drive_link = None
        if drive_enabled:
            drive_service = setup_google_drive()
            if drive_service:
                results_df = pd.DataFrame(results)
                
                # تحويل إلى Excel
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    results_df.to_excel(writer, sheet_name='النتائج', index=False)
                
                output.seek(0)
                upload_result = upload_to_drive(
                    drive_service,
                    f"نتائج_التحليل_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    output.getvalue(),
                    GOOGLE_DRIVE_FOLDER_ID
                )
                drive_link = upload_result.get("link")
        
        return {
            "success": True,
            "total_products": len(results),
            "results": results,
            "drive_link": drive_link,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/send-to-make")
async def send_to_make_endpoint(
    data: dict,
    webhook_url: str = None
):
    """إرسال البيانات إلى Make.com."""
    result = await send_to_make(data, webhook_url)
    return result

@app.post("/api/upload-to-drive")
async def upload_to_drive_endpoint(
    file: UploadFile = File(...),
    folder_id: str = None
):
    """رفع ملف إلى Google Drive."""
    try:
        drive_service = setup_google_drive()
        if not drive_service:
            raise HTTPException(status_code=500, detail="فشل الاتصال بـ Google Drive")
        
        content = await file.read()
        result = upload_to_drive(
            drive_service,
            file.filename,
            content,
            folder_id or GOOGLE_DRIVE_FOLDER_ID
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """فحص صحة الخادم."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "gemini_configured": bool(GEMINI_API_KEY),
        "drive_configured": bool(GOOGLE_DRIVE_FOLDER_ID),
        "make_configured": bool(MAKE_WEBHOOK_URL)
    }

# ── تشغيل الخادم ──────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
