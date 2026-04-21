import asyncio
import re
from typing import Any
from urllib.parse import urlparse

import httpx

from server.config import SERPAPI_KEY, SERP_CONCURRENCY

# serper.dev — Google-backed search API, cheaper than serpapi.com.
SERP_ENDPOINT = "https://google.serper.dev/search"

_GL_HINTS = {
    "germany": "de", "deutschland": "de",
    "usa": "us", "united states": "us", "america": "us",
    "uk": "uk", "britain": "uk", "england": "uk",
    "france": "fr",
    "japan": "jp",
    "china": "cn",
    "taiwan": "tw",
    "korea": "kr", "south korea": "kr",
    "india": "in",
    "malaysia": "my",
    "singapore": "sg",
    "indonesia": "id",
    "thailand": "th",
    "vietnam": "vn",
    "netherlands": "nl",
    "italy": "it",
    "spain": "es",
    "canada": "ca",
    "australia": "au",
    "brazil": "br",
}

_BLOCKED_DOMAINS = {
    # Social / forum
    "wikipedia.org", "youtube.com", "facebook.com", "twitter.com", "x.com",
    "reddit.com", "quora.com", "pinterest.com", "instagram.com", "tiktok.com",
    # Marketplaces / jobs
    "amazon.com", "ebay.com", "indeed.com", "glassdoor.com", "shopee.com.my",
    "lazada.com.my", "lazada.com", "alibaba.com", "aliexpress.com",
    # Business directories / aggregators that pollute candidate lists
    "ensun.io", "trademo.com", "f6s.com", "owler.com", "zoominfo.com",
    "crunchbase.com", "rocketreach.co", "apollo.io", "signalhire.com",
    "europages.com", "kompass.com", "made-in-china.com", "indiamart.com",
    "tradewheel.com", "go4worldbusiness.com", "exportersindia.com",
    "panjiva.com", "importyeti.com",
    # Market-research / news that the classifier shouldn't treat as companies
    "sphericalinsights.com", "grandviewresearch.com", "marketsandmarkets.com",
    "mordorintelligence.com", "fortunebusinessinsights.com",
    "globenewswire.com", "prnewswire.com", "businesswire.com",
}

# Title patterns that indicate the result isn't a single company (market
# research reports, industry overviews, regional clusters, listicles).
_NON_COMPANY_TITLE = re.compile(
    r"\b(Market|Industry\s+(Report|Overview|Analysis)|Report|Overview|"
    r"Top\s+\d+|List\s+of|Cluster|Ecosystem|Forecast|Outlook|Statistics|"
    r"Directory|Guide\s+to|Suppliers?\s+List|Companies?\s+List)\b",
    re.IGNORECASE,
)


def detect_gl(query: str) -> str | None:
    q = query.lower()
    for k, v in _GL_HINTS.items():
        if k in q:
            return v
    return None


def normalize_domain(url: str) -> str:
    try:
        host = urlparse(url).netloc.lower()
    except Exception:
        return ""
    host = host.removeprefix("www.")
    return host


def is_blocked(domain: str) -> bool:
    if not domain:
        return True
    for b in _BLOCKED_DOMAINS:
        if domain == b or domain.endswith("." + b):
            return True
    return False


class SerpClient:
    def __init__(self, api_key: str | None = None, concurrency: int = SERP_CONCURRENCY):
        self.api_key = api_key or SERPAPI_KEY
        self.sem = asyncio.Semaphore(concurrency)
        self.client = httpx.AsyncClient(timeout=30.0)
        self.queries_made = 0

    async def close(self) -> None:
        await self.client.aclose()

    async def search(self, query: str, gl: str | None = None, num: int = 10) -> list[dict[str, Any]]:
        if not self.api_key:
            raise RuntimeError("SERPAPI_KEY is not set")
        payload: dict[str, Any] = {"q": query, "num": num}
        if gl:
            payload["gl"] = gl
        headers = {"X-API-KEY": self.api_key, "Content-Type": "application/json"}
        async with self.sem:
            last_err: Exception | None = None
            for attempt in range(3):
                try:
                    r = await self.client.post(SERP_ENDPOINT, json=payload, headers=headers)
                    if r.status_code == 429:
                        await asyncio.sleep(2 ** attempt)
                        continue
                    r.raise_for_status()
                    self.queries_made += 1
                    data = r.json()
                    return data.get("organic", []) or []
                except Exception as e:
                    last_err = e
                    await asyncio.sleep(1.5 * (attempt + 1))
            raise RuntimeError(f"Serper failed after retries: {last_err}")


_COMPANY_SUFFIXES = re.compile(
    r"\b(GmbH|AG|Inc\.?|Corp\.?|Corporation|Ltd\.?|Limited|LLC|PLC|Pte\.?\s*Ltd\.?|"
    r"Sdn\.?\s*Bhd\.?|Bhd\.?|S\.A\.|SA|SAS|SpA|S\.p\.A\.|BV|B\.V\.|NV|N\.V\.|"
    r"Co\.?,?\s*Ltd\.?|Co\.|Company|Holdings|Group|Industries|Technologies|Tech)\b",
    re.IGNORECASE,
)


def extract_candidate_name(result: dict[str, Any]) -> str:
    title = result.get("title") or ""
    # Common patterns: "ACME GmbH – Solar Modules", "ACME | About us", "ACME - Home"
    for sep in [" - ", " – ", " | ", " :: ", " » "]:
        if sep in title:
            parts = title.split(sep)
            # take the shortest sensible piece that looks name-like
            for p in parts:
                p = p.strip()
                if 2 <= len(p) <= 60:
                    return p
    return title.strip()[:80]


def is_non_company_title(title: str) -> bool:
    """Reject titles that look like market reports, listicles, or cluster overviews."""
    if not title:
        return True
    if _NON_COMPANY_TITLE.search(title):
        return True
    # All-caps reports like "GERMAN SOLAR INDUSTRY"
    words = [w for w in re.findall(r"\w+", title) if len(w) >= 3]
    if words and sum(w.isupper() for w in words) / len(words) > 0.6 and len(words) >= 3:
        return True
    return False


def candidates_from_results(results: list[dict[str, Any]]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for r in results:
        link = r.get("link") or ""
        domain = normalize_domain(link)
        if is_blocked(domain):
            continue
        title = r.get("title") or ""
        if is_non_company_title(title):
            continue
        name = extract_candidate_name(r)
        if not name:
            continue
        out.append({"name": name, "domain": domain, "snippet": r.get("snippet") or ""})
    return out
