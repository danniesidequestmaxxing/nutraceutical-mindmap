import json
import time
from typing import Any

import aiosqlite

from server.config import DB_PATH


SCHEMA = """
CREATE TABLE IF NOT EXISTS queries (
    slug TEXT PRIMARY KEY,
    query TEXT NOT NULL,
    created_at INTEGER NOT NULL,
    status TEXT NOT NULL,
    cost_cents INTEGER NOT NULL DEFAULT 0,
    json_blob TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS spend (
    day TEXT PRIMARY KEY,
    usd_x10000 INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS killswitch (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    disabled INTEGER NOT NULL DEFAULT 0
);
"""


async def init_db() -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(SCHEMA)
        await db.commit()


async def get_query(slug: str) -> dict[str, Any] | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        row = await (await db.execute(
            "SELECT slug, query, created_at, status, cost_cents, json_blob FROM queries WHERE slug = ?",
            (slug,),
        )).fetchone()
        if not row:
            return None
        doc = json.loads(row["json_blob"])
        doc["status"] = row["status"]
        return doc


async def list_queries() -> list[dict[str, Any]]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        rows = await (await db.execute(
            "SELECT slug, query, created_at, status, json_blob FROM queries ORDER BY created_at DESC"
        )).fetchall()
        out = []
        for r in rows:
            doc = json.loads(r["json_blob"])
            out.append({
                "slug": r["slug"],
                "query": r["query"],
                "created_at": r["created_at"],
                "status": r["status"],
                "n_companies": sum(len(g.get("cs", [])) for g in doc.get("companies", [])),
                "n_stages": len(doc.get("stages", [])),
            })
        return out


async def put_query(slug: str, query: str, status: str, doc: dict[str, Any], cost_cents: int = 0) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT INTO queries(slug, query, created_at, status, cost_cents, json_blob)
               VALUES (?, ?, ?, ?, ?, ?)
               ON CONFLICT(slug) DO UPDATE SET
                   status=excluded.status,
                   cost_cents=excluded.cost_cents,
                   json_blob=excluded.json_blob""",
            (slug, query, int(time.time()), status, cost_cents, json.dumps(doc, ensure_ascii=False)),
        )
        await db.commit()


async def set_status(slug: str, status: str) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE queries SET status = ? WHERE slug = ?", (status, slug))
        await db.commit()


async def add_spend(usd: float) -> float:
    day = time.strftime("%Y-%m-%d")
    amt = int(round(usd * 10000))
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT INTO spend(day, usd_x10000) VALUES(?, ?)
               ON CONFLICT(day) DO UPDATE SET usd_x10000 = usd_x10000 + excluded.usd_x10000""",
            (day, amt),
        )
        await db.commit()
        row = await (await db.execute("SELECT usd_x10000 FROM spend WHERE day = ?", (day,))).fetchone()
        return (row[0] if row else 0) / 10000.0


async def todays_spend() -> float:
    day = time.strftime("%Y-%m-%d")
    async with aiosqlite.connect(DB_PATH) as db:
        row = await (await db.execute("SELECT usd_x10000 FROM spend WHERE day = ?", (day,))).fetchone()
        return (row[0] if row else 0) / 10000.0


async def killswitch_on() -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        row = await (await db.execute("SELECT disabled FROM killswitch WHERE id = 1")).fetchone()
        return bool(row and row[0])


async def slug_exists(slug: str) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        row = await (await db.execute("SELECT 1 FROM queries WHERE slug = ?", (slug,))).fetchone()
        return row is not None
