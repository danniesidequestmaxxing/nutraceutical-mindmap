import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request

from server.config import (
    DAILY_RUN_CAP,
    MAX_ANTHROPIC_SPEND_USD,
    PER_IP_RUNS_PER_HOUR,
)
from server import cache


_ip_hits: dict[str, deque[float]] = defaultdict(deque)
_daily_runs: dict[str, int] = defaultdict(int)


def _client_ip(request: Request) -> str:
    fwd = request.headers.get("x-forwarded-for")
    if fwd:
        return fwd.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def check_per_ip(request: Request) -> None:
    ip = _client_ip(request)
    now = time.time()
    window = 3600.0
    hits = _ip_hits[ip]
    while hits and now - hits[0] > window:
        hits.popleft()
    if len(hits) >= PER_IP_RUNS_PER_HOUR:
        raise HTTPException(status_code=429, detail="Per-IP hourly run limit reached")
    hits.append(now)


def check_daily_cap() -> None:
    day = time.strftime("%Y-%m-%d")
    if _daily_runs[day] >= DAILY_RUN_CAP:
        raise HTTPException(status_code=429, detail="Daily run cap reached")
    _daily_runs[day] += 1


async def preflight_budget() -> None:
    if await cache.killswitch_on():
        raise HTTPException(status_code=503, detail="Service disabled")
    spent = await cache.todays_spend()
    if spent >= MAX_ANTHROPIC_SPEND_USD:
        raise HTTPException(status_code=503, detail="Anthropic daily spend cap reached")
