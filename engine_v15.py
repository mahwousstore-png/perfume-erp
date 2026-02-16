# engine_v15.py

# استخدام RapidFuzz للمطابقة الفائقة السرعة (أسرع 10-20x من fuzzywuzzy)

from rapidfuzz import fuzz  # مكتبة المطابقة السريعة - أفضل من fuzzywuzzy

# ... (other content) ...

# حساب نسبة التطابق باستخدام RapidFuzz (أسرع 10-20x من fuzzywuzzy)
# token_set_ratio: يتجاهل ترتيب الكلمات ويركز على التطابق الدلالي
score = fuzz.token_set_ratio(my_name, comp_name)