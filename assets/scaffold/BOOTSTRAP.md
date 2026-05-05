# AletheiaOS Bootstrap

This repository has been initialized with AletheiaOS.

This file is temporary. It should be deleted by `.aletheia/bin/bootstrap_finalize.py` after the project has durable state, model attribution, validation, and a checkpoint.

Bootstrap is model-led. The AI assistant should orchestrate the sequence; the operator only needs to provide high-level intent, domain boundaries, and access restrictions.

1. Read `.aletheia/START_HERE.md`.
2. Run `python3 .aletheia/bin/model_gate.py --task-class bootstrap_finalize --record --objective "Initialize AletheiaOS"`.
3. Determine whether the repository already has source material that should be classified before truth synthesis.
4. For exported research conversations, place files in `.aletheia/truth_intake/inbox/`, then run `python3 .aletheia/bin/truth_intake.py begin --objective "Initialize AletheiaOS"` and `python3 .aletheia/bin/truth_intake.py stage --run <run_id>`.
5. Run `python3 .aletheia/bin/intake_inventory.py`.
6. Classify existing material using `.aletheia/governance/INTAKE_POLICY.md`.
7. Run `python3 .aletheia/bin/guided_bootstrap.py --objective "Initialize AletheiaOS"`.
8. Synthesize candidate project truth first, then promote reviewed items into charter, graph, skeleton, active state, domain profile, risks, decisions, contracts, evidence, and session notes.
9. Run `python3 .aletheia/bin/orient.py` and `python3 .aletheia/bin/validate.py`.
10. Finalize with `python3 .aletheia/bin/bootstrap_finalize.py`.

Do not write production code, copy secrets into `.aletheia/`, treat existing material as automatically true, or skip the initial checkpoint during bootstrap.
