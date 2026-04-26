# Agent Runs

This directory stores durable records of AI assistant sessions that performed or attempted non-trivial work.

Create a run record with:

```bash
python3 scripts/aios_model_gate.py --task-class <task_class> --record --objective "<objective>"
```

Each run record should capture:

- provider
- model id
- assistant tool/interface
- capability tier
- task class
- gate result
- objective
- timestamp
- source of model metadata

Do not store API keys, prompts containing secrets, or private credentials here.
