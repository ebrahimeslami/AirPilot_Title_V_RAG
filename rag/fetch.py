import os, time, hashlib, re, sys, argparse
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from readability import Document as ReadabilityDoc
from pdfminer.high_level import extract_text
from pathlib import Path
from .config import RAW_DIR, USER_AGENT, TIMEOUT, MAX_BYTES, ALLOWED_MIME, SEED_SOURCES

HEADERS = {"User-Agent": USER_AGENT}

def _safe_filename(url: str) -> str:
    h = hashlib.sha256(url.encode()).hexdigest()[:16]
    parsed = urlparse(url)
    name = (parsed.netloc + parsed.path).strip("/").replace("/", "_")
    if not name:
        name = "index"
    return f"{name[:80]}_{h}"

def fetch_url(url: str, session: requests.Session, outdir: Path) -> Path | None:
    try:
        r = session.get(url, headers=HEADERS, timeout=TIMEOUT, stream=True, allow_redirects=True)
        r.raise_for_status()
        ctype = r.headers.get("Content-Type","").split(";")[0].strip().lower()
        if not any(ctype.startswith(a) for a in ALLOWED_MIME):
            # Try to guess by extension
            if url.lower().endswith(".pdf"):
                ctype = "application/pdf"
            elif url.lower().endswith(".html") or url.lower().endswith("/"):
                ctype = "text/html"
            else:
                return None
        # size limit
        content = r.content
        if len(content) > MAX_BYTES:
            return None
        fname = _safe_filename(url)
        ext = ".pdf" if ctype == "application/pdf" or url.lower().endswith(".pdf") else ".html"
        path = outdir / f"{fname}{ext}"
        path.write_bytes(content)
        (outdir / f"{fname}.url").write_text(url)
        return path
    except Exception as e:
        return None

def extract_links(html: str, base: str) -> list[str]:
    soup = BeautifulSoup(html, "lxml")
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("#"):
            continue
        href = urljoin(base, href)
        links.append(href)
    return links

def crawl(seed: list[str], max_per_site: int = 50, delay=0.5):
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    seen = set()
    q = list(seed)
    per_site = {}
    with requests.Session() as s:
        for url in q:
            domain = urlparse(url).netloc
            per_site.setdefault(domain, 0)
        i = 0
        while q:
            url = q.pop(0)
            dom = urlparse(url).netloc
            if per_site.get(dom,0) >= max_per_site:
                continue
            if url in seen:
                continue
            seen.add(url)
            p = fetch_url(url, s, RAW_DIR)
            if not p:
                continue
            per_site[dom] = per_site.get(dom,0) + 1
            if p.suffix == ".html":
                html = p.read_text(errors="ignore")
                # read main content only for link discovery too
                try:
                    doc = ReadabilityDoc(html)
                    main_html = doc.summary(html_partial=True)
                except Exception:
                    main_html = html
                links = extract_links(main_html, (p.with_suffix(".url")).read_text())
                # keep only same-domain or known regulatory domains
                allow = (".tceq.texas.gov", ".epa.gov", "ecfr.gov", "law.cornell.edu", "govinfo.gov", "cdx.epa.gov", "texas-sos.appianportalsgov.com")
                for lk in links:
                    if any(d in lk for d in allow):
                        q.append(lk)
            time.sleep(delay)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-list", default=None, help="Limit to a top-level key in seed_sources.json (e.g., tceq, ecfr, epa)")
    ap.add_argument("--max-per-site", type=int, default=50)
    args = ap.parse_args()
    from .config import SEED_SOURCES
    seeds = []
    if args.source_list:
        seeds = SEED_SOURCES.get(args.source_list, [])
    else:
        for v in SEED_SOURCES.values():
            seeds.extend(v)
    crawl(seeds, max_per_site=args.max_per_site)
    print("Fetch complete.")
