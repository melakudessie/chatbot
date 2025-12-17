import streamlit as st
import tempfile
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS

# --- FIX: USE DIRECT IMPORT PATH TO AVOID VERSION CONFLICTS ---
from langchain.chains.retrieval_qa.base import RetrievalQA

# --- 1. APP CONFIGURATION ---
st.set_page_config(page_title="PrescribeWise Assistant", page_icon="🩺", layout="wide")
st.title("🩺 PrescribeWise: Health Worker Assistant")

# --- 2. SIDEBAR SETUP ---
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("OpenAI API Key", type="password")
    uploaded_file = st.file_uploader("Upload Medical Guidelines (PDF)", type="pdf")
    st.info("ℹ️ Upload the 'WHOAMR.pdf' to start.")

# --- 3. CACHED DOCUMENT PROCESSING ---
@st.cache_resource(show_spinner=False)
def load_and_process_pdf(file, api_key):
    # Create temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(file.getvalue())
        tmp_path = tmp_file.name

    try:
        # Load and Split
        loader = PyPDFLoader(tmp_path)
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(documents)
        
        # Embed
        embeddings = OpenAIEmbeddings(openai_api_key=api_key)
        vectorstore = FAISS.from_documents(documents=splits, embedding=embeddings)
        return vectorstore
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

# --- 4. MAIN LOGIC ---
if not api_key:
    st.warning("Please enter your OpenAI API Key.")
    st.stop()

if not uploaded_file:
    st.info("Please upload the PDF document.")
    st.stop()

# Initialize Chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Process PDF
with st.spinner("Processing PDF... (One-time setup)"):
    try:
        vectorstore = load_and_process_pdf(uploaded_file, api_key)
        retriever = vectorstore.as_retriever()
    except Exception as e:
        st.error(f"Error processing PDF: {e}")
        st.stop()

# --- 5. SETUP QA CHAIN (Direct Import Fix) ---
llm = ChatOpenAI(model="gpt-4", openai_api_key=api_key, temperature=0)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True
)

# --- 6. CHAT INTERFACE ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_input := st.chat_input("Ask about medical guidelines..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Consulting guidelines..."):
            try:
                # 'invoke' is the new standard, but 'run' is safer for older versions
                # We use __call__ dictionary input for maximum compatibility
                response = qa_chain({"query": user_input})
                answer = response["result"]
                
                # Show Sources
                with st.expander("📚 View Source Snippets"):
                    for i, doc in enumerate(response["source_documents"]):
                        page = doc.metadata.get("page", "Unknown")
                        st.markdown(f"**Source {i+1} (Page {page}):**")
                        st.markdown(f"> {doc.page_content[:200]}...")

                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
                
            except Exception as e:
                st.error(f"Error generating response: {e}")
