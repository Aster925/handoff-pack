# 方法论:为什么这套交接包能防漂移 / Methodology

> 本文把「种子文档」([`../claude-code-cloud-and-anti-drift.md`](../claude-code-cloud-and-anti-drift.md))的根因分析,
> 与 2025–2026 的较新 ML/agent 工程实践对接,解释 `handoff-pack` 每个产物背后的原理。

---

## 1. 问题:项目漂移 (project drift)

**现象:** 项目因上下文过长、环境变更、架构描述缺失、跨机器迁移而交到新 LLM session 手上后,
agent 没按原意复现,出现"思考漂移"或遗漏。

**根因(两层):**
1. **物理限制:** 一次能读的 token 有上限,agent 永远只看到项目的**局部**,边扫边猜。
2. **真正元凶——缺浓缩状态:** 即使 context 再大,若仓库没有文件说明"做什么 / 做到哪 / 怎么跑 / 为什么",
   agent 只能从**裸代码逆向重建意图**。代码只体现"怎么做",逆向时必然用假设填空 → 漂移。

> **关键认知:解法不是扩 context,而是降低"理解项目所需的 context"。**
> 这正是 Anthropic 把 context 当作**有限资源**、追求"最小高信号 token 集"的核心思想。
> — *Effective context engineering for AI agents*

迁移时漂移尤其明显,因为最容易丢的恰是**非代码信息**:脑中的计划、与 AI 的对话结论、隐性环境
(依赖版本、运行方式)——这些都没进仓库。

---

## 2. 较新实践如何映射到我们的产物

| 实践 / Practice (来源) | 含义 | 对应产物 |
|---|---|---|
| **AGENTS.md 开放标准** (Linux Foundation Agentic AI Foundation, 2025–) | 跨工具统一的项目上下文文件,放仓库根,就近覆盖 | `AGENTS.md`(唯一真相来源)+ `CLAUDE.md`(薄指针 `@AGENTS.md`) |
| **Context engineering — just-in-time** (Anthropic) | 存轻量标识(路径/查询/链接),运行时按需加载,而非预先塞满 | `HANDOFF.md` / `AGENTS.md` 用**指针**而非粘贴内容 |
| **结构化笔记 / agentic memory** (Anthropic) | agent 把笔记写到 context 之外的持久存储,跨多步保留关键状态 | `PROGRESS.md`(每 session 追加的持久记忆) |
| **Compaction** (Anthropic) | 接近上限前高保真压缩,保留架构决策与未决问题 | 收尾流程:先落盘 `PROGRESS.md`/`HANDOFF.md` 再压缩 |
| **Sub-agent 架构** (Anthropic) | 用干净上下文的子 agent 做深度搜索,主线只收浓缩摘要 | `CLAUDE.md` 约定把 research 放 subagent |
| **右"海拔"系统提示** (Anthropic) | 既不写死脆弱逻辑,也不空泛;用清晰小节组织 | `SKILL.md` 保持精简,细节下沉到 `reference/workflows.md`(渐进披露) |
| **Spec-driven development** (GitHub Spec Kit / Kiro) | 规格先行:Spec→Plan→Tasks→Implement,规格而非代码为中心 | `feature_list.json` 是其轻量版:端到端功能清单,`passes` 受控 |
| **长任务 harness 两大失败模式** (Anthropic, *Effective harnesses…*) | ① 想一次做太多→中途耗尽→留半成品;② 后期 agent 瞄一眼就宣布完工 | 规则:一次一个 feature;`feature_list.json` 只许改 `passes`,验证后才置 true |

---

## 3. 为什么是这些具体设计

- **AGENTS.md 为先,CLAUDE.md 退为指针。** 通用信息只存一处,杜绝"两份文档各自漂移";同时
  AGENTS.md 跨工具可读(Cursor/Copilot/Gemini 等),迁移到别的工具链也不丢上下文。
- **功能清单用 JSON 而非 Markdown,且只允许改 `passes`。** 模型更不容易乱改结构化 JSON;
  把"完工判定"约束成单字段,直接压制"过早宣布做完"的失败模式。
- **脚本只做确定性活,判断留给 agent。** 查缺文件、扫绝对路径、查锁文件、脚手架 —— 这些可被
  规则化的部分交给 `drift_audit.py`(可复现、零依赖、跨平台);理解意图、填内容、判断 e2e 是否
  真的通过,这些需要判断的部分留给 agent。对应"工具应自包含、最小、职责清晰"的工具设计原则。
- **指针优于内容。** 交接文档写"看 `PROGRESS.md` 顶部 N 条 / 见 `feature_list.json`"而不是粘贴,
  既省 token 又避免内容副本随时间漂移。
- **跨平台是第一公民。** stdlib Python 脚本 + 双 init 脚本 (`.sh`/`.ps1`) + `.gitattributes` 行尾规范 +
  绝对路径扫描,直接针对 Windows↔macOS↔Linux 迁移这一高频漂移场景。

---

## 4. "干净状态"的定义 / Definition of clean state

适合合并到主分支、可交接的代码:**无重大 bug、整洁有文档、从干净 clone 能一键重建、别人能直接接手。**
`verify` 模式就是用来确认项目处于这个状态。

---

## 5. 一句话总结

> 漂移的根因不是 LLM 笨,而是项目缺"交接文档"。
> 把意图、进度、运行方式、边界浓缩进 `AGENTS.md` + `PROGRESS.md` + `feature_list.json` + `init.*`,
> 让任何新 session 在 context 限制内一读就懂、精准复现。
> **迁移时带走的不该只是代码,而是 代码 + 这套交接包。**

---

## 6. 2026 现状对照 / Alignment with current practice（复核于 2026-06）

把本工具包对照 2026 年中的最新官方/学术实践复核,结论:**设计与现行最佳实践一致**,并明确与新平台能力的关系。

- **SKILL.md 规范 — 合规。** 仅 `name`+`description` 必填(`name` 小写连字符、≤64、不含保留词 "claude/anthropic"、与文件夹同名;`description` ≤1024、第三人称、**禁用尖括号 `<>`** 以防注入);body 应 <500 行 + 渐进披露(细节下沉子文件,引用一层深)。本 skill 全部满足。[6][7]
- **AGENTS.md 为先 = 2026 共识。** "AGENTS.md 作 canonical 单一真相来源,CLAUDE.md 用 `@AGENTS.md` 导入(或 `ln -s AGENTS.md CLAUDE.md` 软链),Claude 专属内容极简。" 本工具包正是此法。注意**文件要短**:前沿模型可靠遵循约 150–200 条指令,每行都在抢这预算 → AGENTS.md 宜精炼、用指针。[8]
- **PROGRESS.md = Anthropic 自用模式。** 其长任务 harness 即用 `claude-progress.txt` + git history 让新 context 快速接上工作状态;本工具包 `PROGRESS.md` 同此。[2]
- **与平台「记忆工具 / 上下文编辑」的关系(2026 新增,互补不冲突)。** Anthropic 2026 推出 file-based **memory tool** + 自动 **context editing / compaction**(近上限自动清理陈旧工具调用,实测降 token ~84%)。二者层次不同:
  - 平台 memory / context-editing = **运行时、每工作区、基础设施层**的临时记忆 + 自动压缩(API / Managed Agents)。
  - `AGENTS.md` / `PROGRESS.md` / `feature_list.json` = **进 git、可移植、人和任何工具都能读**的持久"唯一真相来源"层。
  - 实践要点:即便开了自动 compaction,**仍要在压缩/结束前把进度落盘到 `PROGRESS.md`** —— 自动清理的是上下文窗口,不是你的仓库;跨机器、跨工具、交接给人时,**只有 git 里的浓缩状态能被带走**。[9][10]

---

## 参考文献 / References

1. Anthropic — *Effective context engineering for AI agents*
   https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
2. Anthropic — *Effective harnesses for long-running agents* (Nov 2025)
   https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
3. Anthropic — *Writing effective tools for AI agents*
   https://www.anthropic.com/engineering/writing-tools-for-agents
4. *AGENTS.md* — open standard for agent instructions
   https://agents.md
5. GitHub — *Spec Kit*(spec-driven development)
   https://github.github.com/spec-kit/
6. Anthropic — *Equipping agents for the real world with Agent Skills*
   https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
7. Claude Platform Docs — *Skill authoring best practices*（SKILL.md 规范）
   https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
8. *AGENTS.md vs CLAUDE.md*（2026 共识:AGENTS.md 为 canonical + CLAUDE.md @import / symlink；AAIF / Linux Foundation 标准）
   https://agents.md
9. Claude Platform Docs — *Memory tool*（file-based 持久记忆,2026 public beta）
   https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool
10. Anthropic — *Managing context on the Claude Developer Platform*（context editing + memory,2026）
    https://anthropic.com/news/context-management
