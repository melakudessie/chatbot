import streamlit as st
import tempfile
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
# --- CHANGED IMPORTS FOR COMPATIBILITY ---
from langchain.chains import RetrievalQA 

# --- 1. APP CONFIGURATION ---
st.set_page_config(page_title="PrescribeWise Assistant", page_icon="🩺", layout="wide")
st.title("🩺 PrescribeWise: Health Worker Assistant")

# --- 2. SIDEBAR SETUP ---
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("OpenAI API Key", type="password")
    uploaded_file = st.file_uploader("Upload Medical Guidelines (PDF)", type="pdf")

# --- 3. CACHED DOCUMENT PROCESSING ---
@st.cache_resource(show_spinner=False)
def load_and_process_pdf(file, api_key):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(file.getvalue())
        tmp_path = tmp_file.name

    try:
        loader = PyPDFLoader(tmp_path)
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(documents)
        embeddings = OpenAIEmbeddings(openai_api_key=api_key)
        vectorstore = FAISS.from_documents(documents=splits, embedding=embeddings)
        return vectorstore
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

# --- 4. MAIN APP LOGIC ---
if not api_key or not uploaded_file:
    st.info("👋 Please enter your API Key and upload a PDF to start.")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.spinner("Processing document..."):
    try:
        vectorstore = load_and_process_pdf(uploaded_file, api_key)
        retriever = vectorstore.as_retriever()
    except Exception as e:
        st.error(f"Error processing file: {e}")
        st.stop()

# --- 5. LEGACY CHAIN SETUP (Works on old versions) ---
llm = ChatOpenAI(model="gpt-4", openai_api_key=api_key, temperature=0)

# Use RetrievalQA instead of create_retrieval_chain
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

if user_input := st.chat_input("Ask about treatment guidelines..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing guidelines..."):
            try:
                # Legacy invocation method
                response = qa_chain.invoke({"query": user_input})
                answer = response["result"] # Note: key is 'result' in legacy chain
                
                with st.expander("📚 View Source Snippets"):
                    for i, doc in enumerate(response["source_documents"]):
                        page = doc.metadata.get("page", "Unknown")
                        st.markdown(f"**Page {page}:** {doc.page_content[:200]}...")

                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                st.error(f"An error occurred: {e}")
