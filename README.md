# Texas Title V RAG (Human-in-the-Loop)

AirPilot Title V RAG is an AI enabled regulatory intelligence platform designed to automate Title V applicability determination, compliance tasks, and document analysis by combining modern retrieval augmented generation with deterministic regulatory logic. The system ingests EPA and TCEQ regulatory materials, facility documents, and permits, then uses hybrid retrieval, structured workflows, and a modular Streamlit interface to provide accurate, transparent, and reproducible guidance. AirPilot reduces manual workload, improves compliance consistency, and offers a scalable foundation for building advanced environmental decision support tools.

=======================================================================================
## Features
Regulatory web crawler and downloader for HTML, PDF, and DOCX sources across TCEQ, EPA, eCFR, Federal Register, and local agencies, with automatic source cataloging.
Document parser and text normalizer supporting PDF, DOCX, HTML, and plain text, producing structured chunks with metadata (URL, title, headings, timestamps).
Hybrid retrieval engine combining BM25 keyword search with BGE-base embeddings and FAISS vector search for accurate regulatory grounding.
Source-grounded responses with citations that reference exact regulatory passages and document locations.
Deterministic workflow engine that performs Title V applicability checks, CAM screening, reporting deadline generation, and permit revision classification.
Human-in-the-loop review features enabling users to validate retrieved sources, flag incorrect passages, and pin authoritative excerpts.
Interactive Streamlit dashboard with chatbot, corpus search, facility uploader, compliance calendar, permit navigator, and emissions visualizer.
Modular architecture allowing easy extension with new regulatory sources, new workflow logic, custom LLM providers, and organization-specific rules.

Included Source Packs (via --source-list)
tceq — Title V overview, SOP/GOP pages, guidance documents, PI-1 forms, Chapters 39 and 122, STEERS EI pages, emission events, and supporting state rules.
ecfr — 40 CFR Parts 60, 63, 64, 70, 72, and related federal regulatory structures mirrored through eCFR.
epa — Title V Petition Database, Region 6 permitting guidance, CEDRI/CDX reporting obligations, air program fact sheets.
law_cornell — Clean, readable CFR mirrors for NSPS and NESHAP subparts.
hgb_local — Houston-Galveston-Brazoria SIP materials, ozone classification history, 30 TAC 117 applicability summaries.
local_county — Harris County Pollution Control permit services information and local contact context.
federal_register — Regulatory announcements including July 24, 2025 HGB RACT proposals and related rulemaking notices.
regulations_gov — Region 6 docket examples for Texas SIP updates and public comment records.

=======================================================================================
## Quickstart
1. Create and activate a virtual environment
python -m venv .venv
# macOS/Linux
source .venv/bin/activate        
# or on Windows:
.venv\Scripts\activate

2. Install Python dependencies
pip install -r requirements.txt
pip install -r requirements_embeddings.txt

3. (Optional) Edit seed_sources.json
This file controls which regulatory sources are fetched.
You may add, remove, or modify URLs before building the corpus.


4. Fetch regulatory documents
You may fetch all groups at once:
python -m rag.fetch

Or fetch specific source groups individually:
python -m rag.fetch --source-list tceq --max-per-site 80
python -m rag.fetch --source-list ecfr --max-per-site 80
python -m rag.fetch --source-list epa --max-per-site 80
python -m rag.fetch --source-list law_cornell --max-per-site 40
python -m rag.fetch --source-list hgb_local --max-per-site 40
python -m rag.fetch --source-list local_county --max-per-site 10
python -m rag.fetch --source-list federal_register --max-per-site 20
python -m rag.fetch --source-list regulations_gov --max-per-site 30

All downloaded documents will appear under:
rag/raw/<source>/

5. Parse and normalize documents
python -m rag.parse

This converts PDF, DOCX, and HTML sources into clean structured text and metadata.

6. Build the search indexes
BM25 (keyword) index

python -m rag.index

Vector (embedding + FAISS) index
python -m rag.index_vector

7. Launch the Streamlit dashboard
streamlit run streamlit_app.py

You will get UI tabs for:
    Corpus search
    Chatbot (RAG)
    Compliance workflow engine
    Facility document uploader
    Permit navigator
    Emissions visualizer
    Index rebuild tools

=======================================================================================
> Important Notes About Environment and Connectivity

This demo environment has no internet access.
To fetch and index regulatory sources, run all rag.fetch commands on your local machine where internet connectivity is available.

Once fetched, parsed, and indexed locally, you can run the full Texas Title V RAG system at:
http://127.0.0.1:7860/

This launches the human-in-the-loop interface, which includes the chatbot, corpus search, workflows, and document explorer.

=======================================================================================
Adding Title V History (Permits, Statements of Basis, Petitions):

AirPilot supports custom regulatory datasets, including historical materials such as:
    Legacy Title V permits
    Statements of basis
    Statement of basis revisions
    Public comments and petitions
    Region 6 orders and responses

You can add these in two ways:
1. Add URLs to seed_sources.json
   
{
  "tceq": [...],
  "ecfr": [...],
  "titlev_history": [
    "https://example.gov/permit.pdf",
    "https://example.gov/sob.pdf"
  ]
}

Then fetch only that group:
python -m rag.fetch --source-list titlev_history --max-per-site 200

2. Drop files directly into the local folder
Place PDFs or DOCX files here:
rag/raw/custom/

Then normalize and index them:
python -m rag.parse
python -m rag.index
python -m rag.index_vector


Curated Subsets (Optional)

You may create curated collections of sources such as:
    "EPA_Region6_petitions"
    "TCEQ_TitleV_history"
    "Pre-2010_SOBs"

Just add them as separate arrays in seed_sources.json and fetch them with:
python -m rag.fetch --source-list EPA_Region6_petitions

This gives you modular control over different datasets.

=======================================================================================
General Usage Notes

All fetched content is public. No authentication is used.
Please respect robots.txt, site terms of use, and federal/state guidance about responsible automated access.
Use --max-per-site to control load; lower numbers reduce server impact.
The starter configuration originally used TF-IDF (BM25) for lightweight retrieval. You can optionally switch to sentence-transformer embeddings (BGE Base) and FAISS indexing for high-quality semantic search.

Human-in-the-loop controls allow operators to:
    Review retrieved citations
    Reject or flag incorrect passages
    Pin authoritative regulatory text
    Export validated answers

This preserves transparency and traceability for regulatory workflows.

=======================================================================================
Best Practices
1. Keep Regulatory Sources Organized and Traceable
    Maintain separate source groups (e.g., "tceq", "ecfr", "epa", "titlev_history") in seed_sources.json.
    Avoid mixing state, federal, and local sources unless intentional.
    Use descriptive names when adding new groups (e.g., "R6_petitions_2000_2010").
    Maintain metadata such as fetch date and URL for auditability.

2. Preserve Ground-Truth Text
    Avoid modifying the raw text from EPA/TCEQ sources.
    Use the normalized text files only for indexing; keep originals in rag/raw/<source>/.
    When correcting OCR or PDF parsing artifacts, store changes separately for reproducibility.

3. Chunk Responsibly
    Use overlapping chunks for dense legal or technical segments.
    Keep chunk size between 500–1500 characters depending on rule complexity.
    Ensure headings, citations, and section numbers stay intact to avoid semantic drift.   

4. Rebuild Indexes When Content Changes
    Whenever you add new documents:
python -m rag.parse
python -m rag.index
python -m rag.index_vector

If documents are heavily revised, clear previous indexes first to avoid duplicate hits.

5. Use Human-in-the-Loop Review for Compliance Answers
    Always review retrieved text and citations before taking compliance actions.
    Pin authoritative passages for future use.
    Reject misleading retrievals to improve system accuracy over time.
    This aligns with best practices for regulatory defensibility.

6. Respect Rate Limits and Public Server Load
    Use --max-per-site when fetching from major sources.
    Avoid parallel fetching unless the server permits it.
    Follow robots.txt and site usage policies.

7. Maintain Separate Environments for Development and Production
    Local/dev environment: unrestricted experimentation.
    Production workflow: pinned versions of dependencies, verified index, locked seed list.
    Consider enabling audit logging for compliance-sensitive projects.

8. Validate Outputs With Multiple Retrieval Methods
Cross-check answers using:
    BM25 (keyword)
    Vector search
    Direct document navigation (Navigator tab)
Discrepancies highlight ambiguous text or sources requiring manual interpretation.

9. Use Version Control for Regulatory Datasets
Regulatory text changes over time.
Maintain:
/data/2023/
/data/2024/
/data/2025/

This supports historical permit analysis and SIP revision tracking.

10. Backup Indexes and Datasets Regularly
    Back up the rag/raw/, rag/parsed/, and rag/processed/ directories.
    Create snapshots before running large fetch operations.
    Keep checksums or hashes for traceability.

11. Document Every Workflow Rule
When adding or modifying logic in workflows.py, note:
    Source citation (CFR/TAC)
    Assumptions
    Thresholds
    Exceptions

This maintains legal defensibility and supports peer review.

12. Validate Emissions or Applicability Outcomes Where Relevant
For workflows involving emissions estimates or applicability determinations:
    Confirm assumptions (hours, fuel, emission factors)
    Re-run using alternative scenarios
    Use bounding cases to test logic robustness
