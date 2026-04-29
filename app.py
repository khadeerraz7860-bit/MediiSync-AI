import streamlit as st
import pandas as pd
import PyPDF2
import re
from transformers import pipeline
import os

# Fix transformer issues
os.environ["TRANSFORMERS_NO_TF"] = "1"

st.set_page_config(page_title="MediSync AI", layout="wide")

st.title("🩺 MediSync AI - Smart Medical Report Analyzer")
st.caption("AI-powered medical report reader and Q&A system")

# -------------------------------
# 📌 Load QA Model (Lightweight)
# -------------------------------
@st.cache_resource
def load_model():
    return pipeline(
        "question-answering",
        model="deepset/minilm-uncased-squad2"
    )

qa_model = load_model()

# -------------------------------
# 📄 Extract text from PDF
# -------------------------------
def extract_text(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# -------------------------------
# 🔍 Extract medical values
# -------------------------------
def extract_values(text):
    patterns = {
        "Sugar": r"(sugar|glucose).*?(\d+\.?\d*)",
        "Hemoglobin": r"(hemoglobin|hb).*?(\d+\.?\d*)",
        "Cholesterol": r"(cholesterol).*?(\d+\.?\d*)",
        "BP": r"(bp|blood pressure).*?(\d+/\d+)"
    }

    results = {}

    for key, pattern in patterns.items():
        match = re.search(pattern, text.lower())
        if match:
            results[key] = match.group(2)

    return results

# -------------------------------
# 📂 Upload PDF
# -------------------------------
uploaded_file = st.file_uploader("📤 Upload Medical Report (PDF)", type="pdf")

if uploaded_file:
    st.success("✅ File uploaded successfully!")

    text = extract_text(uploaded_file)

    # -------------------------------
    # 📊 Extract values
    # -------------------------------
    data = extract_values(text)

    if data:
        st.subheader("📊 Extracted Medical Data")
        df = pd.DataFrame(data.items(), columns=["Test", "Value"])
        st.dataframe(df)

        st.subheader("📈 Health Summary")
        st.bar_chart(df.set_index("Test"))
    else:
        st.warning("⚠️ No medical values found")

    # -------------------------------
    # 🤖 Ask Questions
    # -------------------------------
    st.subheader("💬 Ask Questions from Report")

    question = st.text_input("Ask something (e.g. sugar level?)")

    if question:
        answer = qa_model(
            question=question,
            context=text
        )

        st.success(f"🧠 Answer: {answer['answer']}")
