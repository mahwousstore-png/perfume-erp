"""
engine.py - محرك المطابقة والتصنيف الذكي v3.0
إصلاح شامل للمطابقة: دعم عربي/إنجليزي + تسامح الحجم + مطابقة التستر مع الريتيل
"""
import re
from rapidfuzz import fuzz


# ===== قوانين التصنيف =====

REJECT_KEYWORDS = [
    "sample", "عينة", "عينه", "decant", "تقسيم",
    "split", "miniature", "mini ",
    "0.5ml", "1ml", "2ml", "3ml", "5ml",
    "سبلاش", "splash", "رول", "roll-on", "rollerball",
]

TESTER_KEYWORDS = [
    "tester", "تستر", "test", "تيستر", "(تستر)",
]

HAIR_MIST_KEYWORDS = [
    "hair mist", "هير مست", "للشعر",
]

BODY_MIST_KEYWORDS = [
    "body mist", "بودي مست", "body spray",
    "بودي سبراي", "للجسم",
]

SET_KEYWORDS = [
    "set", "gift set", "طقم", "مجموعة",
    "coffret", "collection", "kit",
]

# كلمات عامة تُزال عند المقارنة
COMMON_WORDS = [
    "عطر", "parfum", "perfume", "eau", "de", "او", "دو",
    "أو", "دي", "بارفيوم", "بارفام", "تواليت", "كولونيا",
    "toilette", "cologne", "edp", "edt",
    "eau de parfum", "eau de toilette",
    "for men", "for women", "pour homme", "pour femme",
    "unisex", "spray", "natural spray",
    "مل", "ml", "للرجال", "للنساء", "للجنسين",
    "الرجالي", "النسائي", "رجالي", "نسائي",
    "برفيوم", "برفوم", "برفيم", "بارفيوم", "بارفام",
    "اكستريم", "اكستريت", "extreme", "extrait",
    "انتنس", "intense", "ايو", "eaux",
    "عالي التركيز", "مستوحى", "بديل", "متقن",
    "لعطر", "من", "from",
]

# قاموس ترجمة الأسماء الشائعة (عربي ↔ إنجليزي)
TRANSLATION_MAP = {
    # ماركات
    "reserve privee": "ريسيرف برايف",
    "réserve privée": "ريسيرف برايف",
    "reserve privée": "ريسيرف برايف",
    "ريزيرف بريفيه": "ريسيرف برايف",
    "ريزيرڤ بريڤيه": "ريسيرف برايف",
    "gentleman": "جنتلمان",
    "جنتل مان": "جنتلمان",
    "society": "سوسايتي",
    "سوسايتى": "سوسايتي",
    "boisée": "بوازيه",
    "boisee": "بوازيه",
    "بوازية": "بوازيه",
    "l'interdit": "لانترديت",
    "linterdit": "لانترديت",
    "la interdit": "لا انترديت",
    "irresistible": "ايرزيستابل",
    "ارزيستبل": "ايرزيستابل",
    "ايرزستبل": "ايرزيستابل",
    "very floral": "فيري فلورال",
    "rouge": "روج",
    "absolu": "ابسولو",
    "noir": "نوار",
    "الاسود": "الأسود",
    "black": "الأسود",
    "blue": "بلو",
    "bleu": "بلو",
    "platinum": "بلاتينيوم",
    "egoiste": "ايجويست",
    "égoïste": "ايجويست",
    "oud wood": "عود وود",
    "عود وود": "عود وود",
    "intense": "انتنس",
    "إنتنس": "انتنس",
    "privé": "برايف",
    "prive": "برايف",
    "cologne": "كولون",
    "كولونيا": "كولون",
    "xeryus": "اكسيروس",
    "garçon manqué": "جارسون مانكي",
    "garcon manque": "جارسون مانكي",
    # أسماء عطور شائعة
    "allure": "الور",
    "اللور": "الور",
    "homme": "هوم",
    "sport": "سبورت",
    "اسبورت": "سبورت",
    "gabrielle": "غابريل",
    "غابريال": "غابريل",
    "essence": "ايسنس",
    "ايسينس": "ايسنس",
    "coco": "كوكو",
    "mademoiselle": "مدموزيل",
    "ميدموزيل": "مدموزيل",
    "مودموزيل": "مدموزيل",
    "chance": "شانس",
    "tender": "تندر",
    "organza": "أورغانزا",
    "اورغانزا": "أورغانزا",
    "amarige": "أماريج",
    "اماريج": "أماريج",
    "dahlia": "داليا",
    "divin": "ديفين",
    "ange": "أنج",
    "انج": "أنج",
    "demon": "ديمون",
    "démon": "ديمون",
    "superlégère": "سوبرليجيرا",
    "superlegere": "سوبرليجيرا",
}


def classify_product(name):
    """تصنيف المنتج حسب اسمه."""
    if not name or not isinstance(name, str):
        name = str(name) if name else ""
    lower = name.lower().strip()
    if not lower:
        return "rejected"

    for kw in REJECT_KEYWORDS:
        if kw in lower:
            return "rejected"

    for kw in TESTER_KEYWORDS:
        if kw in lower:
            return "tester"

    for kw in SET_KEYWORDS:
        if kw in lower:
            return "set"

    for kw in HAIR_MIST_KEYWORDS:
        if kw in lower:
            return "hair_mist"

    for kw in BODY_MIST_KEYWORDS:
        if kw in lower:
            return "body_mist"

    return "retail"


def extract_size(name):
    """استخراج الحجم من اسم المنتج."""
    if not name or not isinstance(name, str):
        name = str(name) if name else ""
    if not name:
        return 0
    patterns = [
        r"(\d+(?:\.\d+)?)\s*(?:ml|مل)",
        r"-\s*(\d+(?:\.\d+)?)\s*(?:ml|مل)",
        r"(\d+(?:\.\d+)?)\s*(?:ML|Ml)",
    ]
    for pat in patterns:
        match = re.search(pat, name, re.IGNORECASE)
        if match:
            val = float(match.group(1))
            if 5 <= val <= 1000:
                return val
    return 0


def extract_brand(name):
    """استخراج الماركة من اسم المنتج - v3.0 موسّعة."""
    if not name or not isinstance(name, str):
        name = str(name) if name else ""
    if not name:
        return ""
    # قائمة موسّعة: (الاسم المعياري, [الأسماء البديلة])
    BRAND_ALIASES = [
        ("tom ford", ["tom ford", "توم فورد"]),
        ("carolina herrera", ["carolina herrera", "كارولينا هيريرا", "كارولينا هريرا"]),
        ("memo paris", ["memo paris", "memo", "ميمو باريس", "ميمو"]),
        ("jean paul gaultier", ["jean paul gaultier", "جان بول غوتييه", "جان بول", "غوتييه"]),
        ("ysl", ["ysl", "yves saint laurent", "ايف سان لوران", "إيف سان", "اف سان", "ايف سان"]),
        ("calvin klein", ["calvin klein", "كالفين كلاين", "كالفن كلاين"]),
        ("roberto cavalli", ["roberto cavalli", "روبرتو كافالي", "روبيرتو كافالي"]),
        ("maison alhambra", ["maison alhambra", "ميزون الهامبرا", "ميزون الحمبرا"]),
        ("paco rabanne", ["paco rabanne", "باكو رابان", "باكو رابين"]),
        ("ralph lauren", ["ralph lauren", "رالف لورين"]),
        ("louis vuitton", ["louis vuitton", "لويس فيتون", "لوي فيتون"]),
        ("dolce gabbana", ["dolce & gabbana", "dolce gabbana", "دولتشي آند غابانا", "دولتشي غابانا", "دولتشي اند غابانا"]),
        ("roja dove", ["roja dove", "roja", "روجا دوف", "روجا"]),
        ("van cleef", ["van cleef", "van cleef & arpels", "فان كليف"]),
        ("montblanc", ["montblanc", "mont blanc", "مونت بلانك", "مون بلان", "مونت بلان"]),
        ("ibrahim al qurashi", ["إبراهيم القرشي", "ابراهيم القرشي"]),
        ("hugo boss", ["hugo boss", "هوغو بوس", "هوقو بوس", "هوجو بوس"]),
        ("tiziana terenzi", ["tiziana terenzi", "تيزيانا تيرينزي", "تيزيانا ترينزى", "تيزيانا ترنزي"]),
        ("acqua di parma", ["acqua di parma", "أكوا دي بارما", "اكوا دي بارما", "أكوا دي"]),
        ("elie saab", ["elie saab", "إيلي صعب", "ايلي صعب"]),
        ("bvlgari", ["bvlgari", "bulgari", "بولغاري", "بلغاري"]),
        ("victoria secret", ["victoria secret", "victoria's secret", "فيكتوريا سيكريت"]),
        ("giorgio armani", ["giorgio armani", "جورجيو أرماني", "جورجيو ارماني", "أرماني", "ارماني"]),
        ("maison margiela", ["maison margiela", "ميزون مارجيلا", "مارجيلا"]),
        ("issey miyake", ["issey miyake", "ايسي مياكي"]),
        ("clive christian", ["clive christian", "كلايف كريستيان", "كلايف كرستيان"]),
        ("carner barcelona", ["carner barcelona", "كارنر برشلونة"]),
        ("estee lauder", ["estee lauder", "إستي لودر", "استي لودر"]),
        ("histoires de parfums", ["histoires de parfums", "هيستوريس دي"]),
        ("rossendo mateu", ["rossendo mateu", "روسيندو ماتيو"]),
        ("costume national", ["costume national", "كوستوم ناشونال"]),
        ("francesca bianchi", ["francesca bianchi", "فرانشيسكا بيانكي"]),
        ("liquides imaginaires", ["liquides imaginaires", "ليكويد اماجينيرز"]),
        ("thomas kosmala", ["thomas kosmala", "توماس كوسمالا"]),
        ("narciso rodriguez", ["narciso rodriguez", "نارسيسو رودريغز", "نارسيسو"]),
        ("juicy couture", ["juicy couture", "جوسي كوتور"]),
        ("nina ricci", ["nina ricci", "نينا ريتشي"]),
        ("min new york", ["min new york", "مين نيويورك"]),
        ("givenchy", ["givenchy", "جيفنشي", "جفنشي", "جيفينشي"]),
        ("dior", ["dior", "ديور"]),
        ("chanel", ["chanel", "شانيل"]),
        ("gucci", ["gucci", "قوتشي", "غوتشي"]),
        ("versace", ["versace", "فرساتشي", "فيرساتشي"]),
        ("prada", ["prada", "برادا"]),
        ("burberry", ["burberry", "بربري"]),
        ("hermes", ["hermes", "hermès", "هيرمز", "هرمز"]),
        ("creed", ["creed", "كريد"]),
        ("valentino", ["valentino", "فالنتينو"]),
        ("cartier", ["cartier", "كارتييه", "كارتير"]),
        ("lancome", ["lancome", "lancôme", "لانكوم", "لانكم"]),
        ("jo malone", ["jo malone", "جو مالون"]),
        ("amouage", ["amouage", "أمواج", "امواج"]),
        ("rasasi", ["rasasi", "رصاصي"]),
        ("lattafa", ["lattafa", "لطافة"]),
        ("arabian oud", ["arabian oud", "العربية للعود"]),
        ("swiss arabian", ["swiss arabian", "سويس أريبيان", "سويس اريبيان"]),
        ("ajmal", ["ajmal", "أجمل", "اجمل"]),
        ("al haramain", ["al haramain", "الحرمين"]),
        ("afnan", ["afnan", "عفنان"]),
        ("armaf", ["armaf", "أرماف", "ارماف"]),
        ("nishane", ["nishane", "نيشان", "نيشاني", "نيشانه"]),
        ("xerjoff", ["xerjoff", "زيرجوف"]),
        ("parfums de marly", ["parfums de marly", "مارلي", "دي مارلي"]),
        ("initio", ["initio", "انيشيو"]),
        ("byredo", ["byredo", "بايريدو"]),
        ("le labo", ["le labo", "لي لابو"]),
        ("diptyque", ["diptyque", "ديبتيك"]),
        ("mancera", ["mancera", "مانسيرا", "منسيرا"]),
        ("montale", ["montale", "مونتال"]),
        ("kilian", ["kilian", "كيليان"]),
        ("penhaligon", ["penhaligon", "penhaligons", "بنهاليغونز"]),
        ("chopard", ["chopard", "شوبارد"]),
        ("azzaro", ["azzaro", "ازارو"]),
        ("dunhill", ["dunhill", "دنهل"]),
        ("bentley", ["bentley", "بنتلي"]),
        ("boucheron", ["boucheron", "بوشرون"]),
        ("ferragamo", ["ferragamo", "فيراغامو"]),
        ("atelier", ["atelier", "اتلييه", "أتيليه"]),
        ("montana", ["montana", "مونتانا"]),
        ("bourjois", ["bourjois", "بورجوا"]),
        ("guerlain", ["guerlain", "جيرلان", "غيرلان"]),
        ("mercedes benz", ["mercedes benz", "مرسيدس بنز"]),
        ("lorenzo pazzaglia", ["lorenzo pazzaglia", "لورينزو بازاجليا"]),
        ("bdk parfums", ["bdk parfums", "بيدي كي"]),
        ("the woods", ["the woods collection", "ذا وودز"]),
        ("marc antoine barrois", ["marc antoine barrois", "مارك انطوان باروا"]),
        ("maison francis kurkdjian", ["maison francis kurkdjian", "ميزون فرانسيس كوركدجيان", "فرانسيس كوركدجيان"]),
        ("thierry mugler", ["thierry mugler", "mugler", "تيري موغلر", "موغلر"]),
        ("lalique", ["lalique", "لاليك"]),
        ("pierre cartra", ["بييرا كاترا"]),
        ("paradise sense", ["بارادايس سنس"]),
    ]
    lower = name.lower()
    for standard, aliases in BRAND_ALIASES:
        for alias in aliases:
            if alias.lower() in lower:
                return standard
    return ""


def _translate_name(name):
    """ترجمة الكلمات الإنجليزية الشائعة إلى العربية والعكس."""
    lower = name.lower()
    for eng, ar in TRANSLATION_MAP.items():
        lower = lower.replace(eng.lower(), ar)
    return lower


def normalize_name(name):
    """تنظيف اسم المنتج للمقارنة."""
    if not name or not isinstance(name, str):
        name = str(name) if name else ""
    if not name:
        return ""
    name = name.lower().strip()
    # ترجمة الأسماء الشائعة
    name = _translate_name(name)
    # إزالة الحجم
    name = re.sub(r"\d+(?:\.\d+)?\s*(?:ml|مل)", "", name, flags=re.I)
    # إزالة الأرقام المنفردة
    name = re.sub(r"\b\d+\b", "", name)
    # إزالة ما بين الأقواس
    name = re.sub(r"\([^)]*\)", "", name)
    # إزالة الكلمات العامة
    for w in COMMON_WORDS:
        name = re.sub(r'\b' + re.escape(w) + r'\b', '', name, flags=re.I)
    # إزالة كلمة عينة/تستر
    name = re.sub(r'\bعينة?\b', '', name)
    name = re.sub(r'\bعينه\b', '', name)
    name = re.sub(r'\bتستر\b', '', name)
    name = re.sub(r'\btester\b', '', name, flags=re.I)
    # إزالة الرموز الزائدة
    name = re.sub(r"[^\w\s]", " ", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name


def _extract_product_core(name):
    """استخراج الجوهر الفريد للمنتج (بدون الماركة والكلمات العامة)."""
    name = normalize_name(name)
    brand_names = [
        "dior", "chanel", "gucci", "tom ford", "توم فورد",
        "versace", "فرساتشي", "armani", "أرماني", "ارماني",
        "ysl", "prada", "برادا", "burberry", "بربري",
        "givenchy", "جيفنشي", "جفنشي", "جيفينشي", "hermes", "هيرمز",
        "creed", "كريد", "montblanc", "مون بلان",
        "calvin klein", "كالفن كلاين", "hugo boss", "هوقو بوس",
        "dolce", "دولتشي", "غابانا", "valentino", "فالنتينو",
        "bvlgari", "بولغاري", "cartier", "كارتييه",
        "lancome", "لانكوم", "jo malone", "جو مالون",
        "amouage", "امواج", "rasasi", "رصاصي",
        "lattafa", "لطافة", "arabian oud", "العربية للعود",
        "ajmal", "أجمل", "al haramain", "الحرمين",
        "afnan", "عفنان", "armaf", "أرماف",
        "nishane", "نيشان", "xerjoff", "زيرجوف",
        "parfums de marly", "مارلي", "دي مارلي",
        "initio", "انيشيو", "byredo", "بايريدو",
        "le labo", "diptyque", "acqua di parma",
        "mancera", "مانسيرا", "منسيرا",
        "montale", "مونتال", "tiziana terenzi", "تيزيانا تيرينزي",
        "kilian", "كيليان", "roja", "روجا",
        "clive christian", "penhaligon", "بنهاليغونز",
        "memo", "ميمو", "aerin",
        "ralph lauren", "رالف لورين", "lalique", "لاليك",
        "montana", "مونتانا", "bourjois", "بورجوا",
        "maison francis kurkdjian", "ميزون فرانسيس كوركدجيان",
        "جيرلان", "guerlain", "غيرلان",
        "chopard", "شوبارد", "narciso", "نارسيسو",
        "carolina herrera", "كارولينا هيريرا",
        "jean paul gaultier", "جان بول غوتييه",
        "issey miyake", "ايسي مياكي", "azzaro", "ازارو",
        "dunhill", "دنهل", "bentley", "بنتلي",
        "boucheron", "بوشرون", "ferragamo", "فيراغامو",
        "اتلييه", "أتيليه", "atelier",
        "الرجالي", "النسائي", "للرجال", "للنساء",
        "عطر الشعر", "هير مست",
    ]
    for b in brand_names:
        name = name.replace(b, "")
    
    # إزالة كلمات مشتركة جداً لا تميز المنتج
    common_words = [
        "ربليكا", "ريبليكا", "replica", "بيوتي",
        "ميزون", "maison", "مارجيلا", "margiela",
        "كريم", "معطر", "الجسم", "شعر",
        "هيرمسنس", "هيرمسينس", "هيرمسيسنس",
        "دوف", "dove",
        "بور هوم", "pour homme", "بور فيم", "pour femme",
        "ايو", "دى", "انتنس", "intense",
        "هيرمس", "hermes", "herm\u00e8s",  # إزالة اسم هيرمز من الجوهر
        "ناسوماتو", "nasomatto",  # إزالة اسم ناسوماتو
        "روسيندو ماتيو", "rossendo mateu",  # إزالة اسم روسيندو
        "شانيل", "chanel",  # إزالة اسم شانيل
        "نيكولاي", "nicolai",  # إزالة اسم نيكولاي
    ]
    for w in common_words:
        name = name.replace(w, "")
    
    name = re.sub(r"\s+", " ", name).strip()
    return name


def _preprocess_comp_products(comp_products):
    """فهرسة مسبقة لمنتجات المنافسين لتسريع المطابقة."""
    indexed = []
    for cp in comp_products:
        cp_name = str(cp.get("product_name", cp.get("name", "")))
        cp_type = classify_product(cp_name)
        if cp_type == "rejected":
            continue
        cp_size = cp.get("size_ml", 0) or extract_size(cp_name)
        cp_price = 0
        try:
            cp_price = float(cp.get("price", 0) or 0)
        except (ValueError, TypeError):
            continue
        cp_norm = normalize_name(cp_name)
        cp_brand = extract_brand(cp_name)
        indexed.append({
            "product": cp,
            "name": cp_name,
            "type": cp_type,
            "size": cp_size,
            "price": cp_price,
            "norm": cp_norm,
            "brand": cp_brand.lower(),
        })
    return indexed


def _types_compatible(my_type, comp_type):
    """
    فحص توافق الأنواع - v3.1
    retail ↔ retail ✅
    tester ↔ tester ✅
    tester ↔ retail ❌ (التستر يقارن فقط بالتستر)
    set ↔ set ✅
    """
    if my_type == comp_type:
        return True
    return False


def match_products(my_products, comp_products, threshold=70):
    """
    مطابقة المنتجات v3.0 - إصلاح شامل.
    
    التحسينات:
    1. ترجمة الأسماء (عربي ↔ إنجليزي) قبل المقارنة
    2. التستر يقارن مع الريتيل
    3. تسامح حجم 30مل بدل 5مل
    4. استخدام token_set_ratio + token_sort_ratio معاً
    5. مطابقة الماركة أولاً (إجبارية) لتسريع وتحسين الدقة
    """
    results = {
        "raise": [],
        "lower": [],
        "ok": [],
        "missing": [],
    }

    matched_comp_ids = set()
    comp_indexed = _preprocess_comp_products(comp_products)

    for my_p in my_products:
        my_name = str(my_p.get("name", ""))
        my_type = classify_product(my_name)
        my_size = my_p.get("size_ml", 0) or extract_size(my_name)
        my_price = 0
        try:
            my_price = float(my_p.get("sell_price", 0) or 0)
        except (ValueError, TypeError):
            continue
        my_norm = normalize_name(my_name)
        my_brand = extract_brand(my_name).lower()

        if my_type == "rejected":
            continue

        best_match = None
        best_score = 0

        for ci in comp_indexed:
            cp_type = ci["type"]
            cp_size = ci["size"]
            cp_price = ci["price"]
            cp_norm = ci["norm"]
            cp_brand = ci["brand"]

            # قانون النوع: يجب توافق النوع
            if not _types_compatible(my_type, cp_type):
                continue

            # قانون الماركة الإجباري: يجب تطابق الماركة
            # إذا كلاهما لديه ماركة، يجب أن تكون نفسها
            if my_brand and cp_brand:
                if my_brand != cp_brand:
                    continue  # ماركات مختلفة = لا مطابقة
            # إذا أحدهما فقط لديه ماركة، لا مطابقة
            elif my_brand or cp_brand:
                continue  # أحدهما معروف والآخر لا = لا مطابقة

            # قانون الحجم: تسامح 30مل
            if my_size > 0 and cp_size > 0:
                if abs(my_size - cp_size) > 30:
                    continue

            # حساب التشابه بعدة طرق
            score_sort = fuzz.token_sort_ratio(my_norm, cp_norm)
            score_set = fuzz.token_set_ratio(my_norm, cp_norm)
            
            # جوهر المنتج (بدون الماركة) - هذا هو المقياس الأهم
            my_core = _extract_product_core(my_name)
            cp_core = _extract_product_core(ci["name"])
            score_core_sort = fuzz.token_sort_ratio(my_core, cp_core) if my_core and cp_core else 0
            score_core_set = fuzz.token_set_ratio(my_core, cp_core) if my_core and cp_core else 0
            score_core = max(score_core_sort, score_core_set)
            
            # فحص إجباري: جوهر المنتج يجب أن يكون متشابهاً بنسبة 70% على الأقل
            if score_core < 70:
                continue  # المنتجات مختلفة تماماً حتى لو نفس الماركة
            
            # النتيجة النهائية: متوسط مرجح بين الاسم الكامل والجوهر
            score_full = max(score_sort, score_set * 0.95)
            score = (score_full * 0.4) + (score_core * 0.6)  # الجوهر أهم
            
            # مكافأة إذا الحجم متطابق تماماً
            if my_size > 0 and cp_size > 0 and my_size == cp_size:
                score = min(100, score * 1.05)

            if score > best_score and score >= threshold:
                best_score = score
                best_match = {
                    "my_product": my_p,
                    "comp_product": ci["product"],
                    "my_price": my_price,
                    "comp_price": cp_price,
                    "match_score": round(score, 1),
                    "my_type": my_type,
                    "comp_type": cp_type,
                    "my_size": my_size,
                    "comp_size": cp_size,
                    "score": round(score, 1),
                    "my_name": my_name,
                    "comp_name": ci["name"],
                }

        if best_match and best_match["comp_price"] > 0:
            cp_id = best_match["comp_product"].get("id", id(best_match["comp_product"]))
            matched_comp_ids.add(cp_id)

            diff = best_match["my_price"] - best_match["comp_price"]
            if best_match["comp_price"] > 0:
                diff_pct = (diff / best_match["comp_price"]) * 100
            else:
                diff_pct = 0

            best_match["price_diff"] = round(diff, 2)
            best_match["diff_percent"] = round(diff_pct, 1)

            abs_pct = abs(diff_pct)
            if abs_pct >= 20:
                risk = "high"
            elif abs_pct >= 10:
                risk = "medium"
            else:
                risk = "low"
            best_match["risk_level"] = risk

            if diff > 0:
                best_match["recommendation"] = "lower"
                results["lower"].append(best_match)
            elif diff < 0:
                best_match["recommendation"] = "raise"
                results["raise"].append(best_match)
            else:
                best_match["recommendation"] = "ok"
                results["ok"].append(best_match)

    # كشف المنتجات المفقودة
    for cp in comp_products:
        cp_id = cp.get("id", id(cp))
        if cp_id not in matched_comp_ids:
            cp_name = str(cp.get("product_name", cp.get("name", "")))
            cp_type = classify_product(cp_name)
            if cp_type != "rejected":
                results["missing"].append({
                    "comp_product": cp,
                    "comp_type": cp_type,
                    "comp_size": (
                        cp.get("size_ml", 0)
                        or extract_size(cp_name)
                    ),
                })

    for key in ["raise", "lower"]:
        results[key].sort(
            key=lambda x: abs(x.get("diff_percent", 0)),
            reverse=True
        )

    return results


def get_risk_color(risk):
    """الحصول على لون الخطورة."""
    colors = {
        "high": "#FF4444",
        "medium": "#FFA500",
        "low": "#44BB44",
    }
    return colors.get(risk, "#888888")


def get_risk_emoji(risk):
    """الحصول على رمز الخطورة."""
    emojis = {
        "high": "🔴",
        "medium": "🟡",
        "low": "🟢",
    }
    return emojis.get(risk, "⚪")


def get_type_label(ptype):
    """الحصول على تسمية النوع بالعربي."""
    labels = {
        "retail": "ريتيل",
        "tester": "تستر",
        "set": "طقم",
        "hair_mist": "هير مست",
        "body_mist": "بودي مست",
        "rejected": "مرفوض",
    }
    return labels.get(ptype, ptype)


def normalize_columns(df):
    """
    تطبيع أسماء الأعمدة لتتطابق مع الأسماء المتوقعة.
    يدعم أسماء الأعمدة العربية والإنجليزية وأسماء CSS.
    """
    column_mapping = {
        'name': ['name', 'اسم', 'اسم المنتج', 'product_name', 'Product Name',
                 'styles_productCard__name__pakbB', 'المنتج', 'عنوان المنتج',
                 'product name', 'title', 'العنوان', 'أسم المنتج'],
        'sell_price': ['sell_price', 'سعر البيع', 'سعر المنتج', 'text-sm-2',
                       'selling_price', 'our_price', 'سعرنا'],
        'price': ['price', 'السعر', 'سعر', 'Price', 'cost', 'التكلفة',
                  'سعر المنافس', 'competitor_price'],
        'size_ml': ['size_ml', 'size', 'الحجم', 'حجم', 'ml', 'الحجم (مل)'],
        'id': ['id', 'رقم', 'رقم المنتج', 'product_id', 'ID', 'No.', 'no',
               'المعرف', 'الرقم'],
        'product_name': ['product_name', 'اسم المنتج', 'المنتج', 'أسم المنتج'],
    }
    
    df_normalized = df.copy()
    
    for target_col, possible_names in column_mapping.items():
        if target_col not in df_normalized.columns:
            for col in df.columns:
                col_clean = col.strip().lower()
                possible_lower = [n.strip().lower() for n in possible_names]
                if col_clean in possible_lower:
                    df_normalized[target_col] = df[col]
                    break
    
    if 'sell_price' not in df_normalized.columns and 'price' in df_normalized.columns:
        df_normalized['sell_price'] = df_normalized['price']
    
    if 'price' not in df_normalized.columns and 'sell_price' in df_normalized.columns:
        df_normalized['price'] = df_normalized['sell_price']
    
    if 'name' not in df_normalized.columns and 'product_name' in df_normalized.columns:
        df_normalized['name'] = df_normalized['product_name']
    
    return df_normalized


def run_full_analysis(my_file, comp_files, threshold=55):
    """
    تشغيل التحليل الكامل للمنتجات v3.0.
    
    المعاملات:
    - my_file: dict بـ {"name": str, "data": bytes} ملف المتجر
    - comp_files: list من dicts ملفات المنافسين
    - threshold: الحد الأدنى لنسبة التطابق (40-100)
    """
    import pandas as pd
    from io import BytesIO
    
    # 1. تحميل ملف المتجر
    try:
        if my_file["name"].endswith(".xlsx"):
            my_data = pd.read_excel(BytesIO(my_file["data"]))
        else:
            my_data = pd.read_csv(BytesIO(my_file["data"]))
        my_data = normalize_columns(my_data)
        my_products = my_data.to_dict(orient="records")
    except Exception as e:
        return {"error": f"خطأ في تحميل ملف المتجر: {str(e)}", "stats": {}}
    
    # 2. تحميل ملفات المنافسين
    all_comp_products = []
    for comp_file in comp_files:
        try:
            if comp_file["name"].endswith(".xlsx"):
                comp_data = pd.read_excel(BytesIO(comp_file["data"]))
            else:
                comp_data = pd.read_csv(BytesIO(comp_file["data"]))
            comp_data = normalize_columns(comp_data)
            comp_products = comp_data.to_dict(orient="records")
            all_comp_products.extend(comp_products)
        except Exception as e:
            continue
    
    if not all_comp_products:
        return {"error": "لم يتم تحميل أي ملفات منافسين", "stats": {}}
    
    # 3. تصفية المنتجات الفارغة
    my_products = [p for p in my_products if p.get('name') or p.get('sell_price')]
    all_comp_products = [p for p in all_comp_products if p.get('name') or p.get('price')]
    
    if not my_products:
        return {"error": "لا توجد منتجات صحيحة في ملف المتجر", "stats": {}}
    if not all_comp_products:
        return {"error": "لا توجد منتجات صحيحة في ملفات المنافسين", "stats": {}}
    
    # 4. تشغيل المطابقة
    match_results = match_products(my_products, all_comp_products, threshold)
    
    # 5. تحويل النتائج إلى DataFrames
    df_raise = pd.DataFrame([
        {
            "المنتج": str(m["my_product"].get("name", "")),
            "السعر": m["my_price"],
            "سعر المنافس": m["comp_price"],
            "الفرق": m["price_diff"],
            "النسبة %": m["diff_percent"],
            "الخطورة": {"high": "حرج", "medium": "متوسط", "low": "عادي"}.get(m["risk_level"], "عادي"),
            "نسبة التطابق": m["match_score"],
            "pid_my": m["my_product"].get("id", ""),
            "pid_comp": m["comp_product"].get("id", ""),
        }
        for m in match_results["raise"]
    ])
    
    df_lower = pd.DataFrame([
        {
            "المنتج": str(m["my_product"].get("name", "")),
            "السعر": m["my_price"],
            "سعر المنافس": m["comp_price"],
            "الفرق": m["price_diff"],
            "النسبة %": m["diff_percent"],
            "الخطورة": {"high": "حرج", "medium": "متوسط", "low": "عادي"}.get(m["risk_level"], "عادي"),
            "نسبة التطابق": m["match_score"],
            "pid_my": m["my_product"].get("id", ""),
            "pid_comp": m["comp_product"].get("id", ""),
        }
        for m in match_results["lower"]
    ])
    
    df_approved = pd.DataFrame([
        {
            "المنتج": str(m["my_product"].get("name", "")),
            "السعر": m["my_price"],
            "سعر المنافس": m["comp_price"],
            "الفرق": m["price_diff"],
            "النسبة %": m["diff_percent"],
            "نسبة التطابق": m["match_score"],
            "pid_my": m["my_product"].get("id", ""),
            "pid_comp": m["comp_product"].get("id", ""),
        }
        for m in match_results["ok"]
    ])
    
    df_missing = pd.DataFrame([
        {
            "المنتج": str(m["comp_product"].get("product_name", m["comp_product"].get("name", ""))),
            "النوع": get_type_label(m["comp_type"]),
            "الحجم": m["comp_size"],
            "pid_comp": m["comp_product"].get("id", ""),
        }
        for m in match_results["missing"]
    ])
    
    # 6. دمج جميع النتائج
    df_all = pd.concat([df_raise, df_lower, df_approved], ignore_index=True)
    
    # 7. إحصائيات
    stats = {
        "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total": len(df_all),
        "raise_count": len(df_raise),
        "lower_count": len(df_lower),
        "approved_count": len(df_approved),
        "missing_count": len(df_missing),
        "critical": len(df_all[df_all["الخطورة"] == "حرج"]) if not df_all.empty and "الخطورة" in df_all.columns else 0,
        "avg_diff": round(df_all["الفرق"].mean(), 2) if not df_all.empty and "الفرق" in df_all.columns else 0,
        "competitors": len(comp_files),
        "my_products_count": len(my_products),
        "comp_products_count": len(all_comp_products),
    }
    
    return {
        "stats": stats,
        "raise": df_raise,
        "lower": df_lower,
        "approved": df_approved,
        "missing": df_missing,
        "all": df_all,
    }


def gemini_verify(my_product_name, comp_product_name, my_price, comp_price, api_key=None):
    """التحقق من صحة المطابقة بين منتجين باستخدام Gemini AI."""
    if not api_key:
        return {"verified": False, "error": "لم يتم توفير Gemini API Key"}
    
    import requests, json
    
    prompt = f"""أنت خبير عطور. تحقق هل هذان نفس المنتج:

منتج 1 (متجري): {my_product_name}
منتج 2 (منافس): {comp_product_name}

سعري: {my_price} ريال
سعر المنافس: {comp_price} ريال

أجب بـ JSON فقط بدون أي نص آخر:
{{
  "is_same_product": true/false,
  "confidence": 0.0-1.0,
  "market_price": سعر السوق التقريبي بالريال,
  "estimated_cost": التكلفة التقديرية بالريال,
  "recommendation": "رفع" أو "خفض" أو "مناسب",
  "notes": "ملاحظات قصيرة"
}}"""
    
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.1, "maxOutputTokens": 500}
        }
        resp = requests.post(url, json=payload, timeout=30)
        if resp.status_code == 200:
            text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
            text = text.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1].rsplit("```", 1)[0]
            result = json.loads(text)
            result["verified"] = True
            return result
        else:
            return {"verified": False, "error": f"خطأ API: {resp.status_code}"}
    except Exception as e:
        return {"verified": False, "error": str(e)}


def gemini_search_product(product_name, api_key=None):
    """البحث عن منتج واستخراج معلوماته باستخدام Gemini AI."""
    if not api_key:
        return {"found": False, "error": "لم يتم توفير Gemini API Key"}
    
    import requests, json
    
    prompt = f"""أنت خبير عطور. ابحث عن هذا المنتج:

المنتج: {product_name}

أجب بـ JSON فقط بدون أي نص آخر:
{{
  "found": true/false,
  "brand": "الماركة",
  "product_line": "خط المنتج",
  "type": "retail/tester/sample/set",
  "size_ml": الحجم بالمل,
  "market_price_sar": سعر السوق بالريال,
  "estimated_cost_sar": التكلفة التقديرية بالريال,
  "gender": "رجالي/نسائي/للجنسين",
  "concentration": "EDP/EDT/Parfum/Cologne",
  "notes": "ملاحظات قصيرة"
}}"""
    
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.1, "maxOutputTokens": 500}
        }
        resp = requests.post(url, json=payload, timeout=30)
        if resp.status_code == 200:
            text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
            text = text.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1].rsplit("```", 1)[0]
            result = json.loads(text)
            return result
        else:
            return {"found": False, "error": f"خطأ API: {resp.status_code}"}
    except Exception as e:
        return {"found": False, "error": str(e)}


def gemini_analyze_supplier(supplier_data, api_key=None):
    """تحليل ملف مورد باستخدام Gemini لاستخراج الأسماء والتكاليف."""
    if not api_key:
        return []
    
    import requests, json
    
    results = []
    batch_size = 20
    
    for i in range(0, len(supplier_data), batch_size):
        batch = supplier_data[i:i+batch_size]
        products_text = "\n".join([
            f"{j+1}. {p.get('name', p.get('product_name', ''))}: {p.get('price', p.get('cost', 'N/A'))}" 
            for j, p in enumerate(batch)
        ])
        
        prompt = f"""أنت خبير عطور. حلل هذه المنتجات من مورد:

{products_text}

لكل منتج، حدد:
- الاسم الصحيح (الماركة + اسم المنتج)
- التكلفة التقديرية بالريال
- سعر السوق بالريال

أجب بـ JSON array فقط:
[
  {{
    "original_name": "الاسم الأصلي",
    "correct_name": "الاسم الصحيح",
    "brand": "الماركة",
    "estimated_cost": التكلفة,
    "market_price": سعر السوق
  }}
]"""
        
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.1, "maxOutputTokens": 2000}
            }
            resp = requests.post(url, json=payload, timeout=60)
            if resp.status_code == 200:
                text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
                text = text.strip()
                if text.startswith("```"):
                    text = text.split("\n", 1)[1].rsplit("```", 1)[0]
                batch_results = json.loads(text)
                results.extend(batch_results)
        except Exception:
            continue
    
    return results


def export_excel(match_results, filename="perfume_analysis.xlsx"):
    """تصدير نتائج المطابقة إلى ملف Excel."""
    import pandas as pd
    from io import BytesIO
    
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        if match_results.get("raise"):
            df_raise = pd.DataFrame([
                {
                    "المنتج": str(m.get("my_product", {}).get("name", "")),
                    "السعر": m.get("my_price", 0),
                    "سعر المنافس": m.get("comp_price", 0),
                    "الفرق": m.get("price_diff", 0),
                    "النسبة %": m.get("diff_percent", 0),
                    "نسبة التطابق": m.get("match_score", 0),
                    "التوصية": "رفع السعر",
                }
                for m in match_results["raise"]
            ])
            df_raise.to_excel(writer, sheet_name="رفع السعر", index=False)
        
        if match_results.get("lower"):
            df_lower = pd.DataFrame([
                {
                    "المنتج": str(m.get("my_product", {}).get("name", "")),
                    "السعر": m.get("my_price", 0),
                    "سعر المنافس": m.get("comp_price", 0),
                    "الفرق": m.get("price_diff", 0),
                    "النسبة %": m.get("diff_percent", 0),
                    "نسبة التطابق": m.get("match_score", 0),
                    "التوصية": "خفض السعر",
                }
                for m in match_results["lower"]
            ])
            df_lower.to_excel(writer, sheet_name="خفض السعر", index=False)
        
        if match_results.get("ok"):
            df_ok = pd.DataFrame([
                {
                    "المنتج": str(m.get("my_product", {}).get("name", "")),
                    "السعر": m.get("my_price", 0),
                    "سعر المنافس": m.get("comp_price", 0),
                    "الفرق": m.get("price_diff", 0),
                    "التوصية": "سعر مناسب",
                }
                for m in match_results["ok"]
            ])
            df_ok.to_excel(writer, sheet_name="سعر مناسب", index=False)
        
        if match_results.get("missing"):
            df_missing = pd.DataFrame([
                {
                    "المنتج": str(m.get("comp_product", {}).get("product_name", m.get("comp_product", {}).get("name", ""))),
                    "النوع": get_type_label(m.get("comp_type", "")),
                    "الحجم": m.get("comp_size", 0),
                }
                for m in match_results["missing"]
            ])
            df_missing.to_excel(writer, sheet_name="منتجات مفقودة", index=False)
    
    output.seek(0)
    return output


def send_to_make(data, webhook_url=None):
    """إرسال البيانات إلى Make.com webhook."""
    import requests
    import json
    
    if not webhook_url:
        return {
            "success": False,
            "message": "لم يتم توفير رابط webhook"
        }
    
    try:
        headers = {"Content-Type": "application/json"}
        
        if isinstance(data, dict):
            payload = data
        else:
            payload = {"data": data}
        
        response = requests.post(
            webhook_url,
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            return {
                "success": True,
                "message": "تم الإرسال بنجاح",
                "status_code": response.status_code,
            }
        else:
            return {
                "success": False,
                "message": f"خطأ: {response.status_code} - {response.text[:200]}",
                "status_code": response.status_code,
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"خطأ في الاتصال: {str(e)}"
        }


# ===== فئات مساعدة =====

class MatchingEngine:
    """محرك المطابقة الرئيسي."""
    
    def __init__(self, threshold=55):
        self.threshold = threshold
    
    def match(self, my_products, comp_products):
        """تشغيل المطابقة."""
        return match_products(my_products, comp_products, self.threshold)


class ProductMatcher:
    """فئة مساعدة لمطابقة المنتجات."""
    
    @staticmethod
    def classify(name):
        """تصنيف المنتج."""
        return classify_product(name)
    
    @staticmethod
    def extract_size(name):
        """استخراج الحجم."""
        return extract_size(name)
    
    @staticmethod
    def extract_brand(name):
        """استخراج الماركة."""
        return extract_brand(name)
    
    @staticmethod
    def normalize(name):
        """تنظيف الاسم."""
        return normalize_name(name)
