# AletheiaOS

**面向 AI 辅助研究与工程的仓库原生事实层。**

**One repo. One project truth. Many agents.**

AletheiaOS 用 `.aletheia/` 为复杂项目维护唯一可信事实源：使命、当前状态、系统图、项目骨架、架构约束、研究证据、决策记录、接口契约、风险和 agent 归因。

它适用于长周期研究与工程项目。在这类项目中，理论、实现、证据、风险和优化会共同演化，局部实现发现也可能推翻顶层假设。AletheiaOS 的目标不是替代 Codex、Claude Code、OpenSpec、Superpowers、gstack、Compound 或其他 AI 编码工作流，而是为它们提供同一份 repo-native project truth。

## 为什么需要 AletheiaOS

AI agent 擅长局部执行，但在长周期一致性上很脆弱。复杂项目通常会出现：

- 局部优化覆盖上层约束；
- 研究结论、架构决策和代码实现彼此脱节；
- 聊天记录、设计文档、README 和当前代码互相矛盾；
- 重要 claim 没有证据、推翻标准或后续决策；
- agent 不清楚当前 active node、父级约束和边界契约；
- 多个 agent 或工具基于不同版本的项目事实工作。

AletheiaOS 通过把项目事实显式化、结构化、可验证并纳入版本控制来减少这种漂移。它让 agent 在当前事实下工作，并在完成后更新事实。

## 定位边界

AletheiaOS 是：

- repo-native truth layer；
- 面向 AI 辅助研究与工程的真实项目记忆；
- 受约束治理的系统图；
- 架构约束、研究证据、决策、契约、风险和 agent 归因的事实账本；
- Codex、Claude Code 及类似工具可共同读写的项目事实控制平面。

AletheiaOS 不是另一个 coding workflow，也不是：

- 任务管理器；
- 通用笔记应用；
- feature spec 工具；
- Claude/Codex memory 的替代品；
- TDD、review、ship 或虚拟团队插件；
- 人类判断的替代品；
- 自动把非结构化项目变得一致的魔法层。

## 与其他工具的关系

```text
Claude Code / Codex 提供 agent runtime。
Superpowers / gstack / Compound 指导 agent 如何工作。
OpenSpec 管理 change-level specs。
AletheiaOS 维护它们共同依赖的 project-level truth。
```

AletheiaOS 不争夺流程入口。它提供 `.aletheia/` 事实层，让不同 agent、技能和工作流在同一份当前事实上 orient、执行、验证和 checkpoint。

## 核心模型

AletheiaOS 将项目表示为一个受约束治理的系统图：

```text
mission -> system graph -> skeleton -> contracts -> evidence -> decisions -> code
```

其中：

- `governance/` 保存 charter、attention policy、model governance、model registry、git policy 和 intake policy；
- `state/` 保存 active state、system graph、project skeleton、frontier board、glossary、domain profile 和 risk register；
- `nodes/` 保存可下钻的系统节点事实；
- `evidence/` 保存实验、验证、观察、推理和解释记录；
- `decisions/` 保存长期项目和架构决策；
- `contracts/` 保存模块、接口和边界契约；
- `risks/` 保存失效模式、不确定性和待证伪假设；
- `agent_runs/` 保存 agent attribution 和模型门控记录。

源码、测试、公开文档和构建配置仍保存在项目常规目录中。`.aletheia/` 是事实控制平面，不是实现与数据平面的替代品。

## 功能

- 为目标仓库初始化 `.aletheia/` truth layer。
- 引导 agent 从唯一事实源读取 mission、active state、system graph、skeleton 和 active node。
- 在 durable writes 前执行模型能力门控和 agent attribution。
- 记录 evidence、decisions、contracts、risks 和 session notes。
- 支持复杂项目的架构演进、约束追踪和逐层展开。
- 提供 repo-native validation、overview、bootstrap finalize 和 checkpoint runtime。
- 通过 model registry 管理 task class、能力层级、注册模型和 denylist。

## 安装

### Claude Code 本地开发安装

Claude Code 插件要求插件根目录包含 `.claude-plugin/plugin.json`，技能等组件放在插件根目录下的 `skills/` 等常规目录中。AletheiaOS 同时保留 `.codex-plugin/plugin.json` 和 `.claude-plugin/plugin.json`，因此同一个发布目录可以被 Codex 和 Claude Code 使用。

从本仓库直接测试：

```bash
cd /Users/joeslee/Projects/GitHub/aletheia-os
claude --plugin-dir .
```

从发布目录测试：

```bash
python3 scripts/package_plugin.py --output /tmp/aletheia-os-dist
claude --plugin-dir /tmp/aletheia-os-dist/aletheia-os
```

启动 Claude Code 后，可在目标仓库中要求 Claude 使用 `aletheia-bootstrap` 初始化 `.aletheia/` truth layer。

### Claude Code Marketplace 安装

如果要通过 Claude Code marketplace 分发，需要把发布后的 `aletheia-os/` 目录加入你的 plugin marketplace。Marketplace entry 的 `name` 应为 `aletheia-os`，本地 source path 应指向该插件目录。

示例：

```json
{
  "name": "aletheia-os",
  "source": {
    "source": "local",
    "path": "./plugins/aletheia-os"
  }
}
```

插件目录准备好后，在 Claude Code 中添加对应 marketplace，再从 `/plugin` 菜单安装 `aletheia-os`。

### Codex 本地安装

Codex 使用 `.codex-plugin/plugin.json` 作为 manifest。发布目录由打包脚本生成：

```bash
python3 scripts/package_plugin.py --output /tmp/aletheia-os-dist
```

输出：

```text
/tmp/aletheia-os-dist/aletheia-os/
```

该目录包含 `.codex-plugin/`、`.claude-plugin/`、`agents/`、`codex-agents/`、`skills/`、`assets/`、`scripts/` 和 `README.zh-CN.md`。

## 可选 subagents

AletheiaOS 提供 3 个可选的真相层审阅 subagents，不改变核心闭环，也不会写入目标仓库的默认 scaffold：

- `truth-auditor`：检查变更是否仍符合 `.aletheia/` 中的 mission、active state、system graph、active node、约束和 checkpoint 要求。
- `evidence-curator`：检查 claim、hypothesis、evidence、decision 之间的证据链，标出缺失证据、弱推翻标准和过度推断。
- `architecture-reviewer`：检查 node 边界、contracts、decisions、skeleton 和实现之间是否漂移。

Claude Code 插件可以直接读取插件根目录下的 `agents/`。安装插件后，这 3 个 profiles 会随插件目录一起提供。

Codex 的自定义 agent 当前以项目级 `.codex/agents/` 或个人级 `~/.codex/agents/` TOML 文件加载。插件发布包提供同语义的 `codex-agents/` profiles；需要在某个目标仓库使用时，将它们放入该仓库的 `.codex/agents/`：

```bash
mkdir -p /path/to/target-repo/.codex/agents
cp /tmp/aletheia-os-dist/aletheia-os/codex-agents/*.toml /path/to/target-repo/.codex/agents/
```

这 3 个 subagents 只用于读取与审阅 `.aletheia/` truth layer，不承担实现、排期、发布或流程编排职责。

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

### 验证插件自带 scaffold

```bash
python3 scripts/validate_scaffold.py assets/scaffold
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

`bin/` 提供 orient、context pack、model gate、intake inventory、guided bootstrap、overview、validate、bootstrap finalize、checkpoint 和 Claude hook runtime。

## 推荐闭环

```text
orient on project truth
-> model gate
-> execute
-> update evidence / decision / contract / risk / active state
-> validate truth layer
-> checkpoint
```

`orient` 会输出固定的 Global View Checksum，帮助 agent 在动手前明确 active node、父级约束、成功标准、推翻标准、需要更新的 truth records、验证路径和 checkpoint 计划。

对应的 plugin skills：

- `aletheia-bootstrap`：初始化目标仓库的 `.aletheia/` truth layer。
- `aletheia-orient`：从唯一事实源建立项目视图并定位 active node。
- `aletheia-checkpoint`：验证并提交 coherent project truth update。
- `aletheia-design-evidence`：为 claim、实验和设计分支创建可证伪证据。
- `aletheia-architecture-evolution`：支持架构决策、契约变更和 skeleton traversal。

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

## 设计原则

1. 仓库是长期事实源，聊天不是长期事实源。
2. 每个重要 claim 都应可证伪或明确标记为解释性判断。
3. 实现必须能追溯到目标、系统节点、契约或证据。
4. 架构迭代是一种设计研究流程，需要 evidence 和 invalidation criteria。
5. `.aletheia/` 是 truth layer，不是源码、测试或公开文档的替代品。
6. plugin 负责操作协议，目标仓库负责保存真实项目事实。
7. 人类总览应从真实项目事实生成，而不是手写状态页。

## 适合谁使用

AletheiaOS 适合正在用 AI agent 维护复杂研究与工程项目的开发者，尤其是：

- 项目目标和约束需要长期保留；
- 架构会持续演进；
- 研究成果和设计取舍需要沉淀为证据与决策；
- 需要区分 claim、evidence、decision 和 implementation；
- 希望多个 agent 每次工作前先对齐同一份项目事实；
- 不希望重要项目状态只存在于聊天上下文。
