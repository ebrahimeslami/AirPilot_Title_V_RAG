import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

SEED_SOURCES = json.loads((Path(__file__).resolve().parent.parent / "seed_sources.json").read_text())

# Fetch options
USER_AGENT = "TitleV-RAG/1.0 (+https://example.com)"
TIMEOUT = 30
MAX_BYTES = 25 * 1024 * 1024  # 25 MB per file
ALLOWED_MIME = {"text/html", "application/pdf"}

# Chunking
CHUNK_SIZE = 1200  # characters
CHUNK_OVERLAP = 200

# Index
INDEX_PATH = PROCESSED_DIR / "tfidf_index.joblib"
DOCS_JSONL = PROCESSED_DIR / "docs.jsonl"
