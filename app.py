import streamlit as st
import re
from PyPDF2 import PdfReader
import matplotlib.pyplot as plt
import pandas as pd

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="MediSync AI", layout="wide")

# ---------- STYLE ----------
st.markdown("""
<style>
body { background-color: #0f172a; }
h1, h2, h3 { color: #38bdf8; }
</style>
""", unsafe_allow_html=True)

# ---------- SESSION ----------
if "history" not in st.session_state:
    st.session_state.history = []

# ---------- SIDEBAR ----------
st.sidebar.title("🏥 MediSync AI")
page = st.sidebar.radio("Navigation", ["Dashboard", "Upload & Analyze", "History"])

# ---------- FUNCTIONS ----------
def extract_text(file):
    reader = PdfReader(file)
    text = ""
    for p in reader.pages:
        text += (p.extract_text() or "") + "\n"
    return text

def extract_values(text):
    patterns = {
        "Hemoglobin": r"Hemoglobin.*?(\d+\.?\d*)",
        "Sugar": r"Sugar.*?(\d+)",
        "Cholesterol": r"Cholesterol.*?(\d+)"
    }
    data = {}
    for k, p in patterns.items():
        m = re.findall(p, text, re.IGNORECASE)
        if m:
            try:
                data[k] = float(m[0])
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

# ---------- DASHBOARD ----------
if page == "Dashboard":
    st.title("📊 Clinical Dashboard")

    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)
        st.line_chart(df)
        st.success("Patient trends visualized")
    else:
        st.info("No data yet. Upload reports to see dashboard.")

# ---------- ANALYSIS ----------
elif page == "Upload & Analyze":
    st.title("📄 Upload & Analyze Report")

    uploaded = st.file_uploader("Upload PDF", type="pdf")

    if uploaded:
        text = extract_text(uploaded)
        values = extract_values(text)

        if values:
            st.session_state.history.append(values)

        st.subheader("📊 Metrics")
        cols = st.columns(3)

        keys = ["Hemoglobin", "Sugar", "Cholesterol"]
        for i, key in enumerate(keys):
            if key in values:
                cols[i].metric(key, values[key])

        st.subheader("🧠 Risk Level")
        st.warning(risk(values))

        st.subheader("📈 Visualization")
        if values:
            st.pyplot(plot(values))

        st.subheader("📋 Summary")
        sentences = [s.strip() for s in text.split(".") if len(s.strip()) > 20]
        if sentences:
            st.success(". ".join(sentences[:5]))
        else:
            st.info("No summary available.")

        with st.expander("📄 Full Report"):
            st.write(text)

# ---------- HISTORY ----------
elif page == "History":
    st.title("📊 Report History")

    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)
        st.dataframe(df)
        st.line_chart(df)
    else:
        st.info("No history available.")

# ---------- FOOTER ----------
st.markdown("---")
st.warning("⚠️ Educational use only. Not a medical diagnosis tool.")
st.caption("MediSync AI | Clinical Intelligence Platform")
