import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# The grade string for Student 4 Sem1:
# 153.50A-3.5925.1381.00B+3.3913.5684.50B+3.3913.5640.50B+3.396.7823.50A3.793.7921.00B+3.393.3921.00B+3.393.390.00P0.000.0022.00A-3.593.59
# Student 4 has 9 courses in sem1: IMP07-10102 thru URR07-10101
# The pattern per grade is: score, letter, points, TOTAL_POINTS

# BUT the current regex only captures: score + letter + points
# The TOTAL_POINTS is being captured as the NEXT score!
# Example: 153.50 A- 3.59 |25.13| 81.00 B+ 3.39 |13.56| ...
# The |25.13| is total_points for course 1, but the parser reads it as score for course 2

# Correct pattern: score + letter + points + total_points (4 fields per grade)
grade_str = '153.50A-3.5925.1381.00B+3.3913.5684.50B+3.3913.5640.50B+3.396.7823.50A3.793.7921.00B+3.393.3921.00B+3.393.390.00P0.000.0022.00A-3.593.59'

# Better regex: each grade = number + letter + number + number
pattern = r'((?:\d+\.\d+(?:\|\|\d+\.\d+)*)|\(Abs\))(A\+|A-|A|B\+|B|C\+|C|D\-|D|F|P|NP)(\d+\.\d{2})(\d+\.\d{2})'
matches = re.findall(pattern, grade_str)

print(f"Matches found: {len(matches)}")
print("Expected: 9 courses")
print()
for i, m in enumerate(matches):
    print(f"  Grade {i+1}: score={m[0]}, letter={m[1]}, points={m[2]}, total_points={m[3]}")

# With 4 fields captured, let's verify:
# Grade 1: 153.50, A-, 3.59, 25.13 -> score=153.50 (THIS IS WRONG - it's too high for a single exam!)
# Wait... let me look at the RAW PDF more carefully
# Line 15-26 shows sem1 has courses with credit hours in parens:
# IMP07-10102_01 (7) - so 7 credit hours
# IMP07-10103_01 (4)
# etc.
# 153.50 for a 7-credit-hour course might make sense if max is like 200
# Actually for medical schools, total marks could be high

# Let's check semester 2 too
grade_str2 = '18.00C+2.992.9972.00C+2.9911.96170.50A-3.5928.7248.00A+4.008.0081.50B+3.3913.560.00P0.000.0023.00A3.793.7924.00||9.00||15.00A+4.004.00'
matches2 = re.findall(pattern, grade_str2)
print(f"\nSem2 Matches: {len(matches2)}")
print("Expected: 8 courses")
for i, m in enumerate(matches2):
    print(f"  Grade {i+1}: score={m[0]}, letter={m[1]}, points={m[2]}, total_points={m[3]}")

# So the KEY ISSUE: the old regex captured 3 fields (score, letter, points)
# But the actual data has 4 fields (score, letter, points, TOTAL_POINTS)
# So "total_points" was being read as the next course's "score"
# That's why we got scores > 100!
print("\n=== CONCLUSION ===")
print("Each grade has 4 fields: score, letter, points, total_points")
print("The current parser only captures 3 fields, causing total_points to become the next score!")
print("This means ALL scores are WRONG for courses after the 1st in each semester!")
