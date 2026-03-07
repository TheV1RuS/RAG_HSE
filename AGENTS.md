# AGENTS.md — RAG Homework Guardrails

## Goal
Build a RAG system that answers questions about **“Национальная стратегия развития искусственного интеллекта в России до 2030 года”** using **ONLY** the provided PDF in this repository.

## Hard Constraints (must follow)
1) **Single-source rule:**
   Use **only** the single source document: `strategy.pdf` (exact filename in repo root) as the factual source.
   Do not index or read any other files as factual sources (including other PDFs, screenshots, notes, exports).
   - Do **not** use web browsing, external datasets, other PDFs, textbooks, Wikipedia, or “common knowledge”.
   - Do **not** add any additional documents to the knowledge base / vector store.
   - The test set file is allowed to be read **only to get questions**, not as a factual source.

2) **No external facts in answers:**
   Every statement in the answer must be supported by retrieved context from the PDF.
   If the answer is not explicitly supported in the retrieved text, respond with:
   **“В документе не указано.”**

3) **LLM is required:**
   The final answer must be produced via an LLM call (not pure extractive copy-paste).
   However, the LLM must be constrained to the retrieved context and must not hallucinate.

4) **Short answers only:**
   Avoid long explanations. Prefer 1–3 sentences or 3–5 bullet points (when appropriate).
   Do not add “water” or generic commentary.

5) **Output format constraints (submission):**
   - Fill answers into the provided test file column: **`answer`**
   - Output must contain **only the answer text** (no citations, no sources, no retrieved context).
   - Save as: `test_set_Shalugin_Dmitrii.xlsx` (or `.xls` / `.csv` if required by the assignment)
   - Do not change the structure of the provided test file (keep existing columns).

## Implementation Requirements
- Build a pipeline:
  1) Extract text from the PDF (no OCR; PDF is text-selectable).
  2) Clean text (line breaks, hyphenation, repeated headers/footers, page numbers when they pollute retrieval).
  3) Chunk the text meaningfully (prefer headings/numbered sections; fallback to paragraph-based chunking with overlap).
  4) Create embeddings and a persistent vector index (so indexing isn’t repeated every run).
  5) Retrieval: top-k + (optional) MMR/dedup to avoid near-duplicate chunks.
  6) Generation: strict prompt that uses only retrieved context; if missing → “В документе не указано.”

## Quality Targets (aligned with RAGAS)
- Prioritize:
  - **answer_correctness**
  - **answer_similarity**
  - **answer_relevancy**
- Minimize hallucinations and verbosity to avoid hurting correctness/similarity.

## Determinism / Reproducibility
- Use low temperature (0–0.2) for LLM calls.
- Make results repeatable across runs where possible (seed if supported).
- Log enough info for debugging (e.g., retrieved chunk ids), but do **not** write contexts into the final submission file.

## What to NOT do
- Do not cite or rely on anything outside the provided PDF.
- Do not “improve” answers with external policy context, definitions, dates, laws, or general AI knowledge.
- Do not output sources/contexts in the submission spreadsheet—only the `answer` text is required.

## Demo / Screencast expectation
Provide a run that clearly shows:
- reading the test set,
- generating answers via the RAG pipeline (retrieval + LLM),
- writing answers into the `answer` column,
- saving the output file.