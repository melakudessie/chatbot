import os
import json
import numpy as np
import faiss
import streamlit as st
from openai import OpenAI

INDEX_DIR = "rag_index"
META_PATH = os.path.join(INDEX_DIR, "meta.jsonl")
FAISS_PATH = os.path.join(INDEX_DIR, "faiss.index")

EMBED_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4o-mini"

TOP_K = 5

SYSTEM_PROMPT = """
You are PrescribeWise, a clinical decision-support assistant.

Source policy: Use ONLY the retrieved WHO document excerpts provided in the Context.
If the Context does not contain enough information, say so clearly and ask a targeted follow-up question.

Clinical safety policy:
Do not diagnose; do not replace national guidelines; encourage clinical judgment.
Keep responses concise and professional.
Always include: stewardship note; and cite relevant pages from the provided Context.
"""

st.set_page_config(page_title="PrescribeWise RAG", page_icon="💊", layout="wide")
st.title("PrescribeWise; RAG Chat")
st.caption("Grounded answers from your local WHO knowledge PDF index; requires ingest.py output.")

client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY"))

@st.cache_resource
def load_index_and_meta():
    if not os.path.exists(FAISS_PATH) or not os.path.exists(META_PATH):
        raise FileNotFoundError(
            "RAG index not found. Run: python ingest.py ; then restart the app."
        )

    index = faiss.read_index(FAISS_PATH)

    meta = []
    with open(META_PATH, "r", encoding="utf-8") as f:
        for line in f:
            meta.append(json.loads(line))

    return index, meta

def embed_query(q: str) -> np.ndarray:
    resp = client.embeddings.create(model=EMBED_MODEL, input=[q])
    v = np.array(resp.data[0].embedding, dtype="float32").reshape(1, -1)
    faiss.normalize_L2(v)
    return v

def retrieve(q: str, k: int = TOP_K):
    index, meta = load_index_and_meta()
    v = embed_query(q)
    scores, ids = index.search(v, k)

    results = []
    for score, idx in zip(scores[0], ids[0]):
        if idx == -1:
            continue
        r = meta[int(idx)]
        results.append({"score": float(score), "page": r["page"], "text": r["text"]})
    return results

def build_context(passages) -> str:
    blocks = []
    for i, p in enumerate(passages, start=1):
        blocks.append(f"Excerpt {i}; page {p['page']}; relevance {p['score']:.3f}\n{p['text']}")
    return "\n\n".join(blocks)

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

user_input = st.chat_input("Ask a question; include patient group; severity; allergies; pregnancy status if relevant.")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    passages = retrieve(user_input, TOP_K)
    context = build_context(passages)

    with st.chat_message("assistant"):
        with st.spinner("Retrieving sources; generating grounded guidance..."):
            resp = client.chat.completions.create(
                model=CHAT_MODEL,
                temperature=0.2,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Context:\n{context}\n\nQuestion:\n{user_input}"}
                ],
            )
            answer = resp.choices[0].message.content
            st.markdown(answer)

            with st.expander("Sources used"):
                for p in passages:
                    st.markdown(f"Page {p['page']}; score {p['score']:.3f}")
                    st.write(p["text"])

    st.session_state.messages.append({"role": "assistant", "content": answer})
