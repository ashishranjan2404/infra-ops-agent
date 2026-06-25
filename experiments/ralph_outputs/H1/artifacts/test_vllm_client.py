"""test_vllm_client.py — validate the vLLM shim WITHOUT a GPU or a running server.

`build_request` is pure, so we assert its shape directly. `call`/`health` are tested
against a faked HTTP layer (monkeypatched requests.post/get) that returns exactly the
JSON shape vLLM's OpenAI-compatible endpoint emits. This proves the shim is API-correct
even though no real vLLM server can run on this CPU/Apple-Silicon host.

Run:  python3 -m pytest experiments/ralph_outputs/H1/artifacts/test_vllm_client.py -q
"""
import importlib.util
import os
import sys
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _load_shim():
    spec = importlib.util.spec_from_file_location("vllm_client", HERE / "vllm_client.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


vc = _load_shim()


# ---- build_request: pure, OpenAI-compatible shape -------------------------
def test_build_request_basic_shape():
    url, headers, payload = vc.build_request("ignored", "hello", max_tokens=64,
                                             temperature=0.3)
    assert url.endswith("/chat/completions")
    assert headers["Authorization"].startswith("Bearer ")
    assert headers["Content-Type"] == "application/json"
    assert payload["max_tokens"] == 64
    assert payload["temperature"] == 0.3
    assert payload["messages"] == [{"role": "user", "content": "hello"}]
    assert "model" in payload


def test_build_request_system_and_stop():
    _, _, payload = vc.build_request("x", "q", system="you are an SRE", stop=["\n\n"])
    assert payload["messages"][0] == {"role": "system", "content": "you are an SRE"}
    assert payload["messages"][1] == {"role": "user", "content": "q"}
    assert payload["stop"] == ["\n\n"]


def test_build_request_no_network():
    # Purity guard: if build_request tried HTTP, importing a broken requests would fail.
    saved = sys.modules.pop("requests", None)
    sys.modules["requests"] = types.ModuleType("requests")  # no .post/.get attrs
    try:
        url, _, _ = vc.build_request("x", "p")
        assert url  # reached here => no network touched
    finally:
        if saved is not None:
            sys.modules["requests"] = saved
        else:
            sys.modules.pop("requests", None)


def test_env_override(monkeypatch):
    monkeypatch.setenv("VLLM_BASE_URL", "http://10.0.0.5:9001/v1")
    monkeypatch.setenv("VLLM_MODEL", "qwen-eval")
    url, _, payload = vc.build_request("x", "p")
    assert url == "http://10.0.0.5:9001/v1/chat/completions"
    assert payload["model"] == "qwen-eval"


# ---- call / health: faked HTTP layer mimicking vLLM -----------------------
class _Resp:
    def __init__(self, status=200, data=None):
        self.status_code = status
        self._data = data or {}
    def json(self):
        return self._data
    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


def _fake_requests(post_data=None, get_status=200):
    m = types.ModuleType("requests")
    def post(url, headers=None, data=None, timeout=None):
        return _Resp(200, post_data)
    def get(url, headers=None, timeout=None):
        return _Resp(get_status, {"data": [{"id": "vllm-local"}]})
    m.post, m.get = post, get
    return m


def test_call_parses_openai_response(monkeypatch):
    # vLLM returns the OpenAI chat shape exactly like this:
    resp = {"choices": [{"message": {"role": "assistant", "content": "step 1: restart pod"}}]}
    monkeypatch.setitem(sys.modules, "requests", _fake_requests(post_data=resp))
    out = vc.call("ignored", "diagnose the incident", max_tokens=128)
    assert out == "step 1: restart pod"


def test_call_handles_empty_content(monkeypatch):
    monkeypatch.setitem(sys.modules, "requests", _fake_requests(post_data={"choices": [{}]}))
    assert vc.call("x", "p") == ""


def test_health_true_when_models_200(monkeypatch):
    monkeypatch.setitem(sys.modules, "requests", _fake_requests(get_status=200))
    assert vc.health() is True


def test_health_false_on_error(monkeypatch):
    monkeypatch.setitem(sys.modules, "requests", _fake_requests(get_status=503))
    assert vc.health() is False


# ---- signature compatibility with agent.llm.call --------------------------
def test_signature_matches_agent_llm():
    import inspect
    repo = HERE.parents[3]   # .../rl
    sys.path.insert(0, str(repo))
    try:
        from agent.llm import call as ref_call
    except Exception:
        import pytest
        pytest.skip("agent.llm not importable in this env")
        return
    ref = list(inspect.signature(ref_call).parameters)
    ours = list(inspect.signature(vc.call).parameters)
    assert ref == ours, f"shim signature {ours} != agent.llm.call {ref}"
