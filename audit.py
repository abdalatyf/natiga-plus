import csv, sys, io
from collections import Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Count students
with open('students.csv', 'r', encoding='utf-8-sig') as f:
    students = list(csv.DictReader(f))
print(f'=== STUDENTS ({len(students)}) ===')

# GPA analysis
valid_gpa = 0
zero_gpa = 0
has_notes = 0
null_chars = 0
for s in students:
    gpa = s['GPA'].strip()
    if gpa == '0' or gpa == '':
        zero_gpa += 1
    elif gpa:
        valid_gpa += 1
    if s['Notes'].strip():
        has_notes += 1
    if '\x00' in s['Name'] or '\x00' in s.get('Status','') or '\x00' in s.get('Nationality',''):
        null_chars += 1

print(f'  Valid GPA: {valid_gpa}')
print(f'  Zero/Empty GPA: {zero_gpa}')
print(f'  With Notes: {has_notes}')
print(f'  Names with null chars: {null_chars}')
print()

# Sample students
print('--- Sample Students ---')
for s in students[:3]:
    sid = s['Student_ID']
    name = s['Name'][:40]
    gpa = s['GPA']
    notes = s['Notes'][:30]
    print(f'  ID={sid} Name={name} GPA={gpa} Notes={notes}')
print()

# Count courses
with open('courses.csv', 'r', encoding='utf-8-sig') as f:
    courses = list(csv.DictReader(f))
print(f'=== COURSES ({len(courses)}) ===')
for c in courses:
    print(f"  {c['Course_Code']} -> {c['Course_Name']}")
print()

# Count grades
with open('grades.csv', 'r', encoding='utf-8-sig') as f:
    grades = list(csv.DictReader(f))
print(f'=== GRADES ({len(grades)}) ===')

# Grade distribution
grade_dist = Counter(g['Grade'] for g in grades)
print(f'  Grade Distribution: {dict(sorted(grade_dist.items()))}')

# Unique students/courses in grades
unique_students_in_grades = len(set(g['Student_ID'] for g in grades))
unique_courses_in_grades = len(set(g['Course_Code'] for g in grades))
print(f'  Unique students with grades: {unique_students_in_grades}')
print(f'  Unique courses with grades: {unique_courses_in_grades}')

# Average grades per student
avg_grades = len(grades) / unique_students_in_grades if unique_students_in_grades else 0
print(f'  Avg grades per student: {avg_grades:.1f}')

# Orphan check
student_ids = set(s['Student_ID'] for s in students)
grade_student_ids = set(g['Student_ID'] for g in grades)
orphans = grade_student_ids - student_ids
print(f'  Orphan student IDs (in grades but NOT in students): {len(orphans)}')
if orphans:
    print(f'    Examples: {list(orphans)[:5]}')

# Missing check
missing = student_ids - grade_student_ids
print(f'  Students with ZERO grades: {len(missing)}')

# Abs and multi-score
abs_count = sum(1 for g in grades if '(Abs)' in g['Score'])
multi_score = sum(1 for g in grades if '||' in g['Score'])
print(f'  Absences: {abs_count}')
print(f'  Multi-score entries (||): {multi_score}')

# Check for bad scores
bad_scores = 0
for g in grades:
    score = g['Score']
    if '(Abs)' not in score:
        try:
            parts = score.split('||')
            for p in parts:
                float(p)
        except ValueError:
            bad_scores += 1
            if bad_scores <= 5:
                print(f'  BAD SCORE: Student={g["Student_ID"]} Course={g["Course_Code"]} Score={score} Grade={g["Grade"]}')
print(f'  Bad/unparseable scores: {bad_scores}')

# Check course codes in grades vs courses.csv
course_codes_csv = set(c['Course_Code'] for c in courses)
course_codes_grades = set(g['Course_Code'] for g in grades)
extra_in_grades = course_codes_grades - course_codes_csv
missing_in_grades = course_codes_csv - course_codes_grades
print(f'  Course codes in grades but NOT in courses.csv: {len(extra_in_grades)}')
if extra_in_grades:
    print(f'    {extra_in_grades}')
print(f'  Course codes in courses.csv but NOT in grades: {len(missing_in_grades)}')
if missing_in_grades:
    print(f'    {missing_in_grades}')

# Per-student grade count distribution
student_grade_counts = Counter()
for g in grades:
    student_grade_counts[g['Student_ID']] += 1
count_dist = Counter(student_grade_counts.values())
print(f'\n=== GRADES PER STUDENT DISTRIBUTION ===')
for count, num_students in sorted(count_dist.items()):
    print(f'  {count} grades: {num_students} students')
