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

延伸阅读：[AletheiaOS：面向 AI 辅助研究与工程的仓库原生事实层](docs/articles/aletheia-os-project-introduction.zh-CN.md)。

## 核心模型

AletheiaOS 将项目表示为一个受约束治理的系统图：

```text
mission -> system graph -> skeleton -> contracts -> evidence -> decisions -> code
```

其中：

- `governance/` 保存 charter、attention policy、model governance、model registry、git policy 和 source policy；
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
- 在大量资料场景下，引导 agent 使用外部 LLM Wiki 编译研究空间，再将确认结果沉淀为项目事实。
- 通过 `python3 .aletheia/bin/help.py` 和 `.aletheia/CAPABILITY_MAP.md` 发现 agent 可完成的项目事实动作。
- 提供 repo-native validation、overview、bootstrap finalize 和 checkpoint runtime。
- 通过 model registry 管理 task class、能力层级、注册模型和 denylist。
- 用 `.aletheia/CAPABILITY_MAP.md` 维护用户动作、agent 能力和 truth record CRUD 覆盖关系。

## 安装

### 推荐：一条命令安装

全局安装到 Claude Code，并为 Codex 注册 marketplace：

```bash
python3 scripts/install_aletheia.py --host both --scope user
```

项目级安装，并把 Codex 可选 subagents 放入目标仓库：

```bash
python3 scripts/install_aletheia.py --host both --scope project --project /path/to/target-repo --with-codex-agents
```

如果希望安装后直接初始化目标仓库的 `.aletheia/` truth layer：

```bash
python3 scripts/install_aletheia.py --host both --scope project --project /path/to/target-repo --with-codex-agents --init-project
```

Claude Code 可以通过 CLI 完成 marketplace 注册和插件安装。Codex CLI 当前可以注册 marketplace；注册后在 Codex 中打开 `/plugins`，从 AletheiaOS marketplace 启用 `aletheia-os`。

### 手动安装

Claude Code 全局安装：

```bash
claude plugin marketplace add zynthium/aletheia-os --scope user
claude plugin install aletheia-os@aletheia-os --scope user
```

Claude Code 项目级安装：

```bash
claude plugin marketplace add zynthium/aletheia-os --scope project
claude plugin install aletheia-os@aletheia-os --scope project
```

Codex 全局注册 marketplace：

```bash
codex plugin marketplace add zynthium/aletheia-os
```

然后在 Codex 中打开 `/plugins`，启用 `aletheia-os`。

### 本地开发安装

本地开发时可以直接从当前 checkout 或发布目录测试。AletheiaOS 同时包含 `.codex-plugin/plugin.json` 和 `.claude-plugin/plugin.json`，同一个发布目录可以被 Codex 和 Claude Code 使用。

```bash
python3 scripts/package_plugin.py --output /tmp/aletheia-os-dist
```

输出：

```text
/tmp/aletheia-os-dist/aletheia-os/
```

该目录包含 `.codex-plugin/`、`.claude-plugin/`、`.agents/`、`agents/`、`codex-agents/`、`skills/`、`assets/`、`scripts/` 和 `README.zh-CN.md`。

本地 Claude Code 测试：

```bash
claude plugin validate .
claude --plugin-dir .
```

真实宿主 smoke 验收见 [Host Smoke Checklist](docs/verification/host-smoke.zh-CN.md)。

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

1. 安装插件。
2. 初始化目标仓库的 `.aletheia/`。
3. 让 agent orient 当前项目事实。
4. 执行当前任务。
5. 更新受影响的 truth records。
6. validate 并 checkpoint。

### 新项目

新项目可以先创建一个普通 git 仓库，再加入 AletheiaOS truth layer：

```bash
mkdir my-project
cd my-project
git init
python3 /path/to/aletheia-os/scripts/init_aletheia.py .
```

也可以在项目级安装插件时直接生成 `.aletheia/`：

```bash
python3 /path/to/aletheia-os/scripts/install_aletheia.py --host both --scope project --project . --with-codex-agents --init-project
```

然后让 AI assistant 按 `BOOTSTRAP.md` 完成第一轮项目事实综合：

```bash
python3 .aletheia/bin/model_gate.py --task-class bootstrap_finalize --provider <provider> --model-id <model_id> --tier C3 --operator-approved --record --objective "Initialize AletheiaOS"
python3 .aletheia/bin/source_inventory.py
python3 .aletheia/bin/guided_bootstrap.py --objective "Initialize AletheiaOS"
python3 .aletheia/bin/bootstrap_finalize.py
```

新项目不要让 agent 编造使命、领域事实或架构结论。先写清楚项目意图、约束、已知边界和第一批候选方向，再把它们综合到 `.aletheia/governance/`、`.aletheia/state/`、`.aletheia/nodes/`、`.aletheia/evidence/`、`.aletheia/decisions/`、`.aletheia/contracts/` 和 `.aletheia/risks/`。

### 已有项目

已有项目可以直接加入 AletheiaOS。建议先确认当前工作树状态，再执行初始化：

```bash
cd /path/to/existing-project
git status --short
python3 /path/to/aletheia-os/scripts/init_aletheia.py .
```

初始化会新增 AletheiaOS 控制平面，不会替换已有源码、测试、构建配置和公开文档。随后让 AI assistant 按已有材料建立第一版项目事实：

```bash
python3 .aletheia/bin/model_gate.py --task-class bootstrap_finalize --provider <provider> --model-id <model_id> --tier C3 --operator-approved --record --objective "Initialize AletheiaOS"
python3 .aletheia/bin/source_inventory.py
python3 .aletheia/bin/guided_bootstrap.py --objective "Initialize AletheiaOS"
python3 .aletheia/bin/orient.py
python3 .aletheia/bin/validate.py
python3 .aletheia/bin/bootstrap_finalize.py
```

已有项目的关键不是把所有材料一次性塞进 `.aletheia/`，而是先建立可审查的事实骨架：当前使命、系统图、项目骨架、active state、重要决策、边界契约、已有证据和主要风险。源码仍然是实现与数据平面；`.aletheia/` 只保存能指导后续 agent 工作的长期项目事实。

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

`bootstrap_finalize.py` 会安装 AletheiaOS Git hooks，并把目标仓库的 `core.hooksPath` 指向 `.aletheia/hooks`。也就是说，bootstrap finalize 会安装 AletheiaOS Git hooks；这是默认强约束，用于让后续提交继续经过 `.aletheia/bin/validate.py`。

### 验证插件自带 scaffold

```bash
python3 scripts/validate_scaffold.py assets/scaffold
```

## 日常闭环

```text
orient -> work -> update truth -> validate -> checkpoint
```

日常使用时，agent 应先读取 `.aletheia/START_HERE.md`，再围绕当前 active node 工作。完成非平凡任务后，更新 evidence、decision、contract、risk、node、session note 或 active state，再运行验证和 checkpoint。

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

`CAPABILITY_MAP.md` 是 action parity 清单：记录安装、初始化、orient、context pack、truth record create/list/show/archive、model gate、source inventory、bootstrap finalize、validate、overview、checkpoint、truth promotion 和只读审阅 agent 等用户动作与 agent 能力的对应关系。

`bin/` 提供 orient、context pack、truth record、model gate、source inventory、guided bootstrap、overview、validate、bootstrap finalize、checkpoint 和 Claude hook runtime。`orient.py` 默认输出 cache 友好的稳定事实和精简 record inventory；`context_pack.py` 默认输出核心 truth files、能力地图、精简 source inventory summary 和完整 truth record inventory。当前 agent run 与最近 session notes 需要显式使用 `--with-runtime`，并追加在稳定上下文之后。

## 外部 LLM Wiki 资料摄入

AletheiaOS core 不内置资料摄入系统。大量非结构化资料先交给外部 LLM Wiki 做编译、去重、主题聚合、概念关系和来源导航；AletheiaOS 只接收经过审查后要沉淀的 project truth。

```text
ChatGPT / Claude / Codex 对话资料
-> 外部 LLM Wiki 编译成可审查研究空间
-> AletheiaOS Wiki Handoff
-> aletheia-promote
-> evidence / hypothesis / decision / contract / risk / node / state
-> validate
-> checkpoint
```

当 agent 发现资料来自长对话、多来源研究或互相冲突的观察时，应引导用户先使用外部 LLM Wiki，并要求输出固定交接包：

```markdown
# AletheiaOS Wiki Handoff

Objective:
Wiki location:
Source corpus:
Source index:

## Candidate Project Skeleton

## Key Claims
- Claim:
  Source refs:
  Confidence:
  Limitations:
  Promote to: evidence | hypothesis | decision | contract | risk | node | state

## Evidence Map

## Conflicts

## Hypotheses

## Architecture Candidates

## Open Questions

## Suggested Promotions
```

详细规则见 `.aletheia/playbooks/external_llm_wiki_handoff.md` 和 `.aletheia/playbooks/wiki_handoff_promotion.md`。Wiki 页面只是 compiled research；使用 `aletheia-promote` 审查 handoff 后，只有晋升到 `.aletheia/evidence/`、`.aletheia/decisions/`、`.aletheia/hypotheses/`、`.aletheia/contracts/`、`.aletheia/risks/`、`.aletheia/nodes/` 或 `.aletheia/state/` 的内容才是 durable project truth。

`orient` 会输出固定的 Global View Checksum，并默认包含能力地图和 durable truth record inventory 摘要，帮助 agent 在动手前明确 active node、父级约束、成功标准、推翻标准、需要更新的 truth records、验证路径和 checkpoint 计划。高频变化的当前 agent run 和最近 session notes 需要显式使用 `python3 .aletheia/bin/orient.py --with-runtime`，最稳定的前置上下文可使用 `--static`。

对应的 plugin skills：

- `aletheia-bootstrap`：初始化目标仓库的 `.aletheia/` truth layer。
- `aletheia-orient`：从唯一事实源建立项目视图并定位 active node。
- `aletheia-checkpoint`：验证并提交 coherent project truth update。
- `aletheia-design-evidence`：为 claim、实验和设计分支创建可证伪证据。
- `aletheia-architecture-evolution`：支持架构决策、契约变更和 skeleton traversal。
- `aletheia-promote`：把外部 LLM Wiki handoff 中已确认的 findings 晋升为 durable truth records。

## 运行时参考

```bash
python3 .aletheia/bin/bootstrap_finalize.py
python3 .aletheia/bin/help.py
python3 .aletheia/bin/orient.py
python3 .aletheia/bin/orient.py --with-runtime
python3 .aletheia/bin/orient.py --static
python3 .aletheia/bin/context_pack.py
python3 .aletheia/bin/context_pack.py --with-runtime
python3 .aletheia/bin/truth_record.py list evidence
python3 .aletheia/bin/truth_record.py create evidence --id EV-0001 --title "Claim title"
python3 .aletheia/bin/truth_record.py show evidence EV-0001
python3 .aletheia/bin/truth_record.py archive evidence EV-0001 --reason "Superseded by stronger evidence"
python3 .aletheia/bin/model_gate.py --task-class <task_class> --provider <provider> --model-id <model_id> --record --objective "<objective>"
python3 .aletheia/bin/model_gate.py --task-class bootstrap_finalize --provider <provider> --model-id <model_id> --tier C3 --operator-approved --record --objective "Initialize AletheiaOS"
python3 .aletheia/bin/source_inventory.py
python3 .aletheia/bin/guided_bootstrap.py --objective "<objective>"
python3 .aletheia/bin/overview.py
python3 .aletheia/bin/overview.py --public-docs
python3 .aletheia/bin/validate.py
python3 .aletheia/bin/checkpoint.py
```

首次 bootstrap 可以用 `--operator-approved` 明确授权当前模型完成初始化；项目固定后，应把可信模型登记到 `.aletheia/governance/model_registry.json`，后续 durable writes 由 registry 决定。

`model_gate.py` 是治理、归因和审计边界，不是安全沙箱，也不是不可绕过的权限系统。它用于让 agent 在写入前显式声明 task class、model、tier 和 objective，并留下可审查记录。

Claude Code 通过 hooks 自动执行门禁和审计；Codex 当前以 skills、显式命令和可选 subagents 执行同一协议，不宣称拥有等同的自动 hook enforcement。

`checkpoint.py` 默认只提交 AletheiaOS state/control-plane 路径；只有显式传入 `--include-worktree` 时才 stage 整个工作树。

`guided_bootstrap.py` 会验证已经记录的 bootstrap gate，不会自行创建新的模型授权。`source_inventory.py` 默认跳过 `.aletheia/`、`.claude/` 和初始化根部控制文件，只扫描项目自身资料。`context_pack.py` 只引用 source inventory 的聚合摘要，不默认展开高频变化的运行时记录。新增或改变用户可执行动作时，应同步更新 `.aletheia/CAPABILITY_MAP.md`。

`overview.py` 和 `source_inventory.py` 默认写入 `.aletheia/` 下的 generated/intermediate 目录，不属于 durable project truth；只有显式使用 `--public-docs` 时才生成 `docs/overview/`。

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
