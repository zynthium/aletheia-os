---
name: aletheia-bootstrap
description: Initialize or migrate repositories into AletheiaOS. Use when the user asks to add AletheiaOS to an empty repo, bootstrap an existing repo, migrate from a prior aletheia_os layout, or generate the repo-native .aletheia control plane.
---

# Aletheia Bootstrap

Use the plugin scaffold to initialize `.aletheia/` into the target repository.

Rules:

- Do not invent a project mission for an empty repository.
- Do not overwrite existing project files unless the user explicitly requests replacement.
- Keep durable state in `.aletheia/`.
- Keep legacy `aletheia_os/` as a preserved reference during migration unless the user explicitly requests deletion.
- Ensure mandatory Claude Code hooks are present in `.claude/settings.json` and point to `.aletheia/bin/`.
- Keep source code, tests, public docs, build files, and CI files in their conventional locations.
- After initialization, orient from `.aletheia/START_HERE.md`.
