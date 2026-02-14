"""
دالة استخراج التركيز من اسم العطر
"""
import re

def extract_concentration(name):
    """
    استخراج تركيز العطر من اسمه.
    
    Returns:
        str: التركيز (edp, edt, parfum, cologne, oil, etc.) أو "" إذا لم يتم العثور عليه
    """
    lower = name.lower()
    
    # قائمة التركيزات مرتبة من الأقوى للأضعف
    concentrations = [
        # Parfum / Extrait
        (r'\bparfum\b|\bextrait\b|\bpure perfume\b|\bعطر خالص\b', 'parfum'),
        
        # Eau de Parfum
        (r'\bedp\b|\beau de parfum\b|\bأو دو بارفان\b|\bاو دي بارفيوم\b', 'edp'),
        
        # Eau de Toilette
        (r'\bedt\b|\beau de toilette\b|\bأو دو تواليت\b|\bاو دي تواليت\b', 'edt'),
        
        # Eau de Cologne
        (r'\bedc\b|\beau de cologne\b|\bكولونيا\b|\bكولون\b', 'cologne'),
        
        # Perfume Oil
        (r'\boil\b|\bperfume oil\b|\bزيت عطر\b|\bعطر زيتي\b', 'oil'),
        
        # Eau Fraiche
        (r'\beau fraiche\b|\bأو فريش\b', 'fraiche'),
        
        # Mist / Spray
        (r'\bmist\b|\bspray\b|\bبخاخ\b|\bمست\b', 'mist'),
    ]
    
    for pattern, conc_type in concentrations:
        if re.search(pattern, lower):
            return conc_type
    
    return ""


def concentrations_match(conc1, conc2):
    """
    التحقق من تطابق التركيزات.
    
    Returns:
        bool: True إذا كانت التركيزات متطابقة أو متوافقة
    """
    # إذا لم يتم تحديد أحدهما، نعتبرها متطابقة
    if not conc1 or not conc2:
        return True
    
    # تطابق تام
    if conc1 == conc2:
        return True
    
    # تطابق متوافق (مثلاً parfum و edp قريبان)
    compatible_groups = [
        {'parfum', 'edp'},  # قريبان في القوة
        {'edt', 'cologne'},  # قريبان في القوة
    ]
    
    for group in compatible_groups:
        if conc1 in group and conc2 in group:
            return True
    
    return False
