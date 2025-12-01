import json, re
from pathlib import Path
from bs4 import BeautifulSoup
from readability import Document as ReadabilityDoc
from pdfminer.high_level import extract_text
from .config import RAW_DIR, PROCESSED_DIR, CHUNK_SIZE, CHUNK_OVERLAP

def _clean_text(txt: str) -> str:
    txt = re.sub(r"\s+", " ", txt)
    return txt.strip()

def _chunk(text: str, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    chunks = []
    i = 0
    while i < len(text):
        chunk = text[i:i+size]
        chunks.append((i, chunk))
        i += size - overlap
    return chunks

def _html_to_text(path: Path) -> tuple[str, str]:
    html = path.read_text(errors="ignore")
    try:
        doc = ReadabilityDoc(html)
        main = doc.summary()
        soup = BeautifulSoup(main, "lxml")
    except Exception:
        soup = BeautifulSoup(html, "lxml")
    # Extract title
    title = soup.title.get_text(strip=True) if soup.title else path.stem
    # Remove scripts/styles
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = soup.get_text(" ")
    return title, _clean_text(text)

def _pdf_to_text(path: Path) -> tuple[str, str]:
    try:
        text = extract_text(str(path)) or ""
    except Exception:
        text = ""
    title = path.stem
    return title, _clean_text(text)

def build_docs():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out = PROCESSED_DIR / "docs.jsonl"
    with out.open("w", encoding="utf-8") as f:
        for file in RAW_DIR.glob("**/*"):
            if file.suffix not in [".html", ".pdf"]:
                continue
            src = (file.with_suffix(".url").read_text() if file.with_suffix(".url").exists() else "")
            if file.suffix == ".html":
                title, text = _html_to_text(file)
            else:
                title, text = _pdf_to_text(file)
            if not text:
                continue
            for offset, chunk in _chunk(text):
                rec = {
                    "title": title,
                    "source": src,
                    "path": str(file),
                    "offset": offset,
                    "text": chunk
                }
                f.write(json.dumps(rec) + "\n")
    return str(out)

if __name__ == "__main__":
    p = build_docs()
    print("Wrote", p)
