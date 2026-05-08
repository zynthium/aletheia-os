#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path


@dataclass(frozen=True)
class EntityConfig:
    directory: str
    template: str | None
    suffix: str
    writable: bool = True
    fixed_path: str | None = None


ENTITY_CONFIG = {
    "agent-run": EntityConfig("agent_runs", None, ".json", writable=False),
    "agent-runs": EntityConfig("agent_runs", None, ".json", writable=False),
    "agent_runs": EntityConfig("agent_runs", None, ".json", writable=False),
    "active-state": EntityConfig("", None, ".md", fixed_path=".aletheia/state/ACTIVE_STATE.md"),
    "active_state": EntityConfig("", None, ".md", fixed_path=".aletheia/state/ACTIVE_STATE.md"),
    "actions-registry": EntityConfig("", None, ".json", fixed_path=".aletheia/governance/actions.json"),
    "actions_registry": EntityConfig("", None, ".json", fixed_path=".aletheia/governance/actions.json"),
    "attention-policy": EntityConfig("", None, ".md", fixed_path=".aletheia/governance/ATTENTION_POLICY.md"),
    "attention_policy": EntityConfig("", None, ".md", fixed_path=".aletheia/governance/ATTENTION_POLICY.md"),
    "capability-map": EntityConfig("", None, ".md", fixed_path=".aletheia/CAPABILITY_MAP.md"),
    "capability_map": EntityConfig("", None, ".md", fixed_path=".aletheia/CAPABILITY_MAP.md"),
    "charter": EntityConfig("", None, ".md", fixed_path=".aletheia/governance/CHARTER.md"),
    "contract": EntityConfig("contracts", "CONTRACT.md", ".md"),
    "contracts": EntityConfig("contracts", "CONTRACT.md", ".md"),
    "decision": EntityConfig("decisions", "DECISION.md", ".md"),
    "decisions": EntityConfig("decisions", "DECISION.md", ".md"),
    "domain-profile": EntityConfig("", None, ".md", fixed_path=".aletheia/state/DOMAIN_PROFILE.md"),
    "domain_profile": EntityConfig("", None, ".md", fixed_path=".aletheia/state/DOMAIN_PROFILE.md"),
    "evidence": EntityConfig("evidence", "EVIDENCE.md", ".md"),
    "frontier-board": EntityConfig("", None, ".md", fixed_path=".aletheia/state/FRONTIER_BOARD.md"),
    "frontier_board": EntityConfig("", None, ".md", fixed_path=".aletheia/state/FRONTIER_BOARD.md"),
    "git-policy": EntityConfig("", None, ".md", fixed_path=".aletheia/governance/GIT_POLICY.md"),
    "git_policy": EntityConfig("", None, ".md", fixed_path=".aletheia/governance/GIT_POLICY.md"),
    "glossary": EntityConfig("", None, ".md", fixed_path=".aletheia/state/GLOSSARY.md"),
    "hypothesis": EntityConfig("hypotheses", "HYPOTHESIS.md", ".md"),
    "hypotheses": EntityConfig("hypotheses", "HYPOTHESIS.md", ".md"),
    "model-governance": EntityConfig("", None, ".md", fixed_path=".aletheia/governance/MODEL_GOVERNANCE.md"),
    "model_governance": EntityConfig("", None, ".md", fixed_path=".aletheia/governance/MODEL_GOVERNANCE.md"),
    "model-registry": EntityConfig("", None, ".json", fixed_path=".aletheia/governance/model_registry.json"),
    "model_registry": EntityConfig("", None, ".json", fixed_path=".aletheia/governance/model_registry.json"),
    "node": EntityConfig("nodes", "NODE.yaml", ".yaml"),
    "nodes": EntityConfig("nodes", "NODE.yaml", ".yaml"),
    "orphan": EntityConfig("", None, ".yaml", fixed_path=".aletheia/state/ORPHANS.yaml"),
    "orphans": EntityConfig("", None, ".yaml", fixed_path=".aletheia/state/ORPHANS.yaml"),
    "risk": EntityConfig("risks", "RISK.md", ".md"),
    "risks": EntityConfig("risks", "RISK.md", ".md"),
    "risk-register": EntityConfig("", None, ".md", fixed_path=".aletheia/state/RISK_REGISTER.md"),
    "risk_register": EntityConfig("", None, ".md", fixed_path=".aletheia/state/RISK_REGISTER.md"),
    "runtime-policy": EntityConfig("", None, ".json", fixed_path=".aletheia/governance/runtime_policy.json"),
    "runtime_policy": EntityConfig("", None, ".json", fixed_path=".aletheia/governance/runtime_policy.json"),
    "session-note": EntityConfig("session_notes", "SESSION_NOTE.md", ".md"),
    "session-notes": EntityConfig("session_notes", "SESSION_NOTE.md", ".md"),
    "session_notes": EntityConfig("session_notes", "SESSION_NOTE.md", ".md"),
    "skeleton": EntityConfig("", None, ".yaml", fixed_path=".aletheia/state/SKELETON.yaml"),
    "source-policy": EntityConfig("", None, ".md", fixed_path=".aletheia/governance/SOURCE_POLICY.md"),
    "source_policy": EntityConfig("", None, ".md", fixed_path=".aletheia/governance/SOURCE_POLICY.md"),
    "system-graph": EntityConfig("", None, ".yaml", fixed_path=".aletheia/state/SYSTEM_GRAPH.yaml"),
    "system_graph": EntityConfig("", None, ".yaml", fixed_path=".aletheia/state/SYSTEM_GRAPH.yaml"),
    "tree-governance": EntityConfig("", None, ".md", fixed_path=".aletheia/governance/TREE_GOVERNANCE.md"),
    "tree_governance": EntityConfig("", None, ".md", fixed_path=".aletheia/governance/TREE_GOVERNANCE.md"),
    "user-preferences": EntityConfig("", None, ".md", fixed_path=".aletheia/state/USER_PREFERENCES.md"),
    "user_preferences": EntityConfig("", None, ".md", fixed_path=".aletheia/state/USER_PREFERENCES.md"),
}
ID_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+$")
ORPHAN_ENTITIES = {"orphan", "orphans"}


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
    if config.fixed_path:
        if record_id != "current":
            raise ValueError(f"fixed truth entity requires record id 'current': {entity}")
        path = root / config.fixed_path
        resolved_root = root.resolve()
        resolved_path = path.resolve()
        if resolved_path != resolved_root and resolved_root not in resolved_path.parents:
            raise ValueError("record path escapes repository")
        return path
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
        raise ValueError(f"truth record entity cannot be created from a template: {entity}")
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


def orphan_path(root: Path) -> Path:
    return root / ".aletheia" / "state" / "ORPHANS.yaml"


def normalize_scalar(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip())


def yaml_quote(value: str) -> str:
    return json.dumps(normalize_scalar(value), ensure_ascii=False)


def yaml_unquote(value: str) -> str:
    stripped = value.strip()
    if stripped.startswith('"') and stripped.endswith('"'):
        try:
            loaded = json.loads(stripped)
            return str(loaded)
        except json.JSONDecodeError:
            return stripped.strip('"')
    return stripped.strip("\"'")


def ensure_orphans_file(path: Path) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "version: 0.1\n"
        "schema: AIOS_ORPHANS\n"
        f"updated: {date.today().isoformat()}\n"
        "\n"
        "review_policy:\n"
        "  default_review_days: 30\n"
        "  max_orphan_age_days: 90\n"
        "\n"
        "orphans: []\n",
        encoding="utf-8",
    )


def orphan_entry_spans(lines: list[str]) -> list[tuple[str, int, int]]:
    spans: list[tuple[str, int, int]] = []
    for index, line in enumerate(lines):
        match = re.match(r"^\s{2}-\s+id:\s*(.+?)\s*$", line)
        if not match:
            continue
        record_id = yaml_unquote(match.group(1))
        end = len(lines)
        for next_index in range(index + 1, len(lines)):
            if re.match(r"^\s{2}-\s+id:\s*", lines[next_index]):
                end = next_index
                break
        spans.append((record_id, index, end))
    return spans


def find_orphan_span(lines: list[str], record_id: str) -> tuple[int, int] | None:
    for orphan_id, start, end in orphan_entry_spans(lines):
        if orphan_id == record_id:
            return start, end
    return None


def update_orphans_timestamp(lines: list[str]) -> None:
    updated = f"updated: {date.today().isoformat()}"
    for index, line in enumerate(lines):
        if line.startswith("updated:"):
            lines[index] = updated
            return
    lines.insert(0, updated)


def orphan_default_review_days(lines: list[str]) -> int:
    for line in lines:
        match = re.match(r"^\s{2}default_review_days:\s*(\d+)\s*$", line)
        if match:
            return int(match.group(1))
    return 30


def orphan_fragment(record_id: str) -> str:
    return f".aletheia/state/ORPHANS.yaml#{record_id}"


def list_orphans(root: Path, as_json: bool = False) -> int:
    path = orphan_path(root)
    ensure_orphans_file(path)
    lines = path.read_text(encoding="utf-8").splitlines()
    records = [orphan_fragment(record_id) for record_id, _start, _end in orphan_entry_spans(lines)]
    if as_json:
        emit_json({"action": "list", "entity": "orphan", "records": records})
        return 0
    if not records:
        print("None")
        return 0
    for record in records:
        print(record)
    return 0


def show_orphan(root: Path, record_id: str, as_json: bool = False) -> int:
    normalized = validate_record_id(record_id)
    path = orphan_path(root)
    ensure_orphans_file(path)
    lines = path.read_text(encoding="utf-8").splitlines()
    span = find_orphan_span(lines, normalized)
    if span is None:
        print(f"orphan not found: {normalized}", file=sys.stderr)
        return 1
    start, end = span
    content = "\n".join(lines[start:end]).rstrip()
    if as_json:
        emit_json({"action": "show", "entity": "orphan", "path": orphan_fragment(normalized), "content": content})
    else:
        print(content)
    return 0


def create_orphan(root: Path, record_id: str, title: str, as_json: bool = False) -> int:
    normalized = validate_record_id(record_id)
    path = orphan_path(root)
    ensure_orphans_file(path)
    lines = path.read_text(encoding="utf-8").splitlines()
    if find_orphan_span(lines, normalized):
        print(f"orphan already exists: {normalized}", file=sys.stderr)
        return 1
    if "orphans: []" in lines:
        lines[lines.index("orphans: []")] = "orphans:"
    elif not any(line.startswith("orphans:") for line in lines):
        if lines and lines[-1].strip():
            lines.append("")
        lines.append("orphans:")
    if lines and lines[-1].strip():
        lines.append("")
    next_review = date.today() + timedelta(days=orphan_default_review_days(lines))
    lines.extend(
        [
            f"  - id: {normalized}",
            "    status: incubating",
            f"    summary: {yaml_quote(title)}",
            "    candidate_parent: unknown",
            "    source_refs: []",
            f"    next_review: {next_review.isoformat()}",
        ]
    )
    update_orphans_timestamp(lines)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    if as_json:
        emit_json({"action": "create", "entity": "orphan", "path": orphan_fragment(normalized)})
    else:
        print(f"created orphan: {orphan_fragment(normalized)}")
    return 0


def replace_orphan_field(block: list[str], field: str, value: str) -> bool:
    replacement = f"    {field}: {value}"
    for index, line in enumerate(block):
        if re.match(rf"^\s{{4}}{re.escape(field)}:\s*", line):
            block[index] = replacement
            return True
    block.append(replacement)
    return False


def update_orphan(
    root: Path,
    record_id: str,
    title: str | None,
    status: str | None,
    section_name: str | None,
    content: str | None,
    as_json: bool = False,
) -> int:
    normalized = validate_record_id(record_id)
    if section_name or content:
        print("orphan updates support --title and --status only", file=sys.stderr)
        return 1
    if not any([title, status]):
        print("update requires at least one of --title or --status for orphan entries", file=sys.stderr)
        return 1
    path = orphan_path(root)
    ensure_orphans_file(path)
    lines = path.read_text(encoding="utf-8").splitlines()
    span = find_orphan_span(lines, normalized)
    if span is None:
        print(f"orphan not found: {normalized}", file=sys.stderr)
        return 1
    start, end = span
    block = lines[start:end]
    updated: list[str] = []
    if title:
        replace_orphan_field(block, "summary", yaml_quote(title))
        updated.append("summary")
    if status:
        replace_orphan_field(block, "status", status)
        updated.append("status")
    lines[start:end] = block
    update_orphans_timestamp(lines)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    if as_json:
        emit_json({"action": "update", "entity": "orphan", "path": orphan_fragment(normalized), "updated": updated})
    else:
        print(f"updated orphan: {orphan_fragment(normalized)}")
    return 0


def archive_orphan(root: Path, record_id: str, reason: str, as_json: bool = False) -> int:
    normalized = validate_record_id(record_id)
    path = orphan_path(root)
    ensure_orphans_file(path)
    lines = path.read_text(encoding="utf-8").splitlines()
    span = find_orphan_span(lines, normalized)
    if span is None:
        print(f"orphan not found: {normalized}", file=sys.stderr)
        return 1
    start, end = span
    block = lines[start:end]
    replace_orphan_field(block, "status", "archived")
    replace_orphan_field(block, "archive_reason", yaml_quote(reason))
    replace_orphan_field(block, "archived_on", date.today().isoformat())
    lines[start:end] = block
    update_orphans_timestamp(lines)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    if as_json:
        emit_json({"action": "archive", "entity": "orphan", "path": orphan_fragment(normalized), "reason": reason})
    else:
        print(f"archived orphan: {orphan_fragment(normalized)}")
    return 0


def list_records(root: Path, entity: str, as_json: bool = False) -> int:
    if entity in ORPHAN_ENTITIES:
        return list_orphans(root, as_json)
    config = entity_config(entity)
    if config.fixed_path:
        path = root / config.fixed_path
        records = [config.fixed_path] if path.exists() else []
        if as_json:
            emit_json({"action": "list", "entity": entity, "records": records})
        elif records:
            print(config.fixed_path)
        else:
            print("None")
        return 0
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
    if entity in ORPHAN_ENTITIES:
        return create_orphan(root, record_id, title, as_json)
    config = entity_config(entity)
    if config.fixed_path:
        print(f"truth record entity already exists as a fixed file: {entity}", file=sys.stderr)
        return 1
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
    if entity in ORPHAN_ENTITIES and record_id != "current":
        return show_orphan(root, record_id, as_json)
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
    if entity in ORPHAN_ENTITIES and record_id != "current":
        return archive_orphan(root, record_id, reason, as_json)
    config = entity_config(entity)
    if not config.writable:
        print(f"truth record entity is read-only: {entity}", file=sys.stderr)
        return 1
    path = record_path(root, entity, record_id)
    if not path.exists():
        print(f"truth record not found: {path.relative_to(root).as_posix()}", file=sys.stderr)
        return 1
    if config.fixed_path:
        archive_path = root / ".aletheia" / "archive" / path.relative_to(root / ".aletheia")
        archive_path.parent.mkdir(parents=True, exist_ok=True)
        archive_path.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
        path.unlink()
        rel = relative(archive_path, root)
        if as_json:
            emit_json({"action": "archive", "entity": entity, "path": rel, "reason": reason})
        else:
            print(f"archived truth record: {rel}")
        return 0
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
    if entity in ORPHAN_ENTITIES and record_id != "current":
        return update_orphan(root, record_id, title, status, section_name, content, as_json)
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
    if config.suffix == ".json":
        print("JSON fixed truth files can be shown or archived; edit them directly for structured changes", file=sys.stderr)
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
