import streamlit as st
import os
from operator import itemgetter

# --- MODERN IMPORTS ---
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# --- CONSTANTS ---
PDF_FILE_PATH = "WHOAMR.pdf"
APP_TITLE = "PrescribeWise - Health Worker Assistant"

# --- 1. PAGE CONFIG ---
st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CSS STYLING ---
st.markdown("""
    <style>
    .header-container {
        background: linear-gradient(90deg, #005c97 0%, #363795 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .header-title { font-size: 2.5rem; font-weight: 800; margin: 0; }
    .header-subtitle { font-size: 1.2rem; opacity: 0.9; margin-top: 5px; }
    .disclaimer-box {
        background-color: #fff3cd;
        border-left: 6px solid #ffc107;
        padding: 15px;
        border-radius: 5px;
        color: #856404;
        font-size: 0.9rem;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. UI LAYOUT ---
st.markdown(f"""
    <div class="header-container">
        <div class="header-title">🩺 PrescribeWise</div>
        <div class="header-subtitle">AI-Powered Assistant for WHO Antimicrobial Guidelines</div>
    </div>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="disclaimer-box">
        <strong>⚠️ IMPORTANT MEDICAL DISCLAIMER</strong><br>
        This AI tool assists healthcare professionals by retrieving information solely from the 
        <em>WHO AWaRe Antibiotic Book</em>. It does <strong>not</strong> replace professional medical judgment. 
        Always verify dosages and treatment protocols with local guidelines.
    </div>
""", unsafe_allow_html=True)

# --- 4. CREDENTIALS ---
if "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]
else:
    st.error("🚨 API Key missing! Please add `OPENAI_API_KEY` to your Streamlit Secrets.")
    st.stop()

if not os.path.exists(PDF_FILE_PATH):
    st.error(f"🚨 Guidelines file not found: `{PDF_FILE_PATH}`. Please upload it to your GitHub repository.")
    st.stop()

# --- 5. LOAD KNOWLEDGE BASE ---
@st.cache_resource(show_spinner=False)
def load_knowledge_base(key):
    try:
        loader = PyPDFLoader(PDF_FILE_PATH)
        docs = loader.load()
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", "●", "•", "-", " "]
        )
        splits = splitter.split_documents(docs)
        embeddings = OpenAIEmbeddings(openai_api_key=key)
        vectorstore = FAISS.from_documents(splits, embeddings)
        return vectorstore
    except Exception as e:
        raise e

# --- 6. SIDEBAR & LANGUAGE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3063/3063176.png", width=50)
    st.header("App Settings")
    st.divider()

    st.markdown("### 🌐 Language / ቋንቋ")
    # Added "native" names to help the AI understand context better
    selected_language = st.selectbox(
        "Choose response language:",
        [
            "English", 
            "Amharic (አማርኛ)", 
            "Swahili (Kiswahili)", 
            "Oromo (Afaan Oromoo)", 
            "French (Français)", 
            "Spanish (Español)", 
            "Arabic (العربية)"
        ]
    )
    st.divider()
    
    st.markdown("### 🚦 AWaRe Color Legend")
    st.markdown(":green[**🟢 First Choice**]")
    st.markdown(":orange[**🟡 Second Choice**]")
    st.markdown(":red[**🔴 Reserve**]")
    st.divider()
    
    if st.button("🔄 Start New Consultation", type="primary", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Load DB
with st.spinner("Initializing medical knowledge base..."):
    try:
        vectorstore = load_knowledge_base(api_key)
        retriever = vectorstore.as_retriever(search_kwargs={"k": 6})
    except Exception as e:
        st.error(f"Initialization Failed: {e}")
        st.stop()

# --- 7. IMPROVED PROMPT FOR TRANSLATION ---
# Major Change: We explicitly tell the AI to draft in English first to ensure accuracy, then translate.
template = """You are PrescribeWise, an expert medical assistant based on the WHO AWaRe Antibiotic Book.

INSTRUCTIONS:
1. **Understand Context:** Read the provided context carefully.
2. **Formulate Answer:** First, formulate the correct medical answer in English to ensure accuracy.
3. **Translate:** Then, translate the final answer naturally into **{language}**.
   - Ensure the grammar is correct for {language}.
   - Do NOT repeat sentences or words in a loop.
   - If a specific medical term (like 'Amoxicillin') has no direct translation, keep it in English or use the widely accepted local medical term.
4. **Formatting:** Apply these Streamlit colors to the final translated text:
   - First Choice / Access: :green[**🟢 First Choice:** ...]
   - Second Choice / Watch: :orange[**🟡 Second Choice:** ...]
   - Reserve: :red[**🔴 Reserve:** ...]
5. **Citation:** Include [Page X] citations at the end.
6. **Unknown Info:** If the answer is not in the context, say "I cannot find this in the guidelines" (translated).

CONTEXT:
{context}

QUESTION:
{question}
"""

prompt = ChatPromptTemplate.from_template(template)

# CRITICAL CHANGE: Switched to 'gpt-4o' (Omni)
# GPT-4o is significantly better at Amharic/Oromo than GPT-4
llm = ChatOpenAI(model="gpt-4o", temperature=0.1, openai_api_key=api_key)

def format_docs(docs):
    return "\n\n".join(f"[Page {doc.metadata.get('page', '?')}] {doc.page_content}" for doc in docs)

# --- 8. CHAT INTERFACE ---
for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else "🩺"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

if user_input := st.chat_input("Ex: What is the treatment for pneumonia?"):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)

    with st.chat_message("assistant", avatar="🩺"):
        with st.spinner(f"Consulting guidelines ({selected_language})..."):
            try:
                # 1. Retrieve
                relevant_docs = retriever.invoke(user_input)
                formatted_context = format_docs(relevant_docs)
                
                # 2. Chain
                rag_chain = (
                    {
                        "context": lambda x: formatted_context, 
                        "question": itemgetter("question"), 
                        "language": itemgetter("language")
                    }
                    | prompt 
                    | llm 
                    | StrOutputParser()
                )
                
                # 3. Stream
                response_container = st.empty()
                full_response = ""
                
                for chunk in rag_chain.stream({"question": user_input, "language": selected_language}):
                    full_response += chunk
                    response_container.markdown(full_response + "▌")
                
                response_container.markdown(full_response)
                
                # 4. Evidence
                with st.expander("🔍 View Clinical Evidence (Source Text)"):
                    for i, doc in enumerate(relevant_docs):
                        st.markdown(f"**Source {i+1} (Page {doc.metadata.get('page', '?')})**")
                        st.caption(doc.page_content)
                        st.divider()
                
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
            except Exception as e:
                st.error(f"An error occurred: {e}")
