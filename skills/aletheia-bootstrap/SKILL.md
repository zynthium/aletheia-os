---
name: aletheia-bootstrap
description: Initialize repositories into AletheiaOS. Use when the user asks to add AletheiaOS to an empty repo, bootstrap an existing repo, or generate the repo-native .aletheia control plane.
---

# Aletheia Bootstrap

Use the plugin scaffold to initialize `.aletheia/` into the target repository.

Rules:

- Do not invent a project mission for an empty repository.
- Do not overwrite existing project files unless the user explicitly requests replacement.
- Keep durable state in `.aletheia/`.
- Ensure mandatory Claude Code hooks are present in `.claude/settings.json` and point to `.aletheia/bin/`.
- Keep source code, tests, public docs, build files, and CI files in their conventional locations.
- After initialization, orient from `.aletheia/START_HERE.md`.
