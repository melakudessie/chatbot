"""
WHO Antibiotics Use Support Chatbot
A professional Streamlit chatbot for WHO antibiotic resistance guidelines
Version: 2.0
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
# CUSTOM CSS STYLING
# ================================
st.markdown("""
<style>
    /* Main title styling */
    .main-title {
        text-align: center;
        color: #0051A5;
        font-size: 2.5em;
        font-weight: bold;
        margin-bottom: 0;
        padding: 20px;
    }
    
    /* Subtitle styling */
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.2em;
        margin-top: 0;
        margin-bottom: 20px;
    }
    
    /* Header container */
    .header-container {
        background: linear-gradient(135deg, #0051A5 0%, #00A3DD 100%);
        padding: 30px;
        border-radius: 10px;
        margin-bottom: 30px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .header-title {
        color: white;
        font-size: 2.8em;
        font-weight: bold;
        margin: 0;
        text-align: center;
    }
    
    .header-subtitle {
        color: #E0F2FF;
        font-size: 1.3em;
        text-align: center;
        margin-top: 10px;
    }
    
    /* Description box */
    .description-box {
        background-color: #F8F9FA;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #0051A5;
        margin: 20px 0;
    }
    
    /* Warning/Disclaimer box */
    .disclaimer-box {
        background-color: #FFF3CD;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #FFC107;
        margin: 20px 0;
    }
    
    /* Feature cards */
    .feature-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 10px 0;
        border-left: 4px solid #0051A5;
    }
    
    /* Sidebar styling */
    .sidebar-header {
        color: #0051A5;
        font-size: 1.5em;
        font-weight: bold;
        margin-bottom: 15px;
    }
    
    /* Chat message styling */
    .stChatMessage {
        background-color: #F8F9FA;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #666;
        padding: 20px;
        margin-top: 50px;
        border-top: 1px solid #E0E0E0;
    }
</style>
""", unsafe_allow_html=True)

# ================================
# HEADER WITH LOGO
# ================================
def create_header():
    """Create professional header with logo and title"""
    
    # Using WHO colors and medical emoji as logo
    st.markdown("""
    <div class="header-container">
        <div style="text-align: center; font-size: 4em; margin-bottom: 10px;">
            💊 🏥 🌍
        </div>
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
        <h3 style="color: #0051A5; margin-top: 0;">📖 About This Chatbot</h3>
        <p style="font-size: 1.1em; line-height: 1.6;">
            This AI-powered chatbot provides comprehensive information based on 
            <strong>World Health Organization (WHO)</strong> guidelines for antibiotic use and 
            antimicrobial resistance. Get evidence-based answers about:
        </p>
        <ul style="font-size: 1.05em; line-height: 1.8;">
            <li>🔹 <strong>Antibiotic Treatment Guidelines</strong> - First-line and alternative therapies</li>
            <li>🔹 <strong>WHO AWaRe Classification</strong> - Access, Watch, and Reserve categories</li>
            <li>🔹 <strong>Antimicrobial Resistance</strong> - Prevention and management strategies</li>
            <li>🔹 <strong>Dosing & Duration</strong> - Age-specific recommendations and safety</li>
            <li>🔹 <strong>Antimicrobial Stewardship</strong> - Best practices for responsible use</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# ================================
# DISCLAIMER SECTION
# ================================
def show_disclaimer():
    """Display medical disclaimer"""
    
    st.markdown("""
    <div class="disclaimer-box">
        <h3 style="color: #856404; margin-top: 0;">⚠️ Important Medical Disclaimer</h3>
        <p style="font-size: 1.05em; line-height: 1.6; color: #856404;">
            <strong>This chatbot is for informational and educational purposes only.</strong>
        </p>
        <ul style="font-size: 1em; line-height: 1.8; color: #856404;">
            <li>❌ This is NOT a substitute for professional medical advice, diagnosis, or treatment</li>
            <li>❌ Always consult qualified healthcare professionals for medical decisions</li>
            <li>❌ Do NOT use this information for self-diagnosis or self-medication</li>
            <li>❌ In case of medical emergency, contact emergency services immediately</li>
            <li>✅ This chatbot provides general WHO guideline information only</li>
            <li>✅ Individual patient care requires personalized clinical assessment</li>
        </ul>
        <p style="font-size: 1em; margin-top: 15px; color: #856404;">
            <strong>By using this chatbot, you acknowledge that you have read and understood this disclaimer.</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)

# ================================
# SIDEBAR CONTENT
# ================================
def create_sidebar():
    """Create informative sidebar"""
    
    with st.sidebar:
        # Logo in sidebar
        st.markdown("""
        <div style="text-align: center; font-size: 3em; margin: 20px 0;">
            💊
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<p class="sidebar-header">Quick Navigation</p>', unsafe_allow_html=True)
        
        # Information sections
        with st.expander("📚 How to Use", expanded=True):
            st.markdown("""
            **Getting Started:**
            1. Type your question in the chat box below
            2. Ask about specific antibiotics, infections, or guidelines
            3. Request detailed information on dosing or resistance patterns
            
            **Example Questions:**
            - "What is the first-line treatment for pneumonia in children?"
            - "Explain the WHO AWaRe classification system"
            - "What are alternatives to penicillin for allergic patients?"
            - "How to prevent antibiotic resistance?"
            """)
        
        with st.expander("🎯 Key Features"):
            st.markdown("""
            - ✅ Comprehensive, detailed responses
            - ✅ Evidence-based WHO guidelines
            - ✅ Age-specific recommendations
            - ✅ Safety and contraindications
            - ✅ Antimicrobial stewardship focus
            - ✅ Real-time streaming responses
            """)
        
        with st.expander("🌐 WHO AWaRe Groups"):
            st.markdown("""
            **Access Group (Green):**
            First-line, narrow-spectrum antibiotics
            
            **Watch Group (Yellow):**
            Broader spectrum, higher resistance risk
            
            **Reserve Group (Red):**
            Last-resort antibiotics for specific cases
            """)
        
        st.divider()
        
        # Statistics
        st.markdown("### 📊 Session Statistics")
        if "messages" in st.session_state:
            message_count = len([m for m in st.session_state.messages if m["role"] != "system"])
            st.metric("Total Messages", message_count)
        else:
            st.metric("Total Messages", 0)
        
        st.divider()
        
        # Clear chat button
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            st.session_state.display_messages = []
            st.rerun()
        
        st.divider()
        
        # Footer links
        st.markdown("""
        ### 🔗 Useful Resources
        - [WHO Antimicrobial Resistance](https://www.who.int/health-topics/antimicrobial-resistance)
        - [WHO AWaRe Classification](https://www.who.int/publications/i/item/2021-aware-classification)
        - [WHO Essential Medicines](https://www.who.int/groups/expert-committee-on-selection-and-use-of-essential-medicines)
        """)

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
2. **Structure your responses**: Use clear organization with headings, sections, and bullet points
3. **Include specific information**: Mention specific antibiotics, dosages (when appropriate), duration of treatment, and age-specific recommendations
4. **Reference guidelines**: Cite WHO guidelines, AWaRe classification, and evidence-based practices
5. **Provide context**: Explain the reasoning behind recommendations and the importance of following guidelines
6. **Consider different scenarios**: Discuss variations based on severity, age groups, resistance patterns, and resource settings
7. **Address safety**: Include contraindications, side effects, and important safety considerations when relevant
8. **Emphasize antimicrobial stewardship**: Highlight the importance of appropriate antibiotic use and resistance prevention

Format your responses with clear headings and organized sections for easy reading. Use markdown formatting for better presentation.

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
    col1, col2 = st.columns([3, 1])
    with col1:
        show_description()
        show_disclaimer()
    with col2:
        if st.button("✅ I Understand - Start Chatting", use_container_width=True):
            st.session_state.show_info = False
            st.rerun()
    
    st.stop()

# ================================
# CHAT INTERFACE
# ================================

# Display chat messages
for message in st.session_state.display_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("💬 Ask me about WHO antibiotic guidelines, resistance patterns, or treatment recommendations..."):
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
            error_message = f"❌ Error: {str(e)}"
            message_placeholder.error(error_message)
            full_response = error_message
    
    # Add assistant response to histories
    st.session_state.display_messages.append({"role": "assistant", "content": full_response})
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# ================================
# FOOTER
# ================================
st.markdown("""
<div class="footer">
    <p style="font-size: 1.1em; margin-bottom: 10px;">
        <strong>💊 WHO Antibiotics Support Chatbot</strong>
    </p>
    <p style="font-size: 0.9em; color: #999;">
        Powered by OpenAI GPT-3.5 | Based on WHO Guidelines | For Educational Purposes Only
    </p>
    <p style="font-size: 0.85em; color: #999; margin-top: 10px;">
        © 2024 | Always Consult Healthcare Professionals for Medical Decisions
    </p>
</div>
""", unsafe_allow_html=True)
