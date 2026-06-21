# path: app/utils/web_search.py
from typing import Any, Dict, List

import httpx
from bs4 import BeautifulSoup

DUCKDUCKGO_HTML_ENDPOINT = "https://html.duckduckgo.com/html/"


def _clean_text(value: str) -> str:
    return " ".join((value or "").split()).strip()


def web_search(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Executes a high-density, zero-cost search pass against public search vectors.
    Parses structural result blocks into clean metadata dictionary records.
    """
    if not query or not query.strip():
        return []

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }

    try:
        with httpx.Client(
            timeout=10.0, headers=headers, follow_redirects=True
        ) as client:
            resp = client.post(DUCKDUCKGO_HTML_ENDPOINT, data={"q": query})
            resp.raise_for_status()
            html = resp.text
    except Exception as e:
        print(f"[Core Web Search Failure Exception] Query: {query} | Log: {e}")
        return []

    results: List[Dict[str, Any]] = []
    soup = BeautifulSoup(html, "html.parser")

    for result in soup.select(".result"):
        if len(results) >= max_results:
            break

        link = result.select_one(".result__title a")
        snippet = result.select_one(".result__snippet")

        title = _clean_text(link.get_text(" ", strip=True) if link else "")
        href = _clean_text(link.get("href", "") if link else "")
        body = _clean_text(snippet.get_text(" ", strip=True) if snippet else "")

        if not title and not href:
            continue

        results.append({"title": title, "href": href, "body": body})

    return results
