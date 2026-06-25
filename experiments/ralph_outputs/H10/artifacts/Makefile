# =============================================================================
# SRE-Degrees / REx — common operations Makefile  (task H10)
#
# Wired to the ACTUAL repo commands. All Python entrypoints are invoked as
# modules (python3 -m rex.<x>) or scripts (python3 experiments/<x>.py) from the
# repo root, matching how they are documented in their own docstrings.
#
# Usage:
#   make help                 # list targets
#   make test                 # full pytest suite
#   make eval-smoke           # tiny, fast eval (1 incident/family, 1 seed)
#   make eval MODEL=glm-5p2   # real pass@k eval
#   make validate-scenarios   # re-validate the generated incident benchmark
#
# Dry-run any target without executing:  make -n <target>
#
# Many targets call FROZEN frontier models through the HUD inference gateway and
# therefore need HUD_API_KEY in the environment:
#   set -a; source ~/.zshrc; set +a
# =============================================================================

# ---- locate repo root (this Makefile lives in experiments/ralph_outputs/H10/
#      artifacts/, so the repo root is four levels up). Override with REPO=... .
MAKEFILE_PATH := $(abspath $(lastword $(MAKEFILE_LIST)))
REPO          ?= $(abspath $(dir $(MAKEFILE_PATH))/../../../..)

PYTHON        ?= python3
PYTEST        ?= $(PYTHON) -m pytest

# ---- tunables (override on the command line, e.g. `make eval MODEL=opus-4p8`)
MODEL         ?= glm-5p2
CONDITIONS    ?= zero_shot,best_of_n,retry_realistic,rex,rex_no_oracle
PER_FAMILY    ?= 5
SEEDS         ?= 5
MAX_WORKERS   ?= 8

# Run every recipe from the repo root so module/relative paths resolve.
.DEFAULT_GOAL := help
.PHONY: help test eval eval-smoke eval-frontier train train-smoke \
        generate-scenarios validate-scenarios figures clean

help: ## Show this help
	@echo "SRE-Degrees / REx — make targets (REPO=$(REPO))"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_PATH) \
	  | sort \
	  | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}'

# ----------------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------------
test: ## Run the full pytest suite
	cd $(REPO) && $(PYTEST) -q tests

# ----------------------------------------------------------------------------
# Evaluation  (rex/eval_pass_at_k.py — deterministic-judge pass@k)
# ----------------------------------------------------------------------------
eval: ## Real pass@k eval: make eval MODEL=glm-5p2 PER_FAMILY=5 SEEDS=5
	cd $(REPO) && $(PYTHON) -m rex.eval_pass_at_k \
	  --model $(MODEL) \
	  --conditions $(CONDITIONS) \
	  --per-family $(PER_FAMILY) \
	  --seeds $(SEEDS) \
	  --max-workers $(MAX_WORKERS)

eval-smoke: ## Fast eval sanity check (1 incident/family, 1 seed, 2 conditions)
	cd $(REPO) && $(PYTHON) -m rex.eval_pass_at_k \
	  --model $(MODEL) \
	  --conditions zero_shot,rex \
	  --per-family 1 \
	  --seeds 1 \
	  --max-workers 2

eval-frontier: ## Baseline-vs-REx across many frontier models
	cd $(REPO) && $(PYTHON) -m rex.eval_pass_at_k \
	  --frontier \
	  --per-family $(PER_FAMILY) \
	  --seeds $(SEEDS) \
	  --max-workers $(MAX_WORKERS)

# ----------------------------------------------------------------------------
# Training  (open Qwen models via the HUD Tinker provider — run under .venv-hud)
# ----------------------------------------------------------------------------
HUD_PY        ?= $(REPO)/.venv-hud/bin/python
TRAIN_MODEL   ?= opensre-qwen3-8b
TRAIN_TASKS   ?= 0,1,3,10
TRAIN_GROUP   ?= 6
TRAIN_STEPS   ?= 30

train: ## RFT/GRPO training run on the opensre incident env (needs HUD_API_KEY)
	cd $(REPO)/opensre-traj && $(HUD_PY) train_rft.py \
	  --model $(TRAIN_MODEL) \
	  --tasks $(TRAIN_TASKS) \
	  --group $(TRAIN_GROUP) \
	  --steps $(TRAIN_STEPS) \
	  --out runs/train_$(TRAIN_MODEL).jsonl

train-smoke: ## Cheap fail-fast training smoke (2 tasks, 1 step)
	cd $(REPO)/opensre-traj && $(HUD_PY) train_rft.py \
	  --model $(TRAIN_MODEL) \
	  --tasks 0,1 \
	  --group 4 \
	  --steps 1 \
	  --smoke

# ----------------------------------------------------------------------------
# Scenario generation / validation  (experiments/build_incidents.py)
# ----------------------------------------------------------------------------
generate-scenarios: ## (Re)emit + self-validate the CIDG incident benchmark
	cd $(REPO) && $(PYTHON) experiments/build_incidents.py

validate-scenarios: ## Validate the existing generated benchmark only
	cd $(REPO) && $(PYTHON) experiments/build_incidents.py --validate

# ----------------------------------------------------------------------------
# Figures  (curriculum chart + paper result tables)
# ----------------------------------------------------------------------------
figures: ## Render charts/tables (curriculum_rewards.png + result tables)
	cd $(REPO) && $(PYTHON) -m rex.chart
	cd $(REPO) && $(PYTHON) experiments/generate_table_pngs.py

# ----------------------------------------------------------------------------
# Housekeeping
# ----------------------------------------------------------------------------
clean: ## Remove Python bytecode caches
	cd $(REPO) && find . -type d -name __pycache__ -not -path './.venv*/*' \
	  -exec rm -rf {} + 2>/dev/null || true
