"""
WHO Antibiotics Use Support Chatbot - WITH LOGO IMAGE
A professional Streamlit chatbot for WHO antibiotic resistance guidelines
Version: 2.0 - Professional Edition with Logo
"""

import streamlit as st
from openai import OpenAI
import base64
from pathlib import Path

# ================================
# PAGE CONFIGURATION
# ================================
st.set_page_config(
    page_title="WHO Antibiotics Support Bot",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.who.int/health-topics/antimicrobial-resistance',
        'Report a bug': None,
        'About': "WHO Antibiotics Support Chatbot - Powered by OpenAI"
    }
)

# ================================
# LOGO HELPER FUNCTION
# ================================
def get_logo_base64():
    """Convert logo to base64 for embedding"""
    logo_path = Path("logo.png")
    if logo_path.exists():
        with open(logo_path, "rb") as f:
            data = f.read()
            return base64.b64encode(data).decode()
    return None

# ================================
# CUSTOM CSS STYLING
# ================================
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Main container */
    .main {
        padding-top: 2rem;
    }
    
    /* Header container */
    .header-container {
        background: linear-gradient(135deg, #0051A5 0%, #00A3DD 100%);
        padding: 40px 30px;
        border-radius: 15px;
        margin-bottom: 30px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        text-align: center;
    }
    
    .logo-img {
        width: 150px;
        height: 150px;
        margin: 0 auto 20px;
        display: block;
        border-radius: 50%;
        border: 5px solid white;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    }
    
    .header-title {
        color: white;
        font-size: 2.8em;
        font-weight: bold;
        margin: 10px 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .header-subtitle {
        color: #E0F2FF;
        font-size: 1.3em;
        margin-top: 10px;
        font-weight: 300;
    }
    
    /* Description box */
    .description-box {
        background-color: #F8F9FA;
        padding: 25px;
        border-radius: 12px;
        border-left: 6px solid #0051A5;
        margin: 20px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .description-box h3 {
        color: #0051A5;
        margin-top: 0;
        font-size: 1.5em;
    }
    
    /* Disclaimer box */
    .disclaimer-box {
        background-color: #FFF3CD;
        padding: 25px;
        border-radius: 12px;
        border-left: 6px solid #FFC107;
        margin: 20px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .disclaimer-box h3 {
        color: #856404;
        margin-top: 0;
        font-size: 1.5em;
    }
    
    /* Feature cards */
    .feature-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 20px;
        border-radius: 12px;
        margin: 10px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* Sidebar styling */
    .sidebar-header {
        color: #0051A5;
        font-size: 1.5em;
        font-weight: bold;
        margin-bottom: 15px;
        text-align: center;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #0051A5 0%, #00A3DD 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,81,165,0.4);
    }
    
    /* Chat messages */
    .stChatMessage {
        background-color: #F8F9FA;
        border-radius: 12px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #666;
        padding: 30px;
        margin-top: 50px;
        border-top: 2px solid #E0E0E0;
        background-color: #F8F9FA;
        border-radius: 10px;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #F0F2F6;
        border-radius: 8px;
        font-weight: 600;
    }
    
    /* Metric styling */
    .stMetric {
        background-color: #F8F9FA;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #0051A5;
    }
</style>
""", unsafe_allow_html=True)

# ================================
# HEADER WITH LOGO
# ================================
def create_header():
    """Create professional header with logo and title"""
    
    logo_base64 = get_logo_base64()
    
    if logo_base64:
        # With custom logo
        st.markdown(f"""
        <div class="header-container">
            <img src="data:image/png;base64,{logo_base64}" class="logo-img" alt="WHO Logo">
            <h1 class="header-title">WHO Antibiotics Support Chatbot</h1>
            <p class="header-subtitle">Evidence-Based Guidance on Antimicrobial Stewardship</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Without logo (fallback to emojis)
        st.markdown("""
        <div class="header-container">
            <div style="font-size: 4em; margin-bottom: 10px;">💊 🏥 🌍</div>
            <h1 class="header-title">WHO Antibiotics Support Chatbot</h1>
            <p class="header-subtitle">Evidence-Based Guidance on Antimicrobial Stewardship</p>
        </div>
        """, unsafe_allow_html=True)

# ================================
# DESCRIPTION SECTION
# ================================
def show_description():
    """Display chatbot description and features"""
    
    st.markdown("""
    <div class="description-box">
        <h3>📖 About This Chatbot</h3>
        <p style="font-size: 1.1em; line-height: 1.8;">
            This AI-powered assistant provides comprehensive, evidence-based information on antibiotic use 
            and antimicrobial resistance based on <strong>World Health Organization (WHO)</strong> guidelines.
        </p>
        <h4 style="color: #0051A5; margin-top: 20px;">What You Can Learn:</h4>
        <ul style="font-size: 1.05em; line-height: 2;">
            <li>🔹 <strong>Treatment Guidelines</strong> - First-line and alternative antibiotic therapies for various infections</li>
            <li>🔹 <strong>WHO AWaRe Classification</strong> - Understanding Access, Watch, and Reserve antibiotic categories</li>
            <li>🔹 <strong>Resistance Patterns</strong> - Current antimicrobial resistance trends and prevention strategies</li>
            <li>🔹 <strong>Dosing Information</strong> - Age-specific recommendations, dosages, and treatment duration</li>
            <li>🔹 <strong>Safety Guidelines</strong> - Contraindications, side effects, and important precautions</li>
            <li>🔹 <strong>Stewardship Best Practices</strong> - Responsible antibiotic use and prescribing practices</li>
        </ul>
        <div style="background-color: #E3F2FD; padding: 15px; border-radius: 8px; margin-top: 20px;">
            <p style="margin: 0; color: #1565C0; font-weight: 600;">
                💡 <strong>Pro Tip:</strong> Ask detailed questions for comprehensive answers including dosing, 
                duration, alternatives, and safety considerations!
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ================================
# DISCLAIMER SECTION
# ================================
def show_disclaimer():
    """Display medical disclaimer"""
    
    st.markdown("""
    <div class="disclaimer-box">
        <h3>⚠️ Important Medical Disclaimer</h3>
        <p style="font-size: 1.1em; line-height: 1.6; color: #856404; font-weight: 600;">
            This chatbot is for <strong>INFORMATIONAL and EDUCATIONAL purposes ONLY</strong>
        </p>
        
        <h4 style="color: #856404; margin-top: 20px;">❌ This Chatbot Does NOT:</h4>
        <ul style="font-size: 1em; line-height: 1.8; color: #856404;">
            <li>Replace professional medical advice, diagnosis, or treatment</li>
            <li>Provide patient-specific medical recommendations</li>
            <li>Authorize prescription or medication changes</li>
            <li>Offer emergency medical guidance</li>
        </ul>
        
        <h4 style="color: #856404; margin-top: 20px;">✅ You MUST:</h4>
        <ul style="font-size: 1em; line-height: 1.8; color: #856404;">
            <li><strong>Always consult qualified healthcare professionals</strong> for medical decisions</li>
            <li><strong>Seek immediate medical attention</strong> for emergencies</li>
            <li><strong>Follow your doctor's prescriptions</strong> and treatment plans</li>
            <li><strong>Report adverse reactions</strong> to your healthcare provider</li>
        </ul>
        
        <div style="background-color: #FFF; padding: 15px; border-radius: 8px; margin-top: 20px; border: 2px solid #856404;">
            <p style="margin: 0; color: #856404; font-weight: 700; text-align: center;">
                ⚕️ By using this chatbot, you acknowledge that you understand this disclaimer 
                and will consult healthcare professionals for medical advice.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ================================
# SIDEBAR CONTENT
# ================================
def create_sidebar():
    """Create informative sidebar"""
    
    with st.sidebar:
        # Logo in sidebar
        logo_base64 = get_logo_base64()
        if logo_base64:
            st.markdown(f"""
            <div style="text-align: center; margin: 20px 0;">
                <img src="data:image/png;base64,{logo_base64}" style="width: 120px; border-radius: 50%; border: 3px solid #0051A5;">
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align: center; font-size: 3em; margin: 20px 0;">
                💊
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('<p class="sidebar-header">Quick Navigation</p>', unsafe_allow_html=True)
        
        # Information sections
        with st.expander("📚 How to Use This Bot", expanded=True):
            st.markdown("""
            **Getting Started:**
            1. 💬 Type your question in the chat box
            2. 📋 Ask about antibiotics, infections, or guidelines
            3. 📊 Request details on dosing, duration, or alternatives
            
            **Example Questions:**
            - *"First-line treatment for pneumonia in children?"*
            - *"Explain WHO AWaRe classification"*
            - *"Alternatives to penicillin for allergies?"*
            - *"How to prevent antibiotic resistance?"*
            - *"Dosing for amoxicillin in pediatrics?"*
            """)
        
        with st.expander("🎯 Key Features"):
            st.markdown("""
            - ✅ **Comprehensive responses** with detailed explanations
            - ✅ **Evidence-based** WHO guideline information
            - ✅ **Age-specific** dosing and recommendations
            - ✅ **Safety focus** including contraindications
            - ✅ **Stewardship emphasis** on responsible use
            - ✅ **Real-time** streaming responses
            - ✅ **Structured output** for easy reading
            """)
        
        with st.expander("🌐 WHO AWaRe Classification"):
            st.markdown("""
            **🟢 ACCESS Group:**
            - First-line, narrow-spectrum
            - Lower resistance risk
            - Examples: Amoxicillin, Penicillin
            
            **🟡 WATCH Group:**
            - Broader spectrum antibiotics
            - Higher resistance potential
            - Examples: Ciprofloxacin, Ceftriaxone
            
            **🔴 RESERVE Group:**
            - Last-resort antibiotics
            - Highest resistance concern
            - Examples: Colistin, Linezolid
            """)
        
        with st.expander("⚕️ When to Seek Medical Help"):
            st.markdown("""
            **🚨 Immediate Emergency:**
            - Difficulty breathing
            - Severe allergic reaction
            - Loss of consciousness
            - Severe pain
            
            **⚠️ Consult Doctor:**
            - Starting new antibiotics
            - Side effects or reactions
            - Symptoms not improving
            - Questions about treatment
            """)
        
        st.divider()
        
        # Statistics
        st.markdown("### 📊 Session Statistics")
        if "messages" in st.session_state:
            message_count = len([m for m in st.session_state.messages if m["role"] != "system"])
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Messages", message_count)
            with col2:
                user_msgs = len([m for m in st.session_state.messages if m["role"] == "user"])
                st.metric("Questions", user_msgs)
        else:
            st.metric("Total Messages", 0)
        
        st.divider()
        
        # Clear chat button
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            st.session_state.display_messages = []
            st.session_state.show_info = True
            st.rerun()
        
        st.divider()
        
        # Footer links
        st.markdown("""
        ### 🔗 WHO Resources
        - [WHO AMR Portal](https://www.who.int/health-topics/antimicrobial-resistance)
        - [AWaRe Database](https://www.who.int/publications/i/item/2021-aware-classification)
        - [Essential Medicines List](https://www.who.int/groups/expert-committee-on-selection-and-use-of-essential-medicines)
        - [Global Action Plan](https://www.who.int/publications/i/item/9789241509763)
        """)
        
        st.markdown("---")
        st.caption("💊 Version 2.0 Professional")

# ================================
# API KEY CHECK
# ================================
if "OPENAI_API_KEY" not in st.secrets:
    st.error("⚠️ **OpenAI API key not found!**")
    st.info("""
    **Configuration Required:**
    
    **For Local Development:**
    1. Create `.streamlit/secrets.toml` file
    2. Add: `OPENAI_API_KEY = "your-api-key-here"`
    
    **For Streamlit Cloud:**
    1. Go to App Settings → Secrets
    2. Add your API key in TOML format
    """)
    st.stop()

# ================================
# INITIALIZE OPENAI CLIENT
# ================================
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except Exception as e:
    st.error(f"❌ Error initializing OpenAI: {str(e)}")
    st.stop()

# ================================
# INITIALIZE SESSION STATE
# ================================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": """You are an expert medical information assistant specializing in WHO (World Health Organization) antibiotic resistance guidelines and antimicrobial stewardship.

Your role is to provide COMPREHENSIVE, DETAILED, and evidence-based information about:
- Antibiotic use and prescribing practices
- WHO AWaRe (Access, Watch, Reserve) classification system
- Antimicrobial resistance patterns and prevention
- Treatment guidelines for various infections
- Best practices in antibiotic stewardship
- WHO recommendations and clinical guidelines

When answering questions, you should:

1. **Be thorough and detailed**: Provide comprehensive explanations with multiple relevant points
2. **Structure your responses**: Use clear organization with headings, sections, and bullet points for readability
3. **Include specific information**: Mention specific antibiotics, dosages (when appropriate), duration of treatment, and age-specific recommendations
4. **Reference guidelines**: Cite WHO guidelines, AWaRe classification, and evidence-based practices
5. **Provide context**: Explain the reasoning behind recommendations and the importance of following guidelines
6. **Consider different scenarios**: Discuss variations based on severity, age groups, resistance patterns, and resource settings
7. **Address safety**: Include contraindications, side effects, and important safety considerations when relevant
8. **Emphasize antimicrobial stewardship**: Highlight the importance of appropriate antibiotic use and resistance prevention

Format your responses with clear markdown formatting:
- Use ## for main headings
- Use ### for subheadings
- Use bullet points for lists
- Use **bold** for emphasis
- Organize information logically

Always maintain accuracy and emphasize that users should consult healthcare professionals for specific medical advice and treatment decisions."""
        }
    ]

if "display_messages" not in st.session_state:
    st.session_state.display_messages = []

if "show_info" not in st.session_state:
    st.session_state.show_info = True

# ================================
# MAIN LAYOUT
# ================================

# Create header
create_header()

# Create sidebar
create_sidebar()

# Show description and disclaimer on first load
if st.session_state.show_info:
    col1, col2 = st.columns([4, 1])
    with col1:
        show_description()
        show_disclaimer()
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("✅ I Understand\n\nStart Chatting →", use_container_width=True):
            st.session_state.show_info = False
            st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Reset to\n\nView Info", use_container_width=True):
            st.session_state.show_info = True
            st.rerun()
    
    st.stop()

# ================================
# CHAT INTERFACE
# ================================

# Quick action buttons above chat
st.markdown("### 💬 Chat Interface")
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("📖 View Info Again"):
        st.session_state.show_info = True
        st.rerun()
with col2:
    if st.button("🔄 New Conversation"):
        st.session_state.display_messages = []
        st.rerun()

st.markdown("---")

# Display chat messages
if not st.session_state.display_messages:
    st.info("👋 Welcome! Ask me anything about WHO antibiotic guidelines, treatment recommendations, or antimicrobial resistance.")

for message in st.session_state.display_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("💬 Ask about antibiotics, infections, WHO guidelines, resistance patterns, or treatment recommendations..."):
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Add to display history
    st.session_state.display_messages.append({"role": "user", "content": prompt})
    
    # Add to full chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Generate response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # Create streaming response
            stream = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=st.session_state.messages,
                stream=True,
                temperature=0.7,
                max_tokens=2500
            )
            
            # Stream the response
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            
            # Display final response
            message_placeholder.markdown(full_response)
            
        except Exception as e:
            error_message = f"❌ Error: {str(e)}\n\nPlease try again or contact support if the issue persists."
            message_placeholder.error(error_message)
            full_response = error_message
    
    # Add assistant response to histories
    st.session_state.display_messages.append({"role": "assistant", "content": full_response})
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# ================================
# FOOTER
# ================================
st.markdown("---")
st.markdown("""
<div class="footer">
    <h3 style="color: #0051A5; margin-bottom: 15px;">💊 WHO Antibiotics Support Chatbot</h3>
    <p style="font-size: 1.05em; margin-bottom: 10px;">
        <strong>Powered by OpenAI GPT-3.5</strong> | Based on WHO Guidelines
    </p>
    <p style="font-size: 0.95em; color: #666; margin-bottom: 20px;">
        For Educational and Informational Purposes Only
    </p>
    <p style="font-size: 0.9em; color: #999;">
        ⚕️ <strong>Medical Disclaimer:</strong> Always consult healthcare professionals for medical advice, diagnosis, and treatment.<br>
        This chatbot does not replace professional medical consultation.
    </p>
    <p style="font-size: 0.85em; color: #999; margin-top: 15px;">
        © 2024 WHO Antibiotics Support Bot | Version 2.0 Professional Edition
    </p>
</div>
""", unsafe_allow_html=True)
