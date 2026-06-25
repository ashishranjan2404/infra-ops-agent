# 10 — Feedback for the next task

The biggest leverage in this repo is that `agent/llm.py` already speaks OpenAI-compatible
chat via its `gateway` provider, so any "add a new model backend" task (vLLM, Ollama,
TGI, llama.cpp) is really just *point that same wire format at a new base URL* — reuse it,
don't reinvent parsing. The no-core-edit rule under parallel Ralph-Loop is satisfiable
cleanly by shipping a standalone drop-in module whose **signature is asserted equal to the
core function** (a cheap test that catches drift), plus a documented `.patch` as the merge
path — do both, and label the patch as a guide since hand-written diffs won't `git apply`.
When a task needs hardware this host lacks (GPU here), validate against the *contract*:
unit-mock the HTTP layer AND run one end-to-end pass against a tiny stdlib mock server to
prove real sockets work — that combination is far more convincing than mocks alone and
costs five minutes. Finally, be loud in the critique about the difference between a
*throughput tool* and a *quality/scientific claim*: swapping to a small local model speeds
eval but changes the policy, so frame it as an added weak anchor, never as "the same
experiment, faster."
