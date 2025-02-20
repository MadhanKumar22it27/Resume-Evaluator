import streamlit as st
import pdfplumber
import spacy
import re
import phonenumbers
from resume_parser import  extract_education_from_resume
# Load NLP model
nlp = spacy.load("en_core_web_sm")

IDEAL_SKILLS = {"Python", "Java", "Flutter", "Machine Learning", "AI", "NLP", "React", "SQL", "PostgreSQL", "Django", "TensorFlow"}

DEGREE_PATTERNS = [
    r"(Bachelor|Master|B\.?Tech|M\.?Tech|BSc|MSc|BCA|MCA|PhD|Diploma)\s?(in\s[A-Za-z\s]+)?",
    r"(B\.E\.|M\.E\.|BBA|MBA|BCom|MCom|B\.Sc|M\.Sc|BCA|MCA)",
]

# # --------------------------------Extract Education-------------------------------
def extract_education_from_resume(doc):
    universities = []

    doc = nlp(doc)

    for entity in doc.ents:
        if entity.label_ == "ORG" and ("university" in entity.text.lower() or "college" in entity.text.lower() or "institute" in entity.text.lower()):
            universities.append(entity.text)

    return universities
# ---------------------------------
def extract_text_from_pdf(pdf_file):
    """Extract text from a PDF resume."""
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def extract_email(text):
    """Extract email from text using regex."""
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    matches = re.findall(email_pattern, text)
    return matches[0] if matches else "Not Found"

def extract_phone_number(text):
    """Extract phone number using phonenumbers library."""
    numbers = []
    for match in phonenumbers.PhoneNumberMatcher(text, "IN"):
        numbers.append(phonenumbers.format_number(match.number, phonenumbers.PhoneNumberFormat.INTERNATIONAL))
    return numbers[0] if numbers else "Not Found"

def extract_name(text):
    """Extract name using spaCy (assumes first PERSON entity is name)."""
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    return "Not Found"

def extract_skills(text):
    """Extract common skills from text using keyword matching."""
    found_skills = {skill for skill in IDEAL_SKILLS if skill.lower() in text.lower()}
    return found_skills

def extract_education(text):
    """Extract education details using regex."""
    degrees_found = []
    for pattern in DEGREE_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            degrees_found.append(" ".join(match).strip())

    return list(set(degrees_found)) if degrees_found else ["No education details found"]

def calculate_score(matched_skills):
    """Calculate score based on matched skills."""
    return round((len(matched_skills) / len(IDEAL_SKILLS)) * 100, 2)

def generate_feedback(matched_skills):
    """Provide feedback based on matched and missing skills."""
    missing_skills = IDEAL_SKILLS - matched_skills
    feedback = []

    if matched_skills:
        feedback.append(f"✅ **Great job! You have the following skills:** {', '.join(matched_skills)}.")

    if missing_skills:
        feedback.append(f"⚠️ **Consider improving these skills:** {', '.join(missing_skills)}.")
        feedback.append("📚 Suggested Learning Resources:")
        for skill in missing_skills:
            feedback.append(f"   - 🔗 Learn {skill}: [Click Here](https://www.google.com/search?q=learn+{skill.replace(' ', '+')})")

    if not matched_skills:
        feedback.append("❗ **No key skills found! Consider adding more technical skills.**")

    return "\n".join(feedback)

# st.set_page_config(page_title="Resume Evaluator", layout="centered", page_icon="✅")
def process_user_mode():
    st.title("Resume Evaluator")

    uploaded_file = st.file_uploader("Upload Your Resume (PDF)", type=["pdf"])

    if uploaded_file:
        st.success("✅ File uploaded successfully!")

        st.markdown('<hr>', unsafe_allow_html=True)
        st.header("🔍 Extracted Information")

        resume_text = extract_text_from_pdf(uploaded_file)
        
        name = extract_name(resume_text)
        email = extract_email(resume_text)
        phone = extract_phone_number(resume_text)
        skills = extract_skills(resume_text)
        education_info = extract_education(resume_text)
        
        score = calculate_score(skills)
        feedback = generate_feedback(skills)

        st.write(f"**👤 Name:** {name}")
        st.write(f"**📧 Email:** {email}")
        st.write(f"**📞 Phone Number:** {phone if phone else 'Not found'}")

        st.markdown('<hr>', unsafe_allow_html=True)
        st.header("🎓 Education")
        education_info = extract_education_from_resume(resume_text)
        st.write(', '.join(education_info) if education_info else "No education information found")

        st.markdown('<hr>', unsafe_allow_html=True)
        st.header("⚡ Skills")
        st.write(skills if skills else "No key skills detected")
        
        st.markdown('<hr>', unsafe_allow_html=True)
        st.header("📊 Resume Score")
        st.write(f"**💯 Resume Score:** {score}/100")
        st.progress(score / 100)

        st.markdown('<hr>', unsafe_allow_html=True)
        st.header("📢 Feedback & Suggestions")
        st.markdown(feedback, unsafe_allow_html=True)

        # with st.expander("📜 View Extracted Resume Text"):
        #     st.text(resume_text[:1000] + "...")  

if __name__ == "__main__":
    process_user_mode()