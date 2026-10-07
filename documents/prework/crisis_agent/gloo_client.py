"""Thin client for the Gloo AI Studio Responses API.

Docs: https://docs.gloo.com/api-guides/responses
Base URL: https://platform.ai.gloo.com/ai/v2/guarded
Endpoint: POST /responses — OpenAI-compatible shape, running through Gloo's
guarded pipeline (guardrails, values alignment, output moderation).
Auth: Authorization: Bearer <GLOO_API_KEY>
"""

import os

import requests

BASE_URL = os.environ.get(
    "GLOO_BASE_URL", "https://platform.ai.gloo.com/ai/v2/guarded"
).rstrip("/")
DEFAULT_MODEL = os.environ.get("GLOO_MODEL", "gloo-anthropic-claude-sonnet-4.6")


class GuardrailBlock(Exception):
    """Raised when Gloo's guardrails hard-block a request (HTTP 403)."""

    def __init__(self, detail=""):
        super().__init__(f"Gloo guardrails blocked this request. {detail}".strip())
        self.detail = detail


class GlooClient:
    def __init__(self, api_key=None, base_url=None, model=None):
        self.api_key = api_key or os.environ.get("GLOO_API_KEY", "")
        if not self.api_key:
            raise RuntimeError("Set GLOO_API_KEY (see .env.example).")
        self.base_url = (base_url or BASE_URL).rstrip("/")
        self.model = model or DEFAULT_MODEL

    def respond(self, user_input, instructions=None, model=None, **kwargs):
        """POST to /responses; returns the raw JSON payload."""
        payload = {"model": model or self.model, "input": user_input}
        if instructions:
            payload["instructions"] = instructions
        payload.update(kwargs)
        resp = requests.post(
            f"{self.base_url}/responses",
            json=payload,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=120,
        )
        if resp.status_code == 403:
            raise GuardrailBlock(resp.text[:500])
        resp.raise_for_status()
        return resp.json()

    @staticmethod
    def text_of(response_json):
        """Extract concatenated assistant text from a Responses API payload."""
        chunks = []
        for item in response_json.get("output", []):
            if item.get("type") == "message":
                for part in item.get("content", []):
                    if part.get("type") == "output_text":
                        chunks.append(part.get("text", ""))
        return "\n".join(chunks).strip()

    def ask(self, user_input, instructions=None, **kwargs):
        """One-shot ask; returns plain text."""
        return self.text_of(self.respond(user_input, instructions, **kwargs))
