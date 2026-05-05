# Attention Policy

Load the smallest context that preserves the global skeleton.

## Read order

1. Root entrypoint and `.aletheia/START_HERE.md`.
2. Charter, attention policy, model governance, and active state.
3. System graph and project skeleton.
4. Active node parent chain, immediate children, and relevant boundary records.
5. Relevant source, tests, docs, or external references only after the active node is identified.

## Expansion rule

Do not scan the whole repository by default. Expand from root to active node, then load siblings only when the task crosses their interfaces or constraints.

## Stop rule

Stop expanding when the current node, parent constraints, contracts, decisions, and directly owned paths are sufficient to answer or execute the task.
