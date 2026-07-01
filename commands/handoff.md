---
description: 保存交接(防漂移):追加 PROGRESS.md 一条 + 更新 feature_list passes,确认后再 commit
---
你要为**当前项目**执行"收尾交接"例程(handoff-pack 防漂移)。工作目录即目标项目。

## 前置检查
- 若项目根既无 `AGENTS.md` 也无 `PROGRESS.md`(或 `docs/PROGRESS.md`):告诉用户"本项目还没有交接包,要先初始化吗?(用 handoff-pack)",然后停止,**不要乱建文件**。

## 步骤
1. 用 `git status --short` + `git diff --stat` + `git log --oneline -5` 搞清这次 session 改了什么、当前分支状态。
2. 在 `PROGRESS.md`(或 `docs/PROGRESS.md`)**顶部**追加一条(最新在最上),按其模板写:**做了 / 状态 / 为什么 / 下一步 / 卡点**。
   - 真实内容;**指针优先** —— 写文件名、commit 短哈希,不要粘贴大段代码/内容。
3. 如果有功能这次**已实际验证通过**,在 `feature_list.json` 把对应项的 `passes` 由 `false` 改成 `true`。**只改 `passes` 字段**;没有该文件就跳过。
4. **提交前必须停下,等用户确认**:
   - 列出你打算提交的**具体文件**(至少 `PROGRESS.md`;若改了则含 `feature_list.json` / `AGENTS.md`)。
   - 给出建议的 commit message(简明中文,说清这次做了什么)。
   - 用户确认后,执行 `git add <这些具体文件>`(**不要 `git add -A`** —— 用户常并发多窗口,避免卷入无关改动)再 `git commit`。
   - **不要 `git push`**,除非用户明确要求。
5. 若用户还有其它未提交改动(不属于交接文件),提醒他单独处理,你不替他提交。

目标:任何新 session 读完 `PROGRESS.md` 顶部 + `AGENTS.md` 就能精准接上,不漂移。
