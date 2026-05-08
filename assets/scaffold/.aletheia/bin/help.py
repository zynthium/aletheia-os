#!/usr/bin/env python3
from __future__ import annotations


CAPABILITIES = [
    (
        "Initialize project truth",
        "Set up `.aletheia/` for a repository and guide first-run bootstrap.",
        [
            "python3 .aletheia/bin/model_gate.py --task-class bootstrap_finalize --provider <provider> --model-id <model_id> --tier C3 --operator-approved --record --objective \"Initialize AletheiaOS\"",
            "python3 .aletheia/bin/source_inventory.py",
            "python3 .aletheia/bin/guided_bootstrap.py --inspect --json",
            "python3 .aletheia/bin/guided_bootstrap.py --objective \"Initialize AletheiaOS\"",
            "python3 .aletheia/bin/bootstrap_finalize.py --inspect --json",
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
        "Build stable or prompt-ready context, with optional run/session context at the end.",
        [
            "python3 .aletheia/bin/context_pack.py",
            "python3 .aletheia/bin/context_pack.py --with-runtime",
            "python3 .aletheia/bin/system_context.py",
            "python3 .aletheia/bin/system_context.py --with-runtime",
        ],
    ),
    (
        "Refresh status",
        "Read active state, validation, record counts, runtime gate status, generated-output boundaries, and hook-free next actions on demand.",
        [
            "python3 .aletheia/bin/action.py list --json",
            "python3 .aletheia/bin/action.py next --json",
            "python3 .aletheia/bin/action.py explain truth.validate --json",
            "python3 .aletheia/bin/action.py run truth.validate --json",
            "python3 .aletheia/bin/capability_audit.py",
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
            "python3 .aletheia/bin/model_gate.py --registry deprecate <name> --reason \"Superseded\"",
            "python3 .aletheia/bin/model_gate.py --registry remove <name>",
            "python3 .aletheia/bin/model_gate.py --registry deny <model_id> --reason \"Reason\"",
        ],
    ),
    (
        "Create truth records",
        "Create, read, update, and archive records, fixed truth files, and incubating orphan entries.",
        [
            "python3 .aletheia/bin/truth_record.py list evidence",
            "python3 .aletheia/bin/truth_record.py create evidence --id EV-0001 --title \"Claim title\"",
            "python3 .aletheia/bin/truth_record.py show evidence EV-0001",
            "python3 .aletheia/bin/truth_record.py update evidence EV-0001 --status active",
            "python3 .aletheia/bin/truth_record.py archive evidence EV-0001 --reason \"Superseded by stronger evidence\"",
            "python3 .aletheia/bin/truth_record.py show capability-map current",
            "python3 .aletheia/bin/truth_record.py show charter current",
            "python3 .aletheia/bin/truth_record.py show tree-governance current",
            "python3 .aletheia/bin/truth_record.py show user-preferences current",
            "python3 .aletheia/bin/truth_record.py update active-state current --section \"Active frontier\" --content \"...\"",
            "python3 .aletheia/bin/truth_record.py create orphan --id ORPH-0001 --title \"Unmounted claim\"",
            "python3 .aletheia/bin/truth_record.py list orphan --json",
            "python3 .aletheia/bin/truth_record.py show orphan ORPH-0001 --json",
            "python3 .aletheia/bin/truth_record.py update orphan ORPH-0001 --status reviewed",
            "python3 .aletheia/bin/truth_record.py update orphan ORPH-0001 --candidate-parent root --source-ref .aletheia/evidence/EV-0001.md --next-review 2099-01-01 --evidence-needed \"Confirm with source inventory\" --disposition attach",
            "python3 .aletheia/bin/truth_record.py archive orphan ORPH-0001 --reason \"Disposition resolved\"",
            "python3 .aletheia/bin/truth_record.py archive runtime-policy current --reason \"Superseded policy\"",
        ],
    ),
    (
        "Validate and checkpoint",
        "Check project truth, then create an attributed checkpoint when the state is coherent.",
        [
            "python3 .aletheia/bin/validate.py",
            "python3 .aletheia/bin/checkpoint.py",
            "python3 .aletheia/bin/checkpoint.py --dry-run",
        ],
    ),
    (
        "Monitor overview",
        "Generate a local HTML/JSON overview once or refresh it repeatedly while reviewing state.",
        [
            "python3 .aletheia/bin/overview.py",
            "python3 .aletheia/bin/overview.py --watch",
            "python3 .aletheia/bin/overview.py --public-docs",
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
    print("- JSON fixed truth files can be shown or archived through `truth_record.py`; structured edits stay with dedicated commands or direct reviewed edits.")
    print("- On hosts without automatic hooks, run `preflight.py --json`, `status.py --json`, `validate.py`, and `checkpoint.py --dry-run` explicitly.")
    print("- `.aletheia/runtime/`, `.aletheia/overview/`, and `.aletheia/source_inventory/` are generated/runtime outputs, not durable truth by default.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
