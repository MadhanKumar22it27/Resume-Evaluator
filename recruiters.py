import streamlit as st
import spacy
from spacy.matcher import Matcher
import csv
import fitz  # PyMuPDF
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

nlp = spacy.load('en_core_web_sm')

def process_recruiters_mode():
    st.title("Recruiter's Panel")

    uploaded_files = st.file_uploader("Upload resumes (PDF)", accept_multiple_files=True)
    
    required_skills_input = st.text_input("Enter required skills (comma-separated)", "")
    required_skills = [skill.strip().lower() for skill in required_skills_input.split(',') if skill.strip()]
    
    if st.button("Save Required Skills"):
        save_required_skills(required_skills)

    candidates_data = []

    if uploaded_files:
        for file in uploaded_files:
            text = extract_text_from_pdf(file)
            doc = nlp(text)
            candidate_name = extract_candidate_name(doc)
            parsed_skills = extract_all_skills(doc)
            skills_found = extract_skills(doc, required_skills)
            not_found_skills = set(required_skills) - skills_found 

            display_candidate_info(candidate_name, file.name)
            display_skills_found(required_skills, skills_found)

            # Store data for report
            candidates_data.append({
                "name": candidate_name,
                "found_skills": skills_found,
                "not_found_skills": not_found_skills
            })

    if candidates_data:
        if st.button("View Report as PDF"):
            pdf_bytes = generate_pdf_report(candidates_data)
            st.download_button(label="Download Report", data=pdf_bytes, file_name="Recruitment_Report.pdf", mime="application/pdf")

def generate_pdf_report(candidates_data):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setFont("Helvetica", 12)
    
    y_position = 750  # Start position for text

    # Title
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(220, y_position, "Recruitment Report")
    y_position -= 30
    
    for candidate in candidates_data:
        # Candidate Name as Heading (centered and bold)
        # pdf.setFont("Helvetica-Bold", 16)
        # pdf.drawString(50, y_position, "Candidate Name")

        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(50, y_position, f"{candidate['name']}")
        y_position -= 20


        # pdf.setFont("Helvetica", 12)
        # pdf.drawString(50, y_position, "Skills Found:")
        # y_position -= 15

        # for idx, skill in enumerate(candidate["found_skills"], 1):
        #     pdf.drawString(70, y_position, f"{idx}. {skill.capitalize()}")
        #     y_position -= 15

        # Add space between candidates
        y_position -= 20

        # Add new page if necessary
        if y_position < 100:  # Check if we need to move to a new page
            pdf.showPage()
            pdf.setFont("Helvetica", 12)
            y_position = 750

    pdf.save()
    buffer.seek(0)
    return buffer

# Function to save required skills
def save_required_skills(required_skills):
    with open('data/UpdatedSkills.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        for skill in required_skills:
            writer.writerow([skill])

# Function to extract text from PDF file
def extract_text_from_pdf(file):
    pdf_document = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text += page.get_text()
    return text

# Function to extract candidate's full name using SpaCy
def extract_candidate_name(doc):
    for ent in doc.ents:
        if ent.label_ == 'PERSON':
            return ent.text
    return "Candidate name not found"

# Function to extract all skills from the resume
def extract_all_skills(doc):
    all_skills = set()
    for token in doc:
        if token.pos_ == 'NOUN' and token.text.isalpha() and len(token.text) > 1:
            all_skills.add(token.text.lower())
    return all_skills

# Function to extract skills using SpaCy Matcher
def extract_skills(doc, required_skills):
    matcher = Matcher(nlp.vocab)
    skills_found = set()

    for skill in required_skills:
        pattern = [{"LOWER": skill}]
        matcher.add(skill, [pattern])

    matches = matcher(doc)
    for match_id, start, end in matches:
        matched_skill = doc[start:end].text.lower()
        skills_found.add(matched_skill)

    return skills_found

# Function to display candidate information
def display_candidate_info(candidate_name, file_name):
    st.subheader(f"**Candidate Name:**")
    st.write(candidate_name)


# Function to display skills found or not
def display_skills_found(required_skills, skills_found):
    st.subheader("\n**Skills**\n")
    for skill in required_skills:
        if skill in skills_found:
            st.write(f"- {skill}: ✅ Found")
        else:
            st.write(f"- {skill}: ❌ Not Found")

if __name__ == "__main__":
    process_recruiters_mode()
