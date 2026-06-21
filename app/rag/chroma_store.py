# path: app/rag/chroma_store.py
from typing import Any, Dict, List

import chromadb
import httpx

from app.config.settings import settings

# Bind variable parameters directly from your global validated configuration layers
CHROMA_HOST = settings.vectorstores.chroma.host
CHROMA_PORT = settings.vectorstores.chroma.port
PREFIX = settings.vectorstores.chroma.collection_prefix
BATCH_SIZE = settings.vectorstores.chroma.upsert_batch_size
OLLAMA_URL = (
    settings.llm.providers.get("ollama", {}).base_url or "http://localhost:11434"
)

# 🎯 FIX: Instantiate a single reusable HttpClient connection pool at the module level
# This stops expensive, blocking sync TCP handshakes inside async graph execution nodes.
_chroma_client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)


def _resolve_collection_name(name: str) -> str:
    """Ensures collection strings are cleanly prefixed without duplication."""
    target = name.strip()
    return target if target.startswith(PREFIX) else f"{PREFIX}{target}"


def get_collection(name: str) -> Any:
    """Returns an active instance mapping to the local vector storage client thread."""
    # Multiplex over the singleton client reference cleanly
    return _chroma_client.get_or_create_collection(name=_resolve_collection_name(name))


async def embed_texts_batch(texts: List[str]) -> List[List[float]]:
    """Executes high-density vector transformations against the local Ollama service."""
    if not texts:
        return []

    # Direct extraction reads your exact configured embedding model structure cleanly
    model_id = getattr(settings.rag, "embedding_model", "nomic-embed-text")
    url = f"{OLLAMA_URL.rstrip('/')}/v1/embeddings"

    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
            resp = await client.post(url, json={"model": model_id, "input": texts})
            resp.raise_for_status()
            payload = resp.json()
            return [item["embedding"] for item in payload["data"]]
    except Exception as e:
        # Structured error logging ensures clear output in background execution dumps
        print(f"[CRITICAL RAG EMBEDDING FAILURE EXCEPTION]: {e}")
        raise RuntimeError(f"Ollama vector transformation failure: {e}") from e


def delete_documents(collection_name: str, where: Dict[str, Any]) -> None:
    """Deletes old metadata profiles from target clusters."""
    collection = get_collection(collection_name)
    collection.delete(where=where)


async def upsert_documents(
    collection_name: str,
    docs: List[str],
    ids: List[str],
    metadatas: List[Dict[str, Any]],
) -> None:
    """Upserts document segments concurrently into local database indices."""
    if not docs:
        return

    collection = get_collection(collection_name)

    # Process text chunks sequentially using array slice steps
    for i in range(0, len(docs), BATCH_SIZE):
        end_slice = i + BATCH_SIZE
        slice_docs = docs[i:end_slice]
        slice_ids = ids[i:end_slice]
        slice_metas = metadatas[i:end_slice]

        # Batch transformation call minimizes network layer round-trip delays
        embeddings = await embed_texts_batch(slice_docs)

        collection.upsert(
            documents=slice_docs,
            embeddings=embeddings,
            metadatas=slice_metas,
            ids=slice_ids,
        )


async def query_documents(
    collection_name: str, query: str, top_k: int = 6
) -> List[Dict[str, Any]]:
    """Queries local data structures and returns top vector matching results."""
    try:
        collection = get_collection(collection_name)
        query_embeddings = await embed_texts_batch([query])

        if not query_embeddings:
            return []

        results = collection.query(
            query_embeddings=[query_embeddings[0]], n_results=top_k
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
                # Concurrency safeguard matches float calculations inside research agents
                "distance": dists[idx] if (dists and idx < len(dists)) else 1.0,
                "score": dists[idx] if (dists and idx < len(dists)) else 1.0,
            }
            for idx in range(len(ids))
        ]
    except Exception as e:
        print(f"[RAG SEARCH INTERFACE EXCEPTION]: {e}")
        # Bubble up a structured message that subgraphs can log safely to their timelines
        raise RuntimeError(f"ChromaDB retrieval interface fault: {e}") from e
