import sys, io, re, csv
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('extracted_raw.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Check seat number formats
seats = []
for l in lines:
    l = l.strip()
    m = re.match(r'^(\d{2})-(\d{5})$', l)
    if m:
        seats.append(l)
    m2 = re.match(r'^(\d{5})--(\d{2})$', l)
    if m2:
        seats.append(l)

print(f"Seat numbers found: {len(seats)}")
print(f"Samples: {seats[:15]}")

# Check grades
with open('grades.csv', 'r', encoding='utf-8-sig') as f:
    grades = list(csv.DictReader(f))

# P/NP analysis
p_grades = [g for g in grades if g['Grade'] == 'P']
np_grades = [g for g in grades if g['Grade'] == 'NP']
print(f"\nP (Pass) grades: {len(p_grades)}")
print(f"NP (Not Pass) grades: {len(np_grades)}")

p_courses = set(g['Course_Code'] for g in p_grades + np_grades)
print(f"P/NP courses: {p_courses}")

# Check what the grade line looks like for a passing student 
# Student 4 (line 112-145 in raw)
print("\n=== RAW GRADE STRINGS ===")
print("Student 4 Sem1 (line 132):")
print(repr(lines[131].strip()))
print("\nStudent 4 Sem2 (line 145):")
print(repr(lines[144].strip()))

# Parse the grade string pattern more carefully
# Each grade entry: score + grade_letter + points + total_points
# So 153.50 A- 3.59 25.13 means score=153.50, grade=A-, points=3.59, total=25.13
# But wait - 153.50 is very high for a single course. Let's check.
print("\n=== CHECKING SCORE RANGES ===")
scores = []
for g in grades:
    s = g['Score']
    if '(Abs)' not in s and '||' not in s:
        try:
            scores.append(float(s))
        except:
            pass

scores.sort()
print(f"Min score: {scores[0]}")
print(f"Max score: {scores[-1]}")
print(f"Median: {scores[len(scores)//2]}")
print(f"Scores > 100: {len([s for s in scores if s > 100])}")
print(f"Scores > 50: {len([s for s in scores if s > 50])}")

# Show some high scores
high = [g for g in grades if '(Abs)' not in g['Score'] and '||' not in g['Score']]
high = [g for g in high if float(g['Score']) > 100]
print(f"\nHigh score examples (>100):")
for g in high[:10]:
    print(f"  Student={g['Student_ID']} Course={g['Course_Code']} Score={g['Score']} Grade={g['Grade']}")

# Current seat number storage check
with open('students.csv', 'r', encoding='utf-8-sig') as f:
    students = list(csv.DictReader(f))
print(f"\n=== STUDENT CSV FIELDS ===")
print(f"Fields: {list(students[0].keys())}")
print(f"Note: Seat number (رقم الجلوس like 05-25001) is NOT stored in the CSV!")
