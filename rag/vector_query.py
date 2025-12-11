# rag/vector_query.py

import json
from pathlib import Path
from typing import List, Tuple, Dict, Any

import numpy as np

# Optional FAISS acceleration
try:
    import faiss  # type: ignore
    HAS_FAISS = True
except Exception:
    HAS_FAISS = False

from sentence_transformers import SentenceTransformer
from .index_vector import MODEL_NAME, INDEX_PATH, META_PATH


def _load_meta() -> List[Dict[str, Any]]:
    """Load row-aligned metadata for each embedding vector."""
    metas: List[Dict[str, Any]] = []
    if not META_PATH.exists():
        return metas
    with META_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                metas.append(json.loads(line))
            except Exception:
                # skip bad lines
                pass
    return metas


def _load_index():
    """Load FAISS index if present; otherwise numpy matrix fallback."""
    if HAS_FAISS and INDEX_PATH.exists():
        return faiss.read_index(str(INDEX_PATH)), "faiss"

    npy = str(INDEX_PATH) + ".npy"
    if Path(npy).exists():
        X = np.load(npy).astype("float32")
        return X, "numpy"

    return None, None


def search_vector(question: str, k: int = 6) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Semantic vector search over the embedded corpus.

    Returns:
      stitched_context: str  -> concatenated top-k chunks separated by rules
      citations: List[Dict]  -> [{title, source, offset, score}, ...]
    """
    metas = _load_meta()
    index, typ = _load_index()
    if index is None or not metas:
        return "Vector index not built yet. Click 'Build Vector Index' in the sidebar.", []

    # Encode the query
    model = SentenceTransformer(MODEL_NAME)
    q_vec = model.encode([question], normalize_embeddings=True)[0].astype("float32")

    # Search
    if typ == "faiss":
        D, I = index.search(q_vec.reshape(1, -1), k)
        scores = D[0]
        idxs = I[0]
    else:
        # numpy cosine similarity (inner product on normalized vectors)
        X = index  # (N, D)
        sims = X @ q_vec  # (N,)
        idxs = np.argsort(-sims)[:k]
        scores = sims[idxs]

    # Collect chunks + citations
    chunks: List[str] = []
    cites: List[Dict[str, Any]] = []
    for idx, sc in zip(idxs, scores):
        if idx < 0 or idx >= len(metas):
            continue
        m = metas[idx]
        chunks.append(m.get("text", ""))
        cites.append({
            "title": m.get("title", ""),
            "source": m.get("source", ""),
            "offset": int(m.get("offset", 0)),
            "score": float(sc),
        })

    stitched = "\n\n---\n\n".join(chunks)
    return stitched, cites
