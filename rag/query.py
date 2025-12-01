from .index import search

def answer(query: str, k=6):
    results = search(query, top_k=k)
    context = []
    citations = []
    for rec, score in results:
        context.append(rec["text"])
        src = rec["source"] or rec["path"]
        citations.append({"title": rec["title"], "source": src, "offset": rec["offset"], "score": score})
    stitched = "\n\n".join(context)
    # Lightweight synthesis: just return top chunks and citations;
    # You can plug an LLM here later for abstractive synthesis.
    return stitched, citations
