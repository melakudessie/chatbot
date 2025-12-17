"""
PrescribeWise - Health Worker Assistant with Optimized RAG
Based on The WHO AWaRe (Access, Watch, Reserve) Antibiotic Book (2022) - 700 Pages
Version: 5.1 - Optimized for Large Documents
"""

import streamlit as st
from openai import OpenAI
import base64
from pathlib import Path
import PyPDF2
from typing import List, Dict
import numpy as np
from dataclasses import dataclass
import time

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
# DATA CLASSES
# ================================
@dataclass
class DocumentChunk:
    """Represents a chunk of text from the document"""
    text: str
    page_number: int
    chunk_id: int
    embedding: np.ndarray = None

# ================================
# OPTIMIZED RAG SYSTEM FOR LARGE DOCUMENTS
# ================================
class PrescribeWiseRAG:
    """Professional RAG system optimized for 700-page documents"""
    
    def __init__(self, openai_client: OpenAI):
        self.client = openai_client
        self.chunks: List[DocumentChunk] = []
        self.embeddings_ready = False
        
    def load_and_process_pdf(self, pdf_path: str = "WHOAMR.pdf", chunk_size: int = 800, overlap: int = 150):
        """Load PDF and create overlapping chunks - optimized for large documents"""
        try:
            if not Path(pdf_path).exists():
                return False, "PDF not found"
            
            st.info("📄 Loading 700-page WHO AWaRe Book... This may take a moment.")
            
            # Extract text from PDF
            full_text = []
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)
                
                progress_bar = st.progress(0, text="Extracting text from PDF...")
                
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    text = page.extract_text()
                    if text.strip():
                        full_text.append((text, page_num))
                    
                    # Update progress every 10 pages
                    if page_num % 10 == 0:
                        progress = page_num / total_pages
                        progress_bar.progress(progress, text=f"Extracting page {page_num}/{total_pages}...")
                
                progress_bar.empty()
            
            st.success(f"✅ Extracted text from {len(full_text)} pages")
            
            # Create overlapping chunks with progress
            all_chunks = []
            chunk_id = 0
            
            progress_bar = st.progress(0, text="Creating text chunks...")
            
            for idx, (text, page_num) in enumerate(full_text):
                # Split into sentences to avoid breaking mid-sentence
                sentences = text.replace('.\n', '. ').split('. ')
                current_chunk = ""
                
                for sentence in sentences:
                    if len(current_chunk) + len(sentence) < chunk_size:
                        current_chunk += sentence + ". "
                    else:
                        if current_chunk.strip():
                            all_chunks.append(DocumentChunk(
                                text=current_chunk.strip(),
                                page_number=page_num,
                                chunk_id=chunk_id
                            ))
                            chunk_id += 1
                        
                        # Start new chunk with overlap
                        overlap_sentences = current_chunk.split(". ")[-3:] if len(current_chunk.split(". ")) > 3 else []
                        current_chunk = ". ".join(overlap_sentences) + " " + sentence + ". " if overlap_sentences else sentence + ". "
                
                # Add remaining text
                if current_chunk.strip():
                    all_chunks.append(DocumentChunk(
                        text=current_chunk.strip(),
                        page_number=page_num,
                        chunk_id=chunk_id
                    ))
                    chunk_id += 1
                
                # Update progress
                if idx % 10 == 0:
                    progress = idx / len(full_text)
                    progress_bar.progress(progress, text=f"Creating chunks... {len(all_chunks)} chunks so far")
            
            progress_bar.empty()
            
            self.chunks = all_chunks
            st.success(f"✅ Created {len(self.chunks)} chunks from {len(full_text)} pages")
            return True, f"Loaded {len(self.chunks)} chunks from {len(full_text)} pages"
            
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def create_embeddings_batch(self, batch_size: int = 100):
        """Create embeddings in batches for efficiency - optimized for large documents"""
        try:
            total_chunks = len(self.chunks)
            
            st.info(f"🔄 Creating embeddings for {total_chunks} chunks. This will take 5-10 minutes...")
            progress_bar = st.progress(0, text="Starting embedding creation...")
            
            start_time = time.time()
            
            # Process in batches
            for batch_start in range(0, total_chunks, batch_size):
                batch_end = min(batch_start + batch_size, total_chunks)
                batch_chunks = self.chunks[batch_start:batch_end]
                
                # Create embeddings for batch
                texts = [chunk.text for chunk in batch_chunks]
                
                try:
                    response = self.client.embeddings.create(
                        model="text-embedding-3-small",
                        input=texts
                    )
                    
                    # Assign embeddings to chunks
                    for idx, chunk in enumerate(batch_chunks):
                        chunk.embedding = np.array(response.data[idx].embedding)
                    
                except Exception as e:
                    st.warning(f"Batch error at {batch_start}-{batch_end}, retrying individually...")
                    # Fallback to individual processing for this batch
                    for chunk in batch_chunks:
                        response = self.client.embeddings.create(
                            model="text-embedding-3-small",
                            input=chunk.text
                        )
                        chunk.embedding = np.array(response.data[0].embedding)
                
                # Update progress
                progress = batch_end / total_chunks
                elapsed = time.time() - start_time
                eta = (elapsed / progress) * (1 - progress) if progress > 0 else 0
                
                progress_bar.progress(
                    progress, 
                    text=f"Processing chunk {batch_end}/{total_chunks} | ETA: {int(eta/60)}m {int(eta%60)}s"
                )
                
                # Small delay to avoid rate limits
                time.sleep(0.5)
            
            progress_bar.empty()
            
            elapsed_total = time.time() - start_time
            st.success(f"✅ Created embeddings for {total_chunks} chunks in {int(elapsed_total/60)}m {int(elapsed_total%60)}s")
            
            self.embeddings_ready = True
            return True, f"Created embeddings for {total_chunks} chunks"
            
        except Exception as e:
            return False, f"Error creating embeddings: {str(e)}"
    
    def semantic_search(self, query: str, top_k: int = 5) -> List[tuple]:
        """Find most relevant chunks using semantic search with similarity scores"""
        if not self.embeddings_ready:
            return []
        
        try:
            # Create query embedding
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=query
            )
            query_embedding = np.array(response.data[0].embedding)
            
            # Calculate cosine similarity for all chunks
            similarities = []
            for chunk in self.chunks:
                similarity = np.dot(query_embedding, chunk.embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(chunk.embedding)
                )
                similarities.append((chunk, similarity))
            
            # Sort by similarity and return top k with scores
            similarities.sort(key=lambda x: x[1], reverse=True)
            return similarities[:top_k]
            
        except Exception as e:
            st.error(f"Search error: {str(e)}")
            return []
    
    def generate_answer(self, query: str, relevant_chunks_with_scores: List[tuple]) -> str:
        """Generate answer using retrieved context with similarity awareness"""
        if not relevant_chunks_with_scores:
            return "I couldn't find relevant information in the WHO AWaRe Book to answer your question. Please try rephrasing or ask a different question."
        
        # Build context from relevant chunks
        context_parts = []
        page_references = set()
        
        for chunk, similarity in relevant_chunks_with_scores:
            # Only use chunks with good similarity (>0.7)
            if similarity > 0.7:
                context_parts.append(f"[Page {chunk.page_number}] (Relevance: {similarity:.2f})\n{chunk.text}")
                page_references.add(chunk.page_number)
        
        if not context_parts:
            return "I found some related content, but it may not directly answer your question. Please try being more specific."
        
        context = "\n\n---\n\n".join(context_parts)
        pages_list = sorted(list(page_references))
        
        # Create the prompt
        system_prompt = """You are PrescribeWise, an expert assistant specialized in The WHO AWaRe (Access, Watch, Reserve) Antibiotic Book (2022) - a comprehensive 700-page guideline.

Your mission: Help health workers prescribe antibiotics appropriately to improve rational use and combat multidrug resistance.

CRITICAL INSTRUCTIONS:

1. **USE ONLY THE PROVIDED CONTEXT** - Base your entire answer on the context provided from the WHO AWaRe Book
2. **ANSWER ONLY WHAT IS ASKED** - Be focused and relevant
3. **BE DETAILED** - Provide comprehensive information including dosing, duration, contraindications
4. **SPECIFY AWaRe GROUP** - Always indicate if antibiotic is ACCESS 🟢, WATCH 🟡, or RESERVE 🔴
5. **CITE PAGES** - Use the page numbers from the context in your citation

RESPONSE STRUCTURE:

For treatment questions:
```
## [Treatment Topic]

### 🟢/🟡/🔴 [AWaRe Group] Recommendation

**[Antibiotic Name]** (WHO AWaRe: ACCESS/WATCH/RESERVE)

**Dosing:** [Specific doses with age groups]
**Duration:** [Treatment length]
**Rationale:** [Why this choice]
**Contraindications:** [When not to use]
**Monitoring:** [What to watch]

---
**Reference:** The WHO AWaRe (Access, Watch, Reserve) Antibiotic Book, 2022 (700 pages)
**Pages:** [page numbers from context]
```

CRITICAL RULES:
- If context doesn't contain enough information, acknowledge this clearly
- Never make up information not in the context
- Always cite specific page numbers from the context
- Focus on what's asked - don't add unnecessary information
- Emphasize rational use and antimicrobial stewardship
- If multiple pages discuss the topic, synthesize the information"""

        user_prompt = f"""Based on the following excerpts from the WHO AWaRe Antibiotic Book (2022) - a 700-page comprehensive guideline, please answer this question:

QUESTION: {query}

CONTEXT FROM WHO AWaRe BOOK (Pages {', '.join(map(str, pages_list))}):
{context}

Please provide a detailed, evidence-based answer using ONLY the information from the context above. Include specific page citations."""

        try:
            # Generate response
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error generating response: {str(e)}"

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
    
    .rag-badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.2);
        padding: 8px 16px;
        border-radius: 20px;
        margin-top: 10px;
        font-size: 0.9em;
        color: white;
        font-weight: 600;
    }
    
    .sidebar-brand {
        text-align: center;
        padding: 15px;
        background: linear-gradient(135deg, #0051A5 0%, #00A3DD 100%);
        border-radius: 10px;
        margin-bottom: 20px;
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
    st.markdown("""
    <div class="header-container">
        <div class="header-icon">💡</div>
        <h1 class="header-title">PrescribeWise</h1>
        <p class="header-subtitle">Health Worker Assistant</p>
        <p class="header-source">Based on The WHO AWaRe Antibiotic Book (2022) - 700 Pages</p>
        <div class="rag-badge">🔍 RAG-Powered • Optimized for Large Documents</div>
    </div>
    """, unsafe_allow_html=True)

# ================================
# SIDEBAR
# ================================
def create_sidebar(rag_system):
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-brand">
            <div style="font-size: 3em; margin-bottom: 10px;">💡</div>
            <h2 style="color: white; margin: 5px 0;">PrescribeWise</h2>
            <p style="color: #E0F2FF; margin: 5px 0;">Health Worker Assistant</p>
            <p style="color: #B3E5FC; font-size: 0.8em; margin-top: 5px;">🔍 RAG-Powered (700 pages)</p>
        </div>
        """, unsafe_allow_html=True)
        
        # RAG Status
        st.markdown("### 🔍 RAG System Status")
        if rag_system and rag_system.embeddings_ready:
            st.success(f"✅ Ready: {len(rag_system.chunks)} chunks")
            st.caption("📄 700-page document fully indexed")
        else:
            st.warning("⚠️ Initializing... (5-10 min)")
        
        st.divider()
        
        # WHO AWaRe Groups
        st.markdown("### 🎯 WHO AWaRe Groups")
        
        with st.expander("🟢 ACCESS Group"):
            st.markdown("""
            **First-line antibiotics**
            - Narrow spectrum
            - Lower resistance risk
            """)
        
        with st.expander("🟡 WATCH Group"):
            st.markdown("""
            **Second-line alternatives**
            - Broader spectrum
            - Higher resistance potential
            """)
        
        with st.expander("🔴 RESERVE Group"):
            st.markdown("""
            **Last-resort antibiotics**
            - Reserved for critical cases
            """)
        
        st.divider()
        
        # Session Stats
        st.markdown("### 📊 Session Stats")
        if "messages" in st.session_state:
            msg_count = len([m for m in st.session_state.messages if m["role"] == "user"])
            st.metric("Queries Made", msg_count)
        else:
            st.metric("Queries Made", 0)
        
        st.divider()
        
        if st.button("🔄 New Consultation", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

# ================================
# INITIALIZE RAG SYSTEM
# ================================
@st.cache_resource
def initialize_rag_system():
    """Initialize and cache the RAG system for 700-page document"""
    try:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        rag = PrescribeWiseRAG(client)
        
        # Load PDF
        success, message = rag.load_and_process_pdf("WHOAMR.pdf", chunk_size=800, overlap=150)
        if not success:
            st.error(f"Failed to load PDF: {message}")
            return None
        
        # Create embeddings in batches
        success, message = rag.create_embeddings_batch(batch_size=100)
        if not success:
            st.error(f"Failed to create embeddings: {message}")
            return None
        
        return rag
        
    except Exception as e:
        st.error(f"Error initializing RAG system: {str(e)}")
        return None

# ================================
# MAIN APP
# ================================

# Check API key
if "OPENAI_API_KEY" not in st.secrets:
    st.error("⚠️ OpenAI API key not found!")
    st.stop()

# Initialize RAG system
if "rag_system" not in st.session_state:
    with st.spinner("🔍 Initializing RAG system for 700-page document... This will take 5-10 minutes (one-time only)."):
        st.session_state.rag_system = initialize_rag_system()

rag_system = st.session_state.rag_system

if not rag_system:
    st.error("Failed to initialize RAG system. Please check your PDF file and API key.")
    st.stop()

# Initialize messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Create layout
create_header()
create_sidebar(rag_system)

# Main chat interface
st.markdown("### 💡 Ask PrescribeWise")

col1, col2 = st.columns(2)
with col1:
    st.caption(f"🔍 RAG-powered • Searching all 700 pages")
with col2:
    if st.button("🔄 New Consultation", key="new_chat_top"):
        st.session_state.messages = []
        st.rerun()

st.markdown("---")

# Welcome message
if not st.session_state.messages:
    st.info("""
    👋 **Welcome to PrescribeWise RAG!**
    
    I use **Retrieval-Augmented Generation (RAG)** to search through the entire 
    **700-page WHO AWaRe Book** and provide accurate, evidence-based answers.
    
    **How it works:**
    1. 🔍 I search all ~3,500 chunks from 700 pages
    2. 📖 I retrieve the 5 most relevant sections
    3. 💡 I provide accurate answers with specific page citations
    
    **Example questions:**
    - "What is the first-line treatment for pneumonia in children?"
    - "Which antibiotics are in the ACCESS group for UTI?"
    - "Alternative options if patient is allergic to penicillin?"
    """)

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("💡 Ask about antibiotics, treatments, or WHO AWaRe guidelines..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("🔍 Searching 700-page WHO AWaRe Book..."):
            # Retrieve relevant chunks
            relevant_chunks_with_scores = rag_system.semantic_search(prompt, top_k=5)
            
            if relevant_chunks_with_scores:
                # Show retrieved pages with similarity scores
                chunks_display = []
                for chunk, score in relevant_chunks_with_scores:
                    chunks_display.append(f"Page {chunk.page_number} ({score:.2f})")
                st.caption(f"📖 Retrieved: {', '.join(chunks_display)}")
            
            # Generate answer
            response = rag_system.generate_answer(prompt, relevant_chunks_with_scores)
            st.markdown(response)
    
    # Add assistant message
    st.session_state.messages.append({"role": "assistant", "content": response})

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 25px; background-color: #F8F9FA; border-radius: 10px;">
    <h3 style="color: #0051A5; margin-bottom: 15px;">💡 PrescribeWise RAG</h3>
    <p style="font-size: 1.1em; margin-bottom: 10px;">
        <strong>RAG-Powered Health Worker Assistant</strong>
    </p>
    <p style="font-size: 1em; color: #666; margin-bottom: 15px;">
        Retrieval-Augmented Generation • 700-Page WHO AWaRe Book • Evidence-Based
    </p>
    <p style="font-size: 0.9em; color: #888;">
        🎯 Accurate Information • ~3,500 Chunks Indexed • Combat Multidrug Resistance
    </p>
    <p style="font-size: 0.85em; color: #999; margin-top: 15px;">
        ⚕️ For Healthcare Professionals Only • Educational Tool
    </p>
</div>
""", unsafe_allow_html=True)
