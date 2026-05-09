#!/usr/bin/env python3
from __future__ import annotations


ALLOWED_ACTIONS = {
    "truth.bootstrap.initialize",
    "truth.tree.transition",
    "truth.node.stabilize",
    "truth.node.weaken",
    "truth.node.falsify",
    "truth.node.archive",
    "engineering.implements_truth",
}
ALLOWED_TREE_OPS = {
    "bootstrap",
    "incubate",
    "attach_orphan",
    "insert_parent",
    "split_node",
    "merge_nodes",
    "move_subtree",
    "promote_node",
    "demote_node",
    "archive_branch",
}
ALLOWED_NODE_STATES = {"candidate", "stable", "weakened", "falsified", "archived"}
ALLOWED_VALIDATION = {"pass"}
ALLOWED_REVIEW = {"human-confirmed", "agent-reviewed", "not-required"}

AIOS_KEYS = {
    "AIOS-Action",
    "AIOS-Tree-Op",
    "AIOS-Node",
    "AIOS-Parent",
    "AIOS-Node-State",
    "AIOS-Evidence",
    "AIOS-Decision",
    "AIOS-Implements",
    "AIOS-Supersedes",
    "AIOS-Validation",
    "AIOS-Review",
}


def parse_trailers(message: str) -> dict[str, list[str]]:
    trailers: dict[str, list[str]] = {}
    for line in message.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        if key not in AIOS_KEYS:
            continue
        trailers.setdefault(key, []).append(value.strip())
    return trailers


def build_aios_trailers(
    *,
    action: str | None,
    tree_op: str | None,
    node: str | None,
    parent: str | None,
    node_state: str | None,
    evidence: list[str],
    decision: list[str],
    implements: list[str],
    supersedes: list[str],
    validation: str | None,
    review: str | None,
) -> str:
    fields: list[tuple[str, str | None]] = [
        ("AIOS-Action", action),
        ("AIOS-Tree-Op", tree_op),
        ("AIOS-Node", node),
        ("AIOS-Parent", parent),
        ("AIOS-Node-State", node_state),
    ]
    fields.extend(("AIOS-Evidence", value) for value in evidence)
    fields.extend(("AIOS-Decision", value) for value in decision)
    fields.extend(("AIOS-Implements", value) for value in implements)
    fields.extend(("AIOS-Supersedes", value) for value in supersedes)
    fields.extend(
        [
            ("AIOS-Validation", validation),
            ("AIOS-Review", review),
        ]
    )
    lines = [f"{key}: {value}" for key, value in fields if value]
    return "\n".join(lines)


def validate_trailer_values(trailers: dict[str, list[str]]) -> list[str]:
    checks = {
        "AIOS-Action": ALLOWED_ACTIONS,
        "AIOS-Tree-Op": ALLOWED_TREE_OPS,
        "AIOS-Node-State": ALLOWED_NODE_STATES,
        "AIOS-Validation": ALLOWED_VALIDATION,
        "AIOS-Review": ALLOWED_REVIEW,
    }
    errors: list[str] = []
    for key, allowed in checks.items():
        for value in trailers.get(key, []):
            if value not in allowed:
                errors.append(f"{key} has unsupported value: {value}")
    return errors
