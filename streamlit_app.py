"""
WHO AWaRe Antibiotics Support Chatbot
Based ONLY on WHO AWaRe (Access, Watch, Reserve) Classification Document
Version: 3.1 - Focused & Detailed Responses
"""

import streamlit as st
from openai import OpenAI
import base64
from pathlib import Path
import PyPDF2

# ================================
# PAGE CONFIGURATION
# ================================
st.set_page_config(
    page_title="WHO AWaRe Antibiotics Bot",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
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
            This chatbot provides detailed information based <strong>exclusively</strong> on the 
            <strong>WHO AWaRe (Access, Watch, Reserve) Classification Document</strong> 
            stored in the project repository.
        </p>
        <h4 style="color: #0051A5; margin-top: 20px;">What You'll Get:</h4>
        <ul style="font-size: 1.05em; line-height: 2;">
            <li>🟢 <strong>ACCESS Group</strong> - First-line, first-choice antibiotics</li>
            <li>🟡 <strong>WATCH Group</strong> - Second-line alternatives with higher resistance risk</li>
            <li>🔴 <strong>RESERVE Group</strong> - Last-resort antibiotics for specific cases</li>
            <li>📚 <strong>Focused Answers</strong> - Get exactly what you ask for with detailed information</li>
            <li>🎯 <strong>Guideline-Based</strong> - All responses follow the WHO AWaRe document closely</li>
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
            <li>✅ Based ONLY on WHO AWaRe classification document</li>
            <li>✅ Always consult healthcare professionals</li>
            <li>✅ Consider local resistance patterns</li>
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
            """)
        
        with st.expander("🟡 WATCH Group"):
            st.markdown("""
            **Second-line alternatives**
            
            - Broader spectrum
            - Higher resistance potential
            - Prioritized stewardship targets
            """)
        
        with st.expander("🔴 RESERVE Group"):
            st.markdown("""
            **Last-resort antibiotics**
            
            - Reserved for specific cases
            - Highest resistance concern
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
    st.sidebar.warning("⚠️ WHOAMR.pdf not found")

# ================================
# API KEY CHECK
# ================================
if "OPENAI_API_KEY" not in st.secrets:
    st.error("⚠️ OpenAI API key not found!")
    st.stop()

try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except Exception as e:
    st.error(f"❌ Error initializing OpenAI: {str(e)}")
    st.stop()

# ================================
# ENHANCED SYSTEM PROMPT - FOCUSED RESPONSES
# ================================
if "messages" not in st.session_state:
    # Truncate PDF text for context
    pdf_context = ""
    if pdf_loaded:
        pdf_context = f"\n\nWHO AWaRe DOCUMENT CONTENT:\n{pdf_text[:10000]}\n[... document continues ...]"
    
    st.session_state.messages = [
        {
            "role": "system",
            "content": f"""You are an expert assistant specialized in the WHO AWaRe (Access, Watch, Reserve) Classification of Antibiotics.

CRITICAL: Base ALL responses EXCLUSIVELY on the WHO AWaRe Classification Document (WHOAMR.pdf) from: https://github.com/melakudessie/chatbot/blob/main/WHOAMR.pdf

{pdf_context}

RESPONSE RULES - READ CAREFULLY:

1. **ANSWER ONLY WHAT IS ASKED:**
   - If user asks ONLY about first-line treatment → provide ONLY first-line information
   - If user asks ONLY about second-line treatment → provide ONLY second-line information
   - If user asks about alternatives → then provide alternatives
   - DO NOT automatically include all treatment options unless asked
   
   Examples:
   - "What is the first-line treatment?" → Answer ONLY first-line, do NOT mention second-line
   - "What are the alternatives?" → Then provide second-line and other options
   - "Complete treatment protocol" → Then provide first-line, second-line, and reserve

2. **BE DETAILED AND COMPREHENSIVE FOR WHAT IS ASKED:**
   - Provide thorough, detailed information
   - Include specific dosages if available in the document
   - Include duration of treatment if specified
   - Include age-specific information when relevant
   - Explain the rationale and reasoning
   - Include contraindications and safety information when relevant
   - Make responses substantive and informative (400-800 words when appropriate)

3. **WHO AWaRe CLASSIFICATION - ALWAYS SPECIFY:**
   
   🟢 **ACCESS GROUP** = First-line, first-choice antibiotics
   - Narrow spectrum
   - Lower resistance risk
   - Should be widely available
   
   🟡 **WATCH GROUP** = Second-line alternatives
   - Broader spectrum
   - Higher resistance potential
   - Use when ACCESS fails or contraindicated
   
   🔴 **RESERVE GROUP** = Last-resort
   - Reserved for specific cases
   - Highest resistance concern
   - Protected antibiotics

4. **STRUCTURE YOUR RESPONSE BASED ON THE QUESTION:**

   For "first-line treatment" questions:
   ```
   ## First-Line Treatment for [Condition]
   
   ### 🟢 ACCESS Group Recommendation
   
   **[Antibiotic Name]** (WHO AWaRe: ACCESS)
   
   **Dosing:**
   - [Detailed dosing information from guideline]
   - [Age-specific doses if applicable]
   
   **Duration:** [Specific duration from guideline]
   
   **Rationale:**
   - [Why this is first-line]
   - [Coverage information]
   - [Benefits and considerations]
   
   **Contraindications:**
   - [When not to use]
   
   **Monitoring/Follow-up:**
   - [What to watch for]
   
   ---
   **Reference:** WHO AWaRe Classification (WHOAMR.pdf)
   ```

   For "second-line" or "alternatives" questions:
   ```
   ## Second-Line/Alternative Treatment for [Condition]
   
   ### 🟡 WATCH Group Alternatives
   
   **When to use:** [Specific scenarios]
   
   **[Antibiotic Name]** (WHO AWaRe: WATCH)
   - Dosing: [Details]
   - Duration: [Details]
   - Indications: [When to use this specific one]
   
   [Additional alternatives as appropriate]
   
   ---
   **Reference:** WHO AWaRe Classification (WHOAMR.pdf)
   ```

5. **CRITICAL GUIDELINES:**
   - Be accurate - stick to what's in the document
   - Be complete - provide all relevant details for what's asked
   - Be focused - don't include unnecessary sections
   - Be specific - include dosages, durations, age ranges
   - If information is not in the document, state: "This specific information is not detailed in the WHO AWaRe classification document"
   - Always specify which AWaRe group (ACCESS/WATCH/RESERVE)
   - Always cite WHOAMR.pdf at the end

6. **CITATION FORMAT (Keep it concise):**
   
   End responses with:
   ```
   ---
   **Reference:** WHO AWaRe Classification of Antibiotics (WHOAMR.pdf)
   **Source:** https://github.com/melakudessie/chatbot/blob/main/WHOAMR.pdf
   ```

7. **EXAMPLES OF FOCUSED RESPONSES:**

   Question: "What is the first-line treatment for pneumonia in children?"
   ✅ CORRECT: Provide detailed first-line information ONLY
   ❌ WRONG: Include first-line, second-line, reserve, and all alternatives
   
   Question: "What are the alternatives to amoxicillin?"
   ✅ CORRECT: Provide detailed information about alternatives
   ❌ WRONG: Just list names without details
   
   Question: "Complete treatment protocol for UTI"
   ✅ CORRECT: Provide first-line, second-line, and reserve options
   ❌ WRONG: Only provide first-line

Remember: 
- Answer what is asked - no more, no less
- Be detailed and comprehensive for what you do answer
- Always follow the WHO AWaRe classification structure
- Base everything on the WHOAMR.pdf document
- Professional consultation is always required for actual treatment decisions"""
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
col1, col2 = st.columns(2)
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
    st.info("👋 Ask about antibiotics and I'll provide focused, detailed information from the WHO AWaRe classification!")

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
    <p><strong>WHO AWaRe Antibiotics Chatbot v3.1</strong></p>
    <p style="font-size: 0.9em;">Based exclusively on WHO AWaRe Classification Document (WHOAMR.pdf)</p>
    <p style="font-size: 0.85em; margin-top: 10px;">
        ⚕️ For educational purposes only • Always consult healthcare professionals
    </p>
</div>
""", unsafe_allow_html=True)
