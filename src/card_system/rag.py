"""Lightweight RAG helpers for card generation.

The existing project includes Chroma examples, but this module keeps keyword
retrieval as the always-available fallback so the card agent can run without a
prepared vector database.
"""

import math
import re
from collections import Counter
from typing import Any


def split_text(text: str, chunk_size: int = 800, chunk_overlap: int = 100) -> list[str]:
    """Split text into overlapping chunks."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")
    if chunk_overlap < 0:
        raise ValueError("chunk_overlap must be greater than or equal to 0")
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    normalized = re.sub(r"\s+", " ", text).strip()
    if not normalized:
        return []

    chunks: list[str] = []
    start = 0
    while start < len(normalized):
        end = min(start + chunk_size, len(normalized))
        chunks.append(normalized[start:end].strip())
        if end == len(normalized):
            break
        start = end - chunk_overlap
    return chunks


def build_document_chunks(
    text: str,
    document_id: str = "default-document",
    chunk_size: int = 800,
    chunk_overlap: int = 100,
) -> list[dict[str, Any]]:
    """Build chunk dictionaries suitable for storage or retrieval."""
    return [
        {
            "id": f"{document_id}-chunk-{index}",
            "document_id": document_id,
            "chunk_index": index,
            "content": chunk,
            "metadata": {"retriever": "keyword_fallback"},
        }
        for index, chunk in enumerate(split_text(text, chunk_size, chunk_overlap))
    ]


def retrieve_relevant_chunks(
    query: str,
    chunks: list[dict[str, Any]],
    top_k: int = 5,
) -> list[dict[str, Any]]:
    """Retrieve relevant chunks with a keyword scoring fallback."""
    if top_k <= 0 or not chunks:
        return []

    query_terms = _tokenize(query)
    if not query_terms:
        return chunks[:top_k]

    scored = []
    for chunk in chunks:
        content = str(chunk.get("content", ""))
        score = _keyword_score(query_terms, _tokenize(content))
        if score > 0:
            scored.append((score, chunk))

    if not scored:
        return chunks[:top_k]

    scored.sort(key=lambda item: item[0], reverse=True)
    return [chunk for _, chunk in scored[:top_k]]


def build_rag_context(
    query: str,
    text: str,
    document_id: str = "default-document",
    chunk_size: int = 800,
    chunk_overlap: int = 100,
    top_k: int = 5,
) -> tuple[str, list[dict[str, Any]]]:
    """Build context text from the most relevant chunks."""
    chunks = build_document_chunks(text, document_id, chunk_size, chunk_overlap)
    relevant_chunks = retrieve_relevant_chunks(query, chunks, top_k)
    context = "\n\n".join(
        f"[Chunk {chunk['chunk_index']}]\n{chunk['content']}" for chunk in relevant_chunks
    )
    return context, chunks


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[\w\u4e00-\u9fff]+", text.lower())


def _keyword_score(query_terms: list[str], chunk_terms: list[str]) -> float:
    counts = Counter(chunk_terms)
    length_norm = math.sqrt(max(len(chunk_terms), 1))
    return sum(counts[term] for term in query_terms) / length_norm

