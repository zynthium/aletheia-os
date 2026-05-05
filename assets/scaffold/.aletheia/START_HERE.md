# AletheiaOS Start Here

Build a top-down view of project truth before local work.

Read order:

1. `.aletheia/governance/CHARTER.md`
2. `.aletheia/governance/ATTENTION_POLICY.md`
3. `.aletheia/governance/MODEL_GOVERNANCE.md`
4. `.aletheia/governance/model_registry.json`
5. `.aletheia/state/ACTIVE_STATE.md`
6. `.aletheia/state/SYSTEM_GRAPH.yaml`
7. `.aletheia/state/SKELETON.yaml`
8. `.aletheia/state/RISK_REGISTER.md`
9. `.aletheia/state/FRONTIER_BOARD.md`, `.aletheia/state/DOMAIN_PROFILE.md`, and relevant decisions, evidence, contracts, risks, nodes, and source files.

Before durable writes, run `.aletheia/bin/model_gate.py` with the correct task class:

```bash
python3 .aletheia/bin/model_gate.py --task-class <task_class> --provider <provider> --model-id <model_id> --record --objective "<short objective>"
```

Useful runtime commands:

```bash
python3 .aletheia/bin/orient.py
python3 .aletheia/bin/context_pack.py
python3 .aletheia/bin/intake_inventory.py
python3 .aletheia/bin/guided_bootstrap.py --objective "Initialize AletheiaOS"
python3 .aletheia/bin/overview.py
python3 .aletheia/bin/validate.py
python3 .aletheia/bin/checkpoint.py
python3 .aletheia/bin/bootstrap_finalize.py
```
