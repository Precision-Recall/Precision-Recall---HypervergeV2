"""
RAG Query & Answer — Streamlit App
Run: streamlit run app.py
"""

import os
import re
import streamlit as st
import requests
from qdrant_client import QdrantClient
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# --- Config ---
QDRANT_HOST = os.getenv("QDRANT_HOST")
if not QDRANT_HOST:
    raise ValueError("QDRANT_HOST environment variable is required")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
COLLECTION = os.getenv("QDRANT_COLLECTION")
if not COLLECTION:
    raise ValueError("QDRANT_COLLECTION environment variable is required")
EMBEDDING_URL = os.getenv("EMBEDDING_URL")
if not EMBEDDING_URL:
    raise ValueError("EMBEDDING_URL environment variable is required")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
if not EMBEDDING_MODEL:
    raise ValueError("EMBEDDING_MODEL environment variable is required")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")
GPT_MODEL = os.getenv("OPENAI_MODEL")
if not GPT_MODEL:
    raise ValueError("OPENAI_MODEL environment variable is required")
TOP_K = int(os.getenv("TOP_K", "10"))

# --- Clients ---
qdrant = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
openai_client = OpenAI(api_key=OPENAI_KEY)


def get_embedding(text: str) -> list[float]:
    resp = requests.post(EMBEDDING_URL, json={"model": EMBEDDING_MODEL, "input": text}, timeout=30)
    resp.raise_for_status()
    return resp.json()["data"][0]["embedding"]


def extract_years(query: str) -> list[int]:
    return [int(y) for y in re.findall(r"\b(20\d{2})\b", query)]


def search(query: str, top_k: int = TOP_K) -> list[dict]:
    vector = get_embedding(query)
    years = extract_years(query)

    filter_conditions = None
    if years:
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        filter_conditions = Filter(should=[
            FieldCondition(key="year", match=MatchValue(value=y)) for y in years
        ])

    results = qdrant.query_points(
        collection_name=COLLECTION,
        query=vector,
        query_filter=filter_conditions,
        limit=top_k,
        with_payload=True,
    )
    return results.points


def answer_query(query: str, contexts: list[dict]) -> str:
    context_text = "\n\n---\n\n".join(
        f"[{c.payload.get('company','')} {c.payload.get('year','')} | {c.payload.get('section','')} | {c.payload.get('type','')}]\n{c.payload.get('text','')}"
        for c in contexts
    )
    resp = openai_client.chat.completions.create(
        model=GPT_MODEL,
        messages=[
            {"role": "system", "content": "You are a financial analyst. Answer the question using ONLY the provided context from SEC filings. Cite the company, year, and section when referencing data."},
            {"role": "user", "content": f"Context:\n{context_text}\n\nQuestion: {query}"},
        ],
        temperature=0.2,
        max_tokens=1000,
    )
    return resp.choices[0].message.content


# --- Streamlit UI ---
st.set_page_config(page_title="RAG Financial Q&A", layout="wide")
st.title("📊 Financial Document RAG — Q&A")

SAMPLE_QUERIES = [
    "What were 3M's total net sales in 2017?",
    "What are the key risk factors mentioned by 3M in 2017?",
    "Describe 3M's business segments in 2017.",
    "What was 3M's R&D spending in 2017?",
    "What is 3M's revenue breakdown by geographic area in 2017?",
    "What restructuring actions did 3M take in 2017?",
    "What are 3M's pension and postretirement benefit obligations in 2017?",
    "What was 3M's earnings per share in 2017?",
]

tab_custom, tab_samples = st.tabs(["🔍 Custom Query", "📋 Sample Queries"])

with tab_custom:
    query = st.text_input("Ask a question about the financial documents:")
    if query:
        with st.spinner("Searching & generating answer..."):
            results = search(query)
            if results:
                answer = answer_query(query, results)
                st.markdown("### Answer")
                st.markdown(answer)
                with st.expander(f"📄 Retrieved Chunks ({len(results)})"):
                    for i, r in enumerate(results):
                        p = r.payload
                        st.markdown(f"**Chunk {i+1}** — {p.get('company','')} {p.get('year','')} | {p.get('section','')} | {p.get('type','')} | Page {p.get('page','')}")
                        st.text(p.get("text", "")[:500])
                        if p.get("renderable") and p.get("raw_content"):
                            st.markdown(p["raw_content"], unsafe_allow_html=True)
                        st.divider()
            else:
                st.warning("No relevant chunks found.")

with tab_samples:
    selected = st.selectbox("Choose a sample query:", SAMPLE_QUERIES)
    if st.button("Run Sample Query"):
        with st.spinner("Searching..."):
            results = search(selected)
            if results:
                answer = answer_query(selected, results)
                st.markdown("### Answer")
                st.markdown(answer)
                st.markdown("---")
                with st.expander(f"📄 Retrieved Chunks ({len(results)})"):
                    for i, r in enumerate(results):
                        p = r.payload
                        st.markdown(f"**Chunk {i+1}** — {p.get('company','')} {p.get('year','')} | {p.get('section','')} | {p.get('type','')} | Page {p.get('page','')}")
                        st.text(p.get("text", "")[:500])
                        if p.get("renderable") and p.get("raw_content"):
                            st.markdown(p["raw_content"], unsafe_allow_html=True)
                        st.divider()
            else:
                st.warning("No results found.")
