from __future__ import annotations

import time
from typing import Any

from openai import OpenAI

from src.config import settings
from src.embeddings import embed_texts
from src.index_faiss import load_index_and_meta, search

STRICT_SYSTEM_PROMPT = (
    "Ты отвечаешь строго по предоставленному контексту из одного документа. "
    "Запрещено использовать внешние знания, догадки и предположения. "
    "Если в контексте нет точного ответа, выведи ровно: В документе не указано. "
    "Ответ должен быть кратким: 1–3 предложения или 3–5 пунктов. "
    "Не добавляй ссылки, номера страниц, chunk_id, цитаты источников или комментарии."
)


def _client() -> OpenAI:
    kwargs = {"api_key": settings.openai_api_key}
    if settings.openai_base_url:
        kwargs["base_url"] = settings.openai_base_url
    return OpenAI(**kwargs)


def retrieve_chunks(question: str, k: int | None = None) -> list[dict]:
    k = k or settings.top_k
    index, meta = load_index_and_meta()
    qv = embed_texts([question])[0]
    ids, scores = search(index, qv, k)

    selected: list[dict] = []
    seen = set()
    for idx, score in zip(ids, scores):
        if idx < 0 or idx >= len(meta):
            continue
        item = dict(meta[idx])
        item["score"] = float(score)
        key = item.get("chunk_id") or f"idx_{idx}"
        if key in seen:
            continue
        if settings.retrieval_min_score is not None and item["score"] < settings.retrieval_min_score:
            continue
        seen.add(key)
        selected.append(item)
    return selected


def _compose_context(chunks: list[dict]) -> str:
    parts = []
    for ch in chunks:
        header = f"[{ch.get('chunk_id','')} | {ch.get('section_path','')} | pages {ch.get('page_start','?')}-{ch.get('page_end','?')}]"
        parts.append(f"{header}\n{ch.get('text','').strip()}")
    return "\n\n---\n\n".join(parts)


def _llm_answer(question: str, context: str, retries: int = 2) -> str:
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")
    client = _client()
    user_prompt = f"Контекст:\n{context}\n\nВопрос: {question}\n\nОтвет:"

    for attempt in range(retries + 1):
        try:
            resp = client.responses.create(
                model=settings.llm_model,
                temperature=settings.temperature,
                max_output_tokens=settings.max_answer_tokens,
                input=[
                    {"role": "system", "content": STRICT_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
            )
            text = (getattr(resp, "output_text", "") or "").strip()
            return text or "В документе не указано."
        except Exception:
            if attempt >= retries:
                raise
            time.sleep(1.5 * (attempt + 1))

    return "В документе не указано."


def _looks_like_injection(q: str) -> bool:
    ql = q.lower()
    triggers = [
        "игнорируй", "ignore", "придумай", "invent", "секретн", "secret",
        "не опирайся", "неважно", "любой ценой", "обойди", "bypass",
        "system prompt", "политик", "policy",
    ]
    return any(t in ql for t in triggers)


def answer_question(question: str) -> tuple[str, dict[str, Any]]:
    q = (question or "").strip()

    # Hard guard against prompt injection / rule-breaking prompts
    if _looks_like_injection(q):
        answer = "В документе не указано."
        return answer, {"question": q, "answer": answer, "model": settings.llm_model, "retrieved_chunks": []}

    chunks = retrieve_chunks(q)
    if not chunks:
        answer = "В документе не указано."
        return answer, {"question": q, "answer": answer, "model": settings.llm_model, "retrieved_chunks": []}

    context = _compose_context(chunks)
    answer = _llm_answer(q, context)
    debug = {
        "question": q,
        "answer": answer,
        "model": settings.llm_model,
        "retrieved_chunks": [
            {
                "chunk_id": ch.get("chunk_id"),
                "section_path": ch.get("section_path"),
                "page_start": ch.get("page_start"),
                "page_end": ch.get("page_end"),
                "score": ch.get("score"),
            }
            for ch in chunks
        ],
    }
    return answer, debug
