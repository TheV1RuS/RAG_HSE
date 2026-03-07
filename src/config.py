from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_base_url: str = os.getenv("OPENAI_BASE_URL", "")

    llm_model: str = os.getenv("LLM_MODEL", "gpt-5.4")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-large")

    top_k: int = int(os.getenv("TOP_K", "6"))
    chunk_target_chars: int = int(os.getenv("CHUNK_TARGET_CHARS", "1200"))
    chunk_overlap_chars: int = int(os.getenv("CHUNK_OVERLAP_CHARS", "200"))

    max_answer_tokens: int = int(os.getenv("MAX_ANSWER_TOKENS", "250"))
    temperature: float = float(os.getenv("TEMPERATURE", "0"))

    retrieval_min_score: float | None = (
        float(os.getenv("RETRIEVAL_MIN_SCORE")) if os.getenv("RETRIEVAL_MIN_SCORE") else None
    )

    chunks_path: Path = Path("data/chunks.jsonl")
    faiss_index_path: Path = Path("data/faiss.index")
    faiss_meta_path: Path = Path("data/faiss_meta.json")
    debug_dump_path: Path = Path(os.getenv("DEBUG_DUMP_PATH", "outputs/debug_retrieval.jsonl"))


settings = Settings()
