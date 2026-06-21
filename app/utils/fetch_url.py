# path: app/utils/fetch_url.py
import httpx


def _clean_text(text: str) -> str:
    """Sub-millisecond regex white-space compressor."""
    return " ".join((text or "").split()).strip()


async def fetch_url_text(url: str, max_chars: int = 5000) -> str:
    """
    Fetches a raw target web page domain and extracts stripped content text.
    Uses high-speed Trafilatura structures with an automated BeautifulSoup fallback.
    """
    if not url or not url.strip():
        return ""

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }

    try:
        async with httpx.AsyncClient(
            timeout=15.0, headers=headers, follow_redirects=True
        ) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            html = resp.text
    except Exception as e:
        print(f"[Core Web Scraper Failure Exception] Address: {url} | Log: {e}")
        return ""

    # Attempt high-performance extraction via trafilatura first
    try:
        import trafilatura

        extracted = trafilatura.extract(html) or ""
    except Exception:
        extracted = ""

    # Native BeautifulSoup fallback if trafilatura fails
    if not extracted:
        try:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(html, "html.parser")

            # Decompose heavy visual layout container artifacts
            for tag in soup(["script", "style", "noscript", "header", "footer", "svg"]):
                tag.decompose()
            extracted = soup.get_text(" ", strip=True)
        except Exception:
            return ""

    clean_payload = _clean_text(extracted)
    return (
        f"{clean_payload[:max_chars]}..."
        if len(clean_payload) > max_chars
        else clean_payload
    )
