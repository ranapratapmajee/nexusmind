# path: app/rag/chunker.py
import re
from typing import Any, Dict, List

from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunk_text_enriched(
    text: str, chunk_size: int = 800, chunk_overlap: int = 200
) -> List[Dict[str, Any]]:
    """
    Splits long plaintext streams into clean, overlapping character matrices.
    Dynamically extracts structural headers to enrich metadata tracing.
    """
    if not text or chunk_size <= 0:
        return []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        is_separator_regex=False,
    )

    raw_chunks = splitter.split_text(text)
    enriched_chunks = []

    # Simple regex pattern to capture structural indicators like Chapter names or structural headers
    header_pattern = re.compile(
        r"(?:chapter\s+\d+|section\s+\d+|[\u25A0\u25C6\u2022]\s+[A-Z][A-Za-z\s]{3,30})",
        re.IGNORECASE,
    )
    current_context = "General Context Layer"

    for chunk in raw_chunks:
        clean_chunk = chunk.strip()
        if not clean_chunk:
            continue

        # Scan chunk buffer for structural markers to update regional context tracking
        header_match = header_pattern.search(clean_chunk)
        if header_match:
            # Extract the first line containing the structural match as context marker
            matched_line = clean_chunk.split("\n")[0].strip()
            if len(matched_line) < 60:
                current_context = matched_line

        enriched_chunks.append({"text": clean_chunk, "context_marker": current_context})

    return enriched_chunks
