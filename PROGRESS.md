# Progress Log / 进度日志(handoff-pack 工具包自身)

> 持久记忆:每次维护**在下方追加**一条(最新在最上)。指针优先(commit 短哈希/文件),不粘大段。架构见 [`AGENTS.md`](AGENTS.md)。

---

## [2026-07-09 b] 防漂移二期:钩子升级(双节钉回+编码修复)+ 法语四层防线补全
- **一期实证:** 法语 z21 会话(TEST1/2/3 OCR 入库)完整遵守新协议——承 canon、新流程主动补进〈固化流程索引〉、纠正旧漂移误判。结构生效。
- **钩子升级(`hooks/handoff_hook.py`):** ① PreCompact 钉回从「边界」扩为**「边界」+「固化流程索引」**(extract_pins,每节 2000 字符上限);② **修真 bug**:stdin 按 Windows 本地编码(GBK)解码会把 BOM/含中文的 cwd 解成垃圾 → json 失败 → **静默回退错误目录**(昨日 A1 测试"通过"实为回退目录侥幸命中)→ 改 `utf-8-sig` + lstrip BOM 双保险;实测 no-BOM/with-BOM 均正确钉回法语两节(2739 字符)。已同步安装副本。
- **法语四层防线(其仓库 `f3e3e17`,授权代做):** ①载入层 CLAUDE@AGENTS(z20)②开场层全局 SessionStart(已有)③压缩层双节钉回(本次)④**回合层新增**:项目级 UserPromptSubmit → `canon_pin.py` 每回合钉一行 canon(治注意力衰减)。+ `docs/会话提示词_防漂移.md`(用户手动开场/收尾/纠偏三段提示词)。
- **方法论:** §6 constraint-pinning 条目补「注意力衰减→每回合一行钉」模式。
- **下一步:** 观察法语漂移率;English 窗口下次顺手 `/handoff` 清过期日志;两仓库均未 push。
- **背景:** 用户报告法语项目「handoff 后 LLM 不读固化流程就自己分析」,**明确授权本窗口校对纠错**(平时边界=只审计不动手,本次例外;实例=其 z15→z16 gated 事件)。
- **诊断(三根因,互相放大):** ① 最关键铁律(零遗漏不丢不藏/先读canon)只活在 PROGRESS 深处 + agent 私有 memory —— 都不保证进新会话上下文;保证加载的 AGENTS.md 反而没有。② `MEMORY.md` 索引嵌 07-03 过期状态快照(内容副本)→ 新会话虚假知情,跳过读 PROGRESS。③ 其 CLAUDE.md 误称 memory 子文件"自动加载"(实际仅索引加载)。
- **修复(法语仓库 `e6de544`,只动交接文档):** AGENTS.md 边界+2铁律 + 新增〈固化流程索引〉(8 类任务→先例脚本,指针逐一 Test-Path 核实)+ 开场例程"动手前查索引";CLAUDE.md 纠正记忆说明 + 根目录开会话提醒(发现 2 套子目录孤儿 memory);MEMORY.md 快照移出 → `tef-co-rebase-turnkey.md`。审计无回归;**提交时避开并行会话的 2 个未跟踪文件,只 add 自己改的 3 个**。
- **反哺工具包(本 commit):** `workflows.md` audit 语义检查 +2 条通用化新失败模式 ——「铁律未进保证加载层」「记忆索引嵌状态快照=虚假知情」。
- **下一步:** 观察法语项目后续 session 是否守〈固化流程索引〉;评估 drift_audit 可否脚本化"索引 vs PROGRESS 新鲜度"信号。
- **做了:** `/toolkit-refresh` 全流程(2 个调研 subagent:Anthropic 官方 + 社区/学术,只收结论)。落地两项代码增强 + 文档增补:
  - **A1 约束重注入**(`hooks/handoff_hook.py`):PreCompact 时从目标项目 AGENTS.md 提取「边界」小节原文重注入 —— 依据《Governance Decay》(arXiv 2606.22528):压缩丢约束后违反率 0%→~30%,缓解 = constraint pinning。实测:本仓库边界节完整钉回。
  - **A2 安装副本同步检查**(`scripts/guardian.py` `install_drift()`):仓库源 ↔ `~/.claude/` 副本(skill 目录 / hook / commands)逐文件 sha256 比对;未安装则跳过。灵感:Spec Kit "workflow as versioned dependency"。实测:当场逮到刚改的 hook 未重装 → 重装后全绿(自检 4→7 项)。
  - **B 文档**(`docs/methodology.md` §6 复核于 2026-07 + 参考文献 11–16):MEMORY.md(agent 私有)vs git 真相层的分层规则;Governance Decay;checkpointing//rewind 与 Ralph 循环互证"git 浓缩状态=可携带层";memory tool 转 GA;SKILL.md 新可选字段;watch AGENTS.md v1.1 提案(未合并,不追)。
- **判为不采纳(有意):** Sonnet 5 1M context(与"降所需 context"正交)、feature_list 加 `depends_on`(碰"只改 passes"硬规则)、AGENTS.md frontmatter(标准未定)、subagent 自动 PR(与本包无接口)。
- **状态:** done。guardian 全绿;`.methodology_review` → 2026-07-08。已同步安装副本(hook)。
- **下一步:** 观察 A1 在真实 PreCompact 事件里的表现;AGENTS.md v1.1 合并后评估模板跟进;下次刷新 ≈ 2026-08-07。

## [2026-07-01] Option B 上线 + 脱敏公开发布 + 实测收尾
- **做了:** Option B = 项目级 `.claude/settings.json` 的 SessionStart 钩子 —— 打开本工具包自动跑 `scripts/guardian.py`(自检+校对+方法论提醒)。公开仓库**脱敏**:去掉具体项目/考试名 → 通用描述;因之前推过带名旧 commit,**压成单一干净 commit `bfd57a8` + force-push**,origin 现仅 1 commit(GitHub API 确认),仍可 clone 即用。
- **状态:** done。`feature_list` T12 → **passes:true**(经 SessionStart 自动触发,非 cron 定时)。
- **实测(本次收尾即测试):** 本会话开场两个 SessionStart 钩子**均自动触发** —— 全局钩子 surface PROGRESS 顶部;Option B guardian 自检全绿、项目A LOW(0)、项目B MEDIUM(4)。guardian **自动逮到项目B 有 6 处未提交**(其自身会话正在开发),正是"每次运行校对两项目"的预期行为 —— 归 **该项目自己的窗口** 自行 `/handoff`,本工具包不碰其文件(边界)。
- **下一步(可选):** 更强的定时(本地计划任务 / 云端调研 PR)留白;距 `.methodology_review` 满 30 天再跑 `/toolkit-refresh`。

## [2026-06-30] 自维护:guardian 自检 + 项目校对 + 方法论提醒
- **做了:** `scripts/guardian.py`(①工具包自检 ②校对 watched 项目跑 audit ③方法论到期提醒)+ `/toolkit-check`、`/toolkit-refresh` 命令 + 本工具包**自己的交接包**(AGENTS/CLAUDE/PROGRESS/feature_list,dogfood)。`watched_projects.txt`(gitignore,含 English/French)+ `.methodology_review` 日期戳。
- **状态:** done。guardian 实测:自检全绿;English LOW(0)、French LOW(3=已追踪的硬编码路径);方法论未到期。
- **为什么:** 用户要"每次运行校对两个项目 + 定期搜新方案 + 即时更新自己 + 优先稳固性"。稳固性=自检先行;校对=guardian 跑 audit;定期=`.methodology_review` + /toolkit-refresh 提醒。
- **下一步(待用户定):** 是否把 guardian 挂成**定时/自动**触发(本地执行,因需访问本地项目);自更新的自主度(报告+提议 vs 自动 commit/push)。

## [2026-06-30] 发布 + 交接自动化
- **做了:** 工具包 `git init` + MIT + `.gitignore`/`.gitattributes`;推送公开仓库 https://github.com/Aster925/handoff-pack(commit `adff5d2`/`2702fc1`/`8957063`)。`/handoff` 命令 + SessionStart/PreCompact 钩子(全局装好)。方法论加 §6(2026 官方/学术对照:SKILL.md 规范、AGENTS.md 共识、memory tool/context editing 互补)。
- **状态:** done。推送前对 tracked 文件做过泄露扫描(个人路径在 gitignore 的 settings.local/watched 里,未公开)。

## [2026-06-30] 工具包成型 + 两个真实项目验证
- **做了:** handoff-pack skill(drift_audit.py + 9 模板 + workflows 5 模式)。应用到 **2 个真实本地项目**:项目 A(app+内容管线,HIGH→LOW:AGENTS+瘦身 CLAUDE+回填 PROGRESS+修看门狗)、项目 B(视频课件管线,HIGH→LOW:git init+合并多份交接文档+集中根路径+归档)。修了 drift_audit 两个 bug(docs/ 子目录 PROGRESS 检测、`\n` 误判为路径)。
- **状态:** done。
- **隐性:** 这两个项目的后续实施归它们各自会话;本工具包只审计,不干涉(见 [[concurrent-sessions-git-add]] 的 git add 教训)。
