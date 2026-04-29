import streamlit as st
from PyPDF2 import PdfReader

st.set_page_config(page_title="MediSync AI", layout="wide")

st.title("🩺 MediSync AI (Free Version)")
st.info("Upload a medical PDF report and get extracted text + summary")

# Upload PDF
uploaded_file = st.file_uploader("Upload Patient Report (PDF)", type="pdf")

if uploaded_file is not None:
    try:
        # Read PDF
        reader = PdfReader(uploaded_file)
        text = ""

        for page in reader.pages:
            text += page.extract_text()

        # Show extracted text
        st.subheader("📄 Extracted Report")
        st.write(text[:2000])  # limit display

        # Simple summary (FREE, no API)
        st.subheader("🧠 Basic Summary")

        sentences = text.split(".")
        summary = ". ".join(sentences[:5])

        st.success(summary)

    except Exception as e:
        st.error("❌ Error reading PDF. Please upload a valid file.")
