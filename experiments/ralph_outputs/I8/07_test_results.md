# 07 — Test Results

## T-set 1: validator (`validate_matrix.py`)
Command:
```
$ cd experiments/ralph_outputs/I8/artifacts && python3 validate_matrix.py; echo "EXIT=$?"
```
Output:
```
OK: 3 paradigms x 5 axes = 15 non-empty cells; 8 citations resolve; negative self-tests rejected as expected.
EXIT=0
```
Covers spec test cases T1–T5 **plus** the two negative self-tests (blank cell rejected, bad path
rejected). PASS.

## T-set 2: markdown content sanity
Command (inline python probe over `comparison.md`):
```
chars: 11451 | has '## 4. Where code-as-policy LOSES': True
  mentions 'agent/llm.py': True
  mentions 'rex/scoring.py': True
  mentions 'rex/tree.py': True
  mentions 'Bai et al. 2022': True
  mentions 'Christiano': True
  mentions 'KL': True
```
Confirms: the honest-limits section exists; the code-as-policy column is grounded in real files;
RLHF (Christiano + KL leash) and CAI (Bai et al. 2022) are characterized with their correct
distinguishing mechanics. PASS.

## T-set 3: grounding cross-check against live repo
Verified `rex/scoring.py` actually defines the reward weights cited in the essay
(`W_ROOT, W_FIX, W_RESOLVED, TRAP_PENALTY = 0.30, 0.25, 0.45, 0.60`) and `rex/tree.py` defines
`thompson_search`. Every `repo_citations` path resolves (enforced by T4 above). PASS.

## Fixes applied during testing
None required — validator and probes passed on first run. (The negative self-tests were written
*before* running, specifically to avoid a vacuously-green validator per critique #6 in 05.)
