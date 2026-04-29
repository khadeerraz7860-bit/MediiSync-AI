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
if "chat" not in st.session_state:
    st.session_state.chat = []

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

def predict(values):
    result = []
    if values.get("Sugar", 0) > 140:
        result.append("⚠️ Risk of Diabetes")
    if values.get("Cholesterol", 0) > 220:
        result.append("⚠️ Risk of Heart Disease")
    if values.get("Hemoglobin", 100) < 11:
        result.append("⚠️ Risk of Anemia")
    return result if result else ["No major risk detected"]

def suggestions(values):
    tips = []
    if values.get("Sugar", 0) > 120:
        tips.append("Reduce sugar intake and exercise daily")
    if values.get("Cholesterol", 0) > 200:
        tips.append("Avoid oily food and increase fiber intake")
    if values.get("Hemoglobin", 100) < 12:
        tips.append("Eat iron-rich foods like spinach and dates")
    return tips if tips else ["Maintain healthy lifestyle"]

def plot(values):
    fig, ax = plt.subplots()
    ax.bar(values.keys(), values.values())
    ax.set_title("Health Metrics")
    return fig

def answer_question(q, text, values):
    q = q.lower()

    if "risk" in q:
        return f"Risk level is {risk(values)}"
    if "summary" in q:
        return ". ".join(text.split(".")[:3])
    if "sugar" in q:
        return f"Sugar level is {values.get('Sugar', 'Not found')}"
    if "hemoglobin" in q:
        return f"Hemoglobin is {values.get('Hemoglobin', 'Not found')}"
    if "cholesterol" in q:
        return f"Cholesterol is {values.get('Cholesterol', 'Not found')}"

    return "I couldn't find that information."

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

    # 🧬 PREDICTION
    st.subheader("🧬 Disease Prediction")
    for item in predict(values):
        st.error(item)

    # 💡 SUGGESTIONS
    st.subheader("💡 Health Suggestions")
    for tip in suggestions(values):
        st.info(tip)

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

    # 💬 CHAT
    st.subheader("💬 Ask about report")
    question = st.text_input("Ask a question")

    if question:
        answer = answer_question(question, text, values)
        st.session_state.chat.append(("You", question))
        st.session_state.chat.append(("AI", answer))

    for sender, msg in st.session_state.chat:
        st.write(f"**{sender}:** {msg}")

    # 📄 FULL TEXT
    with st.expander("📄 View Full Report"):
        st.write(text)

else:
    st.info("Upload a PDF to start analysis")

# ---------- FOOTER ----------
st.markdown("---")
st.warning("⚠️ This system is for educational purposes only.")
st.caption("MediSync AI | Clinical Intelligence Platform")
