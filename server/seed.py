"""Seed the SQLite cache with the legacy Malaysia nutraceutical dataset.

Parses the hand-curated `data.js` file and writes it into the queries table
under slug `malaysia-nutraceutical` so the existing mindmap still renders
via the new /api/queries/{slug} endpoint.

Usage:
    python -m server.seed
"""

import asyncio
import json
import re
import time
from pathlib import Path

from server import cache
from server.config import STATIC_DIR


# Unquoted JS object keys we expect in data.js
_OBJECT_KEYS = ("s", "g", "cs", "n", "l", "d", "c", "w", "x", "t")


def _js_object_to_json(body: str) -> str:
    """Convert the JS object-literal body to JSON.

    Walks the text character-by-character, skipping contents inside string
    literals, and rewrites unquoted identifier keys `key:` → `"key":`. Also
    strips trailing commas before `}`/`]`.
    """
    out: list[str] = []
    i = 0
    n = len(body)
    while i < n:
        ch = body[i]
        if ch == '"':
            # Copy through closing quote, respecting escapes
            j = i + 1
            while j < n:
                if body[j] == "\\":
                    j += 2
                    continue
                if body[j] == '"':
                    break
                j += 1
            out.append(body[i:j + 1])
            i = j + 1
            continue
        # Potential unquoted key at this position if previous non-ws is {, or ,
        if ch.isalpha() or ch == "_":
            # Look back for context
            k = len(out) - 1
            prev_non_ws = ""
            tail = "".join(out)
            for m in range(len(tail) - 1, -1, -1):
                if not tail[m].isspace():
                    prev_non_ws = tail[m]
                    break
            if prev_non_ws in "{,":
                # Read identifier
                j = i
                while j < n and (body[j].isalnum() or body[j] == "_"):
                    j += 1
                ident = body[i:j]
                # Skip whitespace, check for ':'
                k2 = j
                while k2 < n and body[k2].isspace():
                    k2 += 1
                if k2 < n and body[k2] == ":":
                    out.append(f'"{ident}"')
                    i = j
                    continue
        out.append(ch)
        i += 1
    joined = "".join(out)
    joined = re.sub(r",(\s*[}\]])", r"\1", joined)
    return joined


def _extract_js_value(src: str, name: str) -> str:
    """Given `const <name>=<value>;`, return the JSON-convertible value body."""
    m = re.search(rf"const\s+{re.escape(name)}\s*=\s*", src)
    if not m:
        raise ValueError(f"Could not find const {name} in data.js")
    i = m.end()
    # Determine opening bracket
    open_ch = src[i]
    close_ch = {"{": "}", "[": "]"}[open_ch]
    depth = 0
    in_str = False
    esc = False
    j = i
    while j < len(src):
        ch = src[j]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
        else:
            if ch == '"':
                in_str = True
            elif ch == open_ch:
                depth += 1
            elif ch == close_ch:
                depth -= 1
                if depth == 0:
                    return src[i:j + 1]
        j += 1
    raise ValueError(f"Unterminated value for {name}")


def _normalize_x(x: str) -> str:
    """Legacy tags like '4_branded_products' → stage id '4'."""
    if not x:
        return ""
    head = x.split("_", 1)[0]
    return head if head.isdigit() else x


def parse_data_js(path: Path) -> dict:
    src = path.read_text(encoding="utf-8")
    stages_src = _extract_js_value(src, "stageLabels")
    data_src = _extract_js_value(src, "D")
    stages_raw = json.loads(_js_object_to_json(stages_src))
    companies_raw = json.loads(_js_object_to_json(data_src))

    stages = []
    for key, val in stages_raw.items():
        stages.append({
            "id": str(key),
            "n": val.get("n", ""),
            "t": val.get("t", ""),
            "c": val.get("c", f"s{key}"),
        })
    # Sort by numeric id
    stages.sort(key=lambda s: int(s["id"]))

    companies = []
    for grp in companies_raw:
        companies.append({
            "s": str(grp["s"]),
            "g": grp.get("g", "") or "",
            "cs": [
                {
                    "n": c.get("n", ""),
                    "l": c.get("l", ""),
                    "d": c.get("d", ""),
                    "c": c.get("c", []) or [],
                    "w": c.get("w", ""),
                    **({"x": _normalize_x(c["x"])} if c.get("x") else {}),
                }
                for c in grp.get("cs", [])
            ],
        })

    return {
        "slug": "malaysia-nutraceutical",
        "query": "Malaysia nutraceutical industry",
        "created_at": int(time.time()),
        "stages": stages,
        "companies": companies,
        "meta": {"source": "seeded from data.js"},
    }


async def run() -> None:
    await cache.init_db()
    doc = parse_data_js(STATIC_DIR / "data.js")
    await cache.put_query(doc["slug"], doc["query"], "complete", doc, 0)
    total = sum(len(g["cs"]) for g in doc["companies"])
    print(f"Seeded {doc['slug']}: {len(doc['stages'])} stages, {total} companies")


if __name__ == "__main__":
    asyncio.run(run())
