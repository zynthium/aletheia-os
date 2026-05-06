# AGENTS.md

Before non-trivial work, read `.aletheia/START_HERE.md`.

The repository is the durable project truth source. Chat history is not durable memory.

Daily loop:

```text
orient -> work -> update truth -> validate -> checkpoint
```

Before durable writes, run or verify:

```bash
python3 .aletheia/bin/model_gate.py --task-class <task_class> --record --objective "<objective>"
```

Claude Code hooks are mandatory for this scaffold and should point to `.aletheia/bin/`.

For non-trivial completion, update affected `.aletheia/` truth records, run validation, and create or explicitly defer a checkpoint.
