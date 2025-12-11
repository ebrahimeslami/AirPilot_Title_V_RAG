
# streamlit_app.py (vector-enabled version)

import os, re, json, datetime as dt
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
from pdfminer.high_level import extract_text as pdf_extract_text

from rag.config import RAW_DIR, PROCESSED_DIR, DOCS_JSONL, INDEX_PATH
from rag.parse import build_docs as parse_build_docs
from rag.index import build_index as index_build_index
from rag.query import answer as rag_answer
from rag.llm import answer_with_fallback
from rag.index_vector import build_vector_index, VECTOR_DIR, INDEX_PATH as VEC_INDEX_PATH
from rag.vector_query import search_vector

try:
    from docx import Document as DocxDocument
    HAS_DOCX = True
except:
    HAS_DOCX = False

APP_TITLE = "AirPilot • Texas Title V Dashboard (EPA + TCEQ)"
st.set_page_config(page_title=APP_TITLE, layout="wide")

def ensure_dirs():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    (RAW_DIR / "custom").mkdir(exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

def save_uploaded_file(up, dest):
    dest.mkdir(exist_ok=True)
    path = dest / up.name
    path.write_bytes(up.read())
    return path

ensure_dirs()
st.title(APP_TITLE)

with st.sidebar:
    st.subheader("Corpus Status")
    st.write(f"Docs: {'OK' if DOCS_JSONL.exists() else 'Missing'}")
    st.write(f"BM25: {'OK' if INDEX_PATH.exists() else 'Missing'}")
    st.write(f"Vector dir: {'OK' if VECTOR_DIR.exists() else 'Missing'}")
    st.write(f"FAISS index: {'OK' if VEC_INDEX_PATH.exists() else 'Missing'}")

    use_vec = st.checkbox("Use Vector Search (BGE)", value=True)

    if st.button("Build Vector Index"):
        n, msg = build_vector_index()
        st.success(f"Indexed {n} chunks | {msg}")

    if st.button("Rebuild BM25 Index"):
        parse_build_docs()
        index_build_index()
        st.success("BM25 rebuilt.")

tabs = st.tabs([
    "Chatbot",
    "Search",
    "Uploader"
])

with tabs[0]:
    st.subheader("Chatbot (RAG)")
    query = st.text_input("Ask:")
    if st.button("Send"):
        if use_vec:
            ctx, cites = search_vector(query, k=6)
        else:
            ctx, cites = rag_answer(query, k=6)
        ans = answer_with_fallback(query, ctx)
        st.write(ans)
        st.write(cites)

with tabs[1]:
    st.subheader("Search Corpus")
    q = st.text_input("Search:")
    if st.button("Go"):
        if use_vec:
            ctx, cites = search_vector(q, k=6)
        else:
            ctx, cites = rag_answer(q, k=6)
        st.text_area("Results", ctx)

with tabs[2]:
    st.subheader("Upload Documents")
    uploaded = st.file_uploader("Upload", accept_multiple_files=True, type=["pdf","docx","html","htm"])
    if uploaded:
        saved = []
        for f in uploaded:
            p = save_uploaded_file(f, RAW_DIR / "custom")
            saved.append(p.name)
        st.success(f"Saved: {saved}")
