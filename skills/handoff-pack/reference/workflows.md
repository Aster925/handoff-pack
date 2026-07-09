# Handoff Pack — 工作流手册 / Workflows reference

五种模式的逐步操作。`<TARGET>` = 目标项目根目录。脚本路径 `PH = skills/handoff-pack`
(若 skill 已安装到 `~/.claude/skills/handoff-pack`,则用该绝对路径)。

---

## 模式 1 — audit（审计漂移风险）

**何时:** 接手一个陌生/迁移来的项目,或想知道某项目离"可交接"还差多少。

1. 跑审计:
   ```bash
   python "$PH/scripts/drift_audit.py" audit "<TARGET>"
   ```
   - 退出码:0=LOW、1=MEDIUM、2=HIGH。
   - 给 agent 解析时加 `--json`,得到 `{risk, score, findings[]}`。
2. 脚本只覆盖**确定性信号**(缺文件、未锁依赖、.env 被跟踪、绝对路径、行尾、git 状态)。
   再补一层**语义检查**(脚本做不到的):
   - `AGENTS.md` 是否真的说清了"做什么/架构/怎么跑"?还是套话占位符?
   - `PROGRESS.md` 是否反映了 git log 里最近的真实改动?
   - `feature_list.json` 是否和实际代码对得上?
   - **固化流程/用户裁定是否进了"保证加载"层?** 若铁律只活在 PROGRESS 深处条目或
     agent 私有 memory(不进 git、不保证进上下文),新 session 会按"通用最佳实践"自行分析 → 漂移。
     修法:铁律入 `AGENTS.md` 边界;高频任务做「任务→固化流程」指针索引表(入口唯一)。
   - **记忆索引里是否嵌了状态快照?**(用 Claude Code auto-memory 的项目)`MEMORY.md` 索引若
     粘贴了某日的进度/状态副本,会过期并让新 session **虚假知情**、跳过读 PROGRESS(实案已验证)。
     修法:索引只放指针,状态一律归 `PROGRESS.md` 顶条;也别声称"详情文件会自动加载"(只有索引自动加载)。
3. 输出给用户:风险等级 + 按严重度排序的 findings + 建议下一步(通常是 init / handoff)。
4. **不要**在 audit 阶段直接改项目;先报告,等用户确认再动手。

---

## 模式 2 — init（生成完整交接包）

**何时:** 项目缺交接产物,要从零搭一套。

1. 先 audit,知道缺什么。
2. 脚手架(只创建缺失文件,不覆盖已有):
   ```bash
   python "$PH/scripts/drift_audit.py" scaffold "<TARGET>"
   ```
   会落地:`AGENTS.md` `CLAUDE.md` `feature_list.json` `PROGRESS.md` `HANDOFF.md`
   `init.sh` `init.ps1` `.gitattributes` `.env.example`(均为模板)。
3. **核心步骤——填充真实内容**(这是 agent 的活,不是脚本的):
   - 探索项目:读 README、入口文件、目录结构、manifest(package.json / pyproject 等)、
     测试、CI 配置、`git log`。**先查证再写**,不确定的标为开放问题,绝不假设。
   - 填 `AGENTS.md`:用真实内容替换每个 `<...>` / `TODO`。重点是"为什么"和"边界",
     这些是裸代码看不出、最容易漂移的部分。
   - 填 `feature_list.json`:从代码/README 推断端到端功能;**已验证能跑的**才标 `passes:true`,
     其余一律 `false`(宁可保守)。
   - 填 `init.sh` / `init.ps1`:写出真实的安装 + 运行命令;两个文件保持等价。
   - 填 `.env.example`:从代码里 grep 出读取的环境变量名(只写键名,不写值)。
   - `PROGRESS.md`:写第一条 Init 记录(迁移来源、原始环境版本、关键背景)。
4. 卫生整改(按 audit findings):
   - `.env` 被跟踪 → `git rm --cached .env`,加进 `.gitignore`。
   - 缺锁文件 → 生成并提交(`uv lock` / `poetry lock` / `npm ci` 依赖 lockfile)。
   - 委身的 `.venv`/`node_modules` → 从 git 移除,靠 init 脚本重建。
5. 删掉模板顶部的引导注释行(`> 占位符...` 那种),让文件干净。
6. 提交:一个清晰的 commit,例如 `chore: add handoff packet (AGENTS.md, progress, init)`。

> 反模式提醒:别想"一次把整个项目文档化到完美"。先把骨架填对、能跑通,
> 后续 session 增量完善 —— 半成品 + 清晰 PROGRESS 远胜于"做太多中途耗尽"。

---

## 模式 3 — handoff（交接 / 收尾）

**何时:** 一个 session 快结束、要换机器、或交给别人/别的 agent 之前。

1. 跑一次 audit,确保没有新引入的高危信号。
2. 更新 `PROGRESS.md`:在顶部追加一条本 session 记录(做了/状态/为什么/下一步/卡点)。
3. 写/更新 `HANDOFF.md`(用模板):
   - 第 1 节"下一程目标"、第 3 节"完成/进行中/受阻"、第 5 节"未落盘的隐性信息"最关键。
   - **只放指针**:指向文件、路径、分支、commit、`feature_list.json` 条目;不要粘贴大段内容。
   - 记录未提交改动(`git status --porcelain`)和任何 stash 位置。
4. 确保"干净状态":能跑、无重大 bug、改动已 commit(或在 HANDOFF 明确标注未提交项)。
5. 若接近 context 上限:**先完成第 2~3 步落盘,再** compaction / 结束 —— 别在半成品状态耗尽上下文。

---

## 模式 4 — verify（干净状态验证)

**何时:** 想确认"从干净 clone 真的能复现",或标 feature 完成前。

1. 尽量在干净副本验证(新目录 clone,或确认无未跟踪依赖)。
2. 跑 init 脚本:Windows `./init.ps1`,mac/Linux `bash init.sh`。能一键起来才算过。
3. 做**端到端**测试,像真人那样走流程(可用浏览器自动化 / 真实输入),别只信单元测试或 curl。
4. 对照 `feature_list.json` 逐条验证;只有真正通过的才把 `passes` 改成 `true`。
5. 把验证结果记进 `PROGRESS.md`。

---

## 模式 5 — migrate（跨机器 / 跨 OS 迁移）

**何时:** 项目要从一台机器/OS 搬到另一台(典型:Windows ↔ macOS)。

迁移清单(逐项核对,多数能被 audit 自动发现):

| 检查项 | 怎么修 |
|---|---|
| 依赖锁版本 | `requirements.txt` 写死 `==`,或用 `uv`/`poetry` lockfile |
| venv 不可移植 | **不要拷贝** `.venv/`;新机靠 init 脚本重建 |
| 换行符 / 路径分隔符 | `.gitattributes` 设 `* text=auto eol=lf`;代码用 `pathlib`,不写死 `\` 或 `/` |
| 未跟踪文件丢失 | `.env`、被 .gitignore 排除的产物**不会迁移** → 提交 `.env.example`,真值另传 |
| OS 特定配置 | PowerShell / MCP 等只对一个 OS 有效的配置,在 `AGENTS.md`「平台差异」分系统标注 |
| 硬编码绝对路径 | audit 会列出;改成相对路径 / 环境变量 |

迁移后第一件事:在新机跑 **verify**(模式 4),确认能跑再继续开发。

---

## 给 agent 的总原则 / Guiding principles

- **指针优于内容 (just-in-time):** 交接文档存路径/查询/链接,执行时再按需读取,别预先塞满。
- **浓缩优于扩容:** 目标是降低"理解项目所需的 context",不是堆更多文字。
- **保守优于乐观:** 不确定就标 `false` / 开放问题;宁可下个 session 多做,不可过早宣布完工。
- **查证优于假设:** 任何写进 AGENTS.md 的"事实"都应能在代码/历史/配置里找到依据。
- **AGENTS.md 宜短:** 模型可靠遵循约 150–200 条指令,每行都在抢预算 → 用指针、删套话,别把 AGENTS.md 写成长文档。
- **自动压缩 ≠ 落盘:** 即便开了平台的 context editing / compaction,**结束或压缩前仍要把进度写进 `PROGRESS.md`** —— 自动清理的是上下文窗口,不是仓库;跨机器/交接时只有 git 里的浓缩状态能带走。详见本工具包 `docs/methodology.md` §6(2026 现状对照)。
