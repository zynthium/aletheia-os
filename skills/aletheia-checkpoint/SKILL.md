---
name: aletheia-checkpoint
description: Validate and checkpoint AletheiaOS durable state. Use when the user asks to checkpoint, finish a substantial task, record session notes, validate model attribution, or prepare a coherent git commit for AletheiaOS state and implementation changes.
---

# Aletheia Checkpoint

Before claiming completion for non-trivial work:

1. Confirm model gate attribution exists for durable writes.
2. Confirm affected `.aletheia/` state, decisions, evidence, or contracts were updated.
3. Run repository validation when the user asks for verification or checkpointing.
4. Create a checkpoint only when validation state is known and the user has not deferred commits.

Never hide unresolved risks.
