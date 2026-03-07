from __future__ import annotations

import time
from typing import Iterable

from openai import OpenAI

from src.config import settings


def _client() -> OpenAI:
    kwargs = {"api_key": settings.openai_api_key}
    if settings.openai_base_url:
        kwargs["base_url"] = settings.openai_base_url
    return OpenAI(**kwargs)


def batched(items: list[str], size: int) -> Iterable[list[str]]:
    for i in range(0, len(items), size):
        yield items[i : i + size]


def embed_texts(texts: list[str], batch_size: int = 32, retries: int = 2) -> list[list[float]]:
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")

    client = _client()
    vectors: list[list[float]] = []

    for batch in batched(texts, batch_size):
        for attempt in range(retries + 1):
            try:
                res = client.embeddings.create(model=settings.embedding_model, input=batch)
                vectors.extend([d.embedding for d in res.data])
                break
            except Exception:
                if attempt >= retries:
                    raise
                time.sleep(1.5 * (attempt + 1))

    return vectors
