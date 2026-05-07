#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from html import escape
from pathlib import Path


STATE_FILES = [
    ".aletheia/state/ACTIVE_STATE.md",
    ".aletheia/state/SYSTEM_GRAPH.yaml",
    ".aletheia/state/SKELETON.yaml",
    ".aletheia/state/RISK_REGISTER.md",
    ".aletheia/state/FRONTIER_BOARD.md",
    ".aletheia/state/GLOSSARY.md",
    ".aletheia/state/DOMAIN_PROFILE.md",
]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def list_records(root: Path, rel: str) -> list[str]:
    path = root / rel
    if not path.exists():
        return []
    return sorted(str(item.relative_to(root)) for item in path.glob("*") if item.is_file() and item.name != ".gitkeep")


def file_state(root: Path, rel: str) -> dict:
    path = root / rel
    return {
        "path": rel,
        "exists": path.exists(),
        "size": path.stat().st_size if path.exists() else None,
    }


def recent_changes(root: Path, limit: int = 5) -> list[dict]:
    path = root / ".aletheia" / "runtime" / "change_log.jsonl"
    if not path.exists():
        return []
    changes: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines()[-limit:]:
        try:
            data = json.loads(line)
        except Exception as exc:
            changes.append({"invalid": str(exc), "raw": line})
            continue
        if isinstance(data, dict):
            changes.append(data)
        else:
            changes.append({"invalid": "expected JSON object", "raw": line})
    return changes


def count_skeleton_nodes(root: Path) -> int:
    path = root / ".aletheia" / "state" / "SKELETON.yaml"
    if not path.exists():
        return 0
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.startswith("  ") and line.endswith(":"))


def count_orphans(root: Path) -> int:
    path = root / ".aletheia" / "state" / "ORPHANS.yaml"
    if not path.exists():
        return 0
    text = path.read_text(encoding="utf-8")
    if "orphans: []" in text:
        return 0
    return sum(1 for line in text.splitlines() if line.startswith("  - id:"))


def tree_health(root: Path, validation: dict) -> dict:
    combined = f"{validation.get('stdout', '')}\n{validation.get('stderr', '')}"
    signals = [
        line.strip(" -")
        for line in combined.splitlines()
        if any(term in line.lower() for term in ["skeleton", "orphan", "tree"])
    ]
    return {
        "skeleton_nodes": count_skeleton_nodes(root),
        "orphan_count": count_orphans(root),
        "signals": signals,
    }


def write_index(path: Path, status: dict) -> None:
    rows = []
    for state in status["state_files"]:
        rows.append(
            f"<tr><td>{escape(state['path'])}</td><td>{escape(str(state['exists']))}</td><td>{escape(str(state['size']))}</td></tr>"
        )
    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>AletheiaOS Overview</title>
  <style>
    body {{ font-family: ui-sans-serif, system-ui, sans-serif; margin: 2rem; line-height: 1.5; }}
    code, pre {{ background: #f5f5f5; padding: 0.15rem 0.3rem; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #ddd; padding: 0.45rem; text-align: left; }}
  </style>
</head>
<body>
  <h1>AletheiaOS Overview</h1>
  <p>Generated at {escape(status['generated_at'])}</p>
  <h2>State files</h2>
  <table>
    <tr><th>Path</th><th>Exists</th><th>Size</th></tr>
    {''.join(rows)}
  </table>
  <h2>Validation</h2>
  <pre>{escape(json.dumps(status['validation'], indent=2))}</pre>
  <h2>Tree health</h2>
  <pre>{escape(json.dumps(status['tree_health'], indent=2))}</pre>
  <h2>Records</h2>
  <pre>{escape(json.dumps(status['records'], indent=2))}</pre>
  <h2>Recent changes</h2>
  <pre>{escape(json.dumps(status['recent_changes'], indent=2))}</pre>
</body>
</html>
"""
    path.write_text(html, encoding="utf-8")


def validation_state(root: Path) -> dict:
    result = subprocess.run(
        [sys.executable, ".aletheia/bin/validate.py"],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return {
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def ensure_output_dir(path: Path) -> int:
    if path.exists() and not path.is_dir():
        print(f"overview output path exists and is not a directory: {path}", file=sys.stderr)
        return 1
    path.mkdir(parents=True, exist_ok=True)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate an AletheiaOS overview.")
    parser.add_argument("--public-docs", action="store_true", help="Write overview to docs/overview instead of .aletheia/overview")
    parser.add_argument("--watch", action="store_true", help="Refresh overview repeatedly for local UI monitoring")
    parser.add_argument("--interval", type=float, default=2.0, help="Seconds between watch refreshes")
    parser.add_argument("--iterations", type=int, default=0, help="Number of watch refreshes; 0 means run until interrupted")
    args = parser.parse_args()

    root = repo_root()
    output = root / "docs" / "overview" if args.public_docs else root / ".aletheia" / "overview"
    rc = ensure_output_dir(output)
    if rc != 0:
        return rc
    iteration = 0
    while True:
        iteration += 1
        validation = validation_state(root)
        status = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "repo": str(root),
            "refresh": {
                "mode": "watch" if args.watch else "single",
                "iteration": iteration,
            },
            "state_files": [file_state(root, rel) for rel in STATE_FILES],
            "validation": validation,
            "tree_health": tree_health(root, validation),
            "records": {
                "decisions": list_records(root, ".aletheia/decisions"),
                "evidence": list_records(root, ".aletheia/evidence"),
                "contracts": list_records(root, ".aletheia/contracts"),
                "hypotheses": list_records(root, ".aletheia/hypotheses"),
                "nodes": list_records(root, ".aletheia/nodes"),
                "risks": list_records(root, ".aletheia/risks"),
                "agent_runs": list_records(root, ".aletheia/agent_runs"),
            },
            "recent_changes": recent_changes(root),
        }
        (output / "status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
        write_index(output / "index.html", status)
        print(f"overview written: {output}")
        if not args.watch or (args.iterations and iteration >= args.iterations):
            return 0
        time.sleep(max(args.interval, 0))


if __name__ == "__main__":
    raise SystemExit(main())
