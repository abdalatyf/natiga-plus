import csv
import json

COURSE_NAMES = {
    'IMP07-10102_01': 'الجسم البشري الطبي',
    'IMP07-10103_01': 'مبادئ الأمراض والعلاج بالعقاقير',
    'IMP07-10104_01': 'العلوم الطبية الحيوية',
    'IMP07-10105_01': 'البيولوجيا الخلوية والجزيئية ومبادئ الوراثة',
    'IMP07-10106_01': 'علوم الحاسب الآلي وتكنولوجيا المعلومات',
    'IMP07-10107_01': 'اللغة الإنجليزية',
    'IMP07-10108_01': 'المصطلحات الطبية والمهارات الحياتية',
    'IMP07-EA03_01': 'الانعاش القلبي الرئوي',
    'URR07-10101_01': 'فقه',
    'IMP07-10211_01': 'الاخلاقيات الطبية',
    'IMP07-10212_01': 'جهاز مكونات الدم وعلم المناعة الأساسية',
    'IMP07-10213_01': 'العضلات والعظام والجلد',
    'IMP07-10214_01': 'طرق البحث العلمي والإحصاء الحيوي',
    'IMP07-10215_01': 'الجهاز التنفسي',
    'IMP07-ENA04_01': 'الادب: الشعر والنثر',
    'URR07-10209_01': 'عقيدة',
    'URR07-10210_01': 'قرآن كريم',
    'IMP07-EA04_01': 'التغذية',
    'IMP07-EA13_01': 'التأهيل للغة الانجليزية',
    'IMP07-10109_01': 'اللغة',
    'IMP07-10209': 'اللغة'
}

def clean_string(s):
    return s.replace('\x00', '').strip()

def parse_gpa(raw_gpa):
    raw_gpa = raw_gpa.strip()
    if not raw_gpa or raw_gpa == '0':
        return "", 0.0
    
    parts = raw_gpa.split()
    if len(parts) == 2:
        letter, val_str = parts
        # Fix RTL: '-A' -> 'A-', '+B' -> 'B+'
        if letter.startswith('-'):
            letter = letter[1:] + '-'
        elif letter.startswith('+'):
            letter = letter[1:] + '+'
        try:
            val = float(val_str)
            return letter, val
        except ValueError:
            pass
    return raw_gpa, 0.0

def main():
    db = {
        'students': [],
        'courses': COURSE_NAMES,
        'grades': []
    }

    # Load Grades
    with open('grades.csv', 'r', encoding='utf-8-sig') as f:
        grades_data = list(csv.DictReader(f))
        
    for g in grades_data:
        # Handle multiple scores by taking the sum
        score_str = g['Score'].replace('(Abs)', '0')
        if '||' in score_str:
            parts = [float(p) for p in score_str.split('||')]
            score = sum(parts)
        else:
            try:
                score = float(score_str)
            except ValueError:
                score = 0.0
                
        db['grades'].append({
            'student_id': g['Student_ID'],
            'course_code': g['Course_Code'],
            'score': score,
            'grade': g['Grade'],
            'points': float(g['Points'])
        })
        
    # Process Students
    with open('students.csv', 'r', encoding='utf-8-sig') as f:
        students_data = list(csv.DictReader(f))
        
    for s in students_data:
        sid = s['Student_ID']
        name = clean_string(s['Name'])
        status = clean_string(s['Status'])
        nationality = clean_string(s['Nationality'])
        
        gpa_letter, gpa_val = parse_gpa(s['GPA'])
        gpau_letter, gpau_val = parse_gpa(s['GPAU'])
        
        notes = clean_string(s['Notes'])
        if notes.startswith('0'):
            notes = notes[1:].strip()
            
        # Calculate rank or total points later if needed
        # We can also compute pass/fail status
        student_grades = [g for g in db['grades'] if g['student_id'] == sid]
        failed = any(g['grade'] == 'F' for g in student_grades)
        
        db['students'].append({
            'id': sid,
            'name': name,
            'nationality': nationality,
            'status': status,
            'gpa_letter': gpa_letter,
            'gpa': gpa_val,
            'gpau_letter': gpau_letter,
            'gpau': gpau_val,
            'notes': notes,
            'failed': failed
        })

    with open('db.json', 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
        
    print(f"Data prepared successfully! Created db.json with {len(db['students'])} students and {len(db['grades'])} grades.")

if __name__ == '__main__':
    main()
