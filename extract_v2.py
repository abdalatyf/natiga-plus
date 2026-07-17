import sys, io, re, json
from pypdf import PdfReader

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

courses_sem1 = [
    'IMP07-10102_01', 'IMP07-10103_01', 'IMP07-10104_01', 'IMP07-10105_01',
    'IMP07-10106_01', 'IMP07-10107_01', 'IMP07-10108_01', 'IMP07-EA03_01', 'URR07-10101_01'
]
courses_sem2 = [
    'IMP07-10211_01', 'IMP07-10212_01', 'IMP07-10213_01', 'IMP07-10214_01',
    'IMP07-10215_01', 'IMP07-ENA04_01', 'URR07-10209_01', 'URR07-10210_01'
]

course_names = {
    'IMP07-10102_01': 'NHB',
    'IMP07-10103_01': 'POD',
    'IMP07-10104_01': 'BMS',
    'IMP07-10105_01': 'POG',
    'IMP07-10106_01': 'CS',
    'IMP07-10107_01': 'EN',
    'IMP07-10108_01': 'Soft Skills',
    'IMP07-EA03_01': 'CPR',
    'URR07-10101_01': 'Feqh',
    'IMP07-10211_01': 'Ethics',
    'IMP07-10212_01': 'HEM',
    'IMP07-10213_01': 'MSK',
    'IMP07-10214_01': 'Research',
    'IMP07-10215_01': 'RESP',
    'IMP07-ENA04_01': 'Adab',
    'URR07-10209_01': 'Aqeeda',
    'URR07-10210_01': 'Quran'
}

reader = PdfReader('Oula (1).pdf')
lines = []
for i in range(len(reader.pages)):
    page = reader.pages[i]
    text = page.extract_text()
    lines.extend([l.strip() for l in text.split('\n')])

print(f"Extracted {len(lines)} lines from PDF.")

student_bufs = []
cur = []
for l in lines:
    if re.match(r'^\d+$', l) and len(l) < 4 and len(cur) > 10:
        pass
    if re.match(r'^\d{12}$', l):
        if cur:
            if len(cur) > 0 and re.match(r'^\d+$', cur[-1]):
                idx_line = cur.pop()
                student_bufs.append(cur)
                cur = [idx_line, l]
            else:
                student_bufs.append(cur)
                cur = [l]
        else:
            cur.append(l)
    else:
        cur.append(l)
if cur:
    student_bufs.append(cur)

def extract_gpa(line):
    m = re.search(r'(\d+\.\d{2})', line)
    if m:
        return float(m.group(1))
    if line.startswith('0'):
        return 0.0
    return 0.0

students_data = []
grades_data = []

grade_pattern = r'((?:\d+\.\d+(?:\|\|\d+\.\d+)*)|\(Abs\))(A\+|A-|A|B\+|B|C\+|C|D\-|D|F|P|NP)(\d+\.\d{2})(\d+\.\d{2})'

for buf in student_bufs:
    if not buf: continue
    
    seat, name, nationality, status = None, None, None, None
    for i, l in enumerate(buf):
        if re.match(r'^\d{12}$', l):
            name = None
            for j in range(i+1, min(i+10, len(buf))):
                m = re.search(r'(?:05-(\d{5}))|(?:(\d{5})--05)|(?:[A-Z]-(\d{5})-05)|(?:05-[A-Z]-(\d{5}))|(?:\b(\d{5})\b.*05)', buf[j])
                if m:
                    seat = m.group(1) or m.group(2) or m.group(3) or m.group(4) or m.group(5)
                    name = buf[j+1].replace('\x00', '').strip()
                    status = buf[j+2].replace('\x00', '').strip()
                    nationality = buf[j+3].replace('\x00', '').strip()
                    break
            if not seat:
                seat = l # Fallback to 12 digit ID
                name = buf[i+1].replace('\x00', '').strip()
                status = buf[i+2].replace('\x00', '').strip()
                nationality = buf[i+3].replace('\x00', '').strip()
            break
            
    if not seat: continue

    notes = ""
    # Usually the last few lines contain the notes.
    # A simple heuristic: everything after the last grade string that doesn't match standard patterns.
    # Actually, we don't really need notes for now, but let's keep it simple.

    sem1_grades, sem2_grades = [], []
    gpas = []
    
    grade_strings_found = []
    
    for i, l in enumerate(buf):
        matches = re.findall(grade_pattern, l)
        if len(matches) > 0:
            grade_strings_found.append((i, matches))
            
    if len(grade_strings_found) >= 1:
        sem1_idx, sem1_grades = grade_strings_found[0]
        if sem1_idx >= 2:
            gpas.append(extract_gpa(buf[sem1_idx-2]))
            gpas.append(extract_gpa(buf[sem1_idx-1]))
    
    if len(grade_strings_found) >= 2:
        sem2_idx, sem2_grades = grade_strings_found[1]
        if sem2_idx >= 1:
            gpas.append(extract_gpa(buf[sem2_idx-1]))

    # Fallbacks for GPAs
    # gpas[0] is Semester 1 GPA
    # gpas[1] is GPAU
    # gpas[2] is Semester 2 GPA
    gpa1 = gpas[0] if len(gpas) > 0 else 0.0
    gpau = gpas[1] if len(gpas) > 1 else gpa1
    gpa2 = gpas[2] if len(gpas) > 2 else 0.0

    failed = (gpau == 0.0)

    students_data.append({
        'seat': seat,
        'name': name,
        'nationality': nationality,
        'gpa_sem1': gpa1,
        'gpa_sem2': gpa2,
        'gpau': gpau,
        'failed': failed,
        'notes': notes
    })

    # When the string is shorter than courses_sem1, some courses were missing.
    # We will just map them sequentially. If they are missing, the student missed them (F).
    for i, m in enumerate(sem1_grades):
        if i >= len(courses_sem1): break
        c_code = courses_sem1[i]
        
        score_str = m[0]
        if '(Abs)' in score_str:
            score = 0.0
        elif '||' in score_str:
            score = float(score_str.split('||')[-1])
        else:
            score = float(score_str)
            
        grades_data.append({
            'seat': seat,
            'course': course_names[c_code],
            'semester': 1,
            'score': score,
            'grade': m[1],
            'points': float(m[2]),
            'is_pnp': m[1] in ['P', 'NP']
        })

    for i, m in enumerate(sem2_grades):
        if i >= len(courses_sem2): break
        c_code = courses_sem2[i]
        
        score_str = m[0]
        if '(Abs)' in score_str:
            score = 0.0
        elif '||' in score_str:
            score = float(score_str.split('||')[-1])
        else:
            score = float(score_str)
            
        grades_data.append({
            'seat': seat,
            'course': course_names[c_code],
            'semester': 2,
            'score': score,
            'grade': m[1],
            'points': float(m[2]),
            'is_pnp': m[1] in ['P', 'NP']
        })

print(f"Extracted {len(students_data)} students and {len(grades_data)} grades.")

with open('raw_data_v2.json', 'w', encoding='utf-8') as f:
    json.dump({
        'students': students_data,
        'grades': grades_data
    }, f, ensure_ascii=False, indent=2)

print("Saved to raw_data_v2.json")
