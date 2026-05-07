#!/usr/bin/env python3
from __future__ import annotations


CAPABILITIES = [
    (
        "Initialize project truth",
        "Set up `.aletheia/` for a repository and guide first-run bootstrap.",
        [
            "python3 .aletheia/bin/model_gate.py --task-class bootstrap_finalize --provider <provider> --model-id <model_id> --tier C3 --operator-approved --record --objective \"Initialize AletheiaOS\"",
            "python3 .aletheia/bin/source_inventory.py",
            "python3 .aletheia/bin/guided_bootstrap.py --objective \"Initialize AletheiaOS\"",
            "python3 .aletheia/bin/bootstrap_finalize.py",
        ],
    ),
    (
        "Orient on current truth",
        "Load mission, active state, graph, skeleton, constraints, risks, capabilities, and record inventory.",
        [
            "python3 .aletheia/bin/orient.py",
            "python3 .aletheia/bin/orient.py --with-runtime",
            "python3 .aletheia/bin/orient.py --static",
        ],
    ),
    (
        "Refresh context",
        "Build a stable context pack, with optional run/session context at the end.",
        ["python3 .aletheia/bin/context_pack.py", "python3 .aletheia/bin/context_pack.py --with-runtime"],
    ),
    (
        "Refresh status",
        "Read active state, validation, record counts, runtime gate status, and hook-free preflight state on demand.",
        [
            "python3 .aletheia/bin/status.py",
            "python3 .aletheia/bin/status.py --json",
            "python3 .aletheia/bin/preflight.py",
            "python3 .aletheia/bin/preflight.py --json",
        ],
    ),
    (
        "Manage model registry",
        "List, register, enable, disable, deny, and undeny models used by model gate decisions.",
        [
            "python3 .aletheia/bin/model_gate.py --registry list",
            "python3 .aletheia/bin/model_gate.py --registry register <name> --provider <provider> --model-id <model_id> --tier C3",
            "python3 .aletheia/bin/model_gate.py --registry disable <name>",
            "python3 .aletheia/bin/model_gate.py --registry deny <model_id> --reason \"Reason\"",
        ],
    ),
    (
        "Create truth records",
        "Create, read, update, and archive evidence, decisions, contracts, hypotheses, risks, nodes, session notes, and agent runs.",
        [
            "python3 .aletheia/bin/truth_record.py list evidence",
            "python3 .aletheia/bin/truth_record.py create evidence --id EV-0001 --title \"Claim title\"",
            "python3 .aletheia/bin/truth_record.py show evidence EV-0001",
            "python3 .aletheia/bin/truth_record.py update evidence EV-0001 --status active",
            "python3 .aletheia/bin/truth_record.py archive evidence EV-0001 --reason \"Superseded by stronger evidence\"",
        ],
    ),
    (
        "Validate and checkpoint",
        "Check project truth, then create an attributed checkpoint when the state is coherent.",
        [
            "python3 .aletheia/bin/validate.py",
            "python3 .aletheia/bin/checkpoint.py",
        ],
    ),
    (
        "Review truth alignment",
        "Use read-focused review agents for truth, evidence, and architecture drift checks.",
        [
            "truth-auditor",
            "evidence-curator",
            "architecture-reviewer",
        ],
    ),
]


def main() -> int:
    print("# AletheiaOS Capabilities")
    print()
    print("Use this when you want to know what the agent can help accomplish in this repository.")
    print()
    print("## What you can ask")
    print()
    for title, description, _commands in CAPABILITIES:
        print(f"- **{title}**: {description}")
    print()
    print("## Runtime commands")
    print()
    for title, _description, commands in CAPABILITIES:
        print(f"### {title}")
        for command in commands:
            print(f"- `{command}`")
        print()
    print("## Policy notes")
    print()
    print("- Codex marketplace registration is scripted; enabling the plugin happens in `/plugins`.")
    print("- Truth record removal is archive-only by default; no permanent delete command is provided.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
