# Playbook — Drift Audit

Run periodically or after long AI-agent sessions.

Check:

- orphan claims without nodes;
- orphan implementation without claim/contract;
- evidence that did not update the graph;
- decisions without affected nodes;
- code changes without session note;
- active state inconsistent with frontier board;
- branch weight inconsistent with actual work allocation;
- repeated local patches around a Type B/C/D blocker.

Recommended command:

```bash
python3 scripts/aios_validate.py
```
