"""Minimal async client for the Fireworks OpenAI-compatible chat completions API.

ALL calls go through FIREWORKS_BASE_URL (the judging proxy) — never any other host.
Returns token usage so the eval harness can rank runs by total tokens (the leaderboard metric).
"""
import asyncio
from dataclasses import dataclass

import httpx


@dataclass
class ChatResult:
    content: str
    prompt_tokens: int = 0
    completion_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens


class FireworksClient:
    def __init__(self, api_key: str, base_url: str, timeout: float = 25.0):
        # 25s client timeout keeps us under the 30s per-request rule with headroom
        self._client = httpx.AsyncClient(
            base_url=base_url.rstrip("/"),
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=timeout,
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        await self._client.aclose()

    async def chat(self, model: str, messages: list[dict], max_tokens: int, retries: int = 1) -> ChatResult:
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0,
        }
        for attempt in range(retries + 1):
            try:
                r = await self._client.post("/chat/completions", json=payload)
                r.raise_for_status()
                data = r.json()
                content = data["choices"][0]["message"]["content"].strip()
                usage = data.get("usage") or {}
                return ChatResult(
                    content=content,
                    prompt_tokens=usage.get("prompt_tokens", 0),
                    completion_tokens=usage.get("completion_tokens", 0),
                )
            except (httpx.HTTPStatusError, httpx.TransportError, KeyError):
                if attempt == retries:
                    raise
                await asyncio.sleep(1.5 * (attempt + 1))
        return ChatResult("")
