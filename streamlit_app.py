import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
import tempfile
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="PrescribeWise Assistant", layout="wide")
st.title("🩺 PrescribeWise: Health Worker Assistant")

# --- SIDEBAR: CONFIGURATION ---
with st.sidebar:
    st.header("Settings")
    # SECURITY: Ideally use st.secrets, but input works for testing
    api_key = st.text_input("OpenAI API Key", type="password")
    
    # Allow user to upload the 700-page PDF
    uploaded_file = st.file_uploader("Upload Medical Guidelines (PDF)", type="pdf")
    
    st.info("ℹ️ Note: The first time you upload a large PDF, it may take 1-2 minutes to process.")

# --- CACHED FUNCTION FOR PROCESSING PDF ---
# This is the most critical part. @st.cache_resource ensures we don't 
# re-process the 700 pages on every single interaction.
@st.cache_resource(show_spinner=False)
def process_pdf(file, api_key):
    # Save uploaded file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(file.getvalue())
        tmp_path = tmp_file.name

    try:
        # 1. Load PDF
        loader = PyPDFLoader(tmp_path)
        docs = loader.load()

        # 2. Split Text (Optimized for medical context)
        # Larger chunk size helps keep medical contexts (dosages/conditions) together
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ".", " ", ""]
        )
        splits = text_splitter.split_documents(docs)

        # 3. Create Vector Store
        embeddings = OpenAIEmbeddings(api_key=api_key)
        vectorstore = FAISS.from_documents(documents=splits, embedding=embeddings)
        
        return vectorstore
    finally:
        # Cleanup temp file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

# --- MAIN APP LOGIC ---

if not api_key:
    st.warning("Please enter your OpenAI API Key in the sidebar to continue.")
    st.stop()

if not uploaded_file:
    st.warning("Please upload the WHOAMR.pdf file in the sidebar.")
    st.stop()

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Process the PDF only when a new file is uploaded
with st.spinner("Processing medical guidelines... (This happens only once)"):
    try:
        vectorstore = process_pdf(uploaded_file, api_key)
        retriever = vectorstore.as_retriever()
    except Exception as e:
        st.error(f"Error processing PDF: {e}")
        st.stop()

# --- SYSTEM PROMPT (GUARDRAILS) ---
system_prompt = (
    "You are a specialized medical assistant called PrescribeWise. "
    "Use the following pieces of retrieved context to answer the question. "
    "If the answer is not in the context, say 'I do not have this information in the guidelines.' "
    "Do NOT fabricate dosages or treatments. "
    "Always cite the source page number if available. "
    "\n\n"
    "{context}"
)

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}"),
])

# Setup RAG Chain
llm = ChatOpenAI(model="gpt-4o", openai_api_key=api_key, temperature=0) # Low temp for accuracy
question_answer_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(retriever, question_answer_chain)

# --- CHAT INTERFACE ---

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if user_input := st.chat_input("Ask about antibiotic guidelines, dosages, etc..."):
    # 1. Display user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 2. Generate and display assistant response
    with st.chat_message("assistant"):
        with st.spinner("Consulting guidelines..."):
            response = rag_chain.invoke({"input": user_input})
            answer = response["answer"]
            
            # Optional: Add "Sources" dropdown
            if "context" in response and response["context"]:
                sources_text = "\n\n**Sources:**"
                for doc in response["context"][:3]: # Limit to top 3 sources
                    page = doc.metadata.get("page", "Unknown")
                    sources_text += f"\n- Page {page}"
                answer += sources_text

            st.markdown(answer)
    
    # 3. Save assistant response to history
    st.session_state.messages.append({"role": "assistant", "content": answer})
