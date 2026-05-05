#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import shutil
import subprocess
import unicodedata
import zipfile
from datetime import datetime, timezone
from pathlib import Path


SCHEMA = "AIOS_TRUTH_INTAKE_REGISTRY"
SENSITIVE_PATTERNS = [
    re.compile(pattern, re.I)
    for pattern in [
        r"\.env($|\.)",
        r"secret",
        r"credential",
        r"password",
        r"passwd",
        r"token",
        r"apikey",
        r"api[_-]?key",
        r"private[_-]?key",
        r"\.pem$",
        r"\.key$",
        r"id_rsa",
        r"oauth",
    ]
]
TEXT_SUFFIXES = {".md", ".txt", ".json", ".html", ".htm"}
CHUNK_TARGET_CHARS = 3000


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def intake_root(root: Path) -> Path:
    return root / ".aletheia" / "truth_intake"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_id() -> str:
    return "RUN-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonicalize(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text)
    normalized = normalized.replace("\r\n", "\n").replace("\r", "\n")
    normalized = re.sub(r"[\u200b-\u200f\ufeff]", "", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


def is_sensitive(path: Path, text: str = "") -> bool:
    target = f"{path.as_posix()}\n{text[:2000]}"
    return any(pattern.search(target) for pattern in SENSITIVE_PATTERNS)


def load_registry(root: Path) -> dict:
    path = intake_root(root) / "registry.json"
    if not path.exists():
        return {"schema": SCHEMA, "version": 1, "sources": {}, "runs": {}}
    data = json.loads(path.read_text(encoding="utf-8"))
    data.setdefault("schema", SCHEMA)
    data.setdefault("version", 1)
    data.setdefault("sources", {})
    data.setdefault("runs", {})
    return data


def save_registry(root: Path, registry: dict) -> None:
    path = intake_root(root) / "registry.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(registry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_run_state(root: Path, rid: str) -> dict:
    path = intake_root(root) / "runs" / rid / "run_state.json"
    if not path.exists():
        raise SystemExit(f"unknown intake run: {rid}")
    return json.loads(path.read_text(encoding="utf-8"))


def save_run_state(root: Path, rid: str, state: dict) -> None:
    run_dir = intake_root(root) / "runs" / rid
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "run_state.json").write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def extract_html(data: bytes) -> str:
    text = data.decode("utf-8", errors="replace")
    text = re.sub(r"(?is)<(script|style).*?</\1>", " ", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    return html.unescape(text)


def flatten_json(value) -> str:
    parts: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            if isinstance(item, (dict, list)):
                parts.append(flatten_json(item))
            elif item is not None:
                parts.append(f"{key}: {item}")
    elif isinstance(value, list):
        for item in value:
            parts.append(flatten_json(item))
    elif value is not None:
        parts.append(str(value))
    return "\n".join(part for part in parts if part)


def extract_text_from_bytes(name: str, data: bytes) -> str:
    suffix = Path(name).suffix.lower()
    if suffix == ".json":
        try:
            return flatten_json(json.loads(data.decode("utf-8", errors="replace")))
        except Exception:
            return data.decode("utf-8", errors="replace")
    if suffix in {".html", ".htm"}:
        return extract_html(data)
    return data.decode("utf-8", errors="replace")


def source_payloads(path: Path) -> list[tuple[str, bytes]]:
    if path.suffix.lower() == ".zip":
        payloads: list[tuple[str, bytes]] = []
        with zipfile.ZipFile(path) as archive:
            for info in archive.infolist():
                if info.is_dir():
                    continue
                suffix = Path(info.filename).suffix.lower()
                if suffix in TEXT_SUFFIXES:
                    payloads.append((f"{path.name}:{info.filename}", archive.read(info)))
        return payloads
    return [(path.name, path.read_bytes())]


def chunk_text(text: str) -> list[dict]:
    if not text:
        return []
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
    chunks: list[str] = []
    current = ""
    for paragraph in paragraphs or [text]:
        if current and len(current) + len(paragraph) + 2 > CHUNK_TARGET_CHARS:
            chunks.append(current.strip())
            current = paragraph
        else:
            current = f"{current}\n\n{paragraph}".strip()
    if current:
        chunks.append(current.strip())
    return [
        {
            "chunk_id": f"chunk-{index:04d}",
            "canonical_hash": sha256_text(canonicalize(chunk)),
            "char_count": len(chunk),
        }
        for index, chunk in enumerate(chunks, start=1)
    ]


def git_head(root: Path) -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "--verify", "HEAD"],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def git_status_paths(root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        return []
    return [line[3:].strip() for line in result.stdout.splitlines() if line.strip()]


def check_worktree_for_begin(root: Path) -> None:
    paths = git_status_paths(root)
    allowed_prefix = ".aletheia/truth_intake/inbox/"
    unexpected = [path for path in paths if not path.startswith(allowed_prefix)]
    if unexpected:
        raise SystemExit(
            "intake begin blocked: checkpoint existing changes first:\n"
            + "\n".join(f"  - {path}" for path in unexpected)
        )


def cmd_begin(args) -> int:
    root = repo_root()
    if not args.allow_dirty:
        check_worktree_for_begin(root)
    rid = args.run or run_id()
    state = {
        "run_id": rid,
        "objective": args.objective,
        "created_at": utc_now(),
        "status": "begun",
        "staged_sources": [],
        "packet": None,
    }
    save_run_state(root, rid, state)
    registry = load_registry(root)
    registry["runs"][rid] = {
        "objective": args.objective,
        "created_at": state["created_at"],
        "status": "begun",
        "begin_commit": git_head(root),
    }
    save_registry(root, registry)
    print(f"created intake run {rid}")
    return 0


def cmd_stage(args) -> int:
    root = repo_root()
    rid = args.run
    state = load_run_state(root, rid)
    registry = load_registry(root)
    inbox = intake_root(root) / "inbox"
    run_dir = intake_root(root) / "runs" / rid
    sources_dir = run_dir / "sources"
    sources_dir.mkdir(parents=True, exist_ok=True)
    manifest: list[dict] = []
    chunk_index: list[dict] = []
    seen_this_run: set[str] = set()

    for file_path in sorted(path for path in inbox.rglob("*") if path.is_file() and path.name != ".gitkeep"):
        for display_name, data in source_payloads(file_path):
            text = extract_text_from_bytes(display_name, data)
            canonical = canonicalize(text)
            canonical_hash = sha256_text(canonical)
            byte_hash = sha256_bytes(data)
            source_id = f"SRC-{canonical_hash[:12]}"
            sensitive = is_sensitive(file_path, text)
            chunks = [] if sensitive else chunk_text(text)

            source = registry["sources"].setdefault(
                source_id,
                {
                    "source_id": source_id,
                    "canonical_hash": canonical_hash,
                    "status": "blocked_sensitive" if sensitive else "pending_digest",
                    "aliases": [],
                    "chunk_hashes": [],
                    "first_seen_run": rid,
                    "first_seen_commit": git_head(root),
                    "digest_commit": None,
                    "packet_commit": None,
                    "promoted_commit": None,
                    "promoted_refs": [],
                },
            )
            if source_id in seen_this_run or source.get("first_seen_run") != rid:
                source["status"] = source.get("status") if sensitive else source.get("status", "duplicate")
            source["last_seen_run"] = rid
            source["last_seen_commit"] = git_head(root)
            alias = {
                "path": str(file_path.relative_to(root)).replace("\\", "/"),
                "display_name": display_name,
                "byte_hash": byte_hash,
                "seen_at": utc_now(),
            }
            if alias not in source["aliases"]:
                source["aliases"].append(alias)
            existing_hashes = set(source.get("chunk_hashes", []))
            for chunk in chunks:
                existing_hashes.add(chunk["canonical_hash"])
                if source_id not in seen_this_run:
                    chunk_index.append({"source_id": source_id, **chunk})
            source["chunk_hashes"] = sorted(existing_hashes)

            if not sensitive and source_id not in seen_this_run:
                (sources_dir / f"{source_id}.txt").write_text(text, encoding="utf-8")
            manifest.append(
                {
                    "source_id": source_id,
                    "path": alias["path"],
                    "display_name": display_name,
                    "byte_hash": byte_hash,
                    "canonical_hash": canonical_hash,
                    "status": source["status"],
                    "chunks": chunks,
                }
            )
            seen_this_run.add(source_id)

    (run_dir / "source_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (run_dir / "chunk_index.json").write_text(
        json.dumps({"run_id": rid, "chunks": chunk_index}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    state["status"] = "staged"
    state["staged_sources"] = [item["source_id"] for item in manifest]
    save_run_state(root, rid, state)
    registry["runs"].setdefault(rid, {})["status"] = "staged"
    save_registry(root, registry)
    print(f"staged {len(manifest)} intake source entries for {rid}")
    return 0


def cmd_digest_plan(args) -> int:
    root = repo_root()
    rid = args.run
    state = load_run_state(root, rid)
    registry = load_registry(root)
    run_dir = intake_root(root) / "runs" / rid
    digest_dir = run_dir / "digests"
    digest_dir.mkdir(parents=True, exist_ok=True)
    chunk_index_path = run_dir / "chunk_index.json"
    chunk_index = json.loads(chunk_index_path.read_text(encoding="utf-8")) if chunk_index_path.exists() else {"chunks": []}
    pending = []
    for source_id in state.get("staged_sources", []):
        source = registry["sources"].get(source_id, {})
        if source.get("status") in {"pending_digest", "revision"}:
            pending.append(source_id)
            chunks = [
                chunk["chunk_id"]
                for chunk in chunk_index.get("chunks", [])
                if chunk.get("source_id") == source_id
            ]
            template = root / ".aletheia" / "templates" / "CONVERSATION_DIGEST.md"
            draft_path = digest_dir / f"{source_id}.md"
            if not draft_path.exists():
                text = template.read_text(encoding="utf-8")
                text = text.replace("<source title>", source_id)
                text = text.replace("<source id>", source_id)
                text = text.replace("<run id>", rid)
                text = text.replace("<chunk ids>", ", ".join(chunks) or "none")
                draft_path.write_text(text, encoding="utf-8")
            source["status"] = "digest_planned"
    lines = ["# Digest Plan", "", f"Run id: {rid}", "", "## Pending Sources", ""]
    for source_id in sorted(set(pending)):
        lines.append(f"- {source_id}")
    if not pending:
        lines.append("None.")
    (run_dir / "digest_plan.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    save_registry(root, registry)
    print(f"wrote {run_dir / 'digest_plan.md'}")
    return 0


def has_baseline(root: Path) -> bool:
    promotion_log = intake_root(root) / "PROMOTION_LOG.md"
    if promotion_log.exists():
        text = promotion_log.read_text(encoding="utf-8")
        if "Baseline established" in text or "Truth record:" in text:
            return True
    return not (root / "BOOTSTRAP.md").exists()


def cmd_packet(args) -> int:
    root = repo_root()
    rid = args.run
    state = load_run_state(root, rid)
    run_dir = intake_root(root) / "runs" / rid
    template_name = "FUSION_PACKET.md" if has_baseline(root) else "BOOTSTRAP_SYNTHESIS_PACKET.md"
    template = root / ".aletheia" / "templates" / template_name
    text = template.read_text(encoding="utf-8")
    text = text.replace("<run id>", rid).replace("<objective>", state.get("objective", "TBD"))
    (run_dir / template_name).write_text(text, encoding="utf-8")
    state["status"] = "packeted"
    state["packet"] = template_name
    save_run_state(root, rid, state)
    registry = load_registry(root)
    registry["runs"].setdefault(rid, {})["status"] = "packeted"
    registry["runs"][rid]["packet"] = template_name
    save_registry(root, registry)
    print(f"wrote {run_dir / template_name}")
    return 0


def cmd_status(args) -> int:
    root = repo_root()
    registry = load_registry(root)
    if args.run:
        state = load_run_state(root, args.run)
        print(json.dumps(state, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(registry, indent=2, ensure_ascii=False))
    return 0


def cmd_finish(args) -> int:
    root = repo_root()
    rid = args.run
    state = load_run_state(root, rid)
    run_dir = intake_root(root) / "runs" / rid
    inbox = intake_root(root) / "inbox"
    for path in inbox.rglob("*"):
        if path.is_file() and path.name != ".gitkeep":
            path.unlink()
    shutil.rmtree(run_dir)
    registry = load_registry(root)
    registry["runs"].setdefault(rid, {})["status"] = "finished"
    registry["runs"][rid]["finished_at"] = utc_now()
    registry["runs"][rid]["finished_previous_status"] = state.get("status")
    save_registry(root, registry)
    print(f"finished and cleaned intake run {rid}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Run git-native AletheiaOS truth intake.")
    sub = parser.add_subparsers(dest="command", required=True)

    begin = sub.add_parser("begin")
    begin.add_argument("--objective", required=True)
    begin.add_argument("--run", default=None)
    begin.add_argument("--allow-dirty", action="store_true")
    begin.set_defaults(func=cmd_begin)

    stage = sub.add_parser("stage")
    stage.add_argument("--run", required=True)
    stage.set_defaults(func=cmd_stage)

    digest = sub.add_parser("digest-plan")
    digest.add_argument("--run", required=True)
    digest.set_defaults(func=cmd_digest_plan)

    packet = sub.add_parser("packet")
    packet.add_argument("--run", required=True)
    packet.set_defaults(func=cmd_packet)

    status = sub.add_parser("status")
    status.add_argument("--run", default=None)
    status.set_defaults(func=cmd_status)

    finish = sub.add_parser("finish")
    finish.add_argument("--run", required=True)
    finish.set_defaults(func=cmd_finish)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
