"""Gloo guarded Responses client.

POST https://platform.ai.gloo.com/ai/v2/guarded/responses
The key comes from the environment (or repo-root .env). It is never logged.
"""

import os
import time
from pathlib import Path

import requests

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
        resp = requests.post(
            f"{self.base_url}/responses",
            json=payload,
            headers={"Authorization": f"Bearer {self._api_key}"},
            timeout=120,
        )
        latency = round(time.monotonic() - t0, 3)
        if resp.status_code == 403:
            raise GuardrailBlock(resp.text[:500])
        resp.raise_for_status()
        data = resp.json()
        usage = data.get("usage") or {}
        meta = {
            "latency_s": latency,
            "input_tokens": usage.get("input_tokens", 0),
            "output_tokens": usage.get("output_tokens", 0),
            "model": payload["model"],
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
