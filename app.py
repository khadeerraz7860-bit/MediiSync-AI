import streamlit as st
import os

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

# --- PAGE SETUP ---
st.set_page_config(page_title="MediSync AI", page_icon="🏥", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0F172A; color: white; }
    .stButton>button { background-color: #2DD4BF; color: black; border-radius: 8px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏥 MediSync AI: Agentic Healthcare RAG")

# --- API KEY ---
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error("❌ API key not found. Add it in Streamlit Secrets.")
    st.stop()

# --- SIDEBAR ---
st.sidebar.title("Upload Report")
uploaded_file = st.sidebar.file_uploader("Upload Patient Report (PDF)", type="pdf")

# --- WARNING ---
st.warning("⚠️ This AI is for educational purposes only. Consult a doctor.")

if uploaded_file:

    # Save file
    with open("temp_report.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.sidebar.success("✅ File uploaded")

    # --- LOAD PDF (WITH ERROR HANDLING) ---
    try:
        loader = PyPDFLoader("temp_report.pdf")
        documents = loader.load()
    except Exception:
        st.error("❌ Invalid or corrupted PDF. Please upload a proper PDF file.")
        st.stop()

    # --- SPLIT TEXT ---
    text_splitter = CharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )
    texts = text_splitter.split_documents(documents)

    # --- VECTOR DB (NO CACHE NOW) ---
    def create_vector_db(texts):
        embeddings = OpenAIEmbeddings()
        db = Chroma.from_documents(texts, embeddings)
        return db

    vector_db = create_vector_db(texts)

    # --- PROMPT ---
    prompt_template = """
    You are a medical assistant AI.

    Use ONLY the provided context.
    If unsure, say "I don't know".

    Context:
    {context}

    Question:
    {question}

    Answer in simple terms:
    """

    PROMPT = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"]
    )

    # --- QA SYSTEM ---
    qa_chain = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(model="gpt-4o-mini", temperature=0),
        chain_type="stuff",
        retriever=vector_db.as_retriever(),
        chain_type_kwargs={"prompt": PROMPT}
    )

    # --- CHAT ---
    st.subheader("🔍 Analyze Report")
    query = st.text_input("Ask a question:")

    if query:
        with st.spinner("Analyzing..."):
            response = qa_chain.invoke(query)

        st.success("✅ Analysis Complete")
        st.write(response["result"])

        with st.expander("📄 View Extracted Text"):
            st.write(texts[:3])

else:
    st.info("👈 Upload a PDF to begin")

st.markdown("---")
st.caption("MediSync AI | Final Year Project 2026")
