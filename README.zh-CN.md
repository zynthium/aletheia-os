# AletheiaOS

[English](README.md)

![AletheiaOS hero](docs/assets/readme-hero.jpg)

**面向 AI 辅助研究与工程的仓库原生可证伪真理树层。**

**One repo. One falsifiable truth tree. Many agents.**

AletheiaOS = Root-based Truth Tree + Scientific Method Loop + Repo-native Memory + Agent Governance。

AletheiaOS 用 `.aletheia/` 为复杂项目维护唯一可信事实源：根目标、当前状态、系统图、项目骨架、树治理规则、架构约束、研究证据、决策记录、接口契约、风险和 agent 归因。它不只是 repo-native truth layer，也不是普通项目文档系统；它把项目事实组织成一棵可审查、可证伪、可演化的真理树。

可证伪真理树层是 repo-native truth layer（仓库原生事实层）的升级形态：仓库原生事实层保存项目事实，truth tree governance 约束事实如何生长、证伪、晋升和重构。

AletheiaOS 将复杂项目维护为一棵 root-based truth tree：

- 根定义项目的核心目标或研究问题；
- 主干定义核心对象、主要理论或系统骨架；
- 分支承载子理论、子系统、架构方向或研究路径；
- 叶子承载具体证据、假设、决策、契约、实现和任务；
- 无法归属的内容进入 orphan/incubator，等待审查、挂载、拆分、合并或归档。

这棵树通过科学方法循环演化：观察 -> 假设 -> 证据 -> 证伪标准 -> 决策 -> 工程化 -> 反馈 -> 树重构。

AletheiaOS 中的 truth 指“当前最可信、可审查、可证伪的项目事实”，不是绝对真理。

它适用于长周期研究与工程项目。在这类项目中，理论、实现、证据、风险和优化会共同演化，局部实现发现也可能推翻顶层假设。AletheiaOS 的目标不是替代 Codex、Claude Code、OpenSpec、Superpowers、gstack、Compound 或其他 AI 编码工作流，而是为它们提供同一份 repo-native project truth。

## 为什么需要 AletheiaOS

AI agent 擅长局部执行，但在长周期一致性上很脆弱。AletheiaOS 不是为了解决“项目缺少文件夹”问题，而是为了解决复杂 AI 辅助开发中的无结构增生：

- agent 不断增加代码、功能、文档和结论，却无法说明它们服务哪个根目标；
- 新想法不知道应该挂到哪条主干、哪个分支或哪个父节点；
- 局部实现、研究结论和架构决策彼此脱节，甚至覆盖父级约束；
- 重要 claim 没有证据强度、证伪标准、降权条件或后续决策；
- 已削弱或被证伪的 hypothesis 继续支撑 active decision；
- 多个 agent 或工具基于不同版本的项目事实工作；
- 开发者和科研人员在低权重枝叶上持续优化，却偏离主干目标。

AletheiaOS 通过把项目事实显式化、树状化、可验证并纳入版本控制来减少这种漂移。它让 agent 先定位根目标、active node、父级约束和证据状态，再决定新材料进入主树、orphan/incubator，还是触发树重构。

## 适合谁使用

AletheiaOS 适合正在用 AI agent 维护复杂研究与工程项目的开发者，尤其是：

- 项目目标和约束需要长期保留；
- 架构会持续演进；
- 研究成果和设计取舍需要沉淀为证据与决策；
- 需要区分 claim、evidence、decision 和 implementation；
- 希望多个 agent 每次工作前先对齐同一份项目事实；
- 不希望重要项目状态只存在于聊天上下文。

## 功能

- 为目标仓库初始化 `.aletheia/` truth layer。
- 引导 agent 从唯一事实源读取 mission、active state、system graph、skeleton 和 active node。
- 在 durable writes 前执行模型能力门控和 agent attribution。
- 记录 evidence、decisions、contracts、risks 和 session notes。
- 支持复杂项目的架构演进、约束追踪和逐层展开。
- 强制 agent 判断新事实应挂载到主树，还是进入 orphan/incubator 等待审查。
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

Claude Code 可以通过 CLI 完成 marketplace 注册和插件安装。Codex CLI 当前可以注册 marketplace；注册后在 Codex 中打开 `/plugins`，从 AletheiaOS marketplace 启用 `aletheia-os`。Codex 插件启用是宿主 UI 限制，不是仓库脚本可以直接完成的项目能力。

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

该目录包含 `.codex-plugin/`、`.claude-plugin/`、`.agents/`、`agents/`、`codex-agents/`、`skills/`、`assets/`、`scripts/`、`README.md` 和 `README.zh-CN.md`。

本地 Claude Code 测试：

```bash
claude plugin validate .
claude --plugin-dir .
```

真实宿主 smoke 验收见 [Host Smoke Checklist](docs/verification/host-smoke.zh-CN.md)。

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

`bootstrap_finalize.py` 会安装 AletheiaOS Git hooks，并把目标仓库的 `core.hooksPath` 指向 `.aletheia/hooks`。它也会默认创建第一笔 bootstrap checkpoint，提交中带有 `AIOS-Action: truth.bootstrap.initialize` 和 `AIOS-Tree-Op: bootstrap`。也就是说，bootstrap finalize 会安装 AletheiaOS Git hooks；这是默认强约束，用于让后续提交继续经过 `.aletheia/bin/validate.py`。

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

`CAPABILITY_MAP.md` 是 action parity 清单：记录安装、初始化、orient、context pack、tree governance review、truth record create/list/show/update/archive、model gate、source inventory、bootstrap finalize、validate、overview、checkpoint、truth promotion 和只读审阅 agent 等用户动作与 agent 能力的对应关系。

`bin/` 提供 help、capability audit、orient、context pack、system context、preflight、status refresh、truth record、model gate、source inventory、guided bootstrap、overview、validate、bootstrap finalize、checkpoint 和 Claude hook runtime。`orient.py` 默认输出 cache 友好的稳定事实和精简 record inventory；`context_pack.py` 默认输出核心 truth files、能力地图、精简 source inventory summary 和完整 truth record inventory。`system_context.py` 输出可直接放入 agent prompt 的动态上下文块，组合稳定项目事实、用户偏好、能力地图和可选 runtime context。当前 agent run 与最近 session notes 需要显式使用 `--with-runtime`，并追加在稳定上下文之后。`status.py` 是显式动态刷新入口，用于按需查看 active state、validation、record counts、runtime gate、recent changes、generated-output boundaries 和 next actions。`capability_audit.py` 用于检查 `.aletheia/CAPABILITY_MAP.md` 是否覆盖 runtime scripts、skills、review agents 和 CRUD 命令。`preflight.py` 是 Codex 等无自动 hook enforcement 宿主的显式检查入口，会读取 model gate、validation、git status、checkpoint candidate、generated-output boundaries 和 recommended action ids。`playbooks/prompt_native_boundaries.md` 记录哪些运行时脚本应保持 primitive，哪些 workflow judgment 应移到 skills 或 playbooks。

## 运行时参考

```bash
python3 .aletheia/bin/bootstrap_finalize.py
python3 .aletheia/bin/help.py
python3 .aletheia/bin/action.py list --json
python3 .aletheia/bin/action.py next --json
python3 .aletheia/bin/action.py explain truth.validate --json
python3 .aletheia/bin/capability_audit.py
python3 .aletheia/bin/orient.py
python3 .aletheia/bin/orient.py --with-runtime
python3 .aletheia/bin/orient.py --static
python3 .aletheia/bin/context_pack.py
python3 .aletheia/bin/context_pack.py --with-runtime
python3 .aletheia/bin/system_context.py
python3 .aletheia/bin/system_context.py --with-runtime
python3 .aletheia/bin/preflight.py
python3 .aletheia/bin/preflight.py --json
python3 .aletheia/bin/status.py
python3 .aletheia/bin/status.py --json
python3 .aletheia/bin/truth_record.py list evidence
python3 .aletheia/bin/truth_record.py create evidence --id EV-0001 --title "Claim title"
python3 .aletheia/bin/truth_record.py show evidence EV-0001
python3 .aletheia/bin/truth_record.py update evidence EV-0001 --status active
python3 .aletheia/bin/truth_record.py archive evidence EV-0001 --reason "Superseded by stronger evidence"
python3 .aletheia/bin/truth_record.py show charter current
python3 .aletheia/bin/truth_record.py create orphan --id ORPH-0001 --title "Unmounted claim"
python3 .aletheia/bin/truth_record.py list orphan --json
python3 .aletheia/bin/truth_record.py show orphan ORPH-0001 --json
python3 .aletheia/bin/truth_record.py update orphan ORPH-0001 --status reviewed
python3 .aletheia/bin/truth_record.py update orphan ORPH-0001 --candidate-parent root --source-ref .aletheia/evidence/EV-0001.md --next-review 2099-01-01 --evidence-needed "Confirm with source inventory" --disposition attach
python3 .aletheia/bin/truth_record.py archive orphan ORPH-0001 --reason "Disposition resolved"
python3 .aletheia/bin/model_gate.py --task-class <task_class> --provider <provider> --model-id <model_id> --record --objective "<objective>"
python3 .aletheia/bin/model_gate.py --task-class bootstrap_finalize --provider <provider> --model-id <model_id> --tier C3 --operator-approved --record --objective "Initialize AletheiaOS"
python3 .aletheia/bin/model_gate.py --registry list
python3 .aletheia/bin/model_gate.py --registry register <name> --provider <provider> --model-id <model_id> --tier C3
python3 .aletheia/bin/model_gate.py --registry disable <name>
python3 .aletheia/bin/model_gate.py --registry deprecate <name> --reason "<reason>"
python3 .aletheia/bin/model_gate.py --registry remove <name>
python3 .aletheia/bin/model_gate.py --registry deny <model_id> --reason "<reason>"
python3 .aletheia/bin/source_inventory.py
python3 .aletheia/bin/guided_bootstrap.py --inspect --json
python3 .aletheia/bin/guided_bootstrap.py --objective "<objective>"
python3 .aletheia/bin/bootstrap_finalize.py --inspect --json
python3 .aletheia/bin/overview.py
python3 .aletheia/bin/overview.py --watch
python3 .aletheia/bin/overview.py --public-docs
python3 .aletheia/bin/validate.py
python3 .aletheia/bin/checkpoint.py --dry-run
python3 .aletheia/bin/checkpoint.py
```

首次 bootstrap 可以用 `--operator-approved` 明确授权当前模型完成初始化；项目固定后，应把可信模型登记到 `.aletheia/governance/model_registry.json`，后续 durable writes 由 registry 决定。可用 `model_gate.py --registry list/register/show/enable/disable/deprecate/remove/deny/undeny` 显式维护 registry，避免依赖手改 JSON。

`model_gate.py` 是治理、归因和审计边界，不是安全沙箱，也不是不可绕过的权限系统。它用于让 agent 在写入前显式声明 task class、model、tier 和 objective，并留下可审查记录。

Claude Code 通过 hooks 自动执行门禁和审计；Codex 当前以 skills、显式命令和可选 subagents 执行同一协议，不宣称拥有等同的自动 hook enforcement。Codex 上的显式闭环是：`orient.py --with-runtime`、`status.py --json` 或 `preflight.py --json`、写入 truth、`validate.py`、`checkpoint.py --dry-run`。

### Git 可追溯性

AletheiaOS 将 `.aletheia/` 视为当前 truth state，将 Git history 作为 truth-transition log。稳定节点的生长只有在 validate 通过、链接支撑 evidence 和 decision、提交 human-confirmed stable marker，并且 `history_audit.py --json` 能重建该 transition 后才算完成。

`AIOS-Node-State: stable` 是稳定节点 claim 的 durable marker。它必须同时带有 evidence、decision、`AIOS-Validation: pass` 和 `AIOS-Review: human-confirmed`。

Codex 上稳定 truth change 的显式闭环是：

```bash
python3 .aletheia/bin/orient.py --with-runtime
python3 .aletheia/bin/preflight.py --json
python3 .aletheia/bin/validate.py
python3 .aletheia/bin/checkpoint.py --dry-run
python3 .aletheia/bin/checkpoint.py --node theory_model --node-state stable --evidence .aletheia/evidence/EV-001-factor-baseline.md --decision .aletheia/decisions/DEC-001-modeling-lens-policy.md --review human-confirmed
python3 .aletheia/bin/history_audit.py --json
```

truth_record.py 支持 `--json` 输出，便于 agent 稳定组合 list、create、show、update 和 archive 结果。固定 truth files 可用 `current` 作为记录 id，例如 `truth_record.py show capability-map current`、`truth_record.py show charter current`、`truth_record.py update active-state current --section "Active frontier" --content "..."` 和 `truth_record.py archive runtime-policy current --reason "..."`。orphan incubator 的常用生命周期可通过 `truth_record.py create/list/show/update/archive orphan` 完成；少量 review 字段可用 `--candidate-parent`、`--source-ref`、`--next-review`、`--evidence-needed` 和 `--disposition` 更新，复杂 review 仍可直接编辑 `.aletheia/state/ORPHANS.yaml` 后验证。truth record 删除默认采用 archive-only 策略；永久移除属于人工/admin 操作，应先确认没有悬空引用。

`checkpoint.py` 默认只提交 AletheiaOS state/control-plane 路径；只有显式传入 `--include-worktree` 时才 stage 整个工作树。

`guided_bootstrap.py` 会验证已经记录的 bootstrap gate，不会自行创建新的模型授权；`guided_bootstrap.py --inspect --json` 可先只读检查 gate、source inventory 和计划写入。`bootstrap_finalize.py --inspect --json` 可只读检查 model gate、validation、critical truth markers、Git readiness 和计划写入。`source_inventory.py` 默认跳过 `.aletheia/`、`.claude/` 和初始化根部控制文件，只扫描项目自身资料。`context_pack.py` 只引用 source inventory 的聚合摘要，不默认展开高频变化的运行时记录；需要刷新当前状态时运行 `status.py --json`，不要把动态状态前移到默认 orient/context pack。`preflight.py` 会在 Codex 等无自动 hook enforcement 宿主中输出 context、runtime gate、validation、checkpoint candidate、generated-output boundaries 和建议下一步。`runtime_policy.json` 保存只读命令、source inventory 规则、checkpoint state paths、checkpoint excluded generated/runtime paths 和 protected path patterns，让 hook/checkpoint 规则可审查。新增或改变用户可执行动作时，应同步更新 `.aletheia/CAPABILITY_MAP.md`。

`overview.py` 和 `source_inventory.py` 默认写入 `.aletheia/` 下的 generated/intermediate 目录，不属于 durable project truth；`status.py --json`、`preflight.py --json` 和 overview `status.json` 都会显式标注这些 generated/runtime outputs。`overview.py --watch` 可重复刷新本地 status JSON/HTML，只有显式使用 `--public-docs` 时才生成 `docs/overview/`。

## 核心模型

AletheiaOS 的核心模型是：

```text
root objective / research question
-> truth tree skeleton
-> hypotheses / evidence / decisions
-> contracts / nodes / implementation
-> validation / feedback / tree refactor
```

旧有工程链路仍然成立，但它是 truth tree 的一个工程投影：

```text
mission -> system graph -> skeleton -> contracts -> evidence -> decisions -> code
```

其中：

- `skeleton` 负责结构：根、主干、分支、叶子、父子关系和继承约束；
- `hypotheses`、`evidence` 和 `decisions` 负责科学方法循环：观察、假设、证据、证伪标准、接受、削弱或归档；
- `contracts`、`nodes` 和代码负责工程化：把 accepted truth 变成边界契约、系统节点和实现约束；
- `validate`、`preflight`、`overview` 和 `checkpoint` 负责让树的演化可审查、可追踪、可回滚。

目录分工：

- `governance/` 保存 charter、attention policy、tree governance、model governance、model registry、runtime policy、git policy 和 source policy；
- `state/` 保存 active state、system graph、project skeleton、orphan incubator、frontier board、glossary、domain profile 和 risk register；
- `nodes/` 保存可下钻的系统节点事实；
- `evidence/` 保存实验、验证、观察、推理和解释记录；
- `decisions/` 保存长期项目和架构决策；
- `contracts/` 保存模块、接口和边界契约；
- `risks/` 保存失效模式、不确定性和待证伪假设；
- `agent_runs/` 保存 agent attribution 和模型门控记录。

源码、测试、公开文档和构建配置仍保存在项目常规目录中。`.aletheia/` 是事实控制平面，不是实现与数据平面的替代品。

## 定位边界

AletheiaOS 是：

- repo-native truth layer；
- 面向 AI 辅助研究与工程的可证伪真理树层；
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

延伸阅读：

- [AletheiaOS：面向 AI 辅助研究与工程的仓库原生可证伪真理树层](docs/articles/aletheia-os-project-introduction.zh-CN.md)
- [AletheiaOS 工作原理与使用过程](docs/articles/aletheia-os-working-principles-and-usage.zh-CN.md)

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

## 设计原则

0. 项目事实必须从根目标出发，沿主干、分支和叶子有序生长；无法归属的内容不得强行进入主树。
1. 仓库是长期事实源，聊天不是长期事实源。
2. 每个重要 claim 都应可证伪或明确标记为解释性判断。
3. 实现必须能追溯到目标、系统节点、契约或证据。
4. 架构迭代是一种设计研究流程，需要 evidence 和 invalidation criteria。
5. `.aletheia/` 是 truth layer，不是源码、测试或公开文档的替代品。
6. plugin 负责操作协议，目标仓库负责保存真实项目事实。
7. 人类总览应从真实项目事实生成，而不是手写状态页。

重要 truth member 必须能说明：

- 服务哪个上层目标；
- 继承哪些父级约束；
- 当前证据状态是什么；
- 什么条件会削弱或推翻它；
- 是否已经被工程化为 contract、node 或 implementation constraint。
