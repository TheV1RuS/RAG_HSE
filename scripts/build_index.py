from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.chunking import build_chunks, write_chunks_jsonl
from src.config import settings
from src.embeddings import embed_texts
from src.index_faiss import build_faiss_index, save_index_and_meta
from src.pdf_extract import extract_pdf_text
from src.text_clean import clean_pages


def main() -> None:
    pdf_path = Path("strategy.pdf")
    if not pdf_path.exists():
        raise FileNotFoundError("strategy.pdf not found in repository root.")

    raw_pages = extract_pdf_text(pdf_path)
    cleaned_pages = clean_pages(raw_pages)
    chunks = build_chunks(cleaned_pages)
    write_chunks_jsonl(chunks, settings.chunks_path)

    texts = [c["text"] for c in chunks]
    vectors = embed_texts(texts)

    index = build_faiss_index(vectors)
    meta = [
        {
            "chunk_id": c["chunk_id"],
            "text": c["text"],
            "section_path": c.get("section_path", ""),
            "page_start": c.get("page_start"),
            "page_end": c.get("page_end"),
        }
        for c in chunks
    ]

    idx_path, meta_path = save_index_and_meta(index, meta, settings.faiss_index_path, settings.faiss_meta_path)

    print(f"pages={len(cleaned_pages)} chunks={len(chunks)} embedding_model={settings.embedding_model}")
    print(f"index={idx_path} meta={meta_path} chunks_jsonl={settings.chunks_path}")


if __name__ == "__main__":
    main()
