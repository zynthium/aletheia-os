# AletheiaOS：面向 AI 辅助研究与工程的树治理仓库原生事实层

## 由来

AI 编码助手越来越擅长完成局部任务：补一个函数、改一个测试、整理一段文档、按给定计划推进一次迭代。真正困难的地方，往往不是“这一轮能不能写出代码”，而是“项目在几十轮、几百轮对话和提交之后，是否还记得自己为什么这样设计”。

复杂项目的真实状态通常分散在很多地方：README 写着公开叙事，issue 写着待办，对话里有大量未结构化判断，代码里沉淀了一部分真实约束，实验结果和失败经验又散落在不同文件中。时间一长，agent 很容易只看见眼前文件和最近上下文，忘记父级目标、架构边界、证据来源和已经被否定的方向。

AletheiaOS 产生于这个问题：在 AI 辅助研究与工程中，项目需要一份可以被 agent 稳定读取、可以被人审查、可以被 git 追踪的唯一事实源。它不试图替代 Codex、Claude Code 或其他执行环境，也不试图变成任务管理系统。它关注的是更底层的问题：项目事实如何被表达、约束、验证和长期保留。

因此，AletheiaOS 的定位很窄：它是一个 tree-governed repo-native truth layer。项目的使命、当前状态、系统图、骨架、树治理规则、架构约束、研究证据、决策记录、接口契约、风险和 agent 归因，都放在目标仓库的 `.aletheia/` 中。源码、测试、公开文档和构建配置仍然留在各自原本的位置；`.aletheia/` 只负责保存控制平面和事实层。

## 核心设计哲学

### 仓库是长期事实源，聊天不是

聊天记录适合探索，不能承担长期项目记忆。对话上下文会丢失、会被压缩、会带有临时判断，也很难被后续 agent 精准继承。AletheiaOS 的第一原则是：能够影响项目方向、架构、实验解释或实现边界的内容，最终都应该进入仓库内的事实记录。

这并不意味着所有探索材料都要进入 `.aletheia/`。大量长对话、网页、论文笔记或资料编译，可以先由外部 LLM Wiki 工具整理成可审查研究空间。AletheiaOS 只接收经过审查、值得沉淀为项目事实的结果，并要求保留 claim、evidence、hypothesis、decision、contract、risk、node 或 state 的边界。

### 事实层不是工作流

AletheiaOS 不规定你必须怎样写代码、怎样做 TDD、怎样拆任务、怎样开分支、怎样发布。它只规定一件事：非平凡工作开始前，agent 应该先读当前事实；非平凡工作结束后，受影响的事实应该被更新、验证并形成 checkpoint。

这让它可以和不同执行工具共存。Claude Code 可以通过 hooks 自动执行门禁和审计；Codex 可以通过 skills、显式命令和可选 subagents 执行同一协议；其他 agent runtime 也可以读取 `.aletheia/START_HERE.md` 和 `.aletheia/` 下的事实记录。AletheiaOS 不争夺入口，它提供共同底座。

### 自顶向下保持骨架，自底向上修正事实

复杂项目需要一个全局骨架，否则局部改动很容易脱离系统目标。AletheiaOS 用 `mission -> system graph -> skeleton -> contracts -> evidence -> decisions -> code` 表达项目结构：先看使命和系统图，再定位 active node，再加载边界契约、证据和代码。新的 durable truth 必须判断自己属于哪一个父节点；暂时无法归属的材料进入 `.aletheia/state/ORPHANS.yaml`，等待挂载、拆分、合并、归档或晋升。

但它也不把顶层设计当成不可改变的权威。实现、实验和市场反馈可能推翻原有假设。AletheiaOS 要求重要 claim 可证伪，要求 evidence 区分观察、实验、解释和推断，要求本地发现能反向更新 hypothesis、risk、decision 或 skeleton。它是一套“保持全局一致，但允许证据修正全局”的机制。

### 少量强约束，避免流程膨胀

AletheiaOS 的目标不是堆叠功能，而是把 agent 最容易遗忘的几件事固定下来：

- 当前项目到底要解决什么问题；
- 当前 active node 在系统图中的位置；
- 哪些父级约束不能被局部优化覆盖；
- 哪些 claim 有证据，哪些只是猜想；
- 哪些契约和决策会影响当前改动；
- 本轮 durable write 是由哪个 agent、哪个模型、以什么任务类别完成的；
- 完成后是否验证，并形成 coherent checkpoint。

因此它刻意避免成为通用笔记应用、排期工具或项目管理系统。外部工具擅长的事情继续留给外部工具；AletheiaOS 只维护项目事实的最小闭环。

## 重要设计细节

### `.aletheia/` 是控制平面

初始化目标仓库后，AletheiaOS 会建立 `.aletheia/`：

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

其中 `governance/` 保存 charter、attention policy、tree governance、model governance、model registry、git policy 和 source policy；`state/` 保存 active state、system graph、project skeleton、orphan incubator、frontier board、domain profile、glossary 和 risk register；`nodes/` 保存系统节点事实；`evidence/`、`decisions/`、`contracts/`、`risks/` 分别保存证据、决策、契约和风险。

这个结构的重点不是“文件很多”，而是把原本混在一起的项目认知拆成可审查的事实类型。claim 不等于 evidence，evidence 不等于 decision，decision 不等于 contract，contract 也不等于实现。拆清这些边界，agent 才能知道自己能改什么、需要验证什么、不能偷换什么。

### Attention policy 控制上下文加载

AI agent 的上下文窗口再大，也不应该无差别扫描整个仓库。AletheiaOS 的 attention policy 要求从最小但足够的事实开始：

1. 读取 `.aletheia/START_HERE.md`、charter、attention policy、active state 和 model governance；
2. 定位 system graph 与 skeleton 中的 active node；
3. 只在跨边界时加载相关 contracts 和 decisions；
4. 只在评估、验证或修正 claim 时加载相关 evidence、hypotheses 和 risks；
5. 最后再读取源代码、测试和公开文档。

这个顺序是 AletheiaOS 的关键价值之一。它把 agent 的默认行为从“先看代码细节”改为“先确认项目事实和父级约束，再进入局部实现”。

### Model gate 是治理与归因边界

AletheiaOS 在 durable writes 前要求执行 model gate，记录 task class、provider、model id、能力层级、objective 和 gate status。它不是安全沙箱，也不是不可绕过的权限系统；它的作用是让重要写入具备可审计归因。

这解决的是多 agent 项目里的责任和能力边界问题。不同任务对模型能力的要求不同：普通文档整理、架构决策、根使命调整、证据解释、代码实现，风险等级并不相同。AletheiaOS 用 model registry 和 task class 把这些差异显式化，避免 unknown 或 under-tier 模型在没有授权的情况下直接写入 durable truth。

### Bootstrap 与日常闭环分开

Bootstrap 是项目首次建立事实层的阶段。agent 需要读取现有材料、生成 source inventory、综合 mission、skeleton、state、risks、decisions、contracts 和 evidence，并通过 `bootstrap_finalize.py` 完成初始验证和 checkpoint。

日常工作则保持一个更轻的闭环：

```text
orient -> work -> update truth -> validate -> checkpoint
```

这个闭环非常刻意。`orient` 防止 agent 在错误事实下工作；`work` 是普通工程或研究活动；`update truth` 确保结果不会只留在聊天或代码隐含状态中；`validate` 检查事实层结构和语义；`checkpoint` 把 coherent project truth update 交给 git。

### Git hooks 是强约束的一部分

Bootstrap finalize 会安装 AletheiaOS Git hooks，并把目标仓库的 `core.hooksPath` 指向 `.aletheia/hooks`。这不是为了替代人工 review，而是为了让后续提交继续经过 `.aletheia/bin/validate.py`，避免项目事实层在日常提交中逐渐失效。

这里的设计取舍很明确：AletheiaOS 对目标仓库的侵入面应尽量小，控制平面集中在 `.aletheia/`；但对于 checkpoint 和验证这类闭环关键点，Git hooks 提供必要的本地强约束。

### Claude Code 与 Codex 使用同一事实协议

AletheiaOS 同时提供 Claude Code 和 Codex 插件结构。Claude Code 可以读取插件根目录下的 agents，并通过 hooks 配置 SessionStart、PreToolUse、PostToolUse 和 Stop 检查。Codex 使用 skills、显式命令和可选 subagents 执行同一事实协议。

两者的自动化能力并不完全相同，但核心能力保持一致：先 orient，再基于 `.aletheia/` 工作，完成后更新 truth records、验证并 checkpoint。AletheiaOS 的设计重点不是依赖某个 agent runtime 的私有能力，而是让多种工具共享同一份项目事实。

### 外部 LLM Wiki 只负责研究空间，AletheiaOS 负责项目事实

很多项目早期会先在 ChatGPT、Claude 或其他工具中产生大量非结构化探索材料。直接把这些材料写进 `.aletheia/` 会污染事实层，也会让 agent 反复处理重复、冲突和未证实内容。

AletheiaOS 的处理方式是边界化：外部 LLM Wiki 负责资料编译、去重、主题聚合、概念关系和来源导航；AletheiaOS 只接收 Wiki Handoff 中经过审查的候选结论。未确认、互相冲突或来源不足的内容继续留在 wiki 层，不进入 durable project truth。

## 与现有工具的对比

### Superpowers

Superpowers 是面向 agent 行为的技能和方法库，公开文档强调通过具体 skills 改善编码助手的工作方式，例如 brainstorming、TDD、systematic debugging、code review 和 finishing branches。它解决的是“agent 该如何完成一次工作”的问题。

AletheiaOS 解决的是另一层问题：无论使用哪套工作技能，agent 共同依赖的项目事实在哪里、如何读取、如何验证、如何沉淀。Superpowers 可以告诉 agent 如何写计划、如何调试、如何请求 review；AletheiaOS 告诉 agent 这个项目当前的 mission、active node、证据、架构约束和风险是什么。

两者并不冲突。Superpowers 更像执行方法论，AletheiaOS 更像事实底座。

### OpenSpec

OpenSpec 关注 spec-driven development，强调用 proposals、tasks 和 specs 管理需求变更，让 agent 在实现前先理解 change-level spec。它解决的是“一个变更应该怎样被描述、审批和落地”的问题。

AletheiaOS 关注 project-level truth。它并不替代某个 feature 或 change 的 spec，而是维护跨越多个变更周期的项目事实：系统图、项目骨架、长期决策、证据链、风险和约束。OpenSpec 的 spec 可以成为 AletheiaOS 决策或契约的来源之一；AletheiaOS 则为 OpenSpec 变更提供更上层的项目背景。

简化地说，OpenSpec 管一次变更，AletheiaOS 管长期事实。

### gstack

gstack 更偏向工程执行习惯和 agent 操作栈，强调让 coding agent 按一套更稳定的工程流程工作。它的价值在于把成熟开发者的工作节奏、命令和检查步骤传递给 agent。

AletheiaOS 不试图复制这类操作栈。它不关心你用什么分支策略、怎样拆 PR、怎样运行测试矩阵；它关心这些动作背后的事实是否被记录、约束是否被保持、证据是否能支撑结论。gstack 可以提升执行质量，AletheiaOS 则降低长期项目事实漂移。

### Compound Engineering Plugin

Compound Engineering Plugin 更接近虚拟工程团队或复合 agent 工作流：通过多个角色、流程和协作模式来推进软件交付。它解决的是“如何组织 agent 团队完成工程任务”的问题。

AletheiaOS 的可选 subagents 只做 truth layer 审阅，例如 truth-auditor、evidence-curator 和 architecture-reviewer。它们不承担实现、排期、发布或流程编排职责。AletheiaOS 刻意不把自己做成虚拟团队系统，因为那会把事实层和执行层混在一起，增加复杂度，也偏离它的核心目标。

### 总结对比

```text
Codex / Claude Code: agent runtime
Superpowers / gstack: agent work method
Compound: multi-agent engineering workflow
OpenSpec: change-level spec governance
AletheiaOS: project-level repo-native truth layer
```

AletheiaOS 的竞争点不是“比谁更会写代码”，而是“谁能让项目在长期 AI 协作中保持一份可审查、可验证、可继承的事实”。

## AletheiaOS 适合解决的真实需求

AletheiaOS 最适合的项目通常有这些特征：

- 项目周期长，不能只依赖当前对话上下文；
- 架构、研究和实现会共同演化；
- 重要结论需要证据、推翻标准和后续决策；
- 多个 agent 或多种工具会参与同一个仓库；
- 顶层目标、父级约束和局部实现之间容易漂移；
- 用户希望沉淀研究成果和架构判断，维护唯一一份完整事实。

这类需求不会因为大模型能力提升而消失。模型更强会让单轮执行更快、更准，但也会让 agent 更频繁地做出看似合理的局部推断。只要项目需要跨时间、跨工具、跨 agent 保持一致，事实层就仍然有价值。

AletheiaOS 的核心假设是：强模型需要更好的项目事实接口，而不是更长的聊天记录。

## 不适合的场景

如果项目很小、周期很短、目标很清晰，或者所有知识都能轻松保存在一个 README 中，AletheiaOS 可能显得过重。它也不适合被当成个人知识库、待办列表、需求排期系统或通用文档框架。

它要求用户接受一种纪律：重要判断要被结构化，重要结果要进入 git，重要写入要有归因，重要 claim 要能被验证或明确标记为解释性判断。没有这类纪律需求的项目，不需要 AletheiaOS。

## 最终定位

AletheiaOS 的合理定位可以压缩成一句话：

> AletheiaOS 是为 AI 辅助研究与工程项目提供的仓库原生可证伪真理树层，用 `.aletheia/` 维护从根目标到主干、分支、叶子、证据、假设、决策、契约、风险和实现约束的长期项目事实。

它不是更大的工作流，而是更稳定的事实底座。它不替代人类判断，而是让判断有位置沉淀；它不替代 agent runtime，而是让 agent runtime 不再只依赖短期上下文；它不替代 spec 工具、技能库或虚拟团队系统，而是为它们提供同一份长期项目真实状态。

这就是 AletheiaOS 的核心价值：让复杂项目在 AI 协作中不只是持续产出，也能持续记住自己为什么这样产出。

## 参考资料

- Superpowers: <https://github.com/obra/superpowers>
- OpenSpec: <https://github.com/Fission-AI/OpenSpec>
- gstack: <https://github.com/garrytan/gstack>
- Compound Engineering Plugin: <https://github.com/EveryInc/compound-engineering-plugin>
