import sys, io, re, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('extracted_raw.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f.readlines()]

students = []
current_student = {}
buffer = []

def process_student(buf):
    if not buf: return None
    
    # 1. Seat number
    seat = None
    for l in buf[:10]:
        m = re.search(r'(?:05-(\d{5}))|(?:(\d{5})--05)', l)
        if m:
            seat = m.group(1) or m.group(2)
            break
            
    # 2. Name & Nationality (roughly lines 3 and 5 after the 12-digit id)
    # The 12-digit ID is usually the 2nd line, seat is 3rd. Name is 4th.
    name = None
    nationality = None
    status = None
    for i, l in enumerate(buf):
        if re.match(r'^\d{12}$', l):
            # i = 12-digit
            # i+1 = seat
            name = buf[i+2].replace('\x00', '').strip()
            status = buf[i+3].replace('\x00', '').strip()
            nationality = buf[i+4].replace('\x00', '').strip()
            break

    # 3. Grade strings
    # We look for lines that match the grade pattern heavily
    pattern = r'((?:\d+\.\d+(?:\|\|\d+\.\d+)*)|\(Abs\))(A\+|A-|A|B\+|B|C\+|C|D\-|D|F|P|NP)(\d+\.\d{2})(\d+\.\d{2})'
    
    grade_lines = []
    gpa_lines = []
    for i, l in enumerate(buf):
        matches = re.findall(pattern, l)
        if len(matches) >= 5: # It's a grade string
            grade_lines.append((l, matches))
            # The GPA might be on the line immediately above
            if i > 0:
                gpa_lines.append(buf[i-1])

    # Also look for GPAU which might be at the very end of the block
    # It usually looks like 3.48 or 0
    
    return {
        'seat': seat,
        'name': name,
        'nationality': nationality,
        'status': status,
        'grades': grade_lines,
        'gpas_above': gpa_lines,
        'raw_end': buf[-5:]
    }

student_bufs = []
cur = []
for l in lines:
    if re.match(r'^\d+$', l) and len(l) < 4 and len(cur) > 10:
        # A small number like 2, 3, 4 usually indicates the start of a new student (the index)
        # Verify the next line is a 12 digit ID
        pass
    if re.match(r'^\d{12}$', l):
        # We found a 12 digit ID. This is definitely a student. 
        # But wait, the 12-digit ID is line 2. 
        if cur:
            # Pop the index line (line 1) from the end of cur and put it back
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

# Process the first few
print(f"Total students found: {len(student_bufs)}")
for i in range(1, min(6, len(student_bufs))):
    s = process_student(student_bufs[i])
    print(f"\n--- Student {i} ---")
    print(f"Seat: {s['seat']}")
    print(f"Name: {s['name']}")
    print(f"Grades found: {len(s['grades'])}")
    for g, matches in s['grades']:
        print(f"  Count: {len(matches)}")
    print(f"GPAs above lines: {s['gpas_above']}")
    print(f"Raw end of block: {s['raw_end']}")
