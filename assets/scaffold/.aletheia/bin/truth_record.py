#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path


@dataclass(frozen=True)
class EntityConfig:
    directory: str
    template: str | None
    suffix: str
    writable: bool = True


ENTITY_CONFIG = {
    "agent-run": EntityConfig("agent_runs", None, ".json", writable=False),
    "agent-runs": EntityConfig("agent_runs", None, ".json", writable=False),
    "agent_runs": EntityConfig("agent_runs", None, ".json", writable=False),
    "contract": EntityConfig("contracts", "CONTRACT.md", ".md"),
    "contracts": EntityConfig("contracts", "CONTRACT.md", ".md"),
    "decision": EntityConfig("decisions", "DECISION.md", ".md"),
    "decisions": EntityConfig("decisions", "DECISION.md", ".md"),
    "evidence": EntityConfig("evidence", "EVIDENCE.md", ".md"),
    "hypothesis": EntityConfig("hypotheses", "HYPOTHESIS.md", ".md"),
    "hypotheses": EntityConfig("hypotheses", "HYPOTHESIS.md", ".md"),
    "node": EntityConfig("nodes", "NODE.yaml", ".yaml"),
    "nodes": EntityConfig("nodes", "NODE.yaml", ".yaml"),
    "risk": EntityConfig("risks", "RISK.md", ".md"),
    "risks": EntityConfig("risks", "RISK.md", ".md"),
    "session-note": EntityConfig("session_notes", "SESSION_NOTE.md", ".md"),
    "session-notes": EntityConfig("session_notes", "SESSION_NOTE.md", ".md"),
    "session_notes": EntityConfig("session_notes", "SESSION_NOTE.md", ".md"),
}
ID_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+$")


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def entity_config(entity: str) -> EntityConfig:
    config = ENTITY_CONFIG.get(entity)
    if config is None:
        valid = ", ".join(sorted(ENTITY_CONFIG))
        raise ValueError(f"unknown truth record entity: {entity}. Valid entities: {valid}")
    return config


def validate_record_id(record_id: str) -> str:
    normalized = record_id.strip()
    if not normalized or not ID_PATTERN.fullmatch(normalized):
        raise ValueError("record id must contain only letters, numbers, dot, underscore, or hyphen")
    return normalized


def record_path(root: Path, entity: str, record_id: str) -> Path:
    config = entity_config(entity)
    normalized = validate_record_id(record_id)
    if normalized.endswith(config.suffix):
        name = normalized
    else:
        name = normalized + config.suffix
    path = root / ".aletheia" / config.directory / name
    resolved_root = (root / ".aletheia" / config.directory).resolve()
    resolved_path = path.resolve()
    if resolved_path != resolved_root and resolved_root not in resolved_path.parents:
        raise ValueError("record path escapes truth record directory")
    return path


def template_text(root: Path, entity: str) -> str:
    config = entity_config(entity)
    if config.template is None:
        raise ValueError(f"truth record entity is read-only: {entity}")
    path = root / ".aletheia" / "templates" / config.template
    if not path.exists():
        raise ValueError(f"missing template: {path.relative_to(root).as_posix()}")
    return path.read_text(encoding="utf-8")


def apply_template(template: str, title: str, record_id: str) -> str:
    today = date.today().isoformat()
    text = template
    replacements = {
        "<title>": title,
        "<boundary name>": title,
        "TITLE": title,
        "YYYY-MM-DD": today,
        "HYP-0001": record_id,
        "node_id": record_id,
        "Node title": title,
        "<claim>": title,
        "<node id>": "root",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def emit_json(payload: dict) -> None:
    print(json.dumps(payload, indent=2))


def list_records(root: Path, entity: str, as_json: bool = False) -> int:
    config = entity_config(entity)
    directory = root / ".aletheia" / config.directory
    if not directory.exists():
        if as_json:
            emit_json({"action": "list", "entity": entity, "records": []})
            return 0
        print("None")
        return 0
    records = sorted(
        path
        for path in directory.glob("*")
        if path.is_file() and path.name not in {".gitkeep", "INDEX.md"}
    )
    rel_records = [relative(path, root) for path in records]
    if as_json:
        emit_json({"action": "list", "entity": entity, "records": rel_records})
        return 0
    if not records:
        print("None")
        return 0
    for rel in rel_records:
        print(rel)
    return 0


def create_record(root: Path, entity: str, record_id: str, title: str, as_json: bool = False) -> int:
    config = entity_config(entity)
    if not config.writable:
        print(f"truth record entity is read-only: {entity}", file=sys.stderr)
        return 1
    path = record_path(root, entity, record_id)
    if path.exists():
        print(f"truth record already exists: {path.relative_to(root).as_posix()}", file=sys.stderr)
        return 1
    path.parent.mkdir(parents=True, exist_ok=True)
    text = apply_template(template_text(root, entity), title, validate_record_id(record_id))
    path.write_text(text.rstrip() + "\n", encoding="utf-8")
    rel = relative(path, root)
    if as_json:
        emit_json({"action": "create", "entity": entity, "path": rel})
    else:
        print(f"created truth record: {rel}")
    return 0


def show_record(root: Path, entity: str, record_id: str, as_json: bool = False) -> int:
    path = record_path(root, entity, record_id)
    if not path.exists():
        print(f"truth record not found: {path.relative_to(root).as_posix()}", file=sys.stderr)
        return 1
    content = path.read_text(encoding="utf-8").rstrip()
    if as_json:
        emit_json({"action": "show", "entity": entity, "path": relative(path, root), "content": content})
    else:
        print(content)
    return 0


def archive_record(root: Path, entity: str, record_id: str, reason: str, as_json: bool = False) -> int:
    config = entity_config(entity)
    if not config.writable:
        print(f"truth record entity is read-only: {entity}", file=sys.stderr)
        return 1
    path = record_path(root, entity, record_id)
    if not path.exists():
        print(f"truth record not found: {path.relative_to(root).as_posix()}", file=sys.stderr)
        return 1
    text = path.read_text(encoding="utf-8").rstrip()
    lines = text.splitlines()
    status_line = "status: archived" if config.suffix in {".yaml", ".yml"} else "Status: archived"
    archive_lines = ["", "archive:", f"  reason: {reason}", f"  archived_on: {date.today().isoformat()}"]
    if config.suffix == ".md":
        archive_lines = ["", "## Archive", "", f"Archive reason: {reason}", f"Archived on: {date.today().isoformat()}"]

    replaced_status = replace_status(lines, status_line)
    if not replaced_status:
        insert_at = 1 if config.suffix == ".md" and lines and lines[0].startswith("# ") else 0
        if config.suffix == ".md":
            lines.insert(insert_at, "")
            lines.insert(insert_at + 1, status_line)
        else:
            lines.insert(insert_at, status_line)
    lines.extend(archive_lines)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    rel = relative(path, root)
    if as_json:
        emit_json({"action": "archive", "entity": entity, "path": rel, "reason": reason})
    else:
        print(f"archived truth record: {rel}")
    return 0


def replace_status(lines: list[str], replacement: str) -> bool:
    for index, line in enumerate(lines):
        if re.match(r"^\s*Status:\s*", line):
            lines[index] = replacement
            return True
        if re.match(r"^\s*-\s*Status:\s*", line):
            indent = re.match(r"^(\s*)", line).group(1)
            lines[index] = f"{indent}- {replacement}"
            return True
        if re.match(r"^\s*status:\s*", line):
            indent = re.match(r"^(\s*)", line).group(1)
            lines[index] = f"{indent}{replacement}"
            return True
    return False


def update_title(lines: list[str], suffix: str, title: str) -> None:
    if suffix == ".md":
        for index, line in enumerate(lines):
            if line.startswith("# "):
                prefix = line.split(":", 1)[0] if ":" in line else "#"
                lines[index] = f"{prefix}: {title}" if prefix != "#" else f"# {title}"
                return
        lines.insert(0, f"# {title}")
        return

    for index, line in enumerate(lines):
        if re.match(r"^\s*title:\s*", line):
            indent = re.match(r"^(\s*)", line).group(1)
            lines[index] = f"{indent}title: {title}"
            return
    lines.insert(0, f"title: {title}")


def ensure_status(lines: list[str], suffix: str, status: str) -> None:
    status_line = f"status: {status}" if suffix in {".yaml", ".yml"} else f"Status: {status}"
    if replace_status(lines, status_line):
        return
    if suffix == ".md":
        insert_at = 1 if lines and lines[0].startswith("# ") else 0
        lines.insert(insert_at, "")
        lines.insert(insert_at + 1, status_line)
        return
    insert_at = 1 if lines and re.match(r"^\s*title:\s*", lines[0]) else 0
    lines.insert(insert_at, status_line)


def update_markdown_section(text: str, section_name: str, content: str) -> str:
    heading = f"## {section_name}"
    lines = text.rstrip().splitlines()
    replacement = [heading, "", *content.strip().splitlines()]
    for index, line in enumerate(lines):
        if line.strip() != heading:
            continue
        end = index + 1
        while end < len(lines) and not lines[end].startswith("## "):
            end += 1
        lines[index:end] = replacement
        return "\n".join(lines).rstrip() + "\n"
    if lines:
        lines.append("")
    lines.extend(replacement)
    return "\n".join(lines).rstrip() + "\n"


def update_record(
    root: Path,
    entity: str,
    record_id: str,
    title: str | None,
    status: str | None,
    section_name: str | None,
    content: str | None,
    as_json: bool = False,
) -> int:
    config = entity_config(entity)
    if not config.writable:
        print(f"truth record entity is read-only: {entity}", file=sys.stderr)
        return 1
    if bool(section_name) != bool(content):
        print("--section and --content must be provided together", file=sys.stderr)
        return 1
    if not any([title, status, section_name]):
        print("update requires at least one of --title, --status, or --section with --content", file=sys.stderr)
        return 1

    path = record_path(root, entity, record_id)
    if not path.exists():
        print(f"truth record not found: {path.relative_to(root).as_posix()}", file=sys.stderr)
        return 1

    updated: list[str] = []
    text = path.read_text(encoding="utf-8").rstrip()
    lines = text.splitlines()
    if title:
        update_title(lines, config.suffix, title)
        updated.append("title")
    if status:
        ensure_status(lines, config.suffix, status)
        updated.append("status")
    text = "\n".join(lines).rstrip() + "\n"
    if section_name:
        if config.suffix != ".md":
            print("--section updates are only supported for markdown truth records", file=sys.stderr)
            return 1
        text = update_markdown_section(text, section_name, content or "")
        updated.append(f"section:{section_name}")

    path.write_text(text, encoding="utf-8")
    rel = relative(path, root)
    if as_json:
        emit_json({"action": "update", "entity": entity, "path": rel, "updated": updated})
    else:
        print(f"updated truth record: {rel}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Create, list, show, update, or archive AletheiaOS truth records.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List truth records for an entity")
    list_parser.add_argument("entity")
    list_parser.add_argument("--json", action="store_true")

    create_parser = subparsers.add_parser("create", help="Create a truth record from its template")
    create_parser.add_argument("entity")
    create_parser.add_argument("--id", required=True, dest="record_id")
    create_parser.add_argument("--title", required=True)
    create_parser.add_argument("--json", action="store_true")

    show_parser = subparsers.add_parser("show", help="Show one truth record")
    show_parser.add_argument("entity")
    show_parser.add_argument("record_id")
    show_parser.add_argument("--json", action="store_true")

    update_parser = subparsers.add_parser("update", help="Update a truth record title, status, or markdown section")
    update_parser.add_argument("entity")
    update_parser.add_argument("record_id")
    update_parser.add_argument("--title")
    update_parser.add_argument("--status")
    update_parser.add_argument("--section", dest="section_name")
    update_parser.add_argument("--content")
    update_parser.add_argument("--json", action="store_true")

    archive_parser = subparsers.add_parser("archive", help="Mark a truth record archived")
    archive_parser.add_argument("entity")
    archive_parser.add_argument("record_id")
    archive_parser.add_argument("--reason", required=True)
    archive_parser.add_argument("--json", action="store_true")

    args = parser.parse_args()
    root = repo_root()
    try:
        if args.command == "list":
            return list_records(root, args.entity, args.json)
        if args.command == "create":
            return create_record(root, args.entity, args.record_id, args.title, args.json)
        if args.command == "show":
            return show_record(root, args.entity, args.record_id, args.json)
        if args.command == "update":
            return update_record(
                root,
                args.entity,
                args.record_id,
                args.title,
                args.status,
                args.section_name,
                args.content,
                args.json,
            )
        if args.command == "archive":
            return archive_record(root, args.entity, args.record_id, args.reason, args.json)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
