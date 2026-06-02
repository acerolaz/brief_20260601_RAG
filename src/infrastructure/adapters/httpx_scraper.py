"""httpx scraper adapter — implements ScraperPort for real-time URL scraping."""
from __future__ import annotations

import httpx
from bs4 import BeautifulSoup

from src.domain.exceptions import ScrapingError


class HttpxScraperAdapter:
    """Driven adapter: fetches and parses text content from a URL using httpx + BeautifulSoup."""

    def __init__(self, timeout: int = 15) -> None:
        self._timeout = timeout

    async def scrape(self, url: str) -> str:
        """Fetch *url* and return its main text content.

        Raises:
            ScrapingError: On network errors, non-200 responses, or parse failures.
        """
        try:
            async with httpx.AsyncClient(timeout=self._timeout, follow_redirects=True) as client:
                response = await client.get(url)
                response.raise_for_status()
        except httpx.HTTPError as exc:
            raise ScrapingError(f"HTTP error while scraping {url!r}: {exc}") from exc

        try:
            soup = BeautifulSoup(response.text, "html.parser")
            # Remove script / style noise
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()
            return soup.get_text(separator="\n", strip=True)
        except Exception as exc:
            raise ScrapingError(f"Failed to parse HTML from {url!r}: {exc}") from exc

