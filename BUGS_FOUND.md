# الأخطاء المكتشفة في الفحص الشامل

## 1. مشكلة save_results_to_db (السطر 165-168)
**المشكلة:** الدالة تستخدم `.empty` على كائنات قد تكون DataFrames أو Lists
**الحل:** إضافة فحص isinstance قبل استخدام .empty

## 2. مشكلة engine_v2 - GEMINI_AVAILABLE دائماً False
**المشكلة:** `from modules.ai_verification import verify_match_with_gemini` يفشل بصمت
**السبب:** الاستيراد يحدث عند تحميل الملف، وقد يفشل لأسباب مختلفة
**الحل:** التأكد من أن الاستيراد يعمل بشكل صحيح

## 3. مشكلة engine_v2 - المنتجات بدون brand لا تُطابق
**المشكلة:** الفهرس يعتمد على (brand, size_bucket)، إذا كان brand فارغ = لا مطابقة
**الحل:** إضافة fallback عندما يكون brand فارغ

## 4. مشكلة engine_v2 - progress_callback signature مختلف
**المشكلة:** run_smart_matching يستدعي progress_callback(progress, elapsed, eta, stats)
لكن في main.py المحرك القديم يستخدم progress_callback(percent, message)
**الحل:** التأكد من أن smart_progress في main.py يتعامل مع كلا التوقيعين

## 5. مشكلة render_approval_section - أعمدة V2 مختلفة عن V1
**المشكلة:** V2 ينتج أعمدة مثل my_name, comp_name, diff, diff_pct
لكن render_approval_section يتوقع أعمدة عربية مثل المنتج, اسم المنافس, الفرق, النسبة %
**الحل:** تحويل أسماء الأعمدة عند استخدام V2

## 6. مشكلة "all" DataFrame مفقود في V2
**المشكلة:** V2 لا ينشئ results["all"] لكن لوحة القيادة تستخدمه
**الحل:** إضافة results["all"] في V2
