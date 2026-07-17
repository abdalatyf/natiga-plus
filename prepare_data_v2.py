import json
import re
import unicodedata

with open('raw_data_v3.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# The user stated there are 1163 valid students. Let's filter out ones with no grades or missing seat numbers
# Also, remove students whose names are totally blank (unlikely)
students = data['students']
grades = data['grades']

print(f"Initial students: {len(students)}")

# We don't filter out students with no grades, because they might be fully failed students.
# Just deduplicate and clean names.

def clean_arabic_name(name):
    name = name.strip()
    # 1. Fix RTL wrap-around for 'ي ن' (Yaa Noon)
    if name.startswith('ي ن'):
        name = name[3:] + 'ين'
    # 2. Fix RTL wrap-around for 'فى' (Faa AlifMaqsura from Mostafa)
    if name.startswith('فى'):
        name = name[2:] + 'فى'
        
    # 3. Common PyMuPDF replacements
    replacements = {
        'مصطىف': 'مصطفى',
        'مع ز ت': 'معتز',
        'يحىي': 'يحيى',
        'يارس': 'ياسر',
        'عىل': 'علي',
        'قرصاوى': 'قصراوى',
        'لطىف': 'لطفي',
        'حلىم': 'حليم',
        'الميىه': 'الميهي',
        'بالل': 'بلال',
        'بيوىم': 'بيومي',
        'بسيوىن': 'بسيوني',
        'جويىل': 'جويلي',
        'عبد العاىط': 'عبد العاطي',
        'الز ي يد': 'اليزيد',
        'عبد هللا': 'عبد الله',
        'عبدهللا': 'عبدالله',
        'اسالم': 'اسلام',
        'صرب ى': 'صبري',
        'سمري': 'سمير',
        'نرص': 'نصر',
        'سالمه': 'سلامه'
    }
    
    for k, v in replacements.items():
        name = name.replace(k, v)
        
    # Fix trailing letters that got wrapped
    if name.endswith('مصط'):
        name = name[:-3] + 'مصطفى'
        
    name = re.sub(r'\s+', ' ', name).strip()
    return name

# Clean up names: remove extra spaces, normalize unicode, and fix PyMuPDF artifacts
for s in students:
    name = s['name']
    name = unicodedata.normalize('NFKC', name)
    name = clean_arabic_name(name)
    s['name'] = name

# Ensure exactly one record per seat (handle duplicates just in case)
unique_students = {}
for s in students:
    if s['seat'] not in unique_students:
        unique_students[s['seat']] = s
    else:
        # If duplicate, keep the one with a non-zero GPA if possible
        if s['gpau'] > unique_students[s['seat']]['gpau']:
            unique_students[s['seat']] = s
students = list(unique_students.values())

print(f"Students after deduplication: {len(students)}")

# Now we sort students by GPAU to assign rank
# Exclude failed students (GPAU == 0 or failed flag) from getting a numbered rank?
# Wait, the user said:
# "الترتيب يشمل كل الطلاب الـ 1163 (الناجحين والراسبين). الراسب يكون في آخر الترتيب (معدله 0)."
# So we sort ALL students descending by GPAU.
students.sort(key=lambda x: x['gpau'], reverse=True)

current_rank = 1
for i, s in enumerate(students):
    if i > 0 and s['gpau'] < students[i-1]['gpau']:
        current_rank = i + 1
    s['rank'] = current_rank

# Convert GPA to 2 decimal places to be safe
for s in students:
    s['gpa_sem1'] = round(s['gpa_sem1'], 2)
    s['gpa_sem2'] = round(s['gpa_sem2'], 2)
    s['gpau'] = round(s['gpau'], 2)

# Grades also have P/NP, ensure they don't leak "score" values to the UI by zeroing them out in DB
for g in grades:
    if g['is_pnp']:
        g['score'] = 0.0
        g['points'] = 0.0

final_db = {
    'students': students,
    'grades': grades,
    'courses': {
        'NHB': 'IMP07-10102_01',
        'POD': 'IMP07-10103_01',
        'BMS': 'IMP07-10104_01',
        'POG': 'IMP07-10105_01',
        'CS': 'IMP07-10106_01',
        'EN': 'IMP07-10107_01',
        'Soft Skills': 'IMP07-10108_01',
        'CPR': 'IMP07-EA03_01',
        'Feqh': 'URR07-10101_01',
        'Ethics': 'IMP07-10211_01',
        'HEM': 'IMP07-10212_01',
        'MSK': 'IMP07-10213_01',
        'Research': 'IMP07-10214_01',
        'RESP': 'IMP07-10215_01',
        'Adab': 'IMP07-ENA04_01',
        'Aqeeda': 'URR07-10209_01',
        'Quran': 'URR07-10210_01'
    }
}

with open('dashboard/src/data/db.json', 'w', encoding='utf-8') as f:
    json.dump(final_db, f, ensure_ascii=False, separators=(',', ':'))

print(f"Data prepared and saved to db.json. Final student count: {len(students)}")
