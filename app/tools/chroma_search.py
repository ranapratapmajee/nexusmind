# path: app/tools/chroma_search.py

import asyncio
import logging
from typing import Any, Dict, List, Tuple
import chromadb
from app.settings import settings
from app.rag_storage import get_embeddings  # Unified vectorizer helper

logger = logging.getLogger("nexusmind.chroma_search")

# Persistent module-level connection reuse pool
try:
    _chroma_client = chromadb.HttpClient(host=settings.CHROMA_HOST, port=settings.CHROMA_PORT)
except Exception as e:
    logger.error(f"ChromaDB standalone tool connection failed: {e}")
    _chroma_client = None

VECTOR_DISTANCE_THRESHOLD = 0.65


async def fetch_single_query(query: str, collection: Any) -> List[Dict[str, Any]]:
    """Transforms a single query text to vectors and pulls top-k semantic matches from ChromaDB."""
    try:
        query_embeddings = await get_embeddings([query])
        if not query_embeddings:
            return []

        results = collection.query(
            query_embeddings=[query_embeddings[0]], 
            n_results=settings.top_k
        )

        ids = results.get("ids", [[]])[0]
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        dists = results.get("distances", [[]])[0]

        return [
            {
                "id": ids[idx],
                "document": docs[idx],
                "metadata": metas[idx] if metas else {},
                "distance": dists[idx] if (dists and idx < len(dists)) else 1.0,
                "score": dists[idx] if (dists and idx < len(dists)) else 1.0,
            }
            for idx in range(len(ids))
        ]
    except Exception as e:
        logger.error(f"Error querying local vector base for chunk context: {e}")
        return []


async def search_local_vectorbase(expanded_queries: List[str]) -> Tuple[List[Dict[str, Any]], float, bool]:
    """
    Orchestrates concurrent multi-query database lookups.
    Flattens, deduplicates results by text identity, and determines confidence.
    """
    if _chroma_client is None:
        logger.error("Aborting search execution pass: ChromaDB server client is offline.")
        return [], 1.0, False

    collection = _chroma_client.get_or_create_collection(name=settings.CHROMA_COLLECTION)

    # Dispatch flat function executions concurrently across variations
    tasks = [fetch_single_query(q, collection) for q in expanded_queries]
    batch_results = await asyncio.gather(*tasks)

    seen_bodies = set()
    unique_chunks = []
    best_distance = 1.0

    # Cross-query flattening and deduplication pass
    for result_list in batch_results:
        for chunk in result_list:
            body = chunk.get("document", "").strip()
            if body not in seen_bodies:
                seen_bodies.add(body)
                unique_chunks.append(chunk)
                
                # Update directional HNSW match score
                score = chunk.get("score") or chunk.get("distance")
                if score is not None and score < best_distance:
                    best_distance = score

    has_high_confidence = best_distance <= VECTOR_DISTANCE_THRESHOLD
    return unique_chunks[:settings.top_k], best_distance, has_high_confidence