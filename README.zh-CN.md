# AletheiaOS

[English](README.md)

**面向 AI 辅助研究与工程的真实项目记忆。**

AletheiaOS 是一个 AI 原生的项目操作系统，面向长周期研究与工程项目。在这类项目中，理论、实现、证据、风险和优化必须共同演化。

它适用于那些无法用普通工单、笔记或聊天记录管理的复杂项目：量化交易系统、理论研究计划、飞行器或车辆设计、机器人、仿真、市场策略、产品策略，以及其他会持续演化的系统。在这些系统中，局部实现发现可能会推翻顶层假设。

AletheiaOS 把代码仓库，而不是聊天窗口，视为项目的持久记忆。Codex、Claude Code 等 AI 编程助手被用作执行者、调查者、审查者和综合分析引擎；项目本身则由章程、系统图、证据账本、模型门禁、生成式总览和 git checkpoint 治理。

## AletheiaOS 为什么存在

AI agent 擅长局部执行，但在长周期一致性上很脆弱。在大型研究工程项目中，它们很容易滑向：

- 局部优化
- 陈旧假设
- 未链接的主张
- 被遗忘的上层约束
- 未记录的决策
- 与理论脱节的代码
- 没有更新项目状态的实验
- 不清楚哪个模型做了什么修改

AletheiaOS 通过让项目状态显式化、结构化、可验证并纳入版本控制来防止这种漂移。

## 这是什么 / 不是什么

AletheiaOS 是：

- 面向 AI 辅助工作的项目记忆系统；
- 面向长周期研究与工程的治理脚手架；
- 在有限模型上下文中保存自顶向下约束的方法；
- 管理证据、决策、模型归因和 checkpoint 的框架；
- 面向 Codex、Claude Code 及类似工具的仓库原生操作协议。

AletheiaOS 不是：

- 任务管理器；
- 通用笔记应用；
- git 的替代品；
- 人类判断的替代品；
- 保证弱 AI 模型能完成高水平研究的机制；
- 能自动把非结构化项目变得一致的魔法层。

## 适用项目类型

当项目目标无法被压缩成一个短软件工单时，可以使用 AletheiaOS：

- 量化交易研究与生产化
- 带仿真和工程产物的理论物理研究计划
- 飞行器、车辆、机器人、能源、芯片或制造系统设计
- 市场策略、产品策略、供应链优化或投资组合配置
- 任何顶层约束可能被下游可行性发现推翻的项目

## 核心思想

AletheiaOS 将项目表示为一个**受约束治理的系统图**：

- **Charter**：使命、不可协商约束、优先级顺序
- **System Graph**：目标、理论、设计分支、能力、接口和依赖
- **Active State**：当前前沿、阻塞点、受保护假设、下一步行动
- **Evidence Ledger**：实验、仿真、现场测试、市场观察、证明尝试
- **Decision Records**：持久的设计、理论、产品和工程决策
- **Interface Contracts**：模块、学科、团队或抽象之间的边界
- **Risk Register**：不确定性、失效模式、推翻路径
- **Attention Policy**：AI agent 如何在有限上下文中保持自顶向下的注意力
- **Checkpoint Policy**：何时验证、提交、重新平衡或停止

目标是防止局部 AI-agent 漂移。每个任务都应该知道它的上层约束、当前节点、成功标准、推翻标准和下游影响。

## 人类总览

AletheiaOS 支持生成给人类看的总览层。

这个总览不是人工维护的状态页，而是从真实项目状态生成：

- 系统图
- 活动状态
- 证据账本
- 决策记录
- 风险登记表
- 接口契约
- git 状态
- 验证结果
- agent 归因记录

推荐生成的产物：

```text
docs/overview/index.html        # 项目驾驶舱
docs/overview/system_map.svg    # 系统图可视化
docs/overview/status.json       # 编译后的项目状态
docs/overview/nodes/            # 系统图节点的下钻页面
```

真实性规则：

- 总览产物应该由程序生成，而不是手工编辑；
- 缺失状态显示为 `unknown`，不能推断为健康；
- 过期状态必须明确显示；
- 每个展示出的状态都要能链接回源文件或 git 状态；
- 当项目状态不一致时，总览生成应失败或发出警告。

## 作为项目脚手架使用

可以将此仓库作为 GitHub template 使用，也可以 clone 到新项目后运行 bootstrap 流程：

```bash
git clone https://github.com/<your-org>/aletheia-os.git my-project
cd my-project
rm -rf .git
git init
python3 scripts/aios_bootstrap.py --finalize
```

当前 checkout 没有配置 remote；发布命令前请将 `<your-org>` 替换为实际仓库 owner。

## 首次初始化

对于任何 AI 编程助手，bootstrap 之后的稳定入口是 `START_HERE.md`。`BOOTSTRAP.md` 只在首次初始化时使用，初始化后会被删除。

1. 创建或进入项目目录。
2. 将 AletheiaOS 复制到该目录。
3. 从仓库根目录启动 Codex 或 Claude Code。
4. 要求助手执行：

```text
Read BOOTSTRAP.md and initialize this project. Keep the abstraction domain-neutral unless I specify a domain profile. Before changing files, produce the Global View Checksum from START_HERE.md.
```

5. 助手应自定义：
   - `aletheia_os/00_CHARTER.md`
   - `aletheia_os/01_SYSTEM_GRAPH.yaml`
   - `aletheia_os/02_ACTIVE_STATE.md`
   - `aletheia_os/09_DOMAIN_PROFILE.md`
6. 运行：

```bash
python3 scripts/aios_bootstrap.py --finalize
```

这会验证 AletheiaOS，配置本地 git hooks，删除 `BOOTSTRAP.md`，并创建初始 git checkpoint。

## 日常工作流

每个会话默认只处理一个 active node。开始或恢复工作时运行：

```bash
python3 scripts/aios_orient.py
```

它会打印自顶向下的 context pack 和 Global View Checksum 模板。

工作流：

```text
1. Orient: 识别 active graph node、上层约束、成功/失败标准。
2. Frame: 定义目标、非目标、测试、证据要求和停止条件。
3. Execute: 实现、研究、仿真、推导、测试或审查。
4. Verify: 运行工程检查、证据检查和系统图一致性检查。
5. Commit: 更新证据、决策、契约、活动状态和 git checkpoint。
6. Distill: 写 session note，并清理/重置 AI 上下文。
```

## 重要命令

当前脚本前缀 `aios_` 表示 AletheiaOS。

```bash
# 验证必需项目状态文件和链接规则
python3 scripts/aios_validate.py

# 为当前 AI 助手执行任务门禁，并记录归因
python3 scripts/aios_model_gate.py --task-class research_design --record --objective "short objective"

# 为新 AI 会话打印紧凑 context pack
python3 scripts/aios_context_pack.py

# 验证并打印自顶向下的 orientation pack
python3 scripts/aios_orient.py

# 创建安全的项目 checkpoint commit
python3 scripts/aios_checkpoint.py --auto

# 完成首次初始化；会删除 BOOTSTRAP.md
python3 scripts/aios_bootstrap.py --finalize

# 启用本地 git pre-commit validation hook
python3 scripts/aios_bootstrap.py --configure-hooks
```

## 模型治理与归因

AletheiaOS 包含 AI 编程助手能力门禁。它不会假设每个模型都足以胜任研究密集型工作。持久写入前，助手应运行：

```bash
python3 scripts/aios_model_gate.py --task-class <task_class> --record --objective "<short objective>"
```

门禁会检查 `aletheia_os/model_registry.json`，并在 `aletheia_os/agent_runs/` 下创建归因记录。未知模型默认只读。对于不暴露模型标识的工具，可以显式设置元数据：

```bash
AIOS_AGENT_PROVIDER=openai \
AIOS_MODEL_ID="provider-model-id" \
AIOS_AGENT_TOOL=codex \
python3 scripts/aios_model_gate.py --task-class research_design --record --objective "Design evidence protocol"
```

能力层级是实用治理层级，不是字面意义上的 IQ 分数：

```text
C0: unknown/read-only
C1: basic helper/documentation
C2: engineering executor
C3: research-engineering model
C4: strategic research lead / safety-critical model
```

每个非平凡 checkpoint 都应在 git commit message 中包含 agent attribution trailers。请在 `aletheia_os/model_registry.json` 中配置已批准模型，并将弱模型或不希望使用的模型放入 denylist。

## 注意力模型

AletheiaOS 使用分层注意力策略，而不是要求助手读取所有内容。

```text
Tier 0: START_HERE, AGENTS, Charter, Attention Policy, Model Governance, Active State
Tier 1: active system node and parent/child dependencies
Tier 2: contracts and decision records for crossed boundaries
Tier 3: evidence relevant to the current claim or promotion decision
Tier 4: local implementation files, tests, experiments, and simulations
```

这能让助手锚定根使命，同时避免上下文窗口被无关分支消耗。详细规则位于 `aletheia_os/10_ATTENTION_POLICY.md`。

## 最终实现代码的位置

对于交付代码的项目，持久实现代码应放在：

```text
src/<project_package_name>/
```

示例：

```text
src/quant_system/
src/aircraft_design/
src/physics_sim/
src/market_optimizer/
```

目录边界：

- `aletheia_os/`：项目为什么存在、当前什么为真、已有证据、已做决策。
- `src/`：可复用实现代码，未来可能成为生产、仿真或持久系统代码。
- `experiments/`：探索性 notebooks、运行结果、临时分析和研究试验。
- `simulations/`：场景引擎、回放环境、合成世界、压力测试。
- `tests/`：实现、假设、接口、泄漏和回归验证。
- `scripts/`：轻量操作包装器和仓库工具。

`experiments/` 和 `simulations/` 可以从 `src/` 导入；`src/` 不得从 `experiments/` 导入。

## 自动 checkpoint 行为

AletheiaOS 支持保守的自动 git commit。

默认情况下，Claude Code 的 stop hook 只会验证并报告是否建议创建 checkpoint。若要允许 stop 事件自动提交，设置：

```bash
export AIOS_AUTOCOMMIT=1
```

stop-event checkpoint 只有在以下条件满足时才允许：

- validation 通过；
- git 存在变更；
- 没有疑似 secret 的受保护文件被 staged；
- 已记录 allowed agent run，除非 operator 明确覆盖归因要求；
- 任务已经更新持久项目状态，例如 `aletheia_os/02_ACTIVE_STATE.md`、`aletheia_os/evidence/`、`aletheia_os/decisions/`、`aletheia_os/contracts/` 或 `aletheia_os/session_notes/`。

这能避免在未同步项目状态或模型归因时提交半成品 code-only edits。若要允许 code-only 自动提交，设置：

```bash
export AIOS_ALLOW_CODE_ONLY_COMMIT=1
```

若只针对一次人工/operator commit 有意绕过缺失模型归因，设置：

```bash
export AIOS_ALLOW_UNATTRIBUTED_CHECKPOINT=1
```

也可以随时手动 checkpoint：

```bash
python3 scripts/aios_checkpoint.py --auto --message "checkpoint: complete active-node update"
```

## 目录地图

```text
.
├── START_HERE.md                  # 任意 AI 编程助手的稳定入口
├── AGENTS.md                      # Codex/repo 级 agent 操作规则
├── CLAUDE.md                      # Claude Code 项目记忆，导入 AGENTS.md
├── BOOTSTRAP.md                   # 首次初始化协议；初始化后删除
├── README.md                      # 面向人类的英文文档
├── README.zh-CN.md                # 面向人类的中文文档
├── aletheia_os/                   # 持久项目记忆和治理
│   ├── AGENTS.md
│   ├── 00_CHARTER.md
│   ├── 01_SYSTEM_GRAPH.yaml
│   ├── 02_ACTIVE_STATE.md
│   ├── 03_FRONTIER_BOARD.md
│   ├── 04_RISK_REGISTER.md
│   ├── 05_GLOSSARY.md
│   ├── 06_INTERFACE_CONTRACTS.md
│   ├── 07_EVIDENCE_INDEX.md
│   ├── 08_GIT_POLICY.md
│   ├── 09_DOMAIN_PROFILE.md
│   ├── 10_ATTENTION_POLICY.md
│   ├── 11_MODEL_GOVERNANCE.md
│   ├── model_registry.json
│   ├── agent_runs/
│   ├── contracts/
│   ├── decisions/
│   ├── evidence/
│   ├── hypotheses/
│   ├── nodes/
│   ├── playbooks/
│   ├── session_notes/
│   └── templates/
├── scripts/                       # validation、orientation、bootstrap、checkpoint、context 工具
├── src/                           # 持久实现代码
├── tests/                         # 验证
├── experiments/                   # 探索性工作
├── simulations/                   # 仿真和压力场景
├── .agents/skills/                # Codex-compatible skills
├── .claude/skills/                # Claude Code-compatible skills
├── .claude/agents/                # Claude Code subagents
├── .claude/settings.json          # 项目级 Claude Code hooks
└── .githooks/pre-commit           # 可选 git hook path
```

## 操作规则

- 不要让助手只依赖聊天记忆工作。
- 不接受未链接的主张。每个主张都应附着到系统图节点、证据项或决策记录。
- 不允许局部优化静默改写全局目标。
- 没有证据、接口和推翻标准时，不要把想法推向生产。
- 将实现失败视为可能的上游设计证据。
- 根指令保持简短；把可重复工作流放入 skills 和 playbooks。
- 使用 `aletheia_os/10_ATTENTION_POLICY.md` 防止大范围上下文加载和局部漂移。

## Commit message 约定

```text
bootstrap: initialize AletheiaOS
state: update active project state
graph: update system graph
hypothesis: add or revise hypothesis
evidence: add experiment/simulation/proof/field evidence
decision: add or revise decision record
contract: update interface or boundary contract
engineering: implement or refactor system component
risk: update risk register
session: add session distillation
checkpoint: durable project checkpoint
```
