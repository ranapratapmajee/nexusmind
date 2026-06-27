# path: app/tools/web_search.py

import asyncio
from typing import Dict, List
import httpx
from bs4 import BeautifulSoup

DUCKDUCKGO_HTML_ENDPOINT = "https://html.duckduckgo.com/html/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

def _compress_whitespace(value: str) -> str:
    """Sub-millisecond regex-free white-space compressor."""
    return " ".join((value or "").split()).strip()


def _execute_sync_ddg_search(query: str, max_results: int) -> List[Dict[str, str]]:
    """Performs raw parsing against public DuckDuckGo HTML vector pools."""
    if not query or not query.strip():
        return []
    try:
        with httpx.Client(timeout=10.0, headers=HEADERS, follow_redirects=True) as client:
            resp = client.post(DUCKDUCKGO_HTML_ENDPOINT, data={"q": query})
            resp.raise_for_status()
            html = resp.text
    except Exception:
        return []

    results = []
    soup = BeautifulSoup(html, "html.parser")
    for result in soup.select(".result"):
        if len(results) >= max_results:
            break
        link = result.select_one(".result__title a")
        snippet = result.select_one(".result__snippet")

        title = _compress_whitespace(link.get_text(" ", strip=True) if link else "")
        href = _compress_whitespace(link.get("href", "") if link else "")
        body = _compress_whitespace(snippet.get_text(" ", strip=True) if snippet else "")

        if href:
            results.append({"title": title, "href": href, "body": body})
    return results


async def _async_scrape_page_text(url: str, fallback_text: str) -> str:
    """Downloads raw web document strings and extracts clean core text contents."""
    try:
        async with httpx.AsyncClient(timeout=10.0, headers=HEADERS, follow_redirects=True) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            html = resp.text
    except Exception:
        return fallback_text

    # Route A: High-performance extraction via trafilatura text mining engine
    try:
        import trafilatura
        extracted = trafilatura.extract(html) or ""
    except Exception:
        extracted = ""

    # Route B: Basic BeautifulSoup fallbacks if trafilatura missed
    if not extracted:
        try:
            soup = BeautifulSoup(html, "html.parser")
            for tag in soup(["script", "style", "noscript", "header", "footer", "svg"]):
                tag.decompose()
            extracted = soup.get_text(" ", strip=True)
        except Exception:
            return fallback_text

    return _compress_whitespace(extracted)


async def search_live_web(expanded_queries: List[str], max_links_per_query: int = 3) -> List[Dict[str, str]]:
    """Runs concurrent search queries off-thread and handles parallel full-page extractions."""
    
    async def process_single_query(query: str) -> List[Dict[str, str]]:
        query_items = []
        try:
            # Shift synchronous network loop scraper off the primary async event thread safely
            loop = asyncio.get_running_loop()
            hits = await loop.run_in_executor(None, lambda: _execute_sync_ddg_search(query, max_links_per_query))
            
            # Fire concurrent page downloads for links hit
            scrape_tasks = [_async_scrape_page_text(h["href"], h["body"]) for h in hits[:max_links_per_query]]
            scraped_bodies = await asyncio.gather(*scrape_tasks)
            
            for hit, body_text in zip(hits[:max_links_per_query], scraped_bodies):
                final_content = body_text if body_text.strip() else hit["body"]
                query_items.append({
                    "title": hit["title"],
                    "url": hit["href"],
                    "content": final_content[:2000]  # Safe token budget constraint ceiling
                })
        except Exception:
            pass
        return query_items

    # Core execution sweep over query variations concurrently
    tasks = [process_single_query(q) for q in expanded_queries]
    batch_web_results = await asyncio.gather(*tasks)

    # Global multi-query deduplication loop by clean URL string identity
    seen_urls = set()
    unique_web_sources = []
    
    for query_list in batch_web_results:
        for item in query_list:
            if item["url"] not in seen_urls:
                seen_urls.add(item["url"])
                unique_web_sources.append(item)

    return unique_web_sources[:3]