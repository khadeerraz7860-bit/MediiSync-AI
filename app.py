import streamlit as st
import re
from PyPDF2 import PdfReader
import matplotlib.pyplot as plt
import pandas as pd

# ---------- PAGE ----------
st.set_page_config(page_title="MediSync AI", layout="wide")
st.title("🏥 MediSync AI - Healthcare Intelligence Platform")
st.caption("AI-powered Clinical Decision Support System")

# ---------- SESSION ----------
if "history" not in st.session_state:
    st.session_state.history = []   # list of dicts
if "chat" not in st.session_state:
    st.session_state.chat = []      # (user, bot)

# ---------- FUNCTIONS ----------
def extract_text(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        t = page.extract_text() or ""
        text += t + "\n"
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

def status(name, v):
    if name == "Hemoglobin":
        return "Low ❌" if v < 12 else "Normal ✅"
    if name == "Sugar":
        return "High ❌" if v > 120 else "Normal ✅"
    if name == "Cholesterol":
        return "High ❌" if v > 200 else "Normal ✅"
    return "—"

def risk_level(values):
    score = 0
    if values.get("Hemoglobin", 100) < 12: score += 1
    if values.get("Sugar", 0) > 120: score += 1
    if values.get("Cholesterol", 0) > 200: score += 1
    return ["Low 🟢", "Moderate 🟡", "High 🔴"][min(score, 2)]

def predict(values):
    out = []
    if values.get("Sugar", 0) > 140:
        out.append("⚠️ Diabetes risk")
    if values.get("Cholesterol", 0) > 220:
        out.append("⚠️ Heart disease risk")
    if values.get("Hemoglobin", 100) < 11:
        out.append("⚠️ Anemia risk")
    return out or ["No major risk detected"]

def suggestions(values):
    tips = []
    if values.get("Sugar", 0) > 120:
        tips.append("Reduce sugar intake, add daily exercise.")
    if values.get("Cholesterol", 0) > 200:
        tips.append("Avoid oily foods, increase fiber.")
    if values.get("Hemoglobin", 100) < 12:
        tips.append("Increase iron-rich foods (spinach, dates).")
    return tips or ["Maintain current healthy lifestyle."]

def plot_bar(values):
    fig, ax = plt.subplots()
    ax.bar(values.keys(), values.values())
    ax.set_title("Patient Metrics")
    return fig

def plot_trend(history):
    df = pd.DataFrame(history)
    fig, ax = plt.subplots()
    for col in df.columns:
        ax.plot(df[col], marker="o", label=col)
    ax.legend()
    ax.set_title("Trend Across Reports")
    return fig

# simple local QA (keyword + context line)
def answer_q(q, text, values):
    ql = q.lower()
    if "risk" in ql:
        return f"Risk level: {risk_level(values)}"
    if "summary" in ql:
        sents = [s.strip() for s in text.split(".") if len(s.strip()) > 30]
        return ". ".join(sents[:5]) or "Summary not available."
    if "hemoglobin" in ql:
        return f"Hemoglobin: {values.get('Hemoglobin', 'Not found')}"
    if "sugar" in ql:
        return f"Sugar: {values.get('Sugar', 'Not found')}"
    if "cholesterol" in ql:
        return f"Cholesterol: {values.get('Cholesterol', 'Not found')}"
    # fallback: find a line containing a keyword
    for line in text.split("\n"):
        if any(w in line.lower() for w in ql.split()):
            return line.strip()
    return "No relevant information found."

# ---------- UI ----------
uploaded = st.file_uploader("📄 Upload Medical Report (PDF)", type="pdf")

if uploaded:
    text = extract_text(uploaded)
    values = extract_values(text)

    # store history if we extracted anything
    if values:
        st.session_state.history.append(values)

    st.markdown("---")

    # ===== DASHBOARD =====
    st.subheader("📊 Clinical Dashboard")
    c1, c2, c3 = st.columns(3)

    if "Hemoglobin" in values:
        c1.metric("Hemoglobin", values["Hemoglobin"], status("Hemoglobin", values["Hemoglobin"]))
    if "Sugar" in values:
        c2.metric("Blood Sugar", values["Sugar"], status("Sugar", values["Sugar"]))
    if "Cholesterol" in values:
        c3.metric("Cholesterol", values["Cholesterol"], status("Cholesterol", values["Cholesterol"]))

    st.markdown("---")

    # ===== RISK + PREDICTION =====
    st.subheader("🧠 Risk Assessment")
    st.warning(risk_level(values))

    st.subheader("🧬 Disease Prediction")
    for p in predict(values):
        st.error(p)

    st.subheader("💡 Health Suggestions")
    for t in suggestions(values):
        st.info(t)

    st.markdown("---")

    # ===== VISUALS =====
    if values:
        st.subheader("📈 Metrics Visualization")
        st.pyplot(plot_bar(values))

    if len(st.session_state.history) > 1:
        st.subheader("📊 Trend Analysis (Multiple Reports)")
        st.pyplot(plot_trend(st.session_state.history))

    st.markdown("---")

    # ===== SUMMARY =====
    st.subheader("📋 Clinical Summary")
    sents = [s.strip() for s in text.split(".") if len(s.strip()) > 30]
    st.success(". ".join(sents[:6]) if sents else "Summary not available.")

    # ===== CHAT =====
    st.subheader("💬 Query Panel")
    q = st.text_input("Ask about the report")
    if q:
        ans = answer_q(q, text, values)
        st.session_state.chat.append(("You", q))
        st.session_state.chat.append(("AI", ans))

    for role, msg in st.session_state.chat:
        st.write(f"**{role}:** {msg}")

    # ===== RAW =====
    with st.expander("📄 View Full Report"):
        st.write(text)

else:
    st.info("Upload a PDF to begin analysis")

st.markdown("---")
st.warning("⚠️ Educational use only. Not a medical diagnosis tool.")
st.caption("MediSync AI | Clinical Intelligence System")
