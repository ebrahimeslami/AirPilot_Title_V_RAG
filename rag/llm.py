
import os
from typing import Optional

def synthesize_with_openai(prompt: str, context: str, model: Optional[str] = None) -> Optional[str]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        sys_prompt = (
            "You are a compliance assistant for Title V (Texas). "
            "Answer concisely, cite the provided sources by title when referencing rules, "
            "and prefer exact rule language for limits/timings. "
            "If uncertain, say what needs human review."
        )
        messages = [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": f"Question:\n{prompt}\n\nRelevant context:\n{context}\n"}
        ]
        mdl = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        resp = client.chat.completions.create(model=mdl, messages=messages, temperature=0.2)
        return resp.choices[0].message.content.strip()
    except Exception:
        return None

def compress_extractive(context: str, max_chars: int = 1500) -> str:
    ctx = context.strip()
    if len(ctx) <= max_chars:
        return ctx
    return ctx[:max_chars] + "..."

def answer_with_fallback(question: str, retrieved_text: str) -> str:
    gen = synthesize_with_openai(question, retrieved_text)
    if gen and len(gen) > 20:
        return gen
    return compress_extractive(retrieved_text)
