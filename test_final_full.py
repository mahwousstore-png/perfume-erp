"""اختبار نهائي شامل مع كل البيانات + فحص دقة العينة"""
import sys, os, time, random, json
sys.path.insert(0, '/home/ubuntu/perfume-erp')
os.environ['GEMINI_API_KEY'] = os.environ.get('GEMINI_API_KEY', '')

import pandas as pd
from engine import normalize_columns, _get_name, _get_price
from engine_v2 import run_smart_matching

# ===== تحميل البيانات =====
print("=" * 80)
print("📂 تحميل البيانات...")
print("=" * 80)

store_path = '/home/ubuntu/perfume-erp/test_data/منتجاتمهووستنسيقتحيثالاسعار.csv'
my_df = pd.read_csv(store_path)
my_df = normalize_columns(my_df)
print(f"✅ منتجات المتجر: {len(my_df)}")

comp_dir = '/home/ubuntu/perfume-erp/test_data'
store_filename = 'منتجاتمهووستنسيقتحيثالاسعار.csv'
comp_dfs = []
for f in os.listdir(comp_dir):
    if f.endswith('.csv') and f != store_filename:
        df = pd.read_csv(os.path.join(comp_dir, f))
        df = normalize_columns(df)
        df['_competitor'] = f.replace('.csv', '')
        comp_dfs.append(df)
        print(f"  📄 {f}: {len(df)} منتج")

comp_df = pd.concat(comp_dfs, ignore_index=True)
print(f"✅ إجمالي المنافسين: {len(comp_df)} من {len(comp_dfs)} ملف")

# ===== تشغيل المحرك =====
print("\n" + "=" * 80)
print("🚀 بدء المعالجة...")
print("=" * 80)

start = time.time()
results = run_smart_matching(my_df, comp_df, use_gemini=False)
elapsed = time.time() - start

print(f"\n⏱️ الوقت: {elapsed:.1f} ثانية")
print(f"📊 إجمالي النتائج: {len(results)}")

# ===== تحليل النتائج =====
matched = [r for r in results if r.get('category') != 'missing']
missing = [r for r in results if r.get('category') == 'missing']

raise_price = [r for r in results if r.get('category') == 'raise_price']
lower_price = [r for r in results if r.get('category') == 'lower_price']
ok_price = [r for r in results if r.get('category') == 'keep_price']

print(f"\n📈 المطابقات: {len(matched)} ({len(matched)/len(results)*100:.1f}%)")
print(f"  🔴 رفع سعر: {len(raise_price)}")
print(f"  🟡 خفض سعر: {len(lower_price)}")
print(f"  🟢 موافق: {len(ok_price)}")
print(f"🔵 مفقود: {len(missing)} ({len(missing)/len(results)*100:.1f}%)")

# ===== فحص دقة العينة =====
print("\n" + "=" * 80)
print("🔍 فحص دقة العينة (50 مطابقة عشوائية):")
print("=" * 80)

sample = random.sample(matched, min(50, len(matched)))
suspicious = []
for r in sample:
    my_name = r.get('my_name', '')
    comp_name = r.get('comp_name', '')
    confidence = r.get('confidence', 0)
    
    # فحص بسيط: هل الاسمان يحتويان على نفس الكلمات الأساسية؟
    my_words = set(my_name.lower().split())
    comp_words = set(comp_name.lower().split())
    # إزالة كلمات عامة
    noise = {'عطر', 'أو', 'او', 'دو', 'دي', 'برفيوم', 'بارفيوم', 'تواليت', 'مل', 'من', 'في', 'لل', 'ال', '100', '50', '75', '200', '150'}
    my_clean = my_words - noise
    comp_clean = comp_words - noise
    common = my_clean & comp_clean
    all_w = my_clean | comp_clean
    overlap = len(common) / max(len(all_w), 1)
    
    status = "✅" if overlap >= 0.3 else "⚠️"
    if overlap < 0.3:
        suspicious.append(r)
    
    print(f"  {status} [{confidence:.0f}%] {my_name[:50]} ← {comp_name[:50]} (words:{overlap:.0%})")

print(f"\n📊 نتيجة فحص الدقة:")
print(f"  ✅ صحيحة: {len(sample) - len(suspicious)}/{len(sample)}")
print(f"  ⚠️ مشكوك: {len(suspicious)}/{len(sample)}")

if suspicious:
    print(f"\n⚠️ المطابقات المشكوك فيها:")
    for r in suspicious:
        print(f"  - {r.get('my_name', '')[:60]}")
        print(f"    ← {r.get('comp_name', '')[:60]}")
        print(f"    الثقة: {r.get('confidence', 0):.0f}%")

# ===== التحقق من الحقول =====
print("\n" + "=" * 80)
print("🔧 التحقق من الحقول:")
print("=" * 80)

if matched:
    sample_r = matched[0]
    required_fields = ['my_name', 'comp_name', 'my_price', 'comp_price', 'diff', 'diff_pct', 
                       'confidence', 'my_brand', 'comp_brand', 'my_size', 'comp_size',
                       'my_conc', 'comp_conc', 'competitor', 'match_stage', 'status']
    for f in required_fields:
        val = sample_r.get(f, 'MISSING')
        status = "✅" if val != 'MISSING' else "❌"
        print(f"  {status} {f}: {val}")

# ===== حفظ النتائج =====
with open('/home/ubuntu/perfume-erp/test_results_final.json', 'w', encoding='utf-8') as f:
    json.dump({
        'total': len(results),
        'matched': len(matched),
        'missing': len(missing),
        'raise_price': len(raise_price),
        'lower_price': len(lower_price),
        'ok_price': len(ok_price),
        'elapsed': elapsed,
        'suspicious': len(suspicious),
    }, f, ensure_ascii=False, indent=2)

print(f"\n✅ تم حفظ النتائج في test_results_final.json")
print(f"\n{'='*80}")
print(f"🎯 الخلاصة:")
print(f"  - إجمالي: {len(results)} | مطابق: {len(matched)} | مفقود: {len(missing)}")
print(f"  - الدقة: {(len(sample)-len(suspicious))/max(len(sample),1)*100:.0f}%")
print(f"  - الوقت: {elapsed:.1f}ث")
print(f"{'='*80}")
