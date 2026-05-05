#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path


STATE_FILES = [
    ".aletheia/state/ACTIVE_STATE.md",
    ".aletheia/state/SYSTEM_GRAPH.yaml",
    ".aletheia/state/SKELETON.yaml",
    ".aletheia/state/RISK_REGISTER.md",
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
  <h2>Records</h2>
  <pre>{escape(json.dumps(status['records'], indent=2))}</pre>
</body>
</html>
"""
    path.write_text(html, encoding="utf-8")


def main() -> int:
    root = repo_root()
    output = root / "docs" / "overview"
    output.mkdir(parents=True, exist_ok=True)
    status = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo": str(root),
        "state_files": [file_state(root, rel) for rel in STATE_FILES],
        "records": {
            "decisions": list_records(root, ".aletheia/decisions"),
            "evidence": list_records(root, ".aletheia/evidence"),
            "contracts": list_records(root, ".aletheia/contracts"),
            "risks": list_records(root, ".aletheia/risks"),
            "agent_runs": list_records(root, ".aletheia/agent_runs"),
        },
    }
    (output / "status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    write_index(output / "index.html", status)
    print(f"overview written: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
