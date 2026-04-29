import streamlit as st
import pandas as pd
import re
from PyPDF2 import PdfReader
from transformers import pipeline
import os

st.set_page_config(page_title="MediSync AI", layout="wide")

st.title("🏥 MediSync AI - Smart Medical Record System")

# ---------- LOAD MODEL ----------
@st.cache_resource
def load_model():
    return pipeline("question-answering", model="distilbert-base-uncased-distilled-squad")

qa_model = load_model()

# ---------- FILE ----------
DATA_FILE = "patient_data.csv"

# ---------- LOAD DATA ----------
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    df = pd.DataFrame(columns=["Date", "Hemoglobin", "Sugar", "Cholesterol"])

# ---------- FUNCTIONS ----------
def extract_text(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += (page.extract_text() or "") + "\n"
    return text

def extract_values(text):
    patterns = {
        "Hemoglobin": r"Hemoglobin.*?(\d+\.?\d*)",
        "Sugar": r"Sugar.*?(\d+)",
        "Cholesterol": r"Cholesterol.*?(\d+)"
    }
    data = {}
    for key, pattern in patterns.items():
        match = re.findall(pattern, text, re.IGNORECASE)
        if match:
            data[key] = float(match[0])
    return data

def split_text(text, size=400):
    words = text.split()
    return [" ".join(words[i:i+size]) for i in range(0, len(words), size)]

def find_best_chunk(chunks, question):
    question_words = question.lower().split()
    best_chunk = ""
    best_score = 0

    for chunk in chunks:
        score = sum(1 for word in question_words if word in chunk.lower())
        if score > best_score:
            best_score = score
            best_chunk = chunk

    return best_chunk

# ---------- UPLOAD ----------
uploaded = st.file_uploader("📄 Upload Medical Report", type="pdf")

if uploaded:
    text = extract_text(uploaded)
    values = extract_values(text)
    chunks = split_text(text)

    if values:
        new_row = {
            "Date": pd.Timestamp.now().strftime("%Y-%m-%d"),
            "Hemoglobin": values.get("Hemoglobin"),
            "Sugar": values.get("Sugar"),
            "Cholesterol": values.get("Cholesterol")
        }

        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)

        st.success("✅ Report saved successfully!")

    st.markdown("---")

    # ---------- METRICS ----------
    st.subheader("📊 Extracted Values")
    cols = st.columns(3)

    keys = ["Hemoglobin", "Sugar", "Cholesterol"]
    for i, key in enumerate(keys):
        if key in values:
            cols[i].metric(key, values[key])

    # ---------- ASK ----------
    st.subheader("💬 Ask About Report")
    question = st.text_input("Ask a question")

    if question:
        context = find_best_chunk(chunks, question)

        try:
            result = qa_model(question=question, context=context)
            answer = result["answer"]
        except:
            answer = "Couldn't find answer."

        st.write("### ✅ Answer")
        st.write(answer)

# ---------- SEARCH ----------
st.markdown("---")
st.subheader("🔍 Search Parameter History")

query = st.text_input("Type: sugar / hemoglobin / cholesterol")

if query:
    col_map = {
        "sugar": "Sugar",
        "hemoglobin": "Hemoglobin",
        "cholesterol": "Cholesterol"
    }

    col = col_map.get(query.lower())

    if col and col in df.columns:
        st.write(f"### 📊 {col} History")

        st.dataframe(df[["Date", col]])
        st.line_chart(df.set_index("Date")[col])

        if not df[col].dropna().empty:
            latest = df[col].dropna().iloc[-1]
            st.metric("Latest Value", latest)

    else:
        st.warning("Invalid input")

# ---------- ALL DATA ----------
st.markdown("---")
st.subheader("📋 All Patient Records")
st.dataframe(df)

# ---------- FOOTER ----------
st.markdown("---")
st.warning("⚠️ Educational use only")
st.caption("MediSync AI | Smart Healthcare System")
