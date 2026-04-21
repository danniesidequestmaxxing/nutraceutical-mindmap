import asyncio
import json
import re
from typing import Any

from anthropic import AsyncAnthropic

from server.config import (
    ANTHROPIC_API_KEY,
    CLAUDE_MODEL,
    CLAUDE_CONCURRENCY,
    SONNET_INPUT_PER_MTOK,
    SONNET_OUTPUT_PER_MTOK,
    SONNET_CACHE_READ_PER_MTOK,
    SONNET_CACHE_WRITE_PER_MTOK,
)
from server.prompts import STAGE_PROPOSAL_SYSTEM, CLASSIFY_SYSTEM_TEMPLATE


_JSON_BLOCK = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL)


def _extract_json(text: str) -> Any:
    """Pull out the first JSON object or array from Claude's reply."""
    m = _JSON_BLOCK.search(text)
    body = m.group(1) if m else text
    body = body.strip()
    # Find first { or [ and parse from there
    for i, ch in enumerate(body):
        if ch in "{[":
            body = body[i:]
            break
    return json.loads(body)


class ClaudeClient:
    def __init__(self, api_key: str | None = None, concurrency: int = CLAUDE_CONCURRENCY):
        self.client = AsyncAnthropic(api_key=api_key or ANTHROPIC_API_KEY)
        self.sem = asyncio.Semaphore(concurrency)
        self.total_cost_usd = 0.0
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cache_read_tokens = 0
        self.total_cache_write_tokens = 0

    def _accrue_cost(self, usage: Any) -> None:
        inp = getattr(usage, "input_tokens", 0) or 0
        out = getattr(usage, "output_tokens", 0) or 0
        cwrite = getattr(usage, "cache_creation_input_tokens", 0) or 0
        cread = getattr(usage, "cache_read_input_tokens", 0) or 0
        self.total_input_tokens += inp
        self.total_output_tokens += out
        self.total_cache_read_tokens += cread
        self.total_cache_write_tokens += cwrite
        self.total_cost_usd += (
            inp * SONNET_INPUT_PER_MTOK
            + out * SONNET_OUTPUT_PER_MTOK
            + cread * SONNET_CACHE_READ_PER_MTOK
            + cwrite * SONNET_CACHE_WRITE_PER_MTOK
        ) / 1_000_000

    async def propose_stages(self, query: str) -> dict[str, Any]:
        async with self.sem:
            msg = await self.client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=1200,
                system=[{
                    "type": "text",
                    "text": STAGE_PROPOSAL_SYSTEM,
                    "cache_control": {"type": "ephemeral"},
                }],
                messages=[{"role": "user", "content": f"Industry: {query}"}],
            )
        self._accrue_cost(msg.usage)
        text = "".join(b.text for b in msg.content if getattr(b, "type", None) == "text")
        return _extract_json(text)

    async def classify_batch(
        self,
        query: str,
        stages: list[dict[str, Any]],
        companies: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        stages_block = "\n".join(
            f"- id=\"{s['id']}\" name=\"{s['n']}\" tier=\"{s.get('t', '')}\"" for s in stages
        )
        system = CLASSIFY_SYSTEM_TEMPLATE.format(query=query, stages_block=stages_block)

        user_parts = []
        for i, c in enumerate(companies, 1):
            snips = c.get("snippets") or []
            snip_text = "\n".join(f"  - {s}" for s in snips if s)
            user_parts.append(
                f"Company {i}:\n"
                f"  likely_name: {c.get('name', '')}\n"
                f"  likely_domain: {c.get('domain', '')}\n"
                f"  snippets:\n{snip_text or '  (none)'}"
            )
        user_msg = "\n\n".join(user_parts) + "\n\nReturn the JSON array only."

        async with self.sem:
            msg = await self.client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=6000,
                system=[{
                    "type": "text",
                    "text": system,
                    "cache_control": {"type": "ephemeral"},
                }],
                messages=[{"role": "user", "content": user_msg}],
            )
        self._accrue_cost(msg.usage)
        text = "".join(b.text for b in msg.content if getattr(b, "type", None) == "text")
        parsed = _extract_json(text)
        if not isinstance(parsed, list):
            raise ValueError("Claude did not return a JSON array for classification")
        return parsed
