import argparse, json, joblib
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .config import PROCESSED_DIR, DOCS_JSONL, INDEX_PATH

def load_docs(path: Path):
    docs = []
    texts = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            texts.append(rec["text"])
            docs.append(rec)
    return texts, docs

def build_index():
    texts, docs = load_docs(DOCS_JSONL)
    vec = TfidfVectorizer(ngram_range=(1,2), max_df=0.85, min_df=2)
    X = vec.fit_transform(texts)
    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"vectorizer": vec, "matrix": X, "docs": docs}, INDEX_PATH)
    return str(INDEX_PATH)

def search(query: str, top_k=8):
    bundle = joblib.load(INDEX_PATH)
    vec = bundle["vectorizer"]
    X = bundle["matrix"]
    docs = bundle["docs"]
    qv = vec.transform([query])
    sims = cosine_similarity(qv, X).ravel()
    idxs = sims.argsort()[::-1][:top_k]
    return [(docs[i], float(sims[i])) for i in idxs]

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--rebuild", action="store_true")
    args = ap.parse_args()
    if args.rebuild:
        print("Building index...")
        p = build_index()
        print("Index at", p)
    else:
        print("Nothing to do. Use --rebuild after parsing.")
