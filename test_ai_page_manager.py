#!/usr/bin/env python3
"""
اختبار سريع لنظام إدارة الذكاء الاصطناعي للصفحات
"""

import sys
import os

# إضافة مجلد المشروع إلى المسار
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_ai_page_manager():
    """اختبار نظام إدارة الذكاء الاصطناعي"""
    try:
        from modules.ai_page_manager import AIPageManager, PageAIAssistant
        print("✅ تم استيراد AIPageManager بنجاح")

        # إنشاء مدير الصفحات
        manager = AIPageManager()
        print("✅ تم إنشاء AIPageManager بنجاح")

        # اختبار الحصول على مساعد صفحة
        assistant = manager.get_page_ai_assistant("لوحة القيادة")
        if assistant:
            print("✅ تم الحصول على مساعد لوحة القيادة")
            print(f"   الدور: {assistant.role}")
            print(f"   عدد المهام: {len(assistant.tasks)}")
        else:
            print("❌ فشل في الحصول على مساعد لوحة القيادة")
            return False

        # اختبار توليد prompt النظام
        system_prompt = assistant.generate_system_prompt()
        if system_prompt and len(system_prompt) > 100:
            print("✅ تم توليد system prompt بنجاح")
        else:
            print("❌ فشل في توليد system prompt")
            return False

        # اختبار الإجراءات السريعة
        quick_actions = assistant.get_quick_actions()
        if quick_actions and len(quick_actions) > 0:
            print(f"✅ تم الحصول على {len(quick_actions)} إجراءات سريعة")
        else:
            print("❌ فشل في الحصول على الإجراءات السريعة")
            return False

        return True

    except ImportError as e:
        print(f"❌ خطأ في الاستيراد: {e}")
        return False
    except Exception as e:
        print(f"❌ خطأ عام: {e}")
        return False

def test_app_integration():
    """اختبار تكامل النظام مع التطبيق الرئيسي"""
    try:
        # محاولة استيراد app.py
        import app
        print("✅ تم استيراد app.py بنجاح")

        # التحقق من وجود المتغير
        if hasattr(app, 'AI_PAGE_MANAGER_AVAILABLE'):
            if app.AI_PAGE_MANAGER_AVAILABLE:
                print("✅ نظام إدارة الذكاء الاصطناعي متاح في التطبيق")
            else:
                print("⚠️ نظام إدارة الذكاء الاصطناعي غير متاح في التطبيق")
        else:
            print("❌ متغير AI_PAGE_MANAGER_AVAILABLE غير موجود")
            return False

        return True

    except ImportError as e:
        print(f"❌ خطأ في استيراد app.py: {e}")
        return False
    except Exception as e:
        print(f"❌ خطأ في اختبار التكامل: {e}")
        return False

def main():
    """الدالة الرئيسية للاختبار"""
    print("🚀 بدء اختبار نظام إدارة الذكاء الاصطناعي للصفحات")
    print("=" * 60)

    # اختبار النظام الأساسي
    print("\n📋 اختبار النظام الأساسي:")
    basic_test = test_ai_page_manager()

    # اختبار التكامل
    print("\n🔗 اختبار التكامل مع التطبيق:")
    integration_test = test_app_integration()

    print("\n" + "=" * 60)
    if basic_test and integration_test:
        print("🎉 جميع الاختبارات نجحت! النظام جاهز للاستخدام.")
        return 0
    else:
        print("❌ فشل في بعض الاختبارات. يرجى مراجعة الأخطاء أعلاه.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)