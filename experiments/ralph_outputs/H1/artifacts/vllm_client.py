"""vllm_client.py — OpenAI-compatible client shim pointing eval at a local vLLM server.

Drop-in for `agent.llm.call`: same signature `call(name, prompt, **kw) -> str`, same
kwargs (max_tokens, temperature, system, stop). It talks to vLLM's OpenAI-compatible
`/v1/chat/completions`, so eval code (e.g. rex/eval_pass_at_k.py's make_proposer)
can swap remote-API calls for the warm local endpoint with no other change:

    from H1.artifacts.vllm_client import call          # instead of: from agent.llm import call

Config comes from H1/artifacts/vllm_config.env (or env overrides):
    VLLM_BASE_URL  default http://127.0.0.1:8000/v1
    VLLM_MODEL     default vllm-local   (the served-model-name)
    VLLM_API_KEY   default local-key

`build_request` is pure (no network) — unit-testable. `call` does the HTTP round-trip.
`_extract` parses the OpenAI chat response shape that vLLM returns.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

_DEFAULT_BASE = "http://127.0.0.1:8000/v1"
_DEFAULT_MODEL = "vllm-local"
_DEFAULT_KEY = "local-key"


def _load_config() -> None:
    """Populate os.environ from vllm_config.env for any VLLM_* key not already set."""
    cfg = Path(__file__).resolve().parent / "vllm_config.env"
    if not cfg.exists():
        return
    for line in cfg.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())


def _settings() -> tuple[str, str, str]:
    _load_config()
    base = os.environ.get("VLLM_BASE_URL", _DEFAULT_BASE).rstrip("/")
    model = os.environ.get("VLLM_MODEL", _DEFAULT_MODEL)
    key = os.environ.get("VLLM_API_KEY", _DEFAULT_KEY)
    return base, model, key


def build_request(name: str, prompt: str, max_tokens: int = 512,
                  temperature: float = 0.1, system: str | None = None,
                  stop: list | None = None):
    """Return (url, headers, payload) for vLLM's OpenAI chat endpoint.

    `name` is accepted for signature-compatibility with agent.llm.build_request but
    is ignored for routing — the served model is fixed by the local server. Pass the
    real served-model-name via VLLM_MODEL if you run multiple. Pure: no network."""
    base, model, key = _settings()
    url = f"{base}/chat/completions"
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    messages = ([{"role": "system", "content": system}] if system else []) + \
               [{"role": "user", "content": prompt}]
    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": messages,
    }
    if stop:
        payload["stop"] = stop
    return url, headers, payload


def _extract(resp: dict) -> str:
    """Pull assistant text out of an OpenAI-compatible chat completion response."""
    msg = (resp.get("choices") or [{}])[0].get("message", {}) or {}
    return msg.get("content", "") or ""


def _post(url: str, headers: dict, payload: dict, timeout: float = 180.0) -> dict:
    import requests
    r = requests.post(url, headers=headers, data=json.dumps(payload), timeout=timeout)
    r.raise_for_status()
    return r.json()


def call(name: str, prompt: str, **kw) -> str:
    """Run one completion against the local vLLM server, return the text."""
    url, headers, payload = build_request(name, prompt, **kw)
    return _extract(_post(url, headers, payload))


def health(timeout: float = 5.0) -> bool:
    """True if the local vLLM /models endpoint answers. Cheap readiness probe."""
    import requests
    base, _, key = _settings()
    try:
        r = requests.get(f"{base}/models", headers={"Authorization": f"Bearer {key}"},
                         timeout=timeout)
        return r.status_code == 200
    except Exception:
        return False
