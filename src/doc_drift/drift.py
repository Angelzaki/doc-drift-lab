from __future__ import annotations

import json
import math
import re
from collections import Counter
from pathlib import Path

TOKEN = re.compile(r"[a-zA-ZáéíóúñÁÉÍÓÚÑ0-9]+")

QUERIES = [
    ("¿Cuál es el descuento máximo en A1?", "politica_a1"),
    ("¿A2 exige MFA?", "requisitos_a2"),
    ("¿Cuál es el límite comercial?", "limite_comercial"),
]


def tokenize(text: str) -> list[str]:
    return [t.lower() for t in TOKEN.findall(text)]


def load_chunks(docs_dir: Path) -> list[dict]:
    chunks = []
    for path in sorted(docs_dir.glob("*.txt")):
        text = " ".join(path.read_text(encoding="utf-8").split())
        chunks.append({"doc_id": path.stem, "text": text})
    return chunks


def retrieve(chunks: list[dict], query: str, k: int = 3) -> list[dict]:
    tokenized = [tokenize(c["text"]) for c in chunks]
    df: Counter[str] = Counter()
    for tokens in tokenized:
        df.update(set(tokens))
    n = len(tokenized) or 1
    idf = {t: math.log((n + 1) / (f + 1)) + 1.0 for t, f in df.items()}

    def vec(tokens: list[str]) -> dict[str, float]:
        tf = Counter(tokens)
        length = len(tokens) or 1
        return {t: (c / length) * idf.get(t, 0.0) for t, c in tf.items()}

    def cosine(a: dict[str, float], b: dict[str, float]) -> float:
        keys = set(a) | set(b)
        if not keys:
            return 0.0
        dot = sum(a.get(x, 0.0) * b.get(x, 0.0) for x in keys)
        na = math.sqrt(sum(v * v for v in a.values()) or 1)
        nb = math.sqrt(sum(v * v for v in b.values()) or 1)
        return dot / (na * nb)

    q = vec(tokenize(query))
    ranked = sorted(
        ({"doc_id": c["doc_id"], "score": cosine(q, vec(t))} for c, t in zip(chunks, tokenized)),
        key=lambda x: x["score"],
        reverse=True,
    )
    return ranked[:k]


def eval_corpus(docs_dir: Path) -> dict:
    chunks = load_chunks(docs_dir)
    details = []
    hits = 0
    for query, expected in QUERIES:
        if expected not in {c["doc_id"] for c in chunks}:
            details.append({"query": query, "expected": expected, "ok": False, "reason": "missing_doc"})
            continue
        top = retrieve(chunks, query)
        ok = any(r["doc_id"] == expected for r in top)
        hits += int(ok)
        details.append(
            {
                "query": query,
                "expected": expected,
                "retrieved": [r["doc_id"] for r in top],
                "ok": ok,
            }
        )
    return {
        "docs": len({c["doc_id"] for c in chunks}),
        "chunks": len(chunks),
        "hit_rate": round(hits / len(QUERIES), 4),
        "hits": hits,
        "total": len(QUERIES),
        "details": details,
    }


def compare(docs_a: Path, docs_b: Path) -> dict:
    a = eval_corpus(docs_a)
    b = eval_corpus(docs_b)
    delta = round(b["hit_rate"] - a["hit_rate"], 4)
    regressions = []
    by_q_a = {d["query"]: d for d in a["details"]}
    for item in b["details"]:
        prev = by_q_a.get(item["query"])
        if prev and prev.get("ok") and not item.get("ok"):
            regressions.append(item["query"])
    return {
        "scenario_a": a,
        "scenario_b": b,
        "delta": delta,
        "regressions": regressions,
        "ok": len(regressions) == 0,
        "score": b["hit_rate"],
    }
