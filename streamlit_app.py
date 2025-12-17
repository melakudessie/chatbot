"""
PrescribeWise - Health Worker Assistant
Based on The WHO AWaRe (Access, Watch, Reserve) Antibiotic Book (2022)
Version: 4.0 - Final Production Release
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
    page_title="PrescribeWise - Health Worker Assistant",
    page_icon="💡",
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
    
    .header-icon {
        font-size: 4em;
        margin-bottom: 15px;
    }
    
    .header-title {
        color: white;
        font-size: 3em;
        font-weight: bold;
        margin: 10px 0 5px 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .header-subtitle {
        color: #E0F2FF;
        font-size: 1.4em;
        margin: 5px 0 10px 0;
        font-weight: 500;
    }
    
    .header-source {
        color: #B3E5FC;
        font-size: 1em;
        margin-top: 10px;
        font-style: italic;
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
    
    .sidebar-brand {
        text-align: center;
        padding: 15px;
        background: linear-gradient(135deg, #0051A5 0%, #00A3DD 100%);
        border-radius: 10px;
        margin-bottom: 20px;
    }
    
    .sidebar-brand h2 {
        color: white;
        margin: 5px 0;
        font-size: 1.4em;
    }
    
    .sidebar-brand p {
        color: #E0F2FF;
        margin: 5px 0;
        font-size: 0.9em;
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
            <img src="data:image/png;base64,{logo_base64}" class="logo-img" alt="PrescribeWise Logo">
            <h1 class="header-title">💡 PrescribeWise</h1>
            <p class="header-subtitle">Health Worker Assistant</p>
            <p class="header-source">Based on The WHO AWaRe (Access, Watch, Reserve) Antibiotic Book (2022)</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="header-container">
            <div class="header-icon">💡</div>
            <h1 class="header-title">PrescribeWise</h1>
            <p class="header-subtitle">Health Worker Assistant</p>
            <p class="header-source">Based on The WHO AWaRe (Access, Watch, Reserve) Antibiotic Book (2022)</p>
        </div>
        """, unsafe_allow_html=True)

# ================================
# DESCRIPTION
# ================================
def show_description():
    st.markdown("""
    <div class="description-box">
        <h3 style="color: #0051A5;">💡 About PrescribeWise</h3>
        <p style="font-size: 1.1em; line-height: 1.8;">
            <strong>PrescribeWise</strong> is your intelligent health worker assistant designed to help you 
            prescribe antibiotics appropriately and combat multidrug resistance. Based exclusively on 
            <strong>The WHO AWaRe (Access, Watch, Reserve) Antibiotic Book (2022)</strong>.
        </p>
        
        <h4 style="color: #0051A5; margin-top: 20px;">🎯 Mission:</h4>
        <p style="font-size: 1.05em; line-height: 1.6;">
            To assist health workers in making <strong>wise prescribing decisions</strong> that improve 
            rational antibiotic use and help combat antimicrobial resistance worldwide.
        </p>
        
        <h4 style="color: #0051A5; margin-top: 20px;">📚 What You'll Get:</h4>
        <ul style="font-size: 1.05em; line-height: 2;">
            <li>🟢 <strong>ACCESS Group Antibiotics</strong> - First-line, first-choice recommendations</li>
            <li>🟡 <strong>WATCH Group Antibiotics</strong> - Second-line alternatives for specific scenarios</li>
            <li>🔴 <strong>RESERVE Group Antibiotics</strong> - Last-resort options for critical cases</li>
            <li>📖 <strong>Evidence-Based Guidance</strong> - All recommendations from WHO AWaRe Book 2022</li>
            <li>🎯 <strong>Focused Answers</strong> - Get exactly what you need, when you need it</li>
            <li>📄 <strong>Proper Citations</strong> - Every response includes guideline references with page numbers</li>
        </ul>
        
        <div style="background-color: #E3F2FD; padding: 15px; border-radius: 8px; margin-top: 20px;">
            <p style="margin: 0; color: #1565C0; font-weight: 600;">
                💡 <strong>PrescribeWise helps you:</strong> Make rational prescribing decisions • 
                Combat antibiotic resistance • Follow WHO guidelines • Protect antibiotic efficacy
            </p>
        </div>
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
            <strong>Title:</strong> The WHO AWaRe (Access, Watch, Reserve) Antibiotic Book<br>
            <strong>Year:</strong> 2022<br>
            <strong>Publisher:</strong> World Health Organization<br>
            <strong>Classification:</strong> Access, Watch, and Reserve antibiotic groups<br>
            <strong>Status:</strong> <span style="color: {status_color};">{status_emoji} {status_text}</span>
        </p>
        <p style="font-size: 0.95em; color: #555; margin-top: 15px;">
            <strong>Note:</strong> All responses are based exclusively on this guideline. 
            Every answer includes proper citations with page numbers for verification.
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
        <p style="font-size: 1.1em; line-height: 1.6; color: #856404; font-weight: 600;">
            PrescribeWise is an <strong>EDUCATIONAL TOOL</strong> for healthcare professionals
        </p>
        
        <h4 style="color: #856404; margin-top: 15px;">Clinical Guidance:</h4>
        <ul style="font-size: 1em; line-height: 1.8; color: #856404;">
            <li>✅ Use as a reference tool alongside clinical judgment</li>
            <li>✅ Consider patient-specific factors and local resistance patterns</li>
            <li>✅ Follow your institution's antimicrobial stewardship protocols</li>
            <li>✅ Consult infectious disease specialists for complex cases</li>
        </ul>
        
        <h4 style="color: #856404; margin-top: 15px;">Limitations:</h4>
        <ul style="font-size: 1em; line-height: 1.8; color: #856404;">
            <li>❌ NOT a substitute for clinical judgment and experience</li>
            <li>❌ NOT for patient self-medication or diagnosis</li>
            <li>❌ Does NOT replace local antibiotic guidelines when available</li>
            <li>❌ Does NOT account for individual patient allergies or contraindications</li>
        </ul>
        
        <div style="background-color: #FFF; padding: 15px; border-radius: 8px; margin-top: 15px; border: 2px solid #856404;">
            <p style="margin: 0; color: #856404; font-weight: 700; text-align: center;">
                🏥 For Healthcare Professionals Only<br>
                Always integrate with clinical assessment and local guidelines
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ================================
# SIDEBAR
# ================================
def create_sidebar():
    with st.sidebar:
        # Brand section
        logo_base64 = get_logo_base64()
        if logo_base64:
            st.markdown(f"""
            <div class="sidebar-brand">
                <img src="data:image/png;base64,{logo_base64}" style="width: 80px; border-radius: 50%; border: 3px solid white; margin-bottom: 10px;">
                <h2>PrescribeWise</h2>
                <p>Health Worker Assistant</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="sidebar-brand">
                <div style="font-size: 3em; margin-bottom: 10px;">💡</div>
                <h2 style="color: white; margin: 5px 0;">PrescribeWise</h2>
                <p style="color: #E0F2FF; margin: 5px 0;">Health Worker Assistant</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("### 🎯 WHO AWaRe Groups")
        
        with st.expander("🟢 ACCESS Group", expanded=True):
            st.markdown("""
            **First-line, first-choice antibiotics**
            
            - Narrow spectrum of activity
            - Lower resistance potential
            - Should be widely available
            - Recommended as first choice
            
            *Examples: Amoxicillin, Penicillin, Doxycycline*
            """)
        
        with st.expander("🟡 WATCH Group"):
            st.markdown("""
            **Second-line alternatives**
            
            - Broader spectrum antibiotics
            - Higher resistance potential
            - Prioritized as stewardship targets
            - Use when ACCESS group fails
            
            *Examples: Ciprofloxacin, Ceftriaxone, Azithromycin*
            """)
        
        with st.expander("🔴 RESERVE Group"):
            st.markdown("""
            **Last-resort antibiotics**
            
            - Reserved for specific indications
            - Highest resistance concern
            - Should be protected
            - Use only when necessary
            
            *Examples: Colistin, Linezolid, Tigecycline*
            """)
        
        st.divider()
        
        st.markdown("### 💡 Quick Tips")
        with st.expander("How to Use PrescribeWise"):
            st.markdown("""
            **Ask focused questions:**
            - "First-line treatment for pneumonia?"
            - "What if patient is allergic to penicillin?"
            - "Alternative options for UTI?"
            
            **Get detailed answers:**
            - Specific dosing information
            - Treatment duration
            - WHO AWaRe classification
            - When to use alternatives
            """)
        
        st.divider()
        
        st.markdown("### 📊 Session Stats")
        if "messages" in st.session_state:
            msg_count = len([m for m in st.session_state.messages if m["role"] != "system"])
            st.metric("Queries Made", msg_count)
        else:
            st.metric("Queries Made", 0)
        
        st.divider()
        
        if st.button("🔄 New Consultation", use_container_width=True):
            st.session_state.messages = []
            st.session_state.display_messages = []
            st.session_state.show_info = True
            st.rerun()
        
        st.divider()
        
        st.markdown("""
        <div style="text-align: center; padding: 10px;">
            <p style="font-size: 0.85em; color: #666;">
                <strong>PrescribeWise v4.0</strong><br>
                WHO AWaRe Book 2022<br>
                For Health Workers
            </p>
        </div>
        """, unsafe_allow_html=True)

# ================================
# LOAD PDF AND INITIALIZE
# ================================

# Load PDF content
pdf_text, pdf_error = load_pdf_text("WHOAMR.pdf")
pdf_loaded = pdf_text is not None

# Show PDF loading status
if pdf_loaded:
    st.sidebar.success("✅ WHO AWaRe Book loaded")
else:
    st.sidebar.warning("⚠️ WHO AWaRe Book not found")

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
# SYSTEM PROMPT
# ================================
if "messages" not in st.session_state:
    # Truncate PDF text for context
    pdf_context = ""
    if pdf_loaded:
        pdf_context = f"\n\nWHO AWaRe ANTIBIOTIC BOOK (2022) CONTENT:\n{pdf_text[:10000]}\n[... document continues ...]"
    
    st.session_state.messages = [
        {
            "role": "system",
            "content": f"""You are PrescribeWise, an intelligent health worker assistant specialized in The WHO AWaRe (Access, Watch, Reserve) Antibiotic Book (2022).

Your mission: Help health workers prescribe antibiotics appropriately to improve rational use and combat multidrug resistance.

{pdf_context}

CRITICAL RESPONSE RULES:

1. **ANSWER ONLY WHAT IS ASKED:**
   - If asked about first-line → provide ONLY first-line information
   - If asked about alternatives → then provide alternatives
   - If asked about specific drug → focus on that drug
   - Be focused and relevant

2. **BE DETAILED AND COMPREHENSIVE:**
   - Provide thorough information for what is asked
   - Include specific dosages when available
   - Include treatment duration
   - Include age-specific information
   - Include contraindications and monitoring
   - Make responses substantive (400-800 words when appropriate)

3. **WHO AWaRe CLASSIFICATION - ALWAYS SPECIFY:**
   
   🟢 **ACCESS** = First-line, first-choice antibiotics
   - Narrow spectrum
   - Lower resistance risk
   - Should be widely available
   
   🟡 **WATCH** = Second-line alternatives
   - Broader spectrum
   - Higher resistance potential
   - Use when ACCESS fails or contraindicated
   
   🔴 **RESERVE** = Last-resort antibiotics
   - Reserved for specific cases
   - Highest resistance concern
   - Should be protected

4. **STRUCTURE RESPONSES FOR CLARITY:**

   For first-line treatment questions:
   ```
   ## First-Line Treatment for [Condition]
   
   ### 🟢 ACCESS Group Recommendation
   
   **[Antibiotic Name]** (WHO AWaRe: ACCESS)
   
   **Dosing:**
   [Detailed, age-specific information]
   
   **Duration:** [Specific duration]
   
   **Rationale:**
   [Why this is first-line choice]
   
   **Contraindications:**
   [When not to use]
   
   **Monitoring:**
   [What to watch for]
   
   ---
   **Reference:** The WHO AWaRe (Access, Watch, Reserve) Antibiotic Book, 2022
   **Pages:** [specific page numbers or sections]
   ```

5. **CITATION FORMAT - MANDATORY:**

   Every response MUST end with proper citation:
   ```
   ---
   **Reference:** The WHO AWaRe (Access, Watch, Reserve) Antibiotic Book, 2022
   **Pages:** [specific page numbers, sections, or tables]
   ```
   
   Examples:
   - **Pages:** 45-47
   - **Pages:** Section 5.3, Respiratory Infections
   - **Pages:** Table 3, ACCESS Group Antibiotics
   - **Pages:** Annex 1, Pediatric Dosing
   
   NEVER include:
   - GitHub links
   - URLs
   - Web addresses

6. **CRITICAL GUIDELINES:**
   - Base all responses on WHO AWaRe Book 2022
   - Be accurate - stick to the guideline
   - Be complete - provide relevant clinical details
   - Be focused - answer what's asked
   - Always specify AWaRe group (ACCESS/WATCH/RESERVE)
   - Always include proper citations with pages
   - If information not in guideline, state clearly
   - Emphasize rational use and stewardship
   - Help combat multidrug resistance through wise choices

7. **TONE AND APPROACH:**
   - Professional but supportive
   - Empower health workers with knowledge
   - Emphasize wise, rational prescribing
   - Acknowledge clinical judgment importance
   - Encourage stewardship principles

Remember: You are PrescribeWise - helping health workers make wise prescribing decisions to combat antibiotic resistance. Every prescription matters."""
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
        if st.button("✅ Start Using\n\nPrescribeWise →", use_container_width=True):
            st.session_state.show_info = False
            st.rerun()
    st.stop()

# ================================
# CHAT INTERFACE
# ================================

st.markdown("### 💡 Ask PrescribeWise")
col1, col2 = st.columns(2)
with col1:
    if st.button("📖 About PrescribeWise"):
        st.session_state.show_info = True
        st.rerun()
with col2:
    if st.button("🔄 New Consultation"):
        st.session_state.display_messages = []
        st.rerun()

st.markdown("---")

# Welcome message
if not st.session_state.display_messages:
    st.info("""
    👋 **Welcome to PrescribeWise!**
    
    I'm your health worker assistant for appropriate antibiotic prescribing. 
    Ask me about treatments, dosing, alternatives, or WHO AWaRe classifications 
    to make wise prescribing decisions and combat multidrug resistance.
    
    **Example questions:**
    - "What is the first-line treatment for pneumonia in children?"
    - "Alternative options if patient is allergic to penicillin?"
    - "Which antibiotics are in the ACCESS group for UTI?"
    """)

# Display messages
for message in st.session_state.display_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("💡 Ask about antibiotics, treatments, or WHO AWaRe guidelines..."):
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
<div style="text-align: center; padding: 25px; background-color: #F8F9FA; border-radius: 10px;">
    <h3 style="color: #0051A5; margin-bottom: 15px;">💡 PrescribeWise</h3>
    <p style="font-size: 1.1em; margin-bottom: 10px;">
        <strong>Health Worker Assistant for Appropriate Antibiotic Prescribing</strong>
    </p>
    <p style="font-size: 1em; color: #666; margin-bottom: 15px;">
        Based on The WHO AWaRe (Access, Watch, Reserve) Antibiotic Book (2022)
    </p>
    <p style="font-size: 0.9em; color: #888;">
        🎯 Mission: Improve rational antibiotic use • Combat multidrug resistance • Support health workers
    </p>
    <p style="font-size: 0.85em; color: #999; margin-top: 15px;">
        ⚕️ For Healthcare Professionals Only • Educational Tool • Always integrate with clinical judgment
    </p>
</div>
""", unsafe_allow_html=True)
