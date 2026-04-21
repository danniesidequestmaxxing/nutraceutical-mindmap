import asyncio
import re
import time
from collections import OrderedDict
from typing import Any, AsyncIterator, Awaitable, Callable

from slugify import slugify

from server import cache
from server.claude_client import ClaudeClient
from server.config import (
    CLASSIFY_BATCH_SIZE,
    MAX_ANTHROPIC_SPEND_USD,
    MAX_COMPANIES,
)
from server.serp_client import (
    SerpClient,
    candidates_from_results,
    detect_gl,
)


_COMPANY_SUFFIX_RE = re.compile(
    r"\b(gmbh|ag|inc|incorporated|corp|corporation|ltd|limited|llc|plc|"
    r"pte|sdn|bhd|berhad|holdings|holding|group|industries|technologies|"
    r"technology|tech|co|company|sa|sas|spa|bv|nv|oyj|ab|aps|as|oy|"
    r"international|intl|global|enterprise|enterprises)\b\.?",
    re.IGNORECASE,
)


def _normalize_name(name: str) -> str:
    """Normalize a company name for fuzzy dedupe: lowercase, strip punctuation,
    corporate suffixes, and locations in parentheses."""
    s = name.lower()
    s = re.sub(r"\([^)]*\)", " ", s)          # drop "(Munich)" etc.
    s = re.sub(r"[^a-z0-9\s]", " ", s)         # punctuation
    s = _COMPANY_SUFFIX_RE.sub(" ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


_NON_COMPANY_DESC = re.compile(
    r"^\s*(this\s+(refers|represents|appears|is|entry|describes)|"
    r"a\s+(broader|general)\s+|the\s+(broader|entire)\s+|"
    r"limited\s+information|unclear\s+)",
    re.IGNORECASE,
)


ProgressFn = Callable[[str, int, str], Awaitable[None]]


_STAGE_COLORS = [f"s{i}" for i in range(1, 11)]


def _clean_domain(w: str) -> str:
    w = w.strip()
    for prefix in ("https://", "http://", "www."):
        if w.startswith(prefix):
            w = w[len(prefix):]
    return w.rstrip("/")


def _assign_stage_colors(stages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for i, s in enumerate(stages[:10]):
        out.append({
            "id": str(s.get("id") or (i + 1)),
            "n": s.get("n") or f"Stage {i+1}",
            "t": s.get("t") or "",
            "c": _STAGE_COLORS[i],
        })
    return out


def make_slug(query: str) -> str:
    return slugify(query)[:80] or f"query-{int(time.time())}"


async def unique_slug(query: str) -> str:
    base = make_slug(query)
    slug = base
    n = 2
    while await cache.slug_exists(slug):
        slug = f"{base}-{n}"
        n += 1
    return slug


def _dedupe_candidates(cands: list[dict[str, str]], cap: int) -> list[dict[str, str]]:
    """First-pass dedupe by normalized domain, second-pass by normalized name.

    Many companies appear under multiple variants ("Wacker", "Wacker Polysilicon
    AG", "Wacker Chemie AG") with different or missing domains; merging these
    prevents the classifier from emitting duplicate entries.
    """
    by_domain: OrderedDict[str, dict[str, str]] = OrderedDict()
    for c in cands:
        d = c.get("domain", "")
        if not d:
            continue
        if d not in by_domain:
            by_domain[d] = {"name": c["name"], "domain": d, "snippets": [c.get("snippet", "")]}
        else:
            existing = by_domain[d]
            if len(existing["snippets"]) < 6 and c.get("snippet"):
                existing["snippets"].append(c["snippet"])
            if len(c["name"]) < len(existing["name"]):
                existing["name"] = c["name"]

    # Second pass: collapse by normalized name
    by_norm: OrderedDict[str, dict[str, Any]] = OrderedDict()
    for cand in by_domain.values():
        norm = _normalize_name(cand["name"])
        if not norm:
            continue
        if norm not in by_norm:
            by_norm[norm] = cand
        else:
            kept = by_norm[norm]
            # Merge snippets
            for s in cand.get("snippets", []):
                if s and s not in kept["snippets"] and len(kept["snippets"]) < 8:
                    kept["snippets"].append(s)
            # Prefer the variant with a domain over one without
            if not kept.get("domain") and cand.get("domain"):
                kept["domain"] = cand["domain"]
                kept["name"] = cand["name"]
        if len(by_norm) >= cap:
            break
    return list(by_norm.values())


async def _enrich_one(serp: SerpClient, cand: dict[str, Any], gl: str | None) -> dict[str, Any]:
    try:
        results = await serp.search(
            f"{cand['name']} {cand['domain']} about company",
            gl=gl,
            num=5,
        )
        snippets = list(cand.get("snippets", []))
        for r in results:
            snip = r.get("snippet")
            if snip and snip not in snippets:
                snippets.append(snip)
            if len(snippets) >= 6:
                break
        cand["snippets"] = snippets
    except Exception:
        cand["snippets"] = cand.get("snippets", [])
    return cand


def _looks_non_company(entry: dict[str, Any]) -> bool:
    """Post-classification filter: description or name reveals this isn't a
    single company (Claude sometimes classifies anyway even when told to drop)."""
    d = (entry.get("d") or "").strip()
    n = (entry.get("n") or "").strip()
    if not n:
        return True
    if _NON_COMPANY_DESC.match(d):
        return True
    # Name looks like a phrase/report not a proper noun
    if re.search(r"\b(Market|Industry|Report|Overview|Cluster|Ecosystem|Top\s+\d+)\b", n, re.I):
        return True
    return False


def _group_companies(stages: list[dict[str, Any]], classified: list[dict[str, Any]]) -> list[dict[str, Any]]:
    valid_stage_ids = {s["id"] for s in stages}
    fallback = stages[0]["id"] if stages else "1"
    buckets: dict[str, dict[str, list[dict[str, Any]]]] = {}
    seen_norm: set[str] = set()
    dropped_count = 0
    for c in classified:
        if c is None or not isinstance(c, dict):
            dropped_count += 1
            continue
        if _looks_non_company(c):
            dropped_count += 1
            continue
        # Final fuzzy dedupe in case Claude emitted the same entity twice
        norm = _normalize_name(c.get("n", ""))
        if norm in seen_norm:
            dropped_count += 1
            continue
        seen_norm.add(norm)

        s = str(c.get("s") or fallback)
        if s not in valid_stage_ids:
            s = fallback
        g = (c.get("g") or "Other").strip() or "Other"
        buckets.setdefault(s, {}).setdefault(g, []).append({
            "n": c.get("n", "").strip(),
            "l": c.get("l", "").strip(),
            "d": c.get("d", "").strip(),
            "c": [t for t in (c.get("c") or []) if isinstance(t, str)],
            "w": _clean_domain(c.get("w") or ""),
            **({"x": c["x"]} if c.get("x") else {}),
        })
    out: list[dict[str, Any]] = []
    for s in stages:
        groups = buckets.get(s["id"], {})
        for g_name, companies in groups.items():
            companies = [c for c in companies if c["n"]]
            if not companies:
                continue
            out.append({"s": s["id"], "g": g_name, "cs": companies})
    return out, dropped_count


async def run_research(
    query: str,
    slug: str,
    progress: ProgressFn,
) -> dict[str, Any]:
    started = time.time()
    if await cache.killswitch_on():
        raise RuntimeError("Service is temporarily disabled")

    gl = detect_gl(query)
    serp = SerpClient()
    claude = ClaudeClient()

    try:
        await progress("stages_proposed", 5, "Proposing supply chain stages")
        proposal = await claude.propose_stages(query)
        stages_raw = proposal.get("stages") or []
        serp_queries = proposal.get("serp_queries") or []
        known_brands = [b for b in (proposal.get("known_brands") or []) if isinstance(b, str) and b.strip()]
        if not stages_raw or not serp_queries:
            raise RuntimeError("Stage proposal was empty")
        stages = _assign_stage_colors(stages_raw)

        if claude.total_cost_usd > MAX_ANTHROPIC_SPEND_USD:
            raise RuntimeError("Anthropic spend cap reached")

        # Each known brand gets its own explicit SerpAPI query. The region
        # hint (the raw user query) is appended so ambiguous brand names
        # disambiguate correctly ("Mamee Malaysia" not "mamee").
        brand_queries = [f"{b} {query}" for b in known_brands[:15]]

        await progress(
            "queries_built",
            15,
            f"Generated {len(serp_queries)} search queries + {len(brand_queries)} brand lookups",
        )

        # Step 4: discovery fanout. Brand queries run first so their candidates
        # are added to the dedupe list before the MAX_COMPANIES cap kicks in;
        # this prevents household names from being crowded out by noisy generic
        # hits on upstream ingredient suppliers.
        all_serp = brand_queries + serp_queries[:16]
        discovery = await asyncio.gather(
            *[serp.search(q, gl=gl, num=10) for q in all_serp],
            return_exceptions=True,
        )
        all_candidates: list[dict[str, str]] = []
        for res in discovery:
            if isinstance(res, Exception):
                continue
            all_candidates.extend(candidates_from_results(res))

        candidates = _dedupe_candidates(all_candidates, MAX_COMPANIES)
        await progress("serp_done", 35, f"Found {len(candidates)} candidate companies")

        if not candidates:
            raise RuntimeError("No candidates discovered — try a more specific industry query")

        # Step 5: enrichment
        enriched: list[dict[str, Any]] = []
        total = len(candidates)
        chunk_size = 8
        done = 0
        for i in range(0, total, chunk_size):
            batch = candidates[i:i + chunk_size]
            results = await asyncio.gather(*[_enrich_one(serp, c, gl) for c in batch])
            enriched.extend(results)
            done += len(results)
            pct = 35 + int(30 * done / total)
            await progress("enriching", pct, f"Enriched {done}/{total} companies")

        # Step 6: batched classification
        await progress("classifying", 70, "Classifying companies into stages")
        classified: list[dict[str, Any]] = []
        batches = [enriched[i:i + CLASSIFY_BATCH_SIZE] for i in range(0, len(enriched), CLASSIFY_BATCH_SIZE)]
        classify_coros = [claude.classify_batch(query, stages, b) for b in batches]
        results = await asyncio.gather(*classify_coros, return_exceptions=True)
        for res in results:
            if isinstance(res, Exception):
                continue
            classified.extend(res)

        if claude.total_cost_usd > MAX_ANTHROPIC_SPEND_USD:
            raise RuntimeError("Anthropic spend cap reached during classification")

        await progress("classifying", 90, f"Classified {len(classified)} companies")

        companies, dropped = _group_companies(stages, classified)
        doc = {
            "slug": slug,
            "query": query,
            "created_at": int(started),
            "stages": stages,
            "companies": companies,
            "meta": {
                "serp_queries": serp_queries,
                "known_brands": known_brands,
                "focus": proposal.get("focus", "balanced"),
                "n_candidates": len(candidates),
                "n_classified": len(classified),
                "n_dropped": dropped,
                "serp_calls": serp.queries_made,
                "cost_usd": round(claude.total_cost_usd, 4),
                "elapsed_s": round(time.time() - started, 1),
                "gl": gl,
            },
        }
        await cache.put_query(slug, query, "complete", doc, int(claude.total_cost_usd * 100))
        await cache.add_spend(claude.total_cost_usd)
        await progress("complete", 100, f"Done — {sum(len(g['cs']) for g in companies)} companies classified")
        return doc
    finally:
        await serp.close()
