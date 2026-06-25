# SRE-Degrees — Narration Script

Voice: calm, technical, ~140 wpm. Total ~150 words for a 90s cut. Cue IDs map to
the storyboard rows.

**N1 (title, 0:00):**
"Production incidents don't resolve themselves. SRE-Degrees asks: can a small policy,
with no fine-tuning, diagnose and fix a cascading failure — and can we grade it
without it gaming the reward?"

**N2 (page, 0:06):**
"We open a real incident. The search API is failing seventy percent of requests.
This runs on our deterministic cascade simulator — metrics are functions of a hidden
fault and the topology, never set by hand."

**N3 (diagnose, 0:14):**
"The agent localizes the degradation. Critically, the true root-cause kind is hidden
from it — it has to earn the diagnosis from the metric shape."

**N4 (band-aid, 0:24):**
"First it tries the tempting move: restart the pod. Watch the metrics... nothing
changes. Our oracle checks the actual hidden fault, not just the dashboard — and the
root is still active. A restart can't fix CPU starvation."

**N5 (feedback, 0:38):**
"That failure becomes feedback. This is the refinement loop — the agent learns from
a grounded signal, not a guess."

**N6 (causal fix, 0:40):**
"Now it scales the deployment. Error rate drops to zero, SLOs go green, and the
oracle confirms: the root is cleared. Resolved — in one refinement."

**N7 (summary, 0:52):**
"Two attempts, one fix, root-cause-verified. No metric-masking, no lucky guess."

**N8 (architecture, 1:02):**
"Underneath: one transition kernel over a typed dependency graph makes the cascade
emergent, a Thompson-sampling tree proposes refinements, and a deterministic oracle
grades resolution. The oracle reads the hidden fault, so masking the metrics never
counts as a win — that's our defense against reward hacking."

**N9 (close, 1:18):**
"SRE-Degrees: code-as-policy, on a simulator you can't fool. Code and scenarios in
the repo."
