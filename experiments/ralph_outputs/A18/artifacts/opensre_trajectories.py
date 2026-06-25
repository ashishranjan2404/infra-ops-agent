# opensre_trajectories.py
# HuggingFace `datasets` loading script for the OpenSRE Incident-Diagnosis Trajectories dataset.
#
# Usage (after the repo is pushed to the Hub):
#   from datasets import load_dataset
#   ds = load_dataset("<org>/opensre-incident-trajectories", split="train")
#   ds = load_dataset("<org>/opensre-incident-trajectories", "real", split="train")
#
# A loading script is NOT strictly required (a single .jsonl + a `configs:` block in the
# dataset card is enough for `datasets>=2.x`), but we ship it so consumers get:
#   * named configs (`all` / `synthetic` / `real`),
#   * an explicit, typed `features` schema (no inference surprises),
#   * a stable contract that survives schema drift.
#
# This script is self-contained: it reads the bundled `hud_trajectories.jsonl`.
import json

import datasets

_CITATION = """\
@misc{opensre_trajectories_2026,
  title  = {OpenSRE Incident-Diagnosis Trajectories},
  author = {SRE-Degrees RL Project},
  year   = {2026},
  howpublished = {HuggingFace Datasets},
}
"""

_DESCRIPTION = """\
Graded, multi-step SRE incident-diagnosis trajectories. A frozen LLM reads evidence through
diagnostic tools and states a root cause + category + fix, scored on substance vs ground truth.
197 trajectories across a weak->strong model set, split into `synthetic` (single-fault) and
`real` (verified real-world cascading outages with a misleading loud symptom and a trap action).
"""

_HOMEPAGE = "https://github.com/ashishranjan2404/infra-ops-agent"
_LICENSE = "apache-2.0"

# The data file ships alongside this script in the dataset repo root.
_DATA_FILE = "hud_trajectories.jsonl"


class OpenSRETrajectoriesConfig(datasets.BuilderConfig):
    """BuilderConfig for OpenSRE Trajectories.

    `source_filter` selects which split of trajectories to keep:
      None     -> all 197 records
      "synthetic" -> 83 single-fault records
      "real"      -> 114 real-world cascading-outage records
    """

    def __init__(self, source_filter=None, **kwargs):
        super().__init__(**kwargs)
        self.source_filter = source_filter


class OpenSRETrajectories(datasets.GeneratorBasedBuilder):
    """OpenSRE Incident-Diagnosis Trajectories."""

    VERSION = datasets.Version("1.0.0")

    BUILDER_CONFIGS = [
        OpenSRETrajectoriesConfig(
            name="all",
            version=VERSION,
            description="All 197 trajectories (synthetic + real).",
            source_filter=None,
        ),
        OpenSRETrajectoriesConfig(
            name="synthetic",
            version=VERSION,
            description="83 single-fault synthetic incident trajectories.",
            source_filter="synthetic",
        ),
        OpenSRETrajectoriesConfig(
            name="real",
            version=VERSION,
            description="114 verified real-world cascading-outage trajectories.",
            source_filter="real",
        ),
    ]
    DEFAULT_CONFIG_NAME = "all"

    def _info(self):
        features = datasets.Features(
            {
                "model": datasets.Value("string"),
                "trace_id": datasets.Value("string"),
                "scenario_id": datasets.Value("string"),
                "incident": datasets.Value("string"),
                "source": datasets.Value("string"),  # "synthetic" | "real"
                "reward": datasets.Value("float32"),
                "subscores": {
                    "root_cause_category": datasets.Value("float32"),
                    "evidence_keywords": datasets.Value("float32"),
                    "ruled_out_red_herrings": datasets.Value("float32"),
                    "remediation_tool": datasets.Value("float32"),
                },
                "n_tool_calls": datasets.Value("int32"),
                "tools_used": datasets.Sequence(datasets.Value("string")),
                "n_agent_steps": datasets.Value("int32"),
                "true_category": datasets.Value("string"),
                "difficulty": datasets.Value("int32"),
                "source_company": datasets.Value("string"),
                "source_url": datasets.Value("string"),
                "trap_actions": datasets.Sequence(datasets.Value("string")),
                "answer": datasets.Value("string"),
            }
        )
        return datasets.DatasetInfo(
            description=_DESCRIPTION,
            features=features,
            homepage=_HOMEPAGE,
            license=_LICENSE,
            citation=_CITATION,
        )

    def _split_generators(self, dl_manager):
        path = dl_manager.download(_DATA_FILE)
        return [
            datasets.SplitGenerator(
                name=datasets.Split.TRAIN,
                gen_kwargs={"path": path, "source_filter": self.config.source_filter},
            )
        ]

    def _generate_examples(self, path, source_filter):
        idx = 0
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                if source_filter is not None and rec.get("source") != source_filter:
                    continue
                sub = rec.get("subscores") or {}
                yield idx, {
                    "model": rec.get("model"),
                    "trace_id": rec.get("trace_id"),
                    "scenario_id": rec.get("scenario_id"),
                    "incident": rec.get("incident"),
                    "source": rec.get("source"),
                    "reward": rec.get("reward"),
                    "subscores": {
                        "root_cause_category": sub.get("root_cause_category"),
                        "evidence_keywords": sub.get("evidence_keywords"),
                        "ruled_out_red_herrings": sub.get("ruled_out_red_herrings"),
                        "remediation_tool": sub.get("remediation_tool"),
                    },
                    "n_tool_calls": rec.get("n_tool_calls"),
                    "tools_used": rec.get("tools_used") or [],
                    "n_agent_steps": rec.get("n_agent_steps"),
                    "true_category": rec.get("true_category"),
                    # `difficulty` is present only on real records; default 0 for synthetic.
                    "difficulty": rec.get("difficulty") if rec.get("difficulty") is not None else 0,
                    # `source_company`/`source_url`/`trap_actions` are real-only; empty for synthetic.
                    "source_company": rec.get("source_company") or "",
                    "source_url": rec.get("source_url") or "",
                    "trap_actions": rec.get("trap_actions") or [],
                    "answer": rec.get("answer"),
                }
                idx += 1
