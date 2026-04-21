import asyncio
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
        if len(by_domain) >= cap:
            break
    return list(by_domain.values())


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


def _group_companies(stages: list[dict[str, Any]], classified: list[dict[str, Any]]) -> list[dict[str, Any]]:
    valid_stage_ids = {s["id"] for s in stages}
    # Fallback: if Claude returns an id that isn't in the stage list, drop it to first stage
    fallback = stages[0]["id"] if stages else "1"
    buckets: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for c in classified:
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
            # Skip empty entries
            companies = [c for c in companies if c["n"]]
            if not companies:
                continue
            out.append({"s": s["id"], "g": g_name, "cs": companies})
    return out


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
        if not stages_raw or not serp_queries:
            raise RuntimeError("Stage proposal was empty")
        stages = _assign_stage_colors(stages_raw)

        if claude.total_cost_usd > MAX_ANTHROPIC_SPEND_USD:
            raise RuntimeError("Anthropic spend cap reached")

        await progress("queries_built", 15, f"Generated {len(serp_queries)} search queries")

        # Step 4: discovery fanout
        discovery = await asyncio.gather(
            *[serp.search(q, gl=gl, num=10) for q in serp_queries[:15]],
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

        companies = _group_companies(stages, classified)
        doc = {
            "slug": slug,
            "query": query,
            "created_at": int(started),
            "stages": stages,
            "companies": companies,
            "meta": {
                "serp_queries": serp_queries,
                "n_candidates": len(candidates),
                "n_classified": len(classified),
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
