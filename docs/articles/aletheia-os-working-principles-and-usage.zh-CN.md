# AletheiaOS 工作原理与使用过程

AletheiaOS 是一个给 AI 辅助研究与工程项目使用的仓库原生事实层。它的核心目标不是让 agent 多一个工作流，而是让项目在多轮对话、多次提交、多种工具共同参与之后，仍然保留一份可审查、可验证、可回退的当前项目事实。

在普通 AI 编码过程中，很多重要判断会停留在聊天里：为什么选择这个架构，某个实验为什么算有效，某个假设何时被削弱，某个节点为什么可以标记为稳定。聊天适合探索，但不适合长期作为项目事实源。AletheiaOS 把这些事实沉淀到仓库中的 `.aletheia/`，再用 Git 提交历史记录事实如何变化。

可以把它理解为：

```text
.aletheia/ 保存当前事实状态
Git history 保存事实变化过程
validate / preflight / checkpoint / history audit 保证过程可检查
```

## 一句话模型

AletheiaOS = 可证伪真理树 + 项目事实控制平面 + Git 可追溯提交协议 + agent 使用约束。

其中：

- 真理树负责表达项目从根目标到主干、分支和叶子的事实结构；
- `.aletheia/` 负责保存当前最可信的项目事实；
- Git 提交负责保存事实如何从一个状态变成另一个状态；
- runtime scripts 和 skills 负责让 agent 在写入前后执行同一套验证与 checkpoint 协议。

它不替代源码、测试、README、issue、spec 或人工 review。它只是把“项目到底相信什么、为什么相信、什么时候改变过”变成仓库内的结构化事实。

## 为什么需要这一层

AI agent 很擅长完成局部任务，但天然有几个薄弱点：

- 当前对话上下文会丢失、压缩或被新任务覆盖；
- agent 容易根据局部代码做出合理但未对齐根目标的改动；
- 重要结论常常缺少证据、推翻条件和决策记录；
- 多个 agent 可能基于不同版本的项目理解工作；
- “用户确认过”这类信息如果只留在聊天里，后续无法审查；
- 项目树的节点生长、削弱、证伪、归档如果只体现在文件快照里，难以追溯过程。

AletheiaOS 的设计就是补这些洞。它让 agent 每次工作前先 orient 当前项目事实；让重要结论进入 evidence、decision、contract、risk、node 或 state；让结构变化经过 validate；让 checkpoint 生成带有 AletheiaOS 语义的 Git 提交；再用 history audit 从 Git history 反查节点是否真的稳定。

## 核心目录如何分工

初始化后，目标仓库会出现 `.aletheia/`：

```text
.aletheia/
  START_HERE.md
  governance/
  state/
  nodes/
  evidence/
  decisions/
  contracts/
  risks/
  hypotheses/
  session_notes/
  agent_runs/
  playbooks/
  templates/
  bin/
```

这些目录不是普通文档分类，而是事实边界：

- `governance/` 保存项目治理规则，例如 charter、attention policy、tree governance、Git policy、model governance 和 runtime policy。
- `state/` 保存当前状态，例如 active state、system graph、SKELETON.yaml、ORPHANS.yaml、risk register 和 frontier board。
- `nodes/` 保存可下钻的系统节点事实。
- `evidence/` 保存证据、实验、观察和推理记录。
- `hypotheses/` 保存仍需验证或可能被证伪的假设。
- `decisions/` 保存已接受的长期判断或架构决策。
- `contracts/` 保存接口、边界和实现约束。
- `risks/` 保存风险、失效模式和待证伪条件。
- `agent_runs/` 保存 agent 和模型归因。
- `bin/` 保存运行时工具，例如 `orient.py`、`validate.py`、`checkpoint.py`、`history_audit.py`。

这套拆分的目的，是避免 agent 把不同层级的东西混为一谈。一个观察不是决策；一个假设不是稳定事实；一个代码实现也不自动证明上层理论成立。AletheiaOS 要求这些关系显式化。

## 真理树如何工作

AletheiaOS 把项目事实组织成一棵 root-based truth tree：

```text
root objective / research question
-> trunk / core system model
-> branches / sub-theories / subsystems
-> leaves / evidence / decisions / contracts / implementation constraints
```

根节点定义项目要解决的核心问题。主干定义核心对象、主要理论或系统骨架。分支承载子系统、研究方向或架构路径。叶子承载具体证据、决策、契约、风险和实现约束。

新增事实必须回答三个问题：

1. 它服务哪个上层目标？
2. 它继承哪些父级约束？
3. 它当前是证据、假设、决策、契约、风险，还是节点事实？

如果暂时回答不了，材料不应强行进入主树，而应进入 `ORPHANS.yaml` 作为 incubating material，等待后续挂载、拆分、合并或归档。

## 科学方法循环

AletheiaOS 中的 truth 不是绝对真理，而是“当前最可信、可审查、可证伪的项目事实”。它要求重要 claim 尽量经过这样的循环：

```text
observation -> hypothesis -> evidence -> falsification criteria
-> decision -> engineering -> feedback -> tree refactor
```

这意味着：

- observation 只是观察；
- hypothesis 必须有推翻条件；
- evidence 必须说明来源、方法、限制和信心影响；
- decision 应链接支撑 evidence；
- engineering 应能追溯到 decision、contract 或 node；
- 新反馈可以削弱、证伪或重构原来的树。

这也是它适合研究型工程项目的原因。实现不是单向执行上层设计；实现中发现的事实也可以反向修正上层假设。

## Git 在 AletheiaOS 中的角色

`.aletheia/` 保存当前事实状态，但只看当前文件无法回答“它是怎么长成这样的”。Git 正好适合保存不可变的历史过程。因此 AletheiaOS 把 Git history 视为 truth-transition log。

这个设计有两个边界：

- 不另外建立 `.aletheia/ledger/`，避免复制 Git 已经擅长的历史记录能力；
- 不要求每个普通提交都有 AletheiaOS trailers，只要求 truth-tree transition、stable-node claim、weaken/falsify/archive 和实现 accepted truth 的提交带结构化标记。

关键 trailers 包括：

```text
AIOS-Action: truth.bootstrap.initialize | truth.tree.transition | truth.node.stabilize | truth.node.weaken | truth.node.falsify | truth.node.archive | engineering.implements_truth
AIOS-Tree-Op: bootstrap | attach_orphan | insert_parent | split_node | merge_nodes | move_subtree | promote_node | archive_branch
AIOS-Node: theory_model
AIOS-Parent: root
AIOS-Node-State: stable
AIOS-Evidence: .aletheia/evidence/EV-001-factor-baseline.md
AIOS-Decision: .aletheia/decisions/DEC-001-modeling-lens-policy.md
AIOS-Validation: pass
AIOS-Review: human-confirmed
```

当一个节点被声明为稳定时，AletheiaOS 要求提交中至少有：

```text
AIOS-Action: truth.node.stabilize
AIOS-Node: <known node id>
AIOS-Node-State: stable
AIOS-Evidence: <existing evidence record>
AIOS-Decision: <existing accepted decision record>
AIOS-Validation: pass
AIOS-Review: human-confirmed
```

这样，后续审查者不需要相信聊天记录，也不需要猜测某次提交的意图。只要看 Git history，就能知道某个节点何时被稳定、基于什么证据、链接哪个决策、是否经过验证、是否有人类确认。

## Runtime scripts 的职责

AletheiaOS 的 runtime scripts 尽量保持 primitive，而不是变成复杂编排系统。常用脚本职责如下：

- `orient.py`：读取当前项目事实，帮助 agent 建立工作前上下文。
- `system_context.py`：输出可放入 agent prompt 的动态项目上下文。
- `context_pack.py`：生成更完整的上下文包，包含核心 truth files 和 inventory。
- `preflight.py`：在没有自动 hook enforcement 的宿主中做显式检查。
- `validate.py`：验证当前 `.aletheia/` 事实层结构和引用完整性。
- `checkpoint.py`：生成 coherent checkpoint，并可自动追加 AletheiaOS Git trailers。
- `commit_msg_hook.py`：检查提交信息是否满足 tree transition 和 stable-node claim 规则。
- `history_audit.py`：从 Git history 重建 AletheiaOS transition，审计稳定节点、削弱、证伪、归档和实现链接。
- `status.py` / `overview.py`：把当前状态、验证、history audit 和 next actions 汇总给人或 agent。

这套工具刻意不做自动语义证明。它验证结构、引用、状态转移和明确的 review marker。真正的语义判断仍然属于人和审阅 agent。

## 使用过程总览

AletheiaOS 的日常使用可以压缩成一句话：

```text
orient -> work -> update truth -> validate -> checkpoint -> history audit
```

更具体地说：

1. 安装插件或从源码初始化 `.aletheia/`。
2. 首次 bootstrap，让 agent 从现有项目材料综合第一版项目事实。
3. 每次工作前，运行 orient 或 preflight，确认 active node、父级约束和验证状态。
4. 执行当前工程或研究任务。
5. 把影响长期判断的结果写回 `.aletheia/` 中相应的 evidence、decision、contract、risk、node 或 state。
6. 运行 validate，确认当前事实层没有结构错误。
7. 运行 checkpoint dry run，查看将要提交的 durable truth update。
8. 对 truth-tree transition 或 stable-node claim，用 checkpoint 生成带 trailers 的提交。
9. 运行 history audit，确认 Git history 能重建这次事实变化。

## 新项目如何开始

新项目可以先创建普通 Git 仓库：

```bash
mkdir my-project
cd my-project
git init
python3 /path/to/aletheia-os/scripts/init_aletheia.py .
```

然后执行第一轮 bootstrap：

```bash
python3 .aletheia/bin/model_gate.py --task-class bootstrap_finalize --provider <provider> --model-id <model_id> --tier C3 --operator-approved --record --objective "Initialize AletheiaOS"
python3 .aletheia/bin/source_inventory.py
python3 .aletheia/bin/guided_bootstrap.py --objective "Initialize AletheiaOS"
python3 .aletheia/bin/bootstrap_finalize.py
```

这里最重要的原则是：不要让 agent 凭空编造 mission、领域事实或架构结论。用户应先给出项目意图、约束、已知边界和候选方向。agent 的任务是综合、组织和记录，而不是替用户发明项目真相。

bootstrap 完成后，`bootstrap_finalize.py` 会安装 Git hooks，并把仓库的 `core.hooksPath` 指向 `.aletheia/hooks`。它还会默认创建第一笔 bootstrap checkpoint，提交中带有 `AIOS-Action: truth.bootstrap.initialize` 和 `AIOS-Tree-Op: bootstrap`。之后的提交会更难绕过 validation 和 commit-message traceability 检查。

## 已有项目如何接入

已有项目接入前，先看工作树：

```bash
cd /path/to/existing-project
git status --short
python3 /path/to/aletheia-os/scripts/init_aletheia.py .
```

初始化不会替换已有源码、测试、构建配置或公开文档。它只是新增 `.aletheia/` 控制平面。

接下来，让 agent 从已有材料建立第一版项目事实：

```bash
python3 .aletheia/bin/model_gate.py --task-class bootstrap_finalize --provider <provider> --model-id <model_id> --tier C3 --operator-approved --record --objective "Initialize AletheiaOS"
python3 .aletheia/bin/source_inventory.py
python3 .aletheia/bin/guided_bootstrap.py --objective "Initialize AletheiaOS"
python3 .aletheia/bin/orient.py
python3 .aletheia/bin/validate.py
python3 .aletheia/bin/bootstrap_finalize.py
```

已有项目的关键不是把所有资料塞进 `.aletheia/`。更好的做法是先建立一份可审查的事实骨架：当前使命、系统图、项目骨架、active state、重要决策、边界契约、已有证据和主要风险。剩余历史材料可以逐步整理，确认后再晋升。

## 一次日常迭代示例

假设当前任务是修正一个研究模型结论，并最终稳定 `theory_model` 节点。推荐流程如下。

先 orient：

```bash
python3 .aletheia/bin/orient.py --with-runtime
python3 .aletheia/bin/preflight.py --json
```

完成研究和代码工作后，把支撑结论写入 evidence 和 decision。例如：

```text
.aletheia/evidence/EV-002-game-context-break.md
.aletheia/decisions/DEC-001-modeling-lens-policy.md
```

然后验证当前事实层：

```bash
python3 .aletheia/bin/validate.py
python3 .aletheia/bin/checkpoint.py --dry-run
```

如果要把 `theory_model` 标记为稳定，使用带 traceability 参数的 checkpoint：

```bash
python3 .aletheia/bin/checkpoint.py --auto \
  --message "research: stabilize liquidity-gated modeling thesis" \
  --tree-op promote_node \
  --node theory_model \
  --parent root \
  --node-state stable \
  --evidence .aletheia/evidence/EV-002-game-context-break.md \
  --decision .aletheia/decisions/DEC-001-modeling-lens-policy.md \
  --review human-confirmed
```

最后审计历史：

```bash
python3 .aletheia/bin/history_audit.py --node theory_model --json
```

如果 audit 返回 `ok: true`，并且 `theory_model` 的 `latest_state` 是 `stable`，说明当前 Git history 能重建这个节点的稳定过程。

## Codex 与 Claude Code 中的差异

Claude Code 可以通过 hooks 自动执行更多门禁。Codex 当前更适合显式执行同一协议：

```bash
python3 .aletheia/bin/orient.py --with-runtime
python3 .aletheia/bin/preflight.py --json
python3 .aletheia/bin/validate.py
python3 .aletheia/bin/checkpoint.py --dry-run
python3 .aletheia/bin/checkpoint.py ...
python3 .aletheia/bin/history_audit.py --json
```

这不是能力高低的问题，而是宿主集成边界不同。AletheiaOS 的原则是：不虚假宣称 hook parity；在自动化较弱的宿主中，把同样的步骤显式化。

## 什么算稳定节点

稳定节点不是“agent 觉得写得不错”，也不是“这轮测试过了”。在 AletheiaOS 中，稳定节点至少意味着：

- 节点存在于当前 `SKELETON.yaml`；
- 支撑证据记录存在；
- 接受该结论的 decision 存在；
- 当前 `.aletheia/` validate 通过；
- Git commit 中有 `AIOS-Node-State: stable`；
- commit 中有 `AIOS-Review: human-confirmed`；
- `history_audit.py` 能从 Git history 重建这次稳定标记。

这套要求的价值在于把“稳定”从聊天判断变成可审查记录。后续如果发现新证据削弱该节点，可以通过 `truth.node.weaken` 或 `truth.node.falsify` 形成新的历史 transition，而不是悄悄覆盖旧结论。

## 常见误用

### 把 `.aletheia/` 当文档垃圾桶

不是所有资料都应该进入 `.aletheia/`。未整理的对话、长网页摘录、未确认资料、重复研究笔记，应先留在外部研究空间。只有经过审查、能明确归类为 evidence、hypothesis、decision、contract、risk、node 或 state 的内容，才应进入 durable truth。

### 只更新 README，不更新事实层

README 面向读者叙事，`.aletheia/` 面向项目事实。如果一次变更改变了项目使命、架构判断、证据状态或长期约束，只改 README 不够。应同步更新对应 truth records。

### 把 stable 当作普通状态标签

`stable` 是强 claim，不是整理进度。它需要 evidence、decision、validation、human review 和 Git history audit。没有这些条件时，应继续使用 candidate、hypothesis、risk 或 orphan 状态。

### 绕过 checkpoint 手写随意提交

普通代码或文档提交可以继续正常使用 Git。但 truth-tree transition 和 stable-node claim 应通过 checkpoint 或手写等价 trailers 完成。否则后续 history audit 无法重建事实变化。

## 什么时候不需要 AletheiaOS

如果项目很小、周期很短、只有一个人维护，并且所有重要事实都能稳定放在 README 中，AletheiaOS 可能过重。它要求一定纪律：重要判断要结构化，重要证据要记录，重要转变要提交，稳定节点要能审计。

它更适合这些场景：

- 长期研究与工程共同演化；
- 多个 agent 或多种工具参与同一个仓库；
- 架构决策和实验结论需要被追溯；
- 根目标、父级约束和局部实现之间容易漂移；
- 用户希望项目事实能跨会话、跨模型、跨提交稳定继承。

## 最终效果

使用 AletheiaOS 后，一个复杂项目不再只依赖“当前 agent 记得什么”。它会形成三层可追溯结构：

```text
当前事实：.aletheia/
变化过程：Git commits + AIOS trailers
验证工具：validate / preflight / checkpoint / history_audit
```

这样，agent 每次开始工作时能知道自己站在哪棵树的哪个节点上；人类审查时能看到结论来自哪些证据和决策；项目回退时能沿 Git history 找到事实变化点；新的 agent 接手时也不必重新从聊天碎片里猜项目状态。

AletheiaOS 的目标不是让项目流程更重，而是让重要事实不再靠记忆维持。它把 AI 协作中最容易漂移的部分固定在仓库里，让复杂项目可以持续生长，也可以持续被审查。
