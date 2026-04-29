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

# --- SECURITY (API KEY FROM SECRETS) ---
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error("❌ API key not found. Add it in Streamlit Secrets.")
    st.stop()

# --- SIDEBAR ---
st.sidebar.title("Upload Report")
uploaded_file = st.sidebar.file_uploader("Upload Patient Report (PDF)", type="pdf")

# --- WARNING ---
st.warning("⚠️ This AI is for educational purposes only. Consult a doctor for medical advice.")

if uploaded_file:

    with open("temp_report.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.sidebar.success("✅ File uploaded successfully")

    # --- LOAD PDF ---
    loader = PyPDFLoader("temp_report.pdf")
    documents = loader.load()

    # --- SPLIT TEXT ---
    text_splitter = CharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )
    texts = text_splitter.split_documents(documents)

    # --- VECTOR DB (CACHED) ---
    @st.cache_resource
    def create_vector_db(texts):
        embeddings = OpenAIEmbeddings()
        db = Chroma.from_documents(texts, embeddings)
        return db

    vector_db = create_vector_db(texts)

    # --- CUSTOM PROMPT ---
    prompt_template = """
    You are a medical assistant AI.

    Use ONLY the provided context.
    If unsure, say "I don't know".

    Context:
    {context}

    Question:
    {question}

    Answer in simple and clear terms:
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

    # --- USER INPUT ---
    st.subheader("🔍 Analyze Report")
    user_query = st.text_input("Ask a question about the report:")

    if user_query:
        with st.spinner("Analyzing..."):
            response = qa_chain.invoke(user_query)

        st.success("✅ Analysis Complete")
        st.markdown("### 🧠 AI Response")
        st.write(response["result"])

        # Optional: Show extracted text
        with st.expander("📄 View Extracted Content"):
            st.write(texts[:3])

else:
    st.info("👈 Upload a PDF file from the sidebar")

st.markdown("---")
st.caption("MediSync AI | Final Year Project 2026")