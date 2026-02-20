"""
ai_page_manager.py
نظام إدارة الذكاء الاصطناعي لكل صفحة في التطبيق
يدرب الذكاء الاصطناعي على العمل في كل صفحة بالمهمة المناسبة
"""

import streamlit as st
import json
from datetime import datetime
from modules.ai_verification import analyze_for_section, batch_verification
from main import call_gemini, call_openrouter


class AIPageManager:
    """مدير الذكاء الاصطناعي للصفحات"""

    def __init__(self):
        self.page_configs = self._load_page_configs()

    def _load_page_configs(self):
        """تحميل إعدادات كل صفحة"""
        return {
            "لوحة القيادة": {
                "role": "محلل بيانات ومستشار تسعير",
                "tasks": [
                    "تحليل الإحصائيات العامة",
                    "تقديم توصيات استراتيجية",
                    "تحليل اتجاهات الأسعار",
                    "اقتراح تحسينات على العمليات"
                ],
                "context": "لوحة القيادة الرئيسية لنظام التسعير الذكي"
            },

            "رفع الملفات": {
                "role": "مساعد رفع البيانات وتحليل الملفات",
                "tasks": [
                    "فحص جودة الملفات المرفوعة",
                    "اقتراح تحسينات على تنسيق البيانات",
                    "تحليل حجم البيانات وتعقيدها",
                    "تقديم نصائح لتحسين دقة المطابقة"
                ],
                "context": "صفحة رفع وتحليل ملفات المنتجات والمنافسين"
            },

            "رفع سعر": {
                "role": "خبير تسعير استراتيجي",
                "tasks": [
                    "تحليل أسباب الحاجة لرفع السعر",
                    "تقديم توصيات سعرية ذكية",
                    "دراسة تأثير التغييرات على السوق",
                    "اقتراح استراتيجيات تسويقية"
                ],
                "context": "منتجات تحتاج رفع أسعارها بناءً على تحليل المنافسة"
            },

            "خفض سعر": {
                "role": "محلل تنافسي ومستشار تسعير",
                "tasks": [
                    "تحليل أسباب الحاجة لخفض السعر",
                    "تقييم تأثير الخفض على الهوامش",
                    "دراسة ردود فعل العملاء المحتملة",
                    "اقتراح بدائل للحفاظ على الربحية"
                ],
                "context": "منتجات تحتاج خفض أسعارها للحفاظ على التنافسية"
            },

            "موافق عليها": {
                "role": "مدقق جودة المطابقة",
                "tasks": [
                    "التحقق من صحة المطابقات",
                    "تقييم جودة البيانات",
                    "اقتراح تحسينات على خوارزميات المطابقة",
                    "تحليل دقة النتائج"
                ],
                "context": "منتجات تمت مطابقة أسعارها بنجاح مع المنافسين"
            },

            "منتجات مفقودة": {
                "role": "مستشار إضافة منتجات جديدة",
                "tasks": [
                    "تقييم إمكانية إضافة المنتج الجديد",
                    "تحليل الطلب المحتمل في السوق",
                    "دراسة الربحية المتوقعة",
                    "اقتراح استراتيجية تسعير للمنتج الجديد"
                ],
                "context": "منتجات موجودة عند المنافسين وغير موجودة في متجرنا"
            },

            "يحتاج مراجعة": {
                "role": "محقق ومراجع قرارات",
                "tasks": [
                    "مراجعة الحالات المعقدة",
                    "تقديم توصيات للحالات الاستثنائية",
                    "تحليل المخاطر المحتملة",
                    "اقتراح حلول بديلة"
                ],
                "context": "منتجات ذات خطورة عالية تحتاج مراجعة يدوية"
            },

            "تفاصيل المطابقة": {
                "role": "محلل تفصيلي للمطابقات",
                "tasks": [
                    "تحليل عملية المطابقة خطوة بخطوة",
                    "تقييم دقة الخوارزميات",
                    "اقتراح تحسينات على المطابقة",
                    "توثيق الدروس المستفادة"
                ],
                "context": "تفاصيل شاملة عن كيفية مطابقة المنتجات"
            },

            "تحقق AI": {
                "role": "مدير ومشرف على أنظمة الذكاء الاصطناعي",
                "tasks": [
                    "فحص أداء نماذج الذكاء الاصطناعي",
                    "تحليل دقة النتائج",
                    "اقتراح تحسينات على الخوارزميات",
                    "مراقبة استهلاك الموارد"
                ],
                "context": "نظام شامل للتحقق من المنتجات باستخدام الذكاء الاصطناعي"
            },

            "محادثة AI": {
                "role": "مساعد ذكي متخصص في التسعير والعطور",
                "tasks": [
                    "الإجابة على أسئلة التسعير",
                    "تقديم نصائح حول استراتيجيات التسعير",
                    "تحليل اتجاهات سوق العطور",
                    "مساعدة في اتخاذ القرارات التجارية"
                ],
                "context": "دردشة مباشرة مع الذكاء الاصطناعي حول التسعير والعطور"
            },

            "استديو مهووس": {
                "role": "مصمم محتوى ومبدع إعلاني",
                "tasks": [
                    "إنشاء محتوى تسويقي جذاب",
                    "تصميم حملات إعلانية",
                    "كتابة نصوص إعلانية مؤثرة",
                    "اقتراح استراتيجيات تسويقية"
                ],
                "context": "استديو إنشاء المحتوى التسويقي والإعلاني"
            },

            "Make أتمتة": {
                "role": "خبير أتمتة وتكامل الأنظمة",
                "tasks": [
                    "تحليل أداء عمليات الأتمتة",
                    "اقتراح تحسينات على التكامل",
                    "مراقبة سلامة الاتصالات",
                    "حل مشاكل التكامل"
                ],
                "context": "إدارة سيناريوهات Make.com وتتبع الإرسالات"
            },

            "قاعدة البيانات": {
                "role": "مدير قاعدة بيانات ومحلل بيانات",
                "tasks": [
                    "تحليل أداء قاعدة البيانات",
                    "اقتراح تحسينات على هيكل البيانات",
                    "مراقبة سلامة البيانات",
                    "إنشاء تقارير تحليلية"
                ],
                "context": "عرض وإدارة جميع السجلات المحفوظة في السحابة"
            },

            "المشتريات اليومية": {
                "role": "مدير مشتريات ومحلل تكاليف",
                "tasks": [
                    "تحليل أنماط المشتريات",
                    "اقتراح تحسينات على استراتيجية المشتريات",
                    "مراقبة التكاليف والميزانيات",
                    "تحسين علاقات الموردين"
                ],
                "context": "إدارة المشتريات اليومية والتكاليف"
            },

            "إدارة الموردين": {
                "role": "مدير علاقات الموردين",
                "tasks": [
                    "تقييم أداء الموردين",
                    "تحليل جودة المنتجات الموردة",
                    "اقتراح تحسينات على العلاقات التجارية",
                    "إدارة المفاوضات والعقود"
                ],
                "context": "إدارة وتقييم الموردين والشركاء"
            },

            "مذكرة المصروفات": {
                "role": "محاسب ومحلل مالي",
                "tasks": [
                    "تحليل أنماط المصروفات",
                    "اقتراح طرق توفير التكاليف",
                    "مراقبة الميزانيات والمصروفات",
                    "إعداد التقارير المالية"
                ],
                "context": "تتبع وإدارة المصروفات والنفقات"
            },

            "الإعدادات": {
                "role": "خبير تقني ومستشار أنظمة",
                "tasks": [
                    "تحليل إعدادات النظام",
                    "اقتراح تحسينات تقنية",
                    "حل مشاكل الأداء",
                    "تحديث وصيانة النظام"
                ],
                "context": "إعدادات النظام والتكوينات التقنية"
            }
        }

    def get_page_ai_assistant(self, page_name):
        """الحصول على مساعد الذكاء الاصطناعي لصفحة معينة"""
        config = self.page_configs.get(page_name, {})
        if not config:
            return None

        return PageAIAssistant(page_name, config)

    def get_all_page_assistants(self):
        """الحصول على مساعدي الذكاء الاصطناعي لجميع الصفحات"""
        return {name: self.get_page_ai_assistant(name) for name in self.page_configs}


class PageAIAssistant:
    """مساعد الذكاء الاصطناعي لصفحة معينة"""

    def __init__(self, page_name, config):
        self.page_name = page_name
        self.config = config
        self.role = config.get("role", "مساعد عام")
        self.tasks = config.get("tasks", [])
        self.context = config.get("context", "")

    def generate_system_prompt(self):
        """توليد prompt النظام للذكاء الاصطناعي"""
        tasks_text = "\n".join(f"- {task}" for task in self.tasks)

        return f"""أنت {self.role} في نظام ERP للعطور الفاخرة.

الصفحة الحالية: {self.page_name}
السياق: {self.context}

مهامك الرئيسية:
{tasks_text}

تعليمات مهمة:
- أجب دائماً باللغة العربية
- كن مفيداً ومباشراً في إجاباتك
- استخدم الإحصائيات والأرقام عند الاقتضاء
- اقترح حلول عملية قابلة للتطبيق
- كن موضوعياً ومبنياً على الحقائق

كيف يمكنني مساعدتك في {self.page_name}؟"""

    def analyze_page_data(self, page_data=None):
        """تحليل بيانات الصفحة الحالية"""
        if not page_data:
            page_data = self._get_current_page_data()

        analysis_prompt = f"""{self.generate_system_prompt()}

بيانات الصفحة الحالية:
{json.dumps(page_data, ensure_ascii=False, indent=2)}

قم بتحليل هذه البيانات وقدم توصياتك المفيدة."""

        # استخدام Gemini أو OpenRouter حسب التوفر
        try:
            result = call_gemini(analysis_prompt)
            if result["success"]:
                return result["text"]
        except:
            pass

        try:
            result = call_openrouter(analysis_prompt)
            if result["success"]:
                return result["text"]
        except:
            pass

        return "عذراً، لا يمكنني الوصول إلى خدمات الذكاء الاصطناعي حالياً."

    def _get_current_page_data(self):
        """الحصول على بيانات الصفحة الحالية من session state"""
        page_data = {}

        # بيانات عامة
        if "results" in st.session_state and st.session_state.results:
            results = st.session_state.results
            page_data["stats"] = results.get("stats", {})
            page_data["total_products"] = results.get("stats", {}).get("total", 0)

        # بيانات حسب الصفحة
        if self.page_name == "رفع سعر" and "results" in st.session_state:
            df_raise = st.session_state.results.get("raise")
            if df_raise is not None:
                page_data["products_count"] = len(df_raise)
                page_data["sample_products"] = df_raise.head(3).to_dict('records') if not df_raise.empty else []

        elif self.page_name == "خفض سعر" and "results" in st.session_state:
            df_lower = st.session_state.results.get("lower")
            if df_lower is not None:
                page_data["products_count"] = len(df_lower)
                page_data["sample_products"] = df_lower.head(3).to_dict('records') if not df_lower.empty else []

        elif self.page_name == "منتجات مفقودة" and "results" in st.session_state:
            df_missing = st.session_state.results.get("missing")
            if df_missing is not None:
                page_data["products_count"] = len(df_missing)
                page_data["sample_products"] = df_missing.head(3).to_dict('records') if not df_missing.empty else []

        return page_data

    def get_quick_actions(self):
        """الحصول على إجراءات سريعة مقترحة للصفحة"""
        actions = []

        if self.page_name == "لوحة القيادة":
            actions = [
                "📊 تحليل الإحصائيات التفصيلي",
                "🎯 اقتراحات تحسين الأداء",
                "📈 دراسة اتجاهات الأسعار",
                "💡 توصيات استراتيجية"
            ]

        elif self.page_name in ["رفع سعر", "خفض سعر"]:
            actions = [
                "🔍 تحليل شامل للمنتجات",
                "📊 تقييم التأثير المالي",
                "🎯 اقتراحات تسعير بديلة",
                "⚠️ تحليل المخاطر"
            ]

        elif self.page_name == "منتجات مفقودة":
            actions = [
                "💰 تحليل الربحية المتوقعة",
                "📊 دراسة الطلب في السوق",
                "🏷️ اقتراحات التسعير",
                "📦 خطة الإضافة التدريجية"
            ]

        elif self.page_name == "تحقق AI":
            actions = [
                "🔧 فحص شامل للأنظمة",
                "📈 تحليل الأداء",
                "🔄 اقتراحات التحسين",
                "📋 تقرير التشخيص"
            ]

        return actions

    def perform_quick_action(self, action_name):
        """تنفيذ إجراء سريع"""
        prompt = f"""{self.generate_system_prompt()}

الإجراء المطلوب: {action_name}

قم بتنفيذ هذا الإجراء وقدم النتائج بشكل مفصل ومفيد."""

        try:
            result = call_gemini(prompt)
            if result["success"]:
                return result["text"]
        except:
            pass

        try:
            result = call_openrouter(prompt)
            if result["success"]:
                return result["text"]
        except:
            pass

        return "عذراً، لا يمكنني تنفيذ هذا الإجراء حالياً."


# دوال مساعدة للتكامل مع التطبيق
def get_page_ai_assistant(page_name):
    """دالة مساعدة للحصول على مساعد الصفحة"""
    manager = AIPageManager()
    return manager.get_page_ai_assistant(page_name)


def show_page_ai_assistant(page_name):
    """عرض مساعد الذكاء الاصطناعي للصفحة"""
    assistant = get_page_ai_assistant(page_name)
    if not assistant:
        st.warning(f"لا يوجد مساعد ذكاء اصطناعي للصفحة: {page_name}")
        return

    with st.expander(f"🤖 مساعد الذكاء الاصطناعي - {page_name}", expanded=False):
        st.markdown(f"**الدور:** {assistant.role}")
        st.markdown(f"**السياق:** {assistant.context}")

        # المهام
        st.markdown("**المهام الرئيسية:**")
        for task in assistant.tasks:
            st.markdown(f"- {task}")

        # الإجراءات السريعة
        quick_actions = assistant.get_quick_actions()
        if quick_actions:
            st.markdown("**إجراءات سريعة:**")
            cols = st.columns(len(quick_actions))
            for i, action in enumerate(quick_actions):
                if cols[i].button(action, key=f"quick_action_{i}"):
                    with st.spinner("جاري تنفيذ الإجراء..."):
                        result = assistant.perform_quick_action(action)
                        st.markdown("**النتيجة:**")
                        st.write(result)

        # دردشة مباشرة
        st.markdown("---")
        st.markdown("**💬 اسأل المساعد:**")

        user_question = st.text_input(
            "اكتب سؤالك هنا...",
            key=f"ai_question_{page_name}",
            placeholder=f"اسأل عن {page_name}..."
        )

        if user_question and st.button("🚀 اسأل", key=f"ask_ai_{page_name}"):
            with st.spinner("جاري التفكير..."):
                result = assistant.analyze_page_data({"question": user_question})
                st.markdown("**إجابة المساعد:**")
                st.write(result)


def integrate_ai_into_page(page_name, page_content_func):
    """دمج الذكاء الاصطناعي في صفحة معينة"""
    # عرض محتوى الصفحة الأصلي
    page_content_func()

    # إضافة مساعد الذكاء الاصطناعي في الأسفل
    st.markdown("---")
    show_page_ai_assistant(page_name)


# إنشاء instance عام
ai_page_manager = AIPageManager()