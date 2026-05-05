---
name: aletheia-bootstrap
description: Initialize an AletheiaOS project truth layer. Use when the user asks to add AletheiaOS to a repository or generate the repo-native .aletheia facts, constraints, evidence, and attribution control plane.
---

# Aletheia Bootstrap

Use the plugin scaffold to initialize `.aletheia/` as the target repository's project truth layer.

Rules:

- Do not invent a project mission for an empty repository.
- Do not overwrite existing project files unless the user explicitly requests replacement.
- Keep project truth in `.aletheia/`.
- Ensure mandatory Claude Code hooks are present in `.claude/settings.json` and point to `.aletheia/bin/`.
- Keep source code, tests, public docs, build files, and CI files in their conventional locations.
- After initialization, orient from `.aletheia/START_HERE.md` before local implementation.
