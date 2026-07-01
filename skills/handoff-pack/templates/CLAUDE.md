# CLAUDE.md

> 本文件是 **Claude Code 专用指针 (thin pointer)**。
> 项目的全部上下文在 `AGENTS.md` —— 它是唯一真相来源,请先读它。
> 这里只放 Claude Code 特有、不属于通用 AGENTS.md 的内容。

## 首先阅读 / Read first
@AGENTS.md

(`@` 导入语法让 Claude Code 自动把 AGENTS.md 内容纳入上下文;其他工具直接读 AGENTS.md。)

## 每次开场 / Session start
按 `AGENTS.md` 的「每次开场必做 / Session start routine」执行。
不要跳过基础 e2e 验证就开始写新功能。

## Claude Code 专属约定 / Claude-specific
- 子任务用 subagent 隔离上下文 (research/搜索放 subagent,主线保持干净)。
- 接近上下文上限前,先更新 `PROGRESS.md`,再用 compaction —— 别在半成品状态耗尽。
- 涉及破坏性操作 (删文件 / force push / 改 main) 前先确认。
- 可用 skills / hooks: `<如有项目特定的,在此列出>`

## 不要 / Don't
- 不要把通用项目信息写在这里 —— 写进 `AGENTS.md`,避免两份内容漂移。
- 不要修改本节以外的边界规则 (边界见 AGENTS.md)。
