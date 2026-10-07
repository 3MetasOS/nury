"""Model prices as data (pricing.json). The engine reads them to put a cost on each stage.

An environment override still wins: NURY_PRICE_IN and NURY_PRICE_OUT (USD per 1M tokens), as before.
A model that is not in the file has no cost: cost_usd stays None. Nothing is guessed.
Jev has an entry that says "unknown, not quoted"; no Jev cost is ever computed.
"""
import json
import os
from pathlib import Path

_FILE = Path(__file__).resolve().parent / "pricing.json"
_CACHE = {}


def table():
    if "t" not in _CACHE:
        t = json.loads(_FILE.read_text(encoding="utf-8"))
        for name, m in t["models"].items():
            for k in ("input", "output", "source", "as_of"):
                if k not in m:
                    raise ValueError(f"pricing.json: {name} is missing {k}")
        _CACHE["t"] = t
    return _CACHE["t"]


def price(model):
    """{'input', 'output', ...} per 1M tokens, or None when the model is not priced."""
    return table()["models"].get(model or "")


def cost_usd(model, tokens_in, tokens_out):
    """Cost of one call, or None. The environment override wins when both prices are set."""
    try:
        pi, po = float(os.environ["NURY_PRICE_IN"]), float(os.environ["NURY_PRICE_OUT"])
    except (KeyError, ValueError):
        p = price(model)
        if p is None:
            return None
        pi, po = p["input"], p["output"]
    return round((tokens_in * pi + tokens_out * po) / table()["per_tokens"], 6)


def jev_status():
    return table()["classifiers"]["jev"]["status"]
