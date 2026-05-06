# AletheiaOS Bootstrap

This repository has been initialized with AletheiaOS.

This file is temporary. It should be deleted by `.aletheia/bin/bootstrap_finalize.py` after the project has durable state, model attribution, validation, and a checkpoint.

Bootstrap is model-led. The AI assistant should orchestrate the sequence; the operator only needs to provide high-level intent, domain boundaries, and access restrictions.

1. Read `.aletheia/START_HERE.md`.
2. Run `python3 .aletheia/bin/model_gate.py --task-class bootstrap_finalize --provider <provider> --model-id <model_id> --tier C3 --operator-approved --record --objective "Initialize AletheiaOS"`.
3. Determine whether the repository already has source material that should be classified before truth synthesis.
4. Run `python3 .aletheia/bin/source_inventory.py`.
5. Classify existing material using `.aletheia/governance/SOURCE_POLICY.md`.
6. Run `python3 .aletheia/bin/guided_bootstrap.py --objective "Initialize AletheiaOS"`.
7. Synthesize project truth: charter, graph, skeleton, active state, domain profile, risks, decisions, contracts, evidence, and session notes.
8. Run `python3 .aletheia/bin/orient.py` and `python3 .aletheia/bin/validate.py`.
9. Finalize with `python3 .aletheia/bin/bootstrap_finalize.py`.

Do not write production code, copy secrets into `.aletheia/`, treat existing material as automatically true, or skip the initial checkpoint during bootstrap.

After bootstrap, register trusted models in `.aletheia/governance/model_registry.json` so future durable writes do not depend on one-off operator approval.
