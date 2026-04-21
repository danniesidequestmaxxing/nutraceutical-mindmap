# Supply Chain Mindmap

Type an industry (e.g. "solar panels in Germany"). The backend runs Google
searches via SerpAPI for every company operating in that space, uses Claude
to propose industry-specific supply chain stages and classify each company
into one, then renders the result as the same interactive mindmap used
originally for Malaysian nutraceuticals.

Past queries are cached in SQLite and listed in the "past queries" dropdown
— reopening a cached industry is instant.

## Architecture

```
Browser ──POST /api/research──▶ FastAPI
                                   │
                   ┌───────────────┴────────────────┐
                   ▼                                ▼
          Claude: propose stages         SerpAPI: discover companies
          & search queries                       │
                                                 ▼
                                       SerpAPI: enrich each candidate
                                                 │
                                                 ▼
                                       Claude: classify into stages
                                                 │
                                                 ▼
                                      SQLite JSON blob → frontend
```

- `server/main.py` — FastAPI app, routes, SSE progress, static mounts
- `server/pipeline.py` — orchestration (stage proposal → search → enrich → classify → group)
- `server/claude_client.py` — `claude-sonnet-4-6` with prompt caching
- `server/serp_client.py` — async SerpAPI wrapper
- `server/cache.py` — SQLite DAO (queries, spend, killswitch)
- `server/limits.py` — per-IP hourly, daily run cap, spend cap
- `server/seed.py` — imports the existing `data.js` as slug `malaysia-nutraceutical`
- `app.js`, `index.html` — vanilla JS frontend (unchanged look, now dynamic)

## Local development

```bash
pip install -r requirements.txt
cp .env.example .env  # fill in ANTHROPIC_API_KEY and SERPAPI_KEY
python -m server.seed
uvicorn server.main:app --reload
```

Open http://localhost:8000. The seeded Malaysia entry should render exactly
as before. Type a new industry to run a fresh research job.

## Deploy: split (Vercel frontend + Render backend)

This is the recommended deploy: static frontend on Vercel, long-running
pipeline on Render.

### 1. Backend on Render

1. Push this repo to GitHub.
2. Render dashboard → **New +** → **Blueprint** → point at `render.yaml`.
3. Fill in `ANTHROPIC_API_KEY` and `SERPAPI_KEY`.
4. Deploy. Build runs `python -m server.seed`, pre-populating the
   Malaysia entry. Note the service URL,
   e.g. `https://supply-chain-mindmap.onrender.com`.
5. Smoke-test: `curl https://<your-render-url>/healthz` should return
   `{"ok":true, "spent_today_usd":...}`.

### 2. Frontend on Vercel

1. Edit `index.html` line that sets `window.API_BASE` and paste your
   Render URL in the quotes:
   ```html
   <script>window.API_BASE = "https://your-app.onrender.com";</script>
   ```
2. Commit and push.
3. Vercel dashboard → **Add New** → **Project** → import the same repo.
   Vercel auto-detects a static site. `.vercelignore` keeps backend files
   out of the deploy. No build command needed.
4. Open the Vercel URL. The Malaysia mindmap should load from the Render
   backend, and typing a new industry triggers a full research run with
   live progress via SSE.

### CORS

The backend sets `Access-Control-Allow-Origin: *` by default so the
Vercel frontend can call it. If you want to lock this down to just your
Vercel domain, edit `server/main.py`'s `CORSMiddleware(allow_origins=...)`.

### Free-tier notes

- Render free web service spins down after 15 min idle — first request
  after a cold start is slow. Upgrade to $7/mo Starter for always-on.
- Vercel Hobby serves unlimited static — the frontend is free forever.

## Deploy: all-on-Render (single origin)

If you prefer a single URL and don't need Vercel:

1. Push to GitHub.
2. Render dashboard → **New +** → **Blueprint** → `render.yaml`.
3. Add both API keys.
4. Done. FastAPI serves the frontend too, so no CORS setup and no
   `window.API_BASE` change needed.

## Per-query cost / latency

- ~$0.90 per cold run (75 SerpAPI credits ≈ $0.38 + ~50k Claude tokens with caching ≈ $0.50)
- Wall time 60–180 s depending on company count
- Cached re-opens: <200 ms

## Configuration

| Env var | Default | Notes |
|---|---|---|
| `ANTHROPIC_API_KEY` | required | |
| `SERPAPI_KEY` | required | |
| `CLAUDE_MODEL` | `claude-sonnet-4-6` | |
| `MAX_COMPANIES` | 60 | Candidate cap per run |
| `MAX_ANTHROPIC_SPEND_USD` | 50 | Daily spend cap |
| `DAILY_RUN_CAP` | 100 | Hard cap on runs per day |
| `PER_IP_RUNS_PER_HOUR` | 3 | Per-IP rate limit |
| `DATA_DIR` | `/var/data` | SQLite location (falls back to `./data/`) |
