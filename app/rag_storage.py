# path: app/rag_storage.py

import re
import os
import time
import hashlib
import logging
import httpx
import asyncio
import chromadb
from typing import Any, Dict, List, Optional
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.settings import settings

logger = logging.getLogger("nexusmind.rag_storage")

try:
    _chroma_client = chromadb.HttpClient(host=settings.CHROMA_HOST, port=settings.CHROMA_PORT)
except Exception as e:
    logger.error(f"ChromaDB client offline: {e}")
    _chroma_client = None

# =========================================================================
# 🧼 1. PARSING & CHUNKING
# =========================================================================

def get_file_hash(file_path: str) -> str:
    """Generates a fast sha256 hash to track file updates unique identifiers."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def extract_pdf_text(file_path: str) -> Optional[str]:
    """Extracts all text pages cleanly from a target PDF file."""
    try:
        reader = PdfReader(file_path)
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages).strip() or None
    except Exception as e:
        logger.error(f"Error reading PDF {file_path}: {e}")
        return None


def split_text(text: str) -> List[Dict[str, Any]]:
    """Splits text into chunks and tracks active section headers for context."""
    if not text:
        return []

    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=200)
    raw_chunks = splitter.split_text(text)
    
    enriched_chunks = []
    header_regex = re.compile(r"(?:chapter\s+\d+|section\s+\d+|[\u25A0\u25C6\u2022]\s+[A-Z][A-Za-z\s]{3,30})", re.IGNORECASE)
    current_header = "General Context Layer"

    for chunk in raw_chunks:
        clean_chunk = chunk.strip()
        if not clean_chunk:
            continue

        match = header_regex.search(clean_chunk)
        if match:
            first_line = clean_chunk.split("\n")[0].strip()
            if len(first_line) < 60:
                current_header = first_line

        enriched_chunks.append({"text": clean_chunk, "header": current_header})

    return enriched_chunks

# =========================================================================
# 🚀 2. VECTOR GENERATION & EMBEDDINGS
# =========================================================================

async def get_embeddings(texts: List[str]) -> List[List[float]]:
    """Calls local Ollama service to generate batch embedding vectors."""
    if not texts:
        return []

    url = f"{settings.OLLAMA_BASE_URL.rstrip('/')}/v1/embeddings"
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(url, json={"model": "nomic-embed-text", "input": texts})
            resp.raise_for_status()
            return [item["embedding"] for item in resp.json()["data"]]
    except Exception as e:
        logger.critical(f"Ollama vector generation failed: {e}")
        raise RuntimeError(f"Embedding failure: {e}")

# =========================================================================
# 📥 3. PIPELINE INGESTION ENTRY POINT
# =========================================================================

async def run_ingest(target_path: str) -> None:
    """
    Processes file targets into the local ChromaDB collection container.
    Natively accepts a specific filename path string OR scans an entire directory folder.
    """
    if _chroma_client is None:
        logger.error("Ingest aborted: ChromaDB client container connection dropped.")
        return

    # Intelligently adapt if input is a directory scan or a single background file target
    if os.path.isdir(target_path):
        files = [os.path.join(target_path, f) for f in os.listdir(target_path) if f.lower().endswith(".pdf")]
    elif os.path.isfile(target_path) and target_path.lower().endswith(".pdf"):
        files = [target_path]
    else:
        logger.error(f"Ingest aborted: Target reference is not a valid PDF entity or folder: '{target_path}'")
        return

    logger.info(f"💾 RAG Compute Worker started. Ingesting targets count: {len(files)}")
    collection = _chroma_client.get_or_create_collection(name=settings.CHROMA_COLLECTION)

    for idx, path in enumerate(files, start=1):
        start_time = time.perf_counter()
        file_name = os.path.basename(path)
        doc_hash = get_file_hash(path)

        text = extract_pdf_text(path)
        if not text:
            logger.warning(f"  [{idx}/{len(files)}] Skipping broken document block: {file_name}")
            continue

        # Evict prior chunk registrations matching this specific hash footprint to avoid duplicate collisions
        collection.delete(where={"doc_hash": doc_hash})

        chunks = split_text(text)
        if not chunks:
            continue

        docs = [c["text"] for c in chunks]
        ids = [f"{doc_hash}-chunk-{c_idx}" for c_idx in range(len(chunks))]
        metadatas = [
            {
                "source_type": "offline_pdf",
                "file_name": file_name,
                "path": path,
                "doc_hash": doc_hash,
                "chunk_index": c_idx,
                "context_marker": chunks[c_idx]["header"],
            }
            for c_idx in range(len(chunks))
        ]

        # Pre-calculate windows and dispatch embedding tasks concurrently
        batch_size = 100
        tasks = []
        bounds = []
        
        for i in range(0, len(docs), batch_size):
            end = i + batch_size
            bounds.append((i, end))
            tasks.append(get_embeddings(docs[i:end]))
            
        logger.info(f"  ⚡ Computing {len(tasks)} embedding batches concurrently...")
        computed_embeddings_groups = await asyncio.gather(*tasks)

        # Upsert responses back to the local database container
        for index, (start_bound, end_bound) in enumerate(bounds):
            slice_docs = docs[start_bound:end_bound]
            slice_embeddings = computed_embeddings_groups[index]
            
            collection.upsert(
                documents=slice_docs,
                embeddings=slice_embeddings,
                metadatas=metadatas[start_bound:end_bound],
                ids=ids[start_bound:end_bound]
            )

        elapsed = time.perf_counter() - start_time
        logger.info(f"  ✅ Complete [{idx}/{len(files)}] Loaded: '{file_name}' ({len(docs)} chunks) in {elapsed:.2f}s")