import sys, io, csv
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('students.csv', 'r', encoding='utf-8-sig') as f:
    students = list(csv.DictReader(f))

# Notes that start with '0'
notes_with_zero = [s for s in students if s['Notes'].startswith('0')]
print(f'Notes starting with 0: {len(notes_with_zero)}')
for s in notes_with_zero[:3]:
    n = s['Notes']
    print(f'  Notes=[{n}]')

# GPA format samples
print('\nGPA format samples:')
valid_students = [s for s in students if s['GPA'].strip() not in ['0', '']]
for s in valid_students[:10]:
    print(f'  GPA=[{s["GPA"]}] GPAU=[{s["GPAU"]}] Notes=[{s["Notes"][:30]}]')

# Check if GPA contains letter grade
from collections import Counter
gpa_prefixes = Counter()
for s in valid_students:
    gpa = s['GPA'].strip()
    # First non-digit char
    prefix = ''
    for c in gpa:
        if c.isdigit() or c == '.':
            break
        prefix += c
    gpa_prefixes[prefix] = gpa_prefixes.get(prefix, 0) + 1
print(f'\nGPA prefix patterns: {dict(gpa_prefixes)}')

# Check Notes = '0...' pattern (the '0' at the beginning is likely the GPA that leaked into Notes)
print('\n--- Checking if Notes field has GPA data merged ---')
zero_note_students = [s for s in students if s['Notes'].startswith('0')]
for s in zero_note_students[:5]:
    print(f'  ID={s["Student_ID"]} GPA=[{s["GPA"]}] GPAU=[{s["GPAU"]}] Notes=[{s["Notes"]}]')
