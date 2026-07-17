import sys, io, re, json
import fitz

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

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

doc = fitz.open('Oula (1).pdf')
lines = []
for page in doc:
    text = page.get_text()
    lines.extend([l.strip() for l in text.split('\n') if l.strip()])

print(f"Extracted {len(lines)} lines from PDF using PyMuPDF.")

students_dict = {}
grades_data = []

def extract_gpa(line):
    m = re.search(r'(\d+(?:\.\d+)?)', line)
    return float(m.group(1)) if m else 0.0

i = 0
while i < len(lines):
    # Find next student ID
    if re.match(r'^\d{12}$', lines[i]):
        student_id = lines[i]
        i += 1
        
        seat = None
        name = ""
        nationality = ""
        
        # Look ahead for seat number
        for j in range(i, min(i+5, len(lines))):
            m = re.search(r'(?:05-(\d{5}))|(?:(\d{5})--05)|(?:[A-Z]-(\d{5})-05)|(?:05-[A-Z]-(\d{5}))|(?:\b(\d{5})\b.*05)', lines[j])
            if m:
                seat = m.group(1) or m.group(2) or m.group(3) or m.group(4) or m.group(5)
                name = lines[j+1]
                status = lines[j+2]
                nationality = lines[j+3]
                i = j + 4
                break
                
        if not seat:
            seat = student_id
            name = lines[i]
            status = lines[i+1]
            nationality = lines[i+2]
            i += 3
            
        # Fast forward to "أول" (Semester 1)
        while i < len(lines) and lines[i] != "أول" and not re.match(r'^\d{12}$', lines[i]):
            i += 1
            
        if i >= len(lines) or re.match(r'^\d{12}$', lines[i]):
            continue # Malformed or end
            
        i += 1 # skip "أول"
        
        sem1_courses = []
        while i < len(lines):
            m = re.search(r'(IMP07-[A-Z0-9_]+|URR07-[A-Z0-9_]+)', lines[i])
            if m:
                c_code = m.group(1)
                if c_code == 'IMP07-EA': c_code = 'IMP07-EA03_01'
                if c_code == 'IMP07-ENA': c_code = 'IMP07-ENA04_01'
                if c_code in course_names:
                    sem1_courses.append(c_code)
            # Stop if we hit GPA line (starts with letter grade + float, or just a number like 0 or 0.00)
            if re.match(r'^([A-Z\+\-]+\s*)?\d+(?:\.\d+)?$', lines[i]):
                break
            i += 1
            
        # Expecting two GPA lines: Sem1 GPA and GPAU
        gpa_sem1 = 0.0
        gpau = 0.0
        
        if re.match(r'^([A-Z\+\-]+\s*)?(0|0\.00|[0-4]\.\d{2})$', lines[i]):
            gpa_sem1 = extract_gpa(lines[i])
            i += 1
        if re.match(r'^([A-Z\+\-]+\s*)?(0|0\.00|[0-4]\.\d{2})$', lines[i]):
            gpau = extract_gpa(lines[i])
            i += 1
            
        # Parse Sem 1 Grades
        student_grades = []
        for c_code in sem1_courses:
            if i + 3 >= len(lines) or re.match(r'^\d{12}$', lines[i]): break
            score_str = lines[i]
            grade_str = lines[i+1]
            pt1 = lines[i+2]
            pt2 = lines[i+3]
            
            if '||' in score_str:
                score = float(score_str.split('||')[0])
            elif '(Abs)' in score_str or 'Abs' in score_str:
                score = 0.0
            else:
                try:
                    score = float(score_str)
                except:
                    score = 0.0
                    
            try:
                points = float(pt1)
            except:
                points = 0.0
                
            student_grades.append({
                'seat': seat,
                'course': course_names[c_code],
                'semester': 1,
                'score': score,
                'grade': grade_str,
                'points': points,
                'is_pnp': grade_str in ['P', 'NP']
            })
            i += 4
            
        # Find Sem 2
        while i < len(lines) and lines[i] not in ["نىثا", "ثاني"] and not re.match(r'^\d{12}$', lines[i]):
            i += 1
            
        gpa_sem2 = 0.0
        if i < len(lines) and lines[i] in ["نىثا", "ثاني"]:
            i += 1
            sem2_courses = []
            while i < len(lines):
                m = re.search(r'(IMP07-[A-Z0-9_]+|URR07-[A-Z0-9_]+)', lines[i])
                if m:
                    c_code = m.group(1)
                    if c_code == 'IMP07-EA': c_code = 'IMP07-EA03_01'
                    if c_code == 'IMP07-ENA': c_code = 'IMP07-ENA04_01'
                    if c_code in course_names:
                        sem2_courses.append(c_code)
                if re.match(r'^([A-Z\+\-]+\s*)?(0|0\.00|[0-4]\.\d{2})$', lines[i]):
                    break
                if lines[i] == 'ت||ش||م':
                    i += 1
                    break
                i += 1
                
            if re.match(r'^([A-Z\+\-]+\s*)?(0|0\.00|[0-4]\.\d{2})$', lines[i]):
                gpa_sem2 = extract_gpa(lines[i])
                i += 1
                
            for c_code in sem2_courses:
                if i + 3 >= len(lines) or re.match(r'^\d{12}$', lines[i]): break
                score_str = lines[i]
                grade_str = lines[i+1]
                pt1 = lines[i+2]
                pt2 = lines[i+3]
                
                if '||' in score_str:
                    score = float(score_str.split('||')[0])
                elif '(Abs)' in score_str or 'Abs' in score_str:
                    score = 0.0
                else:
                    try:
                        score = float(score_str)
                    except:
                        score = 0.0
                        
                try:
                    points = float(pt1)
                except:
                    points = 0.0
                    
                student_grades.append({
                    'seat': seat,
                    'course': course_names[c_code],
                    'semester': 2,
                    'score': score,
                    'grade': grade_str,
                    'points': points,
                    'is_pnp': grade_str in ['P', 'NP']
                })
                i += 4
                
        # Deduplication logic: Keep the record with the highest GPAU
        student_obj = {
            'seat': seat,
            'name': name,
            'nationality': nationality,
            'gpa_sem1': gpa_sem1,
            'gpa_sem2': gpa_sem2,
            'gpau': gpau,
            'failed': (gpau == 0.0)
        }
        
        if seat not in students_dict or gpau > students_dict[seat]['student']['gpau']:
            students_dict[seat] = {
                'student': student_obj,
                'grades': student_grades
            }
    else:
        i += 1

# Flatten the dictionary
final_students = []
final_grades = []
for seat, data in students_dict.items():
    final_students.append(data['student'])
    final_grades.extend(data['grades'])

print(f"Extracted {len(final_students)} unique students and {len(final_grades)} grades.")

with open('raw_data_v3.json', 'w', encoding='utf-8') as f:
    json.dump({
        'students': final_students,
        'grades': final_grades
    }, f, ensure_ascii=False, indent=2)

print("Saved to raw_data_v3.json")
