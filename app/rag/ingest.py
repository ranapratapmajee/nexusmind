# path: app/rag/ingest.py
import hashlib
import os
import time
from typing import Optional

from pypdf import PdfReader

from app.config.settings import settings
from app.rag.chroma_store import delete_documents, upsert_documents
from app.rag.chunker import chunk_text_enriched  # Synchronize function link


def _calculate_sha256(file_path: str) -> str:
    """Generates unique file identity hash keys to track modifications."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _parse_pdf_text(file_path: str) -> Optional[str]:
    """Extracts raw text strings out of local binary PDF books."""
    try:
        reader = PdfReader(file_path)
        extracted_pages = [page.extract_text() or "" for page in reader.pages]
        full_text = "\n".join(extracted_pages).strip()
        return full_text if full_text else None
    except Exception as e:
        print(f"[PDF Extraction Parse Error Override] file: {file_path} | Log: {e}")
        return None


async def ingest_documents(directory: str) -> None:
    """
    Scans files, chunks documents, hashes changes, and updates database blocks.
    Fully integrated with global configuration schemas and tracking contexts.
    """
    collection_name = settings.vectorstores.collections.get(
        "chroma_collection", "knowledgebase"
    )
    chunk_size = settings.rag.chunk_size
    chunk_overlap = settings.rag.chunk_overlap

    if not os.path.isdir(directory):
        print(f"[Ingest Intercept]: Target pipeline path is missing: {directory}")
        return

    files = [
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if f.lower().endswith(".pdf")
    ]
    print(
        f"[Ingest Pipeline initialization] Scan complete. Found: {len(files)} target documents."
    )

    for idx, path in enumerate(files, start=1):
        start_time = time.perf_counter()
        file_name = os.path.basename(path)
        doc_hash = _calculate_sha256(path)

        raw_text = _parse_pdf_text(path)
        if not raw_text:
            print(f"├── ⚠️ [Skipping Empty or Damaged Content Frame]: {file_name}")
            continue

        # Clear previous records matching this hash identity to prevent duplicate storage updates
        delete_documents(collection_name=collection_name, where={"doc_hash": doc_hash})

        # Segment data chunks cleanly using our enriched layout structure mapper pass
        enriched_chunks = chunk_text_enriched(
            raw_text, chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )
        if not enriched_chunks:
            continue

        # Unpack split text segments and metadata context boundaries cleanly
        docs = [c["text"] for c in enriched_chunks]
        ids = [f"{doc_hash}-chunk-{c_idx}" for c_idx in range(len(enriched_chunks))]

        metadatas = [
            {
                "source_type": "offline_pdf",
                "file_name": file_name,
                "path": path,
                "doc_hash": doc_hash,
                "chunk_index": c_idx,
                # Store the discovered document sub-header directly into metadata parameters
                "context_marker": enriched_chunks[c_idx]["context_marker"],
            }
            for c_idx in range(len(enriched_chunks))
        ]

        # Vectorize and upsert into the active collection
        await upsert_documents(
            collection_name=collection_name, docs=docs, ids=ids, metadatas=metadatas
        )

        elapsed = time.perf_counter() - start_time
        print(
            f"├── ✅ [Processed {idx}/{len(files)}]: {file_name} | Chunks: {len(docs)} | Time: {elapsed:.2f}s"
        )
