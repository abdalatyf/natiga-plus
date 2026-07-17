import csv
import re
from pypdf import PdfReader
import traceback

def parse_pdf_to_csv(pdf_path, max_pages=5):
    reader = PdfReader(pdf_path)
    
    students = []
    courses = {}
    grades = []
    
    # Regex to match a student block start. e.g. a serial number alone on a line followed by a 12 digit ID
    
    all_text = ""
    for i in range(min(max_pages, len(reader.pages))):
        page = reader.pages[i]
        all_text += page.extract_text() + "\n---PAGE---\n"
        
    with open('extracted_raw.txt', 'w', encoding='utf-8') as f:
        f.write(all_text)
        
    print("Raw text saved to extracted_raw.txt for inspection.")

if __name__ == '__main__':
    parse_pdf_to_csv('Oula (1).pdf', 5)
