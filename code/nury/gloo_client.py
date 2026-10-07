"""Gloo guarded Responses client.

POST https://platform.ai.gloo.com/ai/v2/guarded/responses
The key comes from the environment (or repo-root .env). It is never logged.

Retries. A transient failure is retried a bounded number of times (3 tries in all) with exponential backoff
(1 s, then 2 s): HTTP 429, 500, 502, 503 and 504, a dropped connection and a timeout. These are NEVER retried:
402 (no credit), 403 (the guardrail block, which is a safety answer), any other 4xx, and a 429 whose body says the
quota or billing is exhausted (waiting does not help). A Retry-After header is honored up to 10 s. When the tries run
out, the last error is raised exactly as before, so the engine's existing error path is unchanged. The correction
loop is not involved: a retry repeats the same request and does not count as a draft attempt.
"""

import os
import time
from pathlib import Path

import requests

MAX_TRIES = 3
RETRY_STATUS = (429, 500, 502, 503, 504)
RETRY_AFTER_CAP_S = 10.0
_QUOTA = ("insufficient_quota", "insufficient_credit", "quota exceeded", "out of budget", "billing", "usage limit")
_sleep = time.sleep          # replaced in tests


def _backoff_base():
    try:
        return float(os.environ.get("NURY_GLOO_RETRY_BASE", "1.0"))
    except ValueError:
        return 1.0


def retryable_status(status, body=""):
    """True for a transient HTTP status. A 429 about quota or billing is not transient."""
    if status not in RETRY_STATUS:
        return False
    low = (body or "").lower()
    return not (status == 429 and any(q in low for q in _QUOTA))


def _wait(attempt, resp=None):
    """Seconds to wait before try number attempt + 1. Retry-After wins, capped."""
    base = _backoff_base() * (2 ** (attempt - 1))
    ra = None
    try:
        h = getattr(resp, "headers", None) or {}
        ra = float(h.get("Retry-After")) if h.get("Retry-After") else None
    except (TypeError, ValueError):
        ra = None
    return min(ra, RETRY_AFTER_CAP_S) if ra is not None else base


BASE_URL = os.environ.get("GLOO_BASE_URL", "https://platform.ai.gloo.com/ai/v2/guarded").rstrip("/")
DEFAULT_MODEL = "gloo-anthropic-claude-sonnet-4.6"


def load_env():
    """Load repo-root .env into os.environ without overriding existing values."""
    for parent in Path(__file__).resolve().parents:
        env = parent / ".env"
        if env.is_file():
            for line in env.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
            return


class GuardrailBlock(Exception):
    """Gloo guardrails hard-blocked the request (HTTP 403)."""

    def __init__(self, detail=""):
        super().__init__(f"Gloo guardrails blocked this request. {detail}".strip())
        self.detail = detail


class GlooClient:
    def __init__(self, api_key=None, base_url=None, model=None):
        load_env()
        self._api_key = api_key or os.environ.get("GLOO_API_KEY", "")
        if not self._api_key:
            raise RuntimeError("Set GLOO_API_KEY in the environment.")
        self.base_url = (base_url or BASE_URL).rstrip("/")
        self.model = model or os.environ.get("GLOO_MODEL", DEFAULT_MODEL)

    def respond(self, user_input, instructions=None, model=None, **kwargs):
        """Return (json, meta). meta has latency_s and token counts."""
        payload = {"model": model or self.model, "input": user_input}
        if instructions:
            payload["instructions"] = instructions
        payload.update(kwargs)
        t0 = time.monotonic()
        retries = 0
        while True:
            try:
                resp = requests.post(
                    f"{self.base_url}/responses",
                    json=payload,
                    headers={"Authorization": f"Bearer {self._api_key}"},
                    timeout=120,
                )
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                if retries + 1 >= MAX_TRIES:
                    raise
                retries += 1
                _sleep(_wait(retries))
                continue
            if resp.status_code == 403:
                raise GuardrailBlock(resp.text[:500])
            if resp.status_code in RETRY_STATUS and retryable_status(resp.status_code, getattr(resp, "text", "")) and retries + 1 < MAX_TRIES:
                retries += 1
                _sleep(_wait(retries, resp))
                continue
            break
        latency = round(time.monotonic() - t0, 3)
        resp.raise_for_status()
        data = resp.json()
        usage = data.get("usage") or {}
        meta = {
            "latency_s": latency,
            "input_tokens": usage.get("input_tokens", 0),
            "output_tokens": usage.get("output_tokens", 0),
            "model": payload["model"],
            "http_retries": retries,
        }
        return data, meta

    @staticmethod
    def text_of(data):
        chunks = []
        for item in data.get("output", []):
            if item.get("type") == "message":
                for part in item.get("content", []):
                    if part.get("type") == "output_text":
                        chunks.append(part.get("text", ""))
        return "\n".join(chunks).strip()

    def ask(self, user_input, instructions=None, **kwargs):
        """Return (text, meta)."""
        data, meta = self.respond(user_input, instructions, **kwargs)
        return self.text_of(data), meta
