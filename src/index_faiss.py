from __future__ import annotations

import json
from pathlib import Path

import faiss
import numpy as np

from src.config import settings


def _normalize(vectors: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms = np.maximum(norms, 1e-12)
    return vectors / norms


def build_faiss_index(vectors: list[list[float]]) -> faiss.Index:
    arr = np.array(vectors, dtype="float32")
    arr = _normalize(arr)
    dim = arr.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(arr)
    return index


def save_index_and_meta(index: faiss.Index, meta: list[dict], index_path: str | Path | None = None, meta_path: str | Path | None = None) -> tuple[Path, Path]:
    idx_path = Path(index_path or settings.faiss_index_path)
    mp_path = Path(meta_path or settings.faiss_meta_path)
    idx_path.parent.mkdir(parents=True, exist_ok=True)
    mp_path.parent.mkdir(parents=True, exist_ok=True)

    faiss.write_index(index, str(idx_path))
    with mp_path.open("w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    return idx_path, mp_path


def load_index_and_meta(index_path: str | Path | None = None, meta_path: str | Path | None = None) -> tuple[faiss.Index, list[dict]]:
    idx_path = Path(index_path or settings.faiss_index_path)
    mp_path = Path(meta_path or settings.faiss_meta_path)
    index = faiss.read_index(str(idx_path))
    with mp_path.open("r", encoding="utf-8") as f:
        meta = json.load(f)
    return index, meta


def search(index: faiss.Index, query_vector: list[float], k: int) -> tuple[list[int], list[float]]:
    q = np.array([query_vector], dtype="float32")
    q = _normalize(q)
    scores, ids = index.search(q, k)
    return ids[0].tolist(), scores[0].tolist()
