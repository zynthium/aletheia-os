# Guided Bootstrap Playbook

Use when `BOOTSTRAP.md` exists.

1. Read `.aletheia/START_HERE.md`.
2. Run `.aletheia/bin/model_gate.py --task-class bootstrap_finalize --record --objective "Guided bootstrap"`.
3. Run `.aletheia/bin/intake_inventory.py`.
4. Classify material using `.aletheia/governance/INTAKE_POLICY.md`.
5. Run `.aletheia/bin/guided_bootstrap.py --objective "Guided bootstrap"`.
6. Update durable state with provenance.
7. Run `.aletheia/bin/validate.py`.
8. Finalize with `.aletheia/bin/bootstrap_finalize.py`.
