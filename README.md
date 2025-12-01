# Texas Title V RAG (Human-in-the-Loop)

This is a starter RAG for Texas Title V (air) permitting and compliance.
It can **download and index** authoritative TCEQ/EPA rules and guidance, then serve an **interactive Gradio UI** for retrieval-augmented Q&A and compliance checklists.

## Features
- **Crawler/downloader** for HTML/PDF (TCEQ, EPA, eCFR, etc.).
- **Text normalizer and chunker** with metadata (source URL, title, headings).
- **Lightweight vector search** (TF-IDF cosine) — no external embedding service required.
- **Source-grounded answers** with **inline citations** (URL + line offset estimates).
- **Human-in-the-loop** controls: approve/flag sources, pin authoritative passages, export answers.
- **Checklists/state machine** for applicability, reporting deadlines, and revision pathways.

## Quickstart
```bash
python -m venv .venv && source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt

# 1) Seed the corpus (edit seed_sources.json if needed)
python -m rag.fetch --max-per-site 50

# 2) Build the index
python -m rag.index --rebuild

# 3) Launch the UI
python -m rag.ui
```

> This environment has no internet. Run the commands on your own machine (with internet) to fetch and index the sources.

## Adding Title V history (legacy permits, statements of basis, etc.)
- Add URLs to `seed_sources.json` or drop PDFs into `rag/data/raw/custom/` (create the folder) and re-run `rag.index`.
- You can maintain curated subsets (e.g., "EPA_Region6_petitions") by adding separate lists to the JSON and passing `--source-list name` to the fetcher.

## Notes
- Only publicly-available content is fetched. Respect site terms/robots, and keep request rates low.
- This starter uses TF-IDF to keep dependencies light. You can swap in a sentence-transformer later.
