"""
WHO AWaRe Antibiotics Support Chatbot
Based ONLY on WHO AWaRe (Access, Watch, Reserve) Classification Document
Version: 3.0 - Single Source with PDF Integration
"""

import streamlit as st
from openai import OpenAI
import base64
from pathlib import Path
import PyPDF2
import io

# ================================
# PAGE CONFIGURATION
# ================================
st.set_page_config(
    page_title="WHO AWaRe Antibiotics Bot",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/melakudessie/chatbot',
        'Report a bug': None,
        'About': "WHO AWaRe Antibiotics Chatbot - Based on WHOAMR.pdf"
    }
)

# ================================
# PDF LOADER
# ================================
@st.cache_data
def load_pdf_text(pdf_path="WHOAMR.pdf"):
    """Load and extract text from WHO AWaRe PDF"""
    try:
        if not Path(pdf_path).exists():
            return None, f"PDF not found at {pdf_path}"
        
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page_num, page in enumerate(pdf_reader.pages):
                text += f"\n--- Page {page_num + 1} ---\n"
                text += page.extract_text()
            
            return text, None
    except Exception as e:
        return None, str(e)

# ================================
# LOGO HELPER
# ================================
def get_logo_base64():
    """Convert logo to base64"""
    logo_path = Path("logo.png")
    if logo_path.exists():
        with open(logo_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

# ================================
# CUSTOM CSS
# ================================
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .header-container {
        background: linear-gradient(135deg, #0051A5 0%, #00A3DD 100%);
        padding: 40px 30px;
        border-radius: 15px;
        margin-bottom: 30px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        text-align: center;
    }
    
    .logo-img {
        width: 120px;
        height: 120px;
        margin: 0 auto 15px;
        display: block;
        border-radius: 50%;
        border: 4px solid white;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    }
    
    .header-title {
        color: white;
        font-size: 2.5em;
        font-weight: bold;
        margin: 10px 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .header-subtitle {
        color: #E0F2FF;
        font-size: 1.2em;
        margin-top: 10px;
    }
    
    .description-box {
        background-color: #F8F9FA;
        padding: 25px;
        border-radius: 12px;
        border-left: 6px solid #0051A5;
        margin: 20px 0;
    }
    
    .disclaimer-box {
        background-color: #FFF3CD;
        padding: 25px;
        border-radius: 12px;
        border-left: 6px solid #FFC107;
        margin: 20px 0;
    }
    
    .source-box {
        background-color: #E3F2FD;
        padding: 20px;
        border-radius: 12px;
        border-left: 6px solid #1976D2;
        margin: 20px 0;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #0051A5 0%, #00A3DD 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ================================
# HEADER
# ================================
def create_header():
    logo_base64 = get_logo_base64()
    
    if logo_base64:
        st.markdown(f"""
        <div class="header-container">
            <img src="data:image/png;base64,{logo_base64}" class="logo-img" alt="WHO Logo">
            <h1 class="header-title">WHO AWaRe Antibiotics Chatbot</h1>
            <p class="header-subtitle">Based on WHO AWaRe Classification Document</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="header-container">
            <div style="font-size: 3.5em; margin-bottom: 10px;">💊 📚</div>
            <h1 class="header-title">WHO AWaRe Antibiotics Chatbot</h1>
            <p class="header-subtitle">Based on WHO AWaRe Classification Document</p>
        </div>
        """, unsafe_allow_html=True)

# ================================
# DESCRIPTION
# ================================
def show_description():
    st.markdown("""
    <div class="description-box">
        <h3 style="color: #0051A5;">📖 About This Chatbot</h3>
        <p style="font-size: 1.1em; line-height: 1.8;">
            This chatbot provides information based <strong>exclusively</strong> on the 
            <strong>WHO AWaRe (Access, Watch, Reserve) Classification Document</strong> 
            stored in the project repository.
        </p>
        <h4 style="color: #0051A5; margin-top: 20px;">What You'll Get:</h4>
        <ul style="font-size: 1.05em; line-height: 2;">
            <li>🟢 <strong>ACCESS Group</strong> - First-line, first-choice antibiotics</li>
            <li>🟡 <strong>WATCH Group</strong> - Second-line alternatives with higher resistance risk</li>
            <li>🔴 <strong>RESERVE Group</strong> - Last-resort antibiotics for specific cases</li>
            <li>📚 <strong>Citations</strong> - All responses reference the WHOAMR.pdf document</li>
            <li>🎯 <strong>Clear Treatment Hierarchy</strong> - First-line and second-line options identified</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# ================================
# SOURCE DOCUMENT INFO
# ================================
def show_source_info(pdf_loaded):
    status_emoji = "✅" if pdf_loaded else "⚠️"
    status_text = "Loaded Successfully" if pdf_loaded else "Using AI Knowledge Base"
    status_color = "#28A745" if pdf_loaded else "#FFC107"
    
    st.markdown(f"""
    <div class="source-box">
        <h3 style="color: #1976D2;">📚 Source Document</h3>
        <p style="font-size: 1.1em; line-height: 1.8;">
            <strong>Document:</strong> WHO AWaRe Classification of Antibiotics<br>
            <strong>File:</strong> WHOAMR.pdf<br>
            <strong>Location:</strong> <a href="https://github.com/melakudessie/chatbot/blob/main/WHOAMR.pdf" target="_blank">GitHub Repository</a><br>
            <strong>Status:</strong> <span style="color: {status_color};">{status_emoji} {status_text}</span>
        </p>
        <p style="font-size: 0.95em; color: #555; margin-top: 15px;">
            <strong>Note:</strong> All responses are based ONLY on this single WHO AWaRe classification document. 
            No other guidelines or sources are used.
        </p>
    </div>
    """, unsafe_allow_html=True)

# ================================
# DISCLAIMER
# ================================
def show_disclaimer():
    st.markdown("""
    <div class="disclaimer-box">
        <h3 style="color: #856404;">⚠️ Important Medical Disclaimer</h3>
        <p style="font-size: 1.1em; line-height: 1.6; color: #856404;">
            This chatbot is for <strong>EDUCATIONAL purposes ONLY</strong>
        </p>
        <ul style="font-size: 1em; line-height: 1.8; color: #856404;">
            <li>❌ NOT a substitute for professional medical advice</li>
            <li>❌ NOT for self-diagnosis or self-medication</li>
            <li>✅ Based ONLY on WHO AWaRe classification document</li>
            <li>✅ Always consult healthcare professionals</li>
            <li>✅ Consider local resistance patterns and antibiograms</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# ================================
# SIDEBAR
# ================================
def create_sidebar():
    with st.sidebar:
        logo_base64 = get_logo_base64()
        if logo_base64:
            st.markdown(f"""
            <div style="text-align: center; margin: 20px 0;">
                <img src="data:image/png;base64,{logo_base64}" style="width: 100px; border-radius: 50%; border: 3px solid #0051A5;">
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown('<div style="text-align: center; font-size: 2.5em; margin: 20px 0;">💊</div>', unsafe_allow_html=True)
        
        st.markdown("### 🎯 WHO AWaRe Groups")
        
        with st.expander("🟢 ACCESS Group", expanded=True):
            st.markdown("""
            **First-line, first-choice antibiotics**
            
            - Narrow spectrum
            - Lower resistance risk
            - Should be widely available
            - Examples: Amoxicillin, Penicillin, Doxycycline
            """)
        
        with st.expander("🟡 WATCH Group"):
            st.markdown("""
            **Second-line alternatives**
            
            - Broader spectrum
            - Higher resistance potential
            - Prioritized stewardship targets
            - Examples: Ciprofloxacin, Ceftriaxone, Azithromycin
            """)
        
        with st.expander("🔴 RESERVE Group"):
            st.markdown("""
            **Last-resort antibiotics**
            
            - Reserved for specific cases
            - Highest resistance concern
            - Should be protected
            - Examples: Colistin, Linezolid, Tigecycline
            """)
        
        st.divider()
        
        st.markdown("### 📊 Session Stats")
        if "messages" in st.session_state:
            msg_count = len([m for m in st.session_state.messages if m["role"] != "system"])
            st.metric("Messages", msg_count)
        else:
            st.metric("Messages", 0)
        
        st.divider()
        
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.display_messages = []
            st.session_state.show_info = True
            st.rerun()
        
        st.divider()
        
        st.markdown("""
        ### 🔗 Resources
        - [GitHub Repository](https://github.com/melakudessie/chatbot)
        - [WHO AWaRe Database](https://www.who.int/publications/i/item/2021-aware-classification)
        - [WHO Antimicrobial Resistance](https://www.who.int/health-topics/antimicrobial-resistance)
        """)

# ================================
# LOAD PDF AND INITIALIZE
# ================================

# Load PDF content
pdf_text, pdf_error = load_pdf_text("WHOAMR.pdf")
pdf_loaded = pdf_text is not None

# Show PDF loading status in sidebar
if pdf_loaded:
    st.sidebar.success("✅ WHOAMR.pdf loaded")
else:
    st.sidebar.warning("⚠️ WHOAMR.pdf not found - using AI knowledge")
    if pdf_error:
        st.sidebar.caption(f"Error: {pdf_error}")

# ================================
# API KEY CHECK
# ================================
if "OPENAI_API_KEY" not in st.secrets:
    st.error("⚠️ OpenAI API key not found!")
    st.info("""
    **Configuration Required:**
    
    Create `.streamlit/secrets.toml` with:
    ```
    OPENAI_API_KEY = "your-api-key-here"
    ```
    """)
    st.stop()

try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except Exception as e:
    st.error(f"❌ Error initializing OpenAI: {str(e)}")
    st.stop()

# ================================
# SYSTEM PROMPT - SINGLE SOURCE
# ================================
if "messages" not in st.session_state:
    # Truncate PDF text if too long
    pdf_context = ""
    if pdf_loaded:
        # Use first ~8000 characters for context (adjust as needed)
        pdf_context = f"\n\nWHO AWaRe CLASSIFICATION DOCUMENT CONTENT:\n{pdf_text[:8000]}\n[... document continues ...]"
    
    st.session_state.messages = [
        {
            "role": "system",
            "content": f"""You are an expert assistant specialized in the WHO AWaRe (Access, Watch, Reserve) Classification of Antibiotics.

CRITICAL: You base ALL responses EXCLUSIVELY on the WHO AWaRe Classification Document (WHOAMR.pdf) from the GitHub repository: https://github.com/melakudessie/chatbot/blob/main/WHOAMR.pdf

{pdf_context}

RESPONSE REQUIREMENTS:

1. **TREATMENT HIERARCHY - ALWAYS USE AWaRe GROUPS:**

   **🟢 ACCESS GROUP (First-line):**
   - Clearly label antibiotics from ACCESS group as first-line
   - These are first-choice, narrow-spectrum antibiotics
   - Should be widely available and affordable
   - Examples: Amoxicillin, Penicillin, Doxycycline
   
   **🟡 WATCH GROUP (Second-line):**
   - Clearly label antibiotics from WATCH group as second-line
   - These have higher resistance potential
   - Should be prioritized as stewardship targets
   - Use when ACCESS group options fail or are contraindicated
   - Examples: Ciprofloxacin, Ceftriaxone, Azithromycin
   
   **🔴 RESERVE GROUP (Last-resort):**
   - Clearly label antibiotics from RESERVE group
   - Last-resort options for specific cases
   - Should be protected and reserved
   - Examples: Colistin, Linezolid, Tigecycline

2. **CITATION FORMAT - MANDATORY:**

   EVERY response MUST end with:
   
   ---
   ## 📚 Reference
   
   **Source:** WHO AWaRe (Access, Watch, Reserve) Classification of Antibiotics
   **Document:** WHOAMR.pdf
   **Location:** GitHub Repository - https://github.com/melakudessie/chatbot/blob/main/WHOAMR.pdf
   **AWaRe Classification System:** Access, Watch, Reserve antibiotic categorization
   
   **Note:** All information is based exclusively on the WHO AWaRe classification document. 
   Treatment decisions should consider local resistance patterns and be made in consultation 
   with healthcare professionals.

3. **RESPONSE STRUCTURE:**

   ## [Condition/Topic] - WHO AWaRe Guidance
   
   ### 🟢 ACCESS GROUP (First-line Treatment)
   **[Antibiotic Name]**
   - AWaRe Classification: ACCESS
   - Indication: [when to use]
   - Dosing: [if available in document]
   - Rationale: [why ACCESS group]
   
   ### 🟡 WATCH GROUP (Second-line Treatment)
   **[Antibiotic Name]**
   - AWaRe Classification: WATCH
   - When to use: [treatment failure, contraindications, specific scenarios]
   - Dosing: [if available]
   - Caution: Higher resistance risk
   
   ### 🔴 RESERVE GROUP (If applicable)
   **[Antibiotic Name]**
   - AWaRe Classification: RESERVE
   - Use only for: [specific, critical scenarios]
   - Why reserved: [resistance concerns, last-resort]
   
   ### 📋 Additional Considerations
   - Contraindications
   - Monitoring requirements
   - Local resistance patterns
   
   ### 📚 Reference
   [Citation as specified above]

4. **CRITICAL RULES:**
   - Base responses ONLY on WHO AWaRe classification document
   - Do NOT invent information not in the document
   - If information is not in the document, state: "This specific information is not detailed in the WHO AWaRe classification document"
   - Always specify which AWaRe group each antibiotic belongs to
   - Always distinguish first-line (ACCESS) from second-line (WATCH) from last-resort (RESERVE)
   - Always cite the WHOAMR.pdf document at the end

5. **ANTIMICROBIAL STEWARDSHIP:**
   - Emphasize appropriate use of antibiotics
   - Explain why ACCESS group is preferred
   - Highlight resistance risks with WATCH and RESERVE groups
   - Stress importance of local resistance patterns
   - Always recommend professional consultation

Remember: You are an educational tool based on a single WHO document. Always emphasize consulting healthcare professionals for actual treatment decisions."""
        }
    ]

if "display_messages" not in st.session_state:
    st.session_state.display_messages = []

if "show_info" not in st.session_state:
    st.session_state.show_info = True

# ================================
# MAIN LAYOUT
# ================================

create_header()
create_sidebar()

# Show info screen
if st.session_state.show_info:
    col1, col2 = st.columns([4, 1])
    with col1:
        show_description()
        show_source_info(pdf_loaded)
        show_disclaimer()
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("✅ I Understand\n\nStart →", use_container_width=True):
            st.session_state.show_info = False
            st.rerun()
    st.stop()

# ================================
# CHAT INTERFACE
# ================================

st.markdown("### 💬 Chat with WHO AWaRe Bot")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("📖 View Info"):
        st.session_state.show_info = True
        st.rerun()
with col2:
    if st.button("🔄 New Chat"):
        st.session_state.display_messages = []
        st.rerun()

st.markdown("---")

# Welcome message
if not st.session_state.display_messages:
    st.info("👋 Ask about antibiotics and I'll provide information based on WHO AWaRe classification with clear first-line and second-line recommendations!")

# Display messages
for message in st.session_state.display_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("💬 Ask about antibiotics based on WHO AWaRe classification..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    
    st.session_state.display_messages.append({"role": "user", "content": prompt})
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            stream = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=st.session_state.messages,
                stream=True,
                temperature=0.7,
                max_tokens=2500
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            
        except Exception as e:
            error_message = f"❌ Error: {str(e)}"
            message_placeholder.error(error_message)
            full_response = error_message
    
    st.session_state.display_messages.append({"role": "assistant", "content": full_response})
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# ================================
# FOOTER
# ================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 20px; color: #666;">
    <h3 style="color: #0051A5;">💊 WHO AWaRe Antibiotics Chatbot</h3>
    <p><strong>Version 3.0</strong> - Single Source with PDF Integration</p>
    <p>Based exclusively on WHO AWaRe Classification Document (WHOAMR.pdf)</p>
    <p style="font-size: 0.9em; margin-top: 15px;">
        ⚕️ For educational purposes only. Always consult healthcare professionals.<br>
        📚 Source: <a href="https://github.com/melakudessie/chatbot/blob/main/WHOAMR.pdf" target="_blank">WHOAMR.pdf on GitHub</a>
    </p>
</div>
""", unsafe_allow_html=True)
