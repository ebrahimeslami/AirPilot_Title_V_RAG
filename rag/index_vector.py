# rag/index_vector.py

import os
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple
import numpy as np

# Try FAISS
try:
    import faiss  # type: ignore
    HAS_FAISS = True
except Exception:
    HAS_FAISS = False

from sentence_transformers import SentenceTransformer
from .config import PROCESSED_DIR, DOCS_JSONL

# Default model
MODEL_NAME = os.getenv("EMBEDDINGS_MODEL", "BAAI/bge-base-en")

# Vector storage directory
VECTOR_DIR = PROCESSED_DIR / "vector"
VECTOR_DIR.mkdir(parents=True, exist_ok=True)

INDEX_PATH = VECTOR_DIR / "faiss.index"
META_PATH = VECTOR_DIR / "meta.jsonl"
MODEL_TAG_PATH = VECTOR_DIR / "model.txt"


# --------------------------------------------------------------------------------------
# Load parsed documents (JSONL)
# --------------------------------------------------------------------------------------
def _load_docs() -> List[Dict[str, Any]]:
    docs = []
    if not DOCS_JSONL.exists():
        return docs

    with DOCS_JSONL.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                obj = json.loads(line)
                if obj.get("text"):
                    docs.append(obj)
            except:
                pass
    return docs


# --------------------------------------------------------------------------------------
# Build FAISS vector index
# --------------------------------------------------------------------------------------
def build_vector_index(batch_size: int = 64) -> Tuple[int, str]:

    docs = _load_docs()
    if not docs:
        return 0, "No documents found in DOCS_JSONL."

    model = SentenceTransformer(MODEL_NAME)

    texts = [d["text"] for d in docs]
    all_vecs = []

    # Encode in batches
    for i in range(0, len(texts), batch_size):
        chunk = texts[i:i + batch_size]
        vecs = model.encode(chunk, show_progress_bar=True, normalize_embeddings=True)
        all_vecs.append(vecs.astype("float32"))

    # Stack into one matrix
    X = np.vstack(all_vecs)

    # Save FAISS or NumPy
    if HAS_FAISS:
        dim = X.shape[1]
        index = faiss.IndexFlatIP(dim)
        index.add(X)
        faiss.write_index(index, str(INDEX_PATH))
    else:
        np.save(str(INDEX_PATH) + ".npy", X)

    # Save metadata (row-aligned)
    with META_PATH.open("w", encoding="utf-8") as mf:
        for d in docs:
            meta_line = {
                "title": d.get("title", ""),
                "source": d.get("source", ""),
                "offset": d.get("offset", 0),
                "text": d.get("text", "")[:5000]  # preview limit
            }
            mf.write(json.dumps(meta_line) + "\n")

    # Save the model tag
    MODEL_TAG_PATH.write_text(MODEL_NAME, encoding="utf-8")

    return len(docs), f"Successfully built vector index using model {MODEL_NAME}"
