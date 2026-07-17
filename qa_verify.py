import json
import random
from pypdf import PdfReader
import sys

# Load db.json
with open('dashboard/src/data/db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

students = db['students']
# Pick 5 random students who have grades
random.seed(42) # For reproducibility
sampled = random.sample(students, 5)

print("=== SAMPLED STUDENTS ===")
for s in sampled:
    print(f"Seat: {s['seat']} | Name: {s['name']} | GPAU: {s['gpau']} | Rank: {s['rank']}")
    
seats_to_find = {s['seat'] for s in sampled}

print("\n=== PDF RAW TEXT FOR VERIFICATION ===")
reader = PdfReader('Oula (1).pdf')

# We scan the PDF to find these seats.
# Seat format in PDF: 05-{seat} or similar
found_count = 0
for i in range(len(reader.pages)):
    if found_count >= 5:
        break
    page = reader.pages[i]
    text = page.extract_text()
    
    # Check if any seat is on this page
    for seat in seats_to_find:
        if seat in text:
            print(f"\n--- Found {seat} on Page {i+1} ---")
            lines = text.split('\n')
            # Find the line index containing the seat
            for j, line in enumerate(lines):
                if seat in line:
                    # Print context
                    start = max(0, j - 2)
                    end = min(len(lines), j + 18)
                    for k in range(start, end):
                        print(f"{k}: {lines[k]}")
            found_count += 1
            seats_to_find.remove(seat)
            break
            
print("\n=== DB.JSON DATA ===")
for s in sampled:
    print(f"\nStudent DB info for {s['seat']}:")
    print(json.dumps(s, ensure_ascii=False, indent=2))
    grades = [g for g in db['grades'] if g['seat'] == s['seat']]
    for g in grades:
        print(f"  {g['course']}: {g['grade']} ({g['score']}) Points: {g['points']}")
