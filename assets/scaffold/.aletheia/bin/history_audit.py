#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from git_trailers import AIOS_KEYS, parse_trailers, validate_trailer_values


STATE_BY_ACTION = {
    "truth.node.stabilize": "stable",
    "truth.node.weaken": "weakened",
    "truth.node.falsify": "falsified",
    "truth.node.archive": "archived",
}
IMPLEMENT_TARGET_PREFIXES = (
    ".aletheia/decisions/",
    ".aletheia/contracts/",
    ".aletheia/evidence/",
    ".aletheia/nodes/",
)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def run_git_log(root: Path, max_count: int) -> list[tuple[str, str]]:
    result = subprocess.run(
        ["git", "log", f"--max-count={max_count}", "--format=%H%x00%B%x00END%x00"],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        return []
    parts = result.stdout.split("\x00END\x00")
    commits: list[tuple[str, str]] = []
    for part in parts:
        part = part.strip("\n\x00")
        if not part:
            continue
        commit_hash, sep, message = part.partition("\x00")
        if sep:
            commits.append((commit_hash.strip(), message.strip()))
    commits.reverse()
    return commits


def unknown_aios_keys(message: str) -> list[str]:
    unknown: list[str] = []
    for line in message.splitlines():
        if not line.startswith("AIOS-") or ":" not in line:
            continue
        key = line.split(":", 1)[0].strip()
        if key not in AIOS_KEYS and key not in unknown:
            unknown.append(key)
    return unknown


def unsafe_path(path: str) -> bool:
    value = Path(path)
    return value.is_absolute() or ".." in value.parts


def ensure_node(nodes: dict[str, dict[str, object]], node_id: str) -> dict[str, object]:
    return nodes.setdefault(
        node_id,
        {
            "latest_state": None,
            "stable_commit": None,
            "evidence": [],
            "decision": [],
            "implements": [],
            "supersedes": [],
            "transitions": [],
        },
    )


def append_unique(values: list[str], new_values: list[str]) -> None:
    for value in new_values:
        if value not in values:
            values.append(value)


def node_list(node: dict[str, object], key: str) -> list[str]:
    values = node.setdefault(key, [])
    if not isinstance(values, list):
        values = []
        node[key] = values
    return values


def require_existing_refs(root: Path, commit_hash: str, node_id: str, kind: str, refs: list[str], errors: list[str]) -> None:
    for ref in refs:
        if unsafe_path(ref):
            errors.append(f"{commit_hash} {node_id} stable {kind} uses unsafe path: {ref}")
        elif not (root / ref).exists():
            errors.append(f"{commit_hash} {node_id} stable {kind} path missing: {ref}")


def validate_implements(root: Path, commit_hash: str, refs: list[str], errors: list[str]) -> None:
    for ref in refs:
        if unsafe_path(ref):
            errors.append(f"{commit_hash} AIOS-Implements uses unsafe path: {ref}")
        elif not ref.startswith(IMPLEMENT_TARGET_PREFIXES):
            errors.append(f"{commit_hash} AIOS-Implements target is outside allowed truth records: {ref}")
        elif not (root / ref).exists():
            errors.append(f"{commit_hash} AIOS-Implements target missing: {ref}")


def audit_history(root: Path, *, node_filter: str | None, max_count: int) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    nodes: dict[str, dict[str, object]] = {}
    implementation_links: list[dict[str, object]] = []

    for commit_hash, message in run_git_log(root, max_count):
        for key in unknown_aios_keys(message):
            warnings.append(f"{commit_hash} unknown AIOS trailer key: {key}")
        trailers = parse_trailers(message)
        if not trailers:
            continue
        errors.extend(f"{commit_hash} {error}" for error in validate_trailer_values(trailers))

        node_values = trailers.get("AIOS-Node", [])
        action = trailers.get("AIOS-Action", [None])[-1]
        state = trailers.get("AIOS-Node-State", [None])[-1] or STATE_BY_ACTION.get(action)
        evidence = trailers.get("AIOS-Evidence", [])
        decision = trailers.get("AIOS-Decision", [])
        implements = trailers.get("AIOS-Implements", [])
        supersedes = trailers.get("AIOS-Supersedes", [])

        validate_implements(root, commit_hash, implements, errors)
        if implements:
            implementation_links.append({"commit": commit_hash, "targets": implements})

        for node_id in node_values:
            if node_filter and node_id != node_filter:
                continue
            node = ensure_node(nodes, node_id)
            node["transitions"].append(
                {
                    "commit": commit_hash,
                    "action": action,
                    "state": state,
                    "tree_op": trailers.get("AIOS-Tree-Op", [None])[-1],
                }
            )
            if state:
                node["latest_state"] = state
            append_unique(node_list(node, "evidence"), evidence)
            append_unique(node_list(node, "decision"), decision)
            append_unique(node_list(node, "implements"), implements)
            append_unique(node_list(node, "supersedes"), supersedes)
            if state == "stable":
                node["stable_commit"] = commit_hash
                if action != "truth.node.stabilize":
                    errors.append(f"{commit_hash} {node_id} stable node requires AIOS-Action: truth.node.stabilize")
                if not evidence:
                    errors.append(f"{commit_hash} {node_id} stable node requires AIOS-Evidence")
                if not decision:
                    errors.append(f"{commit_hash} {node_id} stable node requires AIOS-Decision")
                if "pass" not in trailers.get("AIOS-Validation", []):
                    errors.append(f"{commit_hash} {node_id} stable node requires AIOS-Validation: pass")
                if "human-confirmed" not in trailers.get("AIOS-Review", []):
                    errors.append(f"{commit_hash} {node_id} stable node requires AIOS-Review: human-confirmed")
                require_existing_refs(root, commit_hash, node_id, "evidence", evidence, errors)
                require_existing_refs(root, commit_hash, node_id, "decision", decision, errors)

    payload = {
        "ok": not errors,
        "returncode": 0 if not errors else 1,
        "errors": errors,
        "warnings": warnings,
        "nodes": nodes,
        "implementation_links": implementation_links,
    }
    return payload


def print_markdown(payload: dict) -> None:
    print("# AletheiaOS Git Truth History Audit")
    print()
    print(f"- ok: {payload['ok']}")
    print(f"- errors: {len(payload['errors'])}")
    print(f"- warnings: {len(payload['warnings'])}")
    print(f"- nodes: {len(payload['nodes'])}")
    for node_id, node in payload["nodes"].items():
        print(f"- {node_id}: {node.get('latest_state') or 'unknown'}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit AletheiaOS Git truth-transition history.")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--node")
    parser.add_argument("--max-count", type=int, default=500)
    args = parser.parse_args()

    payload = audit_history(repo_root(), node_filter=args.node, max_count=args.max_count)
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print_markdown(payload)
    return int(payload["returncode"])


if __name__ == "__main__":
    raise SystemExit(main())
