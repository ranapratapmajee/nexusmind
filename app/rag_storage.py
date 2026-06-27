# path: app/rag_storage.py

import os
import hashlib
import logging
import asyncio
from typing import List
from pdfminer.high_level import extract_text
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from app.settings import settings

logger = logging.getLogger("nexusmind.rag_storage")

# =========================================================================
# 📝 CENTRALIZED HELPER UTILITIES
# =========================================================================

def get_file_hash(file_path: str) -> str:
    """Generates a fast sha256 hash to track file updates unique identifiers."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

def get_vector_store() -> Chroma:
    """Mounts unified connection directly into ChromaDB using LangChain types."""
    embeddings = OllamaEmbeddings(
        base_url=settings.OLLAMA_BASE_URL,
        model=settings.OLLAMA_EMBED_MODEL
    )
    return Chroma(
        collection_name=settings.CHROMA_COLLECTION,
        embedding_function=embeddings,
        persist_directory="./chroma-data"
    )

# =========================================================================
# 📥 PIPELINE INGESTION ENTRY POINT
# =========================================================================

async def run_ingest(target_path: str) -> None:
    """Processes file targets into the local ChromaDB collection container.
    Combines LangChain's data types with ultra-fast concurrent async dispatch loops.
    """
    if os.path.isdir(target_path):
        files = [os.path.join(target_path, f) for f in os.listdir(target_path) if f.lower().endswith(".pdf")]
    elif os.path.isfile(target_path) and target_path.lower().endswith(".pdf"):
        files = [target_path]
    else:
        logger.error(f"Ingest aborted: Target reference is not a valid PDF or folder: '{target_path}'")
        return

    logger.info(f"💾 RAG High-Performance Worker started. Ingesting targets count: {len(files)}")
    
    vector_db = get_vector_store()
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)

    for idx, path in enumerate(files, start=1):
        file_name = os.path.basename(path)
        doc_hash = get_file_hash(path)

        try:
            text = extract_text(path).strip()
            if not text:
                logger.warning(f"  [{idx}/{len(files)}] Skipping empty document: {file_name}")
                continue
                
            # Clear existing data duplicates natively
            vector_db.delete(where={"doc_hash": doc_hash})

            # Generate structured LangChain documents matching the schema blueprint
            documents = splitter.create_documents(
                texts=[text],
                metadatas=[{
                    "source_type": "offline_pdf",
                    "file_name": file_name,
                    "path": path,
                    "doc_hash": doc_hash
                }]
            )

            # 🟢 HIGH-PERFORMANCE PATCH: Concurrent Batch Splicing Loop
            # We slice the documents list and dispatch them concurrently into ChromaDB [1, 2]
            batch_size = 100
            async_tasks = []
            
            for i in range(0, len(documents), batch_size):
                batch_slice = documents[i : i + batch_size]
                # Enqueue the asynchronous generation task using the native async connector [1, 2]
                async_tasks.append(vector_db.aadd_documents(batch_slice))
            
            logger.info(f"  ⚡ Concurrently dispatching {len(async_tasks)} embedding batches to local GPU/CPU queues...")
            
            # Fire all async embedding worker tasks at once across active channels [1, 2]
            await asyncio.gather(*async_tasks)
            
            logger.info(f"  ✅ Complete [{idx}/{len(files)}] Loaded: '{file_name}' ({len(documents)} chunks)")

        except Exception as doc_err:
            logger.error(f"Failed to process asset context payload [{file_name}]: {doc_err}")
