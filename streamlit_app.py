import streamlit as st
import tempfile
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

# --- 1. APP CONFIGURATION ---
st.set_page_config(page_title="PrescribeWise Assistant", page_icon="🩺", layout="wide")
st.title("🩺 PrescribeWise: Health Worker Assistant")

# --- 2. SIDEBAR SETUP ---
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Secure API Key Input
    api_key = st.text_input("OpenAI API Key", type="password")
    if not api_key:
        st.warning("Please enter your OpenAI API Key to proceed.")
    
    # File Uploader
    uploaded_file = st.file_uploader("Upload Medical Guidelines (PDF)", type="pdf")
    st.markdown("---")
    st.markdown("### ℹ️ Instructions")
    st.markdown("1. Enter your OpenAI API Key.\n2. Upload the **WHOAMR.pdf**.\n3. Wait for the 'Processed' message.\n4. Ask questions about dosages, treatments, etc.")

# --- 3. CACHED DOCUMENT PROCESSING FUNCTION ---
# @st.cache_resource is CRITICAL. It ensures we only process the 700-page PDF ONCE.
# If you remove this, the app will rebuild the database on every single chat message (very slow).
@st.cache_resource(show_spinner=False)
def load_and_process_pdf(file, api_key):
    # Create a temporary file to store the uploaded PDF
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(file.getvalue())
        tmp_path = tmp_file.name

    try:
        # Load the PDF
        loader = PyPDFLoader(tmp_path)
        documents = loader.load()

        # Split text into chunks (optimized for medical texts)
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ".", " ", ""]
        )
        splits = text_splitter.split_documents(documents)

        # Create Vector Store (FAISS)
        embeddings = OpenAIEmbeddings(openai_api_key=api_key)
        vectorstore = FAISS.from_documents(documents=splits, embedding=embeddings)
        return vectorstore

    finally:
        # Clean up the temporary file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

# --- 4. MAIN APP LOGIC ---

# Check if API Key and File are present
if not api_key or not uploaded_file:
    st.info("👋 Welcome to PrescribeWise. Please configure the sidebar to start.")
    st.stop()

# Initialize Chat History in Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

# Process PDF (Only runs once due to caching)
with st.spinner("Processing document... this may take a minute for large files."):
    try:
        vectorstore = load_and_process_pdf(uploaded_file, api_key)
        retriever = vectorstore.as_retriever()
        st.success("✅ Guidelines loaded successfully!")
    except Exception as e:
        st.error(f"Error processing file: {e}")
        st.stop()

# --- 5. DEFINE THE AI CHAIN ---

# System Prompt: Strict medical guardrails
system_prompt = (
    "You are PrescribeWise, a helpful assistant for health workers. "
    "Use the following pieces of retrieved context to answer the question. "
    "If the answer is not in the context, clearly state: 'I cannot find this information in the provided guidelines.' "
    "Do NOT make up dosages or treatments. "
    "Always cite the page number for every claim (e.g., [Page 12])."
    "\n\n"
    "{context}"
)

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}"),
])

llm = ChatOpenAI(model="gpt-4", openai_api_key=api_key, temperature=0) # Temperature 0 for maximum factual accuracy
question_answer_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(retriever, question_answer_chain)

# --- 6. CHAT INTERFACE ---

# Display previous chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle new user input
if user_input := st.chat_input("Ask about treatment guidelines (e.g., 'Amikacin dosing for children?')..."):
    # Display user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Generate Response
    with st.chat_message("assistant"):
        with st.spinner("Analyzing guidelines..."):
            try:
                response = rag_chain.invoke({"input": user_input})
                answer = response["answer"]
                
                # OPTIONAL: Add a "Show Sources" expander for transparency
                with st.expander("📚 View Source Snippets"):
                    for i, doc in enumerate(response["context"]):
                        page_num = doc.metadata.get("page", "Unknown")
                        st.markdown(f"**Source {i+1} (Page {page_num}):**")
                        st.markdown(f"> {doc.page_content[:300]}...") # Show first 300 chars
                
                st.markdown(answer)
                
                # Save to history
                st.session_state.messages.append({"role": "assistant", "content": answer})
            
            except Exception as e:
                st.error(f"An error occurred: {e}")
