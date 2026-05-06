# Guided Bootstrap Playbook

Use when `BOOTSTRAP.md` exists.

1. Read `.aletheia/START_HERE.md`.
2. Run `.aletheia/bin/model_gate.py --task-class bootstrap_finalize --provider <provider> --model-id <model_id> --tier C3 --operator-approved --record --objective "Guided bootstrap"`.
3. Run `.aletheia/bin/source_inventory.py`.
4. Classify material using `.aletheia/governance/SOURCE_POLICY.md`.
5. Run `.aletheia/bin/guided_bootstrap.py --objective "Guided bootstrap"`; it verifies the recorded bootstrap gate.
6. Update durable state with provenance.
7. Run `.aletheia/bin/validate.py`.
8. Finalize with `.aletheia/bin/bootstrap_finalize.py`.
