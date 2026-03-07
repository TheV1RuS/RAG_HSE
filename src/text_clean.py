from __future__ import annotations

import re
from collections import Counter


def _normalize_newlines(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text


def _fix_hyphenation(text: str) -> str:
    return re.sub(r"([А-Яа-яA-Za-z])-\n([А-Яа-яA-Za-z])", r"\1\2", text)


def _remove_polluting_page_lines(line: str) -> str:
    if re.fullmatch(r"\s*\d+\s*", line):
        return ""
    return line


def clean_pages(raw_pages: list[dict]) -> list[dict]:
    split_pages: list[tuple[int, list[str]]] = []
    edge_lines: list[str] = []

    for item in raw_pages:
        page = int(item["page"])
        text = _normalize_newlines(str(item.get("text", "")))
        text = _fix_hyphenation(text)
        lines = [ln.strip() for ln in text.split("\n")]
        lines = [_remove_polluting_page_lines(ln) for ln in lines]
        lines = [ln for ln in lines if ln != ""]
        split_pages.append((page, lines))

        if lines:
            edge_lines.extend(lines[:2])
            edge_lines.extend(lines[-2:])

    counts = Counter(edge_lines)
    repeated = {line for line, cnt in counts.items() if cnt >= max(3, len(split_pages) // 4)}

    cleaned: list[dict] = []
    for page, lines in split_pages:
        kept = [ln for ln in lines if ln not in repeated]
        reconstructed = "\n".join(kept)
        reconstructed = re.sub(r"(?<!\n)\n(?!\n)", " ", reconstructed)
        reconstructed = re.sub(r"\n{3,}", "\n\n", reconstructed)
        reconstructed = re.sub(r"[ \t]+", " ", reconstructed).strip()
        cleaned.append({"page": page, "text": reconstructed})

    return cleaned
