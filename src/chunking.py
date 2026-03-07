from __future__ import annotations

import json
import re
from pathlib import Path

from src.config import settings

ROMAN_RE = re.compile(r"^(?:ГЛАВА\s+)?([IVXLCDM]+)\.?\s+", re.IGNORECASE)
POINT_RE = re.compile(r"^(\d+)[\.|\)]\s+")
SUBPOINT_RE = re.compile(r"^([а-я])\)\s+", re.IGNORECASE)


def _detect_section_path(text: str, current_chapter: str | None, current_point: str | None) -> tuple[str | None, str | None, str | None]:
    chapter, point, subpoint = current_chapter, current_point, None
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        m = ROMAN_RE.match(line)
        if m:
            chapter = m.group(1).upper()
            point = None
            continue
        m = POINT_RE.match(line)
        if m:
            point = m.group(1)
            continue
        m = SUBPOINT_RE.match(line)
        if m:
            subpoint = f"{m.group(1)})"
            break
    return chapter, point, subpoint


def _split_blocks(pages: list[dict]) -> list[dict]:
    marker = re.compile(r"(?m)^(?:ГЛАВА\s+[IVXLCDM]+|[IVXLCDM]+\.?\s+.+|\d+[\.|\)]\s+.+|[а-я]\)\s+.+)$", re.IGNORECASE)
    blocks: list[dict] = []
    for item in pages:
        page = item["page"]
        text = item.get("text", "")
        if not text.strip():
            continue
        starts = [m.start() for m in marker.finditer(text)]
        if not starts:
            blocks.append({"page_start": page, "page_end": page, "text": text.strip()})
            continue
        starts.append(len(text))
        for i in range(len(starts) - 1):
            chunk = text[starts[i] : starts[i + 1]].strip()
            if chunk:
                blocks.append({"page_start": page, "page_end": page, "text": chunk})
    return blocks


def build_chunks(pages: list[dict], target_chars: int | None = None, overlap_chars: int | None = None) -> list[dict]:
    target_chars = target_chars or settings.chunk_target_chars
    overlap_chars = overlap_chars or settings.chunk_overlap_chars
    blocks = _split_blocks(pages)

    chunks: list[dict] = []
    current_chapter: str | None = None
    current_point: str | None = None
    i = 0

    while i < len(blocks):
        block = blocks[i]
        chapter, point, subpoint = _detect_section_path(block["text"], current_chapter, current_point)
        current_chapter, current_point = chapter, point

        text = block["text"]
        page_start = block["page_start"]
        page_end = block["page_end"]
        j = i + 1

        while len(text) < 800 and j < len(blocks):
            nxt = blocks[j]
            n_ch, n_pt, _ = _detect_section_path(nxt["text"], current_chapter, current_point)
            if n_ch != current_chapter and current_chapter is not None:
                break
            text = f"{text}\n\n{nxt['text']}"
            page_end = nxt["page_end"]
            current_chapter, current_point = n_ch, n_pt
            j += 1

        if len(text) > 1600:
            start = 0
            local_idx = 0
            while start < len(text):
                end = min(start + target_chars, len(text))
                fragment = text[start:end].strip()
                if fragment:
                    sp = []
                    if chapter:
                        sp.append(chapter)
                    if point:
                        sp.append(point)
                    if subpoint:
                        sp.append(subpoint)
                    section_path = " > ".join(sp)
                    chunks.append(
                        {
                            "chunk_id": f"chunk_{len(chunks):05d}_{local_idx}",
                            "page_start": page_start,
                            "page_end": page_end,
                            "section_path": section_path,
                            "text": fragment,
                        }
                    )
                if end >= len(text):
                    break
                start = max(0, end - overlap_chars)
                local_idx += 1
        else:
            sp = []
            if chapter:
                sp.append(chapter)
            if point:
                sp.append(point)
            if subpoint:
                sp.append(subpoint)
            section_path = " > ".join(sp)
            chunks.append(
                {
                    "chunk_id": f"chunk_{len(chunks):05d}",
                    "page_start": page_start,
                    "page_end": page_end,
                    "section_path": section_path,
                    "text": text.strip(),
                }
            )

        i = max(j, i + 1)

    return chunks


def write_chunks_jsonl(chunks: list[dict], path: str | Path | None = None) -> Path:
    out = Path(path or settings.chunks_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for chunk in chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")
    return out
