# path: app/tools/chroma_search.py

import asyncio
import logging
from app.settings import settings
from typing import Any, Dict, List, Tuple
from app.rag_storage import get_vector_store

logger = logging.getLogger("nexusmind.chroma_search")

VECTOR_DISTANCE_THRESHOLD = 0.65

async def fetch_single_query(query: str, vector_db: Any) -> List[Dict[str, Any]]:
    """🟢 NATIVE RETRIEVAL STEP: Leverages LangChain to handle similarity parsing.
    Automatically takes care of query text vectorization and returns distance scores.
    """
    try:
        # Fetch matching chunks with their relevance scores (1.0 - score = distance)
        # We grab top-k config via a standard default fallback block
        top_k = getattr(settings, "top_k", 4)
        raw_hits = await vector_db.asimilarity_search_with_relevance_scores(query, k=top_k)
        
        return [
            {
                "document": doc.page_content,
                "metadata": doc.metadata,
                "distance": 1.0 - score
            }
            for doc, score in raw_hits
        ]
    except Exception as e:
        logger.error(f"Error querying local vector base via LangChain adapter: {e}")
        return []

async def search_local_vectorbase(expanded_queries: List[str]) -> Tuple[List[Dict[str, Any]], float, bool]:
    """Orchestrates concurrent multi-query database lookups.
    Flattens raw response vectors, deduplicates content duplicates, and checks certainty.
    """
    try:
        # Get the unified, pre-configured LangChain vector store client block
        vector_db = get_vector_store()
    except Exception as err:
        logger.error(f"Aborting search pass: ChromaDB connection dropped: {err}")
        return [], 1.0, False

    # 🟢 CONCURRENT DISPATCH: Fires all query search tasks across thread channels simultaneously
    tasks = [fetch_single_query(q, vector_db) for q in expanded_queries]
    batch_results = await asyncio.gather(*tasks)

    seen_bodies = set()
    unique_chunks = []
    best_distance = 1.0

    # Cross-query flattening and string deduplication loop
    for result_list in batch_results:
        for chunk in result_list:
            body = chunk.get("document", "").strip()
            if body not in seen_bodies:
                seen_bodies.add(body)
                unique_chunks.append(chunk)
                
                # Update absolute lowest distance track score metric
                dist = chunk.get("distance", 1.0)
                if dist < best_distance:
                    best_distance = dist

    # Evaluate grounding status confidence based on our distance barrier ceiling limit
    has_high_confidence = best_distance <= VECTOR_DISTANCE_THRESHOLD
    top_k = getattr(settings, "top_k", 4)
    
    return unique_chunks[:top_k], best_distance, has_high_confidence
