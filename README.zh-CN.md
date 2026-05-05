# AletheiaOS

AletheiaOS 是一个面向 Codex 的项目状态操作系统。它让 AI agent 在开发复杂项目时，不再只依赖聊天上下文，而是把项目目标、当前状态、系统骨架、证据、决策、契约和 agent 运行记录沉淀到仓库本身。

这个项目以 Codex plugin 的形式发布。安装后，Codex 可以用它为任意仓库建立 `.aletheia/` 控制平面，并在后续开发中按统一协议进行取向、模型门控、证据记录、架构迭代、总览生成、验证和 checkpoint。Claude Code hooks 是默认 scaffold 的一部分，hook 命令指向 `.aletheia/bin/`。

## 为什么需要 AletheiaOS

复杂项目不是一组孤立文件。它们通常具有逐层展开的结构：

```text
mission -> objectives -> system graph -> skeleton -> contracts -> code
```

AI agent 如果只读取局部文件，很容易在错误的目标、过期的假设或不完整的架构边界下优化。AletheiaOS 的目标是让 agent 每次工作前都能先获得项目骨架，再按需展开到具体节点和文件。

## 核心边界

```text
AletheiaOS plugin = Codex 的分发与操作层
.aletheia/ = 目标仓库的长期项目记忆
src/tests/docs = 项目的实现与数据平面
```

插件负责初始化和操作 `.aletheia/`。项目的真实状态保存在目标仓库中，而不是保存在聊天记录或插件内部。

## 功能

- 为目标仓库初始化 `.aletheia/` 控制平面。
- 引导 Codex 读取项目 mission、active state、system graph 和 project skeleton。
- 在写入前执行模型能力门控和 agent attribution。
- 记录 evidence、decisions、contracts、risks 和 session notes。
- 支持复杂项目的架构演进和逐层展开。
- 提供 repo-native validation、overview、bootstrap finalize 和 checkpoint runtime。
- 通过 model registry 管理 task class、能力层级、注册模型和 denylist。
- 保持源码、测试、公开文档和构建配置在项目常规目录中。

## 目录结构

```text
.codex-plugin/
  plugin.json
skills/
  aletheia-bootstrap/
  aletheia-orient/
  aletheia-checkpoint/
  aletheia-design-evidence/
  aletheia-architecture-evolution/
assets/
  scaffold/
    AGENTS.md
    START_HERE.md
    .claude/settings.json
    .aletheia/
scripts/
  aletheia_scaffold.py
  init_aletheia.py
  migrate_aletheia.py
  validate_scaffold.py
  package_plugin.py
```

## 快速开始

### 初始化目标仓库

```bash
python3 scripts/init_aletheia.py /path/to/target-repo
```

目标仓库会得到：

```text
AGENTS.md
START_HERE.md
BOOTSTRAP.md
.claude/settings.json
.aletheia/
```

`.claude/settings.json` 会配置 SessionStart、PreToolUse、PostToolUse 和 Stop hooks，用 `.aletheia/bin/model_gate.py`、`change_hook.py` 和 `stop_hook.py` 执行强制门禁与审计。

### 迁移旧版 `aletheia_os/`

```bash
python3 scripts/migrate_aletheia.py /path/to/target-repo
```

迁移会把旧控制面复制到 `.aletheia/`，重写 active `.aletheia` 文档里的旧路径引用，生成 `.aletheia/bootstrap_intake/IMPORT_REPORT.md`，并默认保留原 `aletheia_os/` 目录。

### 验证插件自带 scaffold

```bash
python3 scripts/validate_scaffold.py assets/scaffold
```

### 生成发布目录

```bash
python3 scripts/package_plugin.py --output /tmp/aletheia-os-dist
```

输出：

```text
/tmp/aletheia-os-dist/aletheia-os-plugin/
```

## `.aletheia/` 中有什么

初始化后的目标仓库会包含：

```text
.aletheia/
  START_HERE.md
  VERSION
  governance/
  state/
  hypotheses/
  nodes/
  playbooks/
  decisions/
  evidence/
  contracts/
  risks/
  session_notes/
  agent_runs/
  templates/
  bin/
```

其中：

- `governance/` 保存 charter、attention policy、model governance、model registry、git policy 和 intake policy。
- `state/` 保存 active state、system graph、project skeleton、frontier board、glossary、domain profile 和 risk register。
- `decisions/` 保存长期项目和架构决策。
- `evidence/` 保存实验、验证、观察、推理和解释记录。
- `contracts/` 保存模块、接口和边界契约。
- `agent_runs/` 保存 agent attribution 和模型门控记录。
- `templates/` 提供 decision、evidence、risk、contract、hypothesis、node、task card、agent run 和 session note 模板。
- `bin/` 提供 orient、context pack、model gate、intake inventory、guided bootstrap、overview、validate、bootstrap finalize、checkpoint 和 Claude hook runtime。

## 推荐工作流

```text
orient
-> model gate
-> execute
-> update durable state
-> validate
-> checkpoint
```

对应的 plugin skills：

- `aletheia-bootstrap`：初始化目标仓库。
- `aletheia-orient`：建立全局项目视图并定位 active node。
- `aletheia-checkpoint`：验证并创建 checkpoint。
- `aletheia-design-evidence`：为 claim、实验和设计分支创建可证伪证据。
- `aletheia-architecture-evolution`：支持架构决策、契约变更和 skeleton traversal。

## AletheiaOS 能力闭环

AletheiaOS 不只是初始化 `.aletheia/`，它还提供完整的项目记忆闭环：

```text
bootstrap
-> orient
-> model gate
-> execute
-> evidence / decision / contract / risk update
-> overview
-> validate
-> checkpoint
```

关键 runtime：

```bash
python3 .aletheia/bin/bootstrap_finalize.py
python3 .aletheia/bin/orient.py
python3 .aletheia/bin/context_pack.py
python3 .aletheia/bin/model_gate.py --task-class <task_class> --provider <provider> --model-id <model_id> --record --objective "<objective>"
python3 .aletheia/bin/intake_inventory.py
python3 .aletheia/bin/guided_bootstrap.py --objective "<objective>"
python3 .aletheia/bin/overview.py
python3 .aletheia/bin/validate.py
python3 .aletheia/bin/checkpoint.py
```

## 项目骨架感知

AletheiaOS 通过 `SYSTEM_GRAPH.yaml` 和 `SKELETON.yaml` 帮助 agent 保持全局骨架感知。

每个 skeleton node 可以描述：

- 所在层级；
- 父节点和子节点；
- 目的和不变量；
- 接口和依赖；
- 拥有的路径；
- 测试路径；
- 相关 contracts、decisions 和 evidence；
- 何时展开，何时停止。

这样 agent 可以从 root mission 逐层展开，而不是默认扫描整个仓库。

## 设计原则

1. 仓库是长期记忆，聊天不是长期记忆。
2. 每个重要 claim 都应可证伪或明确标记为解释性判断。
3. 实现必须能追溯到目标、系统节点、契约或证据。
4. 架构迭代是一种设计研究流程，需要 evidence 和 invalidation criteria。
5. `.aletheia/` 是控制平面，不是源码、测试或公开文档的替代品。
6. plugin 负责操作协议，目标仓库负责保存真实项目状态。
7. 人类总览应从真实项目状态生成，而不是手写状态页。

## 适合谁使用

AletheiaOS 适合正在用 Codex 维护复杂项目的开发者，尤其是：

- 项目目标和约束需要长期保留；
- 架构会持续演进；
- 需要区分 claim、evidence、decision 和 implementation；
- 希望 agent 每次工作前先理解全局骨架；
- 不希望重要项目状态只存在于聊天上下文。
