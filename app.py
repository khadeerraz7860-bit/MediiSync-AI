import streamlit as st
import re
from PyPDF2 import PdfReader
import matplotlib.pyplot as plt
import pandas as pd

# ---------- PAGE ----------
st.set_page_config(page_title="MediSync AI", layout="wide")

# ---------- UI ----------
st.title("🏥 MediSync AI - Healthcare Intelligence Platform")
st.caption("AI-powered Clinical Decision Support System")

# ---------- SESSION ----------
if "history" not in st.session_state:
    st.session_state.history = []

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
            try:
                data[key] = float(match[0])
            except:
                pass
    return data

def risk(values):
    score = 0
    if values.get("Hemoglobin", 100) < 12:
        score += 1
    if values.get("Sugar", 0) > 120:
        score += 1
    if values.get("Cholesterol", 0) > 200:
        score += 1
    return ["Low 🟢", "Moderate 🟡", "High 🔴"][min(score, 2)]

def plot(values):
    fig, ax = plt.subplots()
    ax.bar(values.keys(), values.values())
    ax.set_title("Health Metrics")
    return fig

# ---------- MAIN ----------
uploaded = st.file_uploader("📄 Upload Medical Report (PDF)", type="pdf")

if uploaded:
    text = extract_text(uploaded)
    values = extract_values(text)

    if values:
        st.session_state.history.append(values)

    st.markdown("---")

    # 📊 METRICS
    st.subheader("📊 Patient Metrics")
    cols = st.columns(3)

    keys = ["Hemoglobin", "Sugar", "Cholesterol"]
    for i, key in enumerate(keys):
        if key in values:
            cols[i].metric(key, values[key])

    # 🧠 RISK
    st.subheader("🧠 Risk Level")
    st.warning(risk(values))

    # 📈 GRAPH
    st.subheader("📈 Visualization")
    if values:
        st.pyplot(plot(values))

    # 📊 TREND
    if len(st.session_state.history) > 1:
        st.subheader("📊 Trend Analysis")
        df = pd.DataFrame(st.session_state.history)
        st.line_chart(df)

    # 📋 SUMMARY
    st.subheader("📋 Summary")
    sentences = [s.strip() for s in text.split(".") if len(s.strip()) > 20]
    if sentences:
        st.success(". ".join(sentences[:5]))
    else:
        st.info("No summary available.")

    # 📄 FULL TEXT
    with st.expander("📄 View Full Report"):
        st.write(text)

else:
    st.info("Upload a PDF to start analysis")

# ---------- FOOTER ----------
st.markdown("---")
st.warning("⚠️ This system is for educational purposes only.")
st.caption("MediSync AI | Clinical Intelligence Platform")

