import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain_community.llms import HuggingFacePipeline

from transformers import pipeline

# --- PAGE SETUP ---
st.set_page_config(page_title="MediSync AI", page_icon="🏥")
st.title("🏥 MediSync AI (FREE VERSION)")

# --- FILE UPLOAD ---
uploaded_file = st.file_uploader("Upload Patient Report (PDF)", type="pdf")

if uploaded_file:
    with open("temp.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success("PDF uploaded!")

    # --- LOAD PDF ---
    loader = PyPDFLoader("temp.pdf")
    documents = loader.load()

    # --- SPLIT TEXT ---
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    texts = text_splitter.split_documents(documents)

    # --- FREE EMBEDDINGS ---
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vector_db = Chroma.from_documents(texts, embeddings)

    # --- FREE LLM ---
    pipe = pipeline(
        "text2text-generation",
        model="google/flan-t5-base",
        max_length=512
    )

    llm = HuggingFacePipeline(pipeline=pipe)

    qa = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vector_db.as_retriever()
    )

    # --- QUERY ---
    query = st.text_input("Ask about report:")

    if query:
        with st.spinner("Thinking..."):
            result = qa.run(query)
            st.write("### AI Answer:")
            st.write(result)

else:
    st.info("Upload a PDF to start")
