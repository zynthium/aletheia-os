---
name: checkpoint
description: Validate durable project state, create session distillation, and commit an appropriate git checkpoint.
---

# Checkpoint Skill

Use at the end of non-trivial work.

Required:
1. update durable state;
2. run `python3 scripts/aios_validate.py`;
3. run `python3 scripts/aios_checkpoint.py --auto`;
4. report commit status.

If checkpoint is blocked, report exact blocker and next action.
