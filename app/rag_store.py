import json
import re
from functools import lru_cache
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "rag_data"
SAFE_PATH = DATA_DIR / "demo_clean_chunks.json"
RAW_PATH = DATA_DIR / "demo_raw_cases.json"

STOPWORDS = {
    "a", "as", "o", "os", "de", "da", "do", "das", "dos", "e", "em", "no", "na",
    "nos", "nas", "um", "uma", "para", "por", "com", "que", "qual", "quais", "me",
    "mostre", "liste", "diga", "sobre", "caso", "cliente", "parte", "texto", "completo"
}


def _normalize(text: str) -> list[str]:
    text = text.lower()
    text = re.sub(r"[^a-z0-9áàâãéèêíìîóòôõúùûç\s-]", " ", text)
    tokens = [t for t in text.split() if t and t not in STOPWORDS]
    return tokens


@lru_cache(maxsize=1)
def load_safe_chunks() -> list[dict]:
    return json.loads(SAFE_PATH.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def load_raw_cases() -> list[dict]:
    return json.loads(RAW_PATH.read_text(encoding="utf-8"))


def _score(query: str, text: str) -> int:
    q_tokens = set(_normalize(query))
    t_tokens = set(_normalize(text))
    return len(q_tokens.intersection(t_tokens))


def retrieve_safe_context(query: str, top_k: int = 3) -> str:
    chunks = load_safe_chunks()
    ranked = sorted(
        chunks,
        key=lambda item: _score(query, item.get("content", "") + " " + " ".join(item.get("tags", []))),
        reverse=True,
    )
    selected = [item for item in ranked if _score(query, item.get("content", "")) > 0][:top_k]

    if not selected:
        selected = chunks[:top_k]

    parts = []
    for item in selected:
        parts.append(
            f"[Fonte {item['chunk_id']} | {item['case_id']} | {item['title']}]\n{item['content']}"
        )
    return "\n\n".join(parts)


def retrieve_unsafe_context(query: str, top_k: int = 1) -> str:
    cases = load_raw_cases()
    ranked = sorted(
        cases,
        key=lambda item: _score(
            query,
            json.dumps(item, ensure_ascii=False)
        ),
        reverse=True,
    )
    selected = ranked[:top_k] if ranked else []

    parts = []
    for item in selected:
        parts.append(json.dumps(item, ensure_ascii=False, indent=2))
    return "\n\n".join(parts)
