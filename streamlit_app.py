"""
WHO Antibiotics Use Support Chatbot
A Streamlit chatbot application for providing guidance on WHO antibiotic resistance guidelines
"""

import streamlit as st
from openai import OpenAI

# Page configuration
st.set_page_config(
    page_title="WHO Antibiotics Support",
    page_icon="💊",
    layout="centered",
    initial_sidebar_state="auto"
)

# Title and description
st.title("💬 WHO Antibiotics Use Support Chatbot")
st.caption("🚀 A chatbot to help with WHO Antibiotic resistance guidelines")

# Sidebar information
with st.sidebar:
    st.header("ℹ️ About")
    st.markdown("""
    This chatbot provides information and guidance based on WHO (World Health Organization) 
    antibiotic resistance guidelines.
    
    **Disclaimer:** This chatbot provides general information only and should not replace 
    professional medical advice. Always consult with healthcare professionals for medical decisions.
    """)
    
    st.divider()
    
    # Add clear chat button
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    
    st.markdown("### 📊 Chat Statistics")
    if "messages" in st.session_state:
        st.metric("Messages", len(st.session_state.messages))
    else:
        st.metric("Messages", 0)

# Check for API key in secrets
if "OPENAI_API_KEY" not in st.secrets:
    st.error("⚠️ **OpenAI API key not found!**")
    st.info("""
    **For local development:**
    1. Create a `.streamlit` folder in your project root
    2. Create a `secrets.toml` file inside it
    3. Add your API key: `OPENAI_API_KEY = "your-api-key-here"`
    
    **For Streamlit Cloud:**
    1. Go to your app settings
    2. Navigate to "Secrets" section
    3. Add your API key in TOML format
    """)
    st.stop()

# Initialize OpenAI client with API key from secrets
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except Exception as e:
    st.error(f"❌ Error initializing OpenAI client: {str(e)}")
    st.stop()

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": """You are a helpful medical information assistant specializing in WHO 
            (World Health Organization) antibiotic resistance guidelines. You provide accurate, 
            evidence-based information about antibiotic use, resistance patterns, and WHO 
            recommendations. Always emphasize that users should consult healthcare professionals 
            for specific medical advice. Be clear, concise, and reference WHO guidelines when 
            appropriate."""
        }
    ]

# Initialize user-facing messages (excludes system message)
if "display_messages" not in st.session_state:
    st.session_state.display_messages = []

# Display chat messages from history (excluding system message)
for message in st.session_state.display_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask me about WHO antibiotic guidelines..."):
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Add user message to display history
    st.session_state.display_messages.append({"role": "user", "content": prompt})
    
    # Add user message to full chat history (for API)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Generate assistant response
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
                max_tokens=1000
            )
            
            # Stream the response
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            
            # Display final response
            message_placeholder.markdown(full_response)
            
        except Exception as e:
            error_message = f"❌ Error generating response: {str(e)}"
            message_placeholder.error(error_message)
            full_response = error_message
    
    # Add assistant response to both histories
    st.session_state.display_messages.append({"role": "assistant", "content": full_response})
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# Footer
st.divider()
st.caption("""
💡 **Tips:** 
- Ask about specific antibiotics or resistance patterns
- Request information about WHO AWaRe classification
- Inquire about best practices in antibiotic prescribing

⚠️ **Remember:** This is for informational purposes only. Always consult healthcare professionals for medical advice.
""")
