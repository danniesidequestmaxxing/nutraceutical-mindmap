import asyncio
import json
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from server import cache, limits
from server.config import STATIC_DIR
from server.pipeline import run_research, unique_slug


# In-memory channel per slug so SSE clients can stream progress while a
# background task runs the pipeline. Only one active run per slug is expected.
_channels: dict[str, asyncio.Queue] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    await cache.init_db()
    yield


app = FastAPI(title="Supply Chain Researcher", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


class ResearchReq(BaseModel):
    query: str


@app.post("/api/research")
async def start_research(req: ResearchReq, request: Request):
    q = (req.query or "").strip()
    if len(q) < 3:
        raise HTTPException(status_code=400, detail="Query too short")
    if len(q) > 200:
        raise HTTPException(status_code=400, detail="Query too long")

    limits.check_per_ip(request)
    limits.check_daily_cap()
    await limits.preflight_budget()

    slug = await unique_slug(q)
    channel: asyncio.Queue = asyncio.Queue()
    _channels[slug] = channel

    # Mark row pending so the library listing shows it immediately
    await cache.put_query(slug, q, "running", {
        "slug": slug, "query": q, "stages": [], "companies": [],
    }, 0)

    async def _runner():
        async def progress(phase: str, pct: int, msg: str) -> None:
            await channel.put({"phase": phase, "pct": pct, "msg": msg})
        try:
            await run_research(q, slug, progress)
            await channel.put({"phase": "done", "pct": 100, "msg": "done"})
        except Exception as e:
            await cache.set_status(slug, "error")
            await channel.put({"phase": "error", "pct": 100, "msg": str(e)[:300]})
        finally:
            await channel.put(None)  # sentinel

    asyncio.create_task(_runner())
    return {"slug": slug, "status": "running"}


@app.get("/api/research/{slug}/stream")
async def stream(slug: str):
    channel = _channels.get(slug)
    if channel is None:
        # If the run already finished (or never existed), just emit current status
        doc = await cache.get_query(slug)
        if not doc:
            raise HTTPException(status_code=404, detail="Unknown slug")

        async def once():
            yield {"event": "message", "data": json.dumps({
                "phase": doc.get("status", "complete"),
                "pct": 100,
                "msg": "cached",
            })}
        return EventSourceResponse(once())

    async def gen():
        while True:
            evt = await channel.get()
            if evt is None:
                break
            yield {"event": "message", "data": json.dumps(evt)}
        _channels.pop(slug, None)
    return EventSourceResponse(gen())


@app.get("/api/queries")
async def api_list_queries() -> list[dict[str, Any]]:
    return await cache.list_queries()


@app.get("/api/queries/{slug}")
async def api_get_query(slug: str) -> dict[str, Any]:
    doc = await cache.get_query(slug)
    if not doc:
        raise HTTPException(status_code=404, detail="Not found")
    return doc


@app.get("/healthz")
async def health():
    return {"ok": True, "spent_today_usd": await cache.todays_spend()}


# Static frontend. Mount AFTER api routes so /api/* wins.
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
async def root() -> FileResponse:
    return FileResponse(str(STATIC_DIR / "index.html"))


@app.get("/app.js")
async def appjs() -> FileResponse:
    return FileResponse(str(STATIC_DIR / "app.js"), media_type="application/javascript")


@app.get("/data.js")
async def datajs() -> FileResponse:
    return FileResponse(str(STATIC_DIR / "data.js"), media_type="application/javascript")
