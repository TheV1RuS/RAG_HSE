from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import settings
from src.debug_dump import append_debug_record
from src.fill_testset import fill_testset
from src.rag_answer import answer_question


def main() -> None:
    if not settings.openai_api_key:
        print("[WARN] OPENAI_API_KEY is missing. Skipping API-dependent smoke checks.")
        return

    if not settings.faiss_index_path.exists() or not settings.faiss_meta_path.exists():
        print("[INFO] FAISS index not found. Build it first with scripts/build_index.py")
        return

    sample_qs = [
        "Какова цель стратегии?",
        "Какой документ утвердил стратегию?",
    ]
    for q in sample_qs:
        ans, dbg = answer_question(q)
        print(f"Q: {q}\nA: {ans}\n")
        append_debug_record(settings.debug_dump_path, dbg)

    sample_out = Path("outputs/smoke_test_output.xlsx")
    fill_testset("test_set_Shalugin_Dmitrii.xlsx", sample_out)
    print(f"[OK] XLSX pipeline test written to: {sample_out}")


if __name__ == "__main__":
    main()
