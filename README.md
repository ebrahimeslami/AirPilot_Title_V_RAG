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

What’s included (with --source-list)

tceq — Title V overview, SOP/GOP pages, guidance, forms, Chapter 122 & 39, STEERS/EI, emission events. 
ecfr — 40 CFR Parts 70/60/63/64/72. 
epa — Title V Petition Database, CAA Permitting in Texas, CEDRI/CDX. 
law_cornell — readable CFR mirrors for Part 60/63/64. 
hgb_local — HGB SIP status/history and EPA SIP sections for 30 TAC 117 (minor/major sources). 
local_county — Harris County Pollution Control permit services page (local contact context). 
federal_register — July 24, 2025 HGB RACT proposal page. 
regulations_gov — Region 6 docket example for Texas SIP updates.

## Quickstart
```bash
python -m venv .venv && source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt

# 1) Seed the corpus (edit seed_sources.json if needed)

# 1) Seed the corpus (edit seed_sources.json if needed)
cd "---\Title_V"
.venv\Scripts\Activate.ps1   # or .venv\Scripts\activate.bat

# Fetch per group (or omit --source-list to fetch all groups)
python -m rag.fetch --source-list tceq --max-per-site 80
python -m rag.fetch --source-list ecfr --max-per-site 80
python -m rag.fetch --source-list epa --max-per-site 80
python -m rag.fetch --source-list law_cornell --max-per-site 40
python -m rag.fetch --source-list hgb_local --max-per-site 40
python -m rag.fetch --source-list local_county --max-per-site 10
python -m rag.fetch --source-list federal_register --max-per-site 20
python -m rag.fetch --source-list regulations_gov --max-per-site 30


# 2) Build the index
python -m rag.index --rebuild

# 3) Launch the UI
python -m rag.ui

# 2) Build the index
python -m rag.index --rebuild

# 3) Launch the UI
python -m rag.ui
```

> This environment has no internet. Run the commands on your own machine (with internet) to fetch and index the sources.

Texas Title V RAG (Human-in-the-Loop) can be found here:
http://127.0.0.1:7860/

## Adding Title V history (legacy permits, statements of basis, etc.)
- Add URLs to `seed_sources.json` or drop PDFs into `rag/data/raw/custom/` (create the folder) and re-run `rag.index`.
- You can maintain curated subsets (e.g., "EPA_Region6_petitions") by adding separate lists to the JSON and passing `--source-list name` to the fetcher.

## Notes
- Only publicly-available content is fetched. Respect site terms/robots, and keep request rates low.
- This starter uses TF-IDF to keep dependencies light. You can swap in a sentence-transformer later.
