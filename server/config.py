import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")

CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")

MAX_COMPANIES = int(os.getenv("MAX_COMPANIES", "60"))
MAX_ANTHROPIC_SPEND_USD = float(os.getenv("MAX_ANTHROPIC_SPEND_USD", "50"))
DAILY_RUN_CAP = int(os.getenv("DAILY_RUN_CAP", "100"))
PER_IP_RUNS_PER_HOUR = int(os.getenv("PER_IP_RUNS_PER_HOUR", "3"))

SERP_CONCURRENCY = int(os.getenv("SERP_CONCURRENCY", "10"))
CLAUDE_CONCURRENCY = int(os.getenv("CLAUDE_CONCURRENCY", "3"))
CLASSIFY_BATCH_SIZE = int(os.getenv("CLASSIFY_BATCH_SIZE", "10"))

DATA_DIR = Path(os.getenv("DATA_DIR", "/var/data"))
if not DATA_DIR.exists():
    DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "app.db"

STATIC_DIR = Path(__file__).resolve().parent.parent

SONNET_INPUT_PER_MTOK = 3.0
SONNET_OUTPUT_PER_MTOK = 15.0
SONNET_CACHE_READ_PER_MTOK = 0.30
SONNET_CACHE_WRITE_PER_MTOK = 3.75
