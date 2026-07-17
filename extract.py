import csv
import re
from pypdf import PdfReader

def parse_pdf(pdf_path, max_pages=5):
    reader = PdfReader(pdf_path)
    lines = []
    for i in range(min(max_pages, len(reader.pages))):
        page = reader.pages[i]
        text = page.extract_text()
        lines.extend(text.split('\n'))

    students = []
    courses_dict = {}
    grades = []
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Detect student start: A serial number followed by 12-digit ID
        if re.match(r'^\d+$', line) and i+1 < len(lines) and re.match(r'^\d{12}$', lines[i+1].strip()):
            student_id = lines[i+1].strip()
            seat_num = lines[i+2].strip()
            name = lines[i+3].strip()
            status = lines[i+4].strip()
            nationality = lines[i+5].strip()
            
            # Now we look for 'أول'
            j = i + 6
            while j < len(lines) and lines[j].strip() != 'أول':
                j += 1
            
            if j >= len(lines):
                break
                
            # Parse Semester 1 courses
            j += 1
            sem1_courses = []
            while j < len(lines) and lines[j].strip() not in ['0', 'ت', 'ﺛﺎ'] and not re.match(r'^[A-D\+\-\s]+\d\.\d{2}$', lines[j].strip()):
                line_text = lines[j]
                # Find all course codes in this line
                matches = list(re.finditer(r'(IMP07-[A-Z0-9_\s]+|URR07-[A-Z0-9_\s]+)', line_text))
                if matches:
                    start_idx = 0
                    for m in matches:
                        code = m.group(1).replace(' ', '') # some codes have spaces like EA 03
                        name_part = line_text[start_idx:m.start()].replace('-', '').strip()
                        if not name_part and j+1 < len(lines) and '(' in lines[j+1] and not re.search(r'(IMP07|URR07)', lines[j+1]):
                            name_part = lines[j+1].strip()
                        name_part = re.sub(r'^\(\d+', '', name_part).strip()
                        # If name_part is empty, maybe it's in the previous part or next part.
                        # Since Arabic text is sometimes right-to-left, the name might precede the code.
                        if name_part:
                            courses_dict[code] = name_part
                        elif code not in courses_dict:
                            courses_dict[code] = "Unknown"
                            
                        sem1_courses.append(code)
                        start_idx = m.end()
                j += 1
            
            # Now we are at GPA or Notes
            gpa1 = ""
            gpau = ""
            while j < len(lines) and (lines[j].strip() == '0' or re.match(r'^[A-D\+\-\s]+\d\.\d{2}$', lines[j].strip())):
                val = lines[j].strip()
                if not gpa1:
                    gpa1 = val
                else:
                    gpau = val
                j += 1
                
            # Now we should be at the grades string for sem 1
            grades_str1 = lines[j].strip()
            j += 1
            
            # Parse Semester 2
            while j < len(lines) and lines[j].strip() != 'ﺛﺎ':
                j += 1
                
            j += 1
            sem2_courses = []
            while j < len(lines) and lines[j].strip() != 'ت':
                line_text = lines[j]
                matches = list(re.finditer(r'(IMP07-[A-Z0-9_\s]+|URR07-[A-Z0-9_\s]+)', line_text))
                if matches:
                    start_idx = 0
                    for m in matches:
                        code = m.group(1).replace(' ', '')
                        name_part = line_text[start_idx:m.start()].replace('-', '').strip()
                        if not name_part and j+1 < len(lines) and '(' in lines[j+1] and not re.search(r'(IMP07|URR07)', lines[j+1]):
                            name_part = lines[j+1].strip()
                        name_part = re.sub(r'^\(\d+', '', name_part).strip()
                        if name_part:
                            courses_dict[code] = name_part
                        elif code not in courses_dict:
                            courses_dict[code] = "Unknown"
                            
                        sem2_courses.append(code)
                        start_idx = m.end()
                j += 1
                
            j += 1 # Skip 'ت'
            
            # Now we are at GPA2 / Notes
            gpa2 = ""
            notes = ""
            while j < len(lines) and not re.search(r'([A-D][+-]?|F|P|NP)\d+\.\d{2}', lines[j].strip()) and not '||' in lines[j].strip() and not '(Abs)' in lines[j].strip() and len(lines[j].strip()) < 50:
                val = lines[j].strip()
                if re.match(r'^[A-D\+\-\s]+\d\.\d{2}$', val):
                    gpa2 = val
                else:
                    notes = val
                j += 1
                
            if j < len(lines):
                grades_str2 = lines[j].strip()
            else:
                grades_str2 = ""
            j += 1
            
            students.append({
                'Student_ID': student_id,
                'Name': name,
                'Nationality': nationality,
                'Status': status,
                'GPA': gpa2 if gpa2 else gpa1, # Final GPA
                'GPAU': gpau,
                'Notes': notes
            })
            
            # Extract grades from grades_str1 and grades_str2 using Regex
            # Grade pattern: score (number or Abs or number||number), letter, points, total_points
            grade_pattern = r'((?:\d+\.\d+(?:\|\|\d+\.\d+)*)|\(Abs\))([A-D][\+\-]?|F|P|NP)(\d+\.\d{2})(\d+\.\d{2})'
            
            matches1 = re.findall(grade_pattern, grades_str1)
            for k, match in enumerate(matches1):
                if k < len(sem1_courses):
                    grades.append({
                        'Student_ID': student_id,
                        'Course_Code': sem1_courses[k],
                        'Score': match[0],
                        'Grade': match[1],
                        'Points': match[2]
                    })
                    
            matches2 = re.findall(grade_pattern, grades_str2)
            for k, match in enumerate(matches2):
                if k < len(sem2_courses):
                    grades.append({
                        'Student_ID': student_id,
                        'Course_Code': sem2_courses[k],
                        'Score': match[0],
                        'Grade': match[1],
                        'Points': match[2]
                    })
                    
            i = j
        else:
            i += 1
            
    # Write to CSV
    with open('students.csv', 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=['Student_ID', 'Name', 'Nationality', 'Status', 'GPA', 'GPAU', 'Notes'])
        writer.writeheader()
        writer.writerows(students)
        
    with open('courses.csv', 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['Course_Code', 'Course_Name'])
        for code, name in courses_dict.items():
            writer.writerow([code, name])
            
    with open('grades.csv', 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=['Student_ID', 'Course_Code', 'Score', 'Grade', 'Points'])
        writer.writeheader()
        writer.writerows(grades)
        
    print(f"Extracted {len(students)} students, {len(courses_dict)} courses, and {len(grades)} grades.")

if __name__ == '__main__':
    parse_pdf('Oula (1).pdf', 9999)
