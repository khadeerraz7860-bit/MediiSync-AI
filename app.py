import streamlit as st
import re
from PyPDF2 import PdfReader

st.set_page_config(page_title="MediSync AI", layout="wide")
st.title("🏥 MediSync AI - Smart Report Analyzer")

st.markdown("Upload a medical report and get intelligent insights (Free Version)")

uploaded_file = st.file_uploader("Upload PDF", type="pdf")

# --- FUNCTION: Extract Text ---
def extract_text(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# --- FUNCTION: Smart Summary ---
def generate_summary(text):
    sentences = text.split(".")
    important = [s for s in sentences if len(s) > 40]
    return ". ".join(important[:5])

# --- FUNCTION: Detect Abnormal Values ---
def detect_abnormal(text):
    findings = []

    # Hemoglobin
    hb = re.findall(r"Hemoglobin.*?(\d+\.?\d*)", text, re.IGNORECASE)
    if hb and float(hb[0]) < 12:
        findings.append("⚠️ Low Hemoglobin (Possible anemia)")

    # Sugar
    sugar = re.findall(r"Sugar.*?(\d+)", text, re.IGNORECASE)
    if sugar and int(sugar[0]) > 120:
        findings.append("⚠️ High Blood Sugar")

    # Cholesterol
    chol = re.findall(r"Cholesterol.*?(\d+)", text, re.IGNORECASE)
    if chol and int(chol[0]) > 200:
        findings.append("⚠️ High Cholesterol")

    return findings

# --- FUNCTION: Q&A ---
def answer_question(question, text):
    if "hemoglobin" in question.lower():
        return "Hemoglobin is mentioned in the report. Check abnormal section."
    elif "sugar" in question.lower():
        return "Blood sugar values are analyzed above."
    elif "summary" in question.lower():
        return generate_summary(text)
    else:
        return "Answer not found. Try asking about sugar, hemoglobin, or summary."

# --- MAIN ---
if uploaded_file:
    try:
        text = extract_text(uploaded_file)

        st.subheader("📄 Extracted Text")
        st.write(text[:1500])

        st.subheader("🧠 Smart Summary")
        st.success(generate_summary(text))

        st.subheader("⚠️ Abnormal Findings")
        issues = detect_abnormal(text)

        if issues:
            for i in issues:
                st.error(i)
        else:
            st.success("No major abnormalities detected")

        st.subheader("💬 Ask Questions")
        q = st.text_input("Ask about the report")

        if q:
            st.info(answer_question(q, text))

    except:
        st.error("Invalid PDF. Please upload proper file.")

else:
    st.info("Upload a PDF to start")
