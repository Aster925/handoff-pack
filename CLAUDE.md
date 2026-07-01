# CLAUDE.md — Claude Code 专用指针 / thin pointer

> 全貌、结构、运行、自维护循环、边界 全部在 [`AGENTS.md`](AGENTS.md) —— 先读它。本文件只放 Claude 特有内容。

## 首先阅读 / Read first
@AGENTS.md

## 每次开场 / Session start
先跑 `python scripts/guardian.py`(或 `/toolkit-check`)→ 读 `PROGRESS.md` 顶部。自检失败先修工具包。

## 命令 / Commands
- `/toolkit-check` — 自检工具包 + 校对被看护项目 + 方法论到期提醒。
- `/toolkit-refresh` — 搜最新防漂移/handoff/context 方案 → 提议更新方法论/skill → 更新复核日期。
- `/handoff` — 收尾保存(用在**被看护项目**里,不是这里)。

## 专属约定 / Specific
- 结束维护会话:更新 `PROGRESS.md` + commit;**公开仓库,push 前先对 tracked 文件做泄露扫描**(个人路径/密钥/IP)。
- 大块调研放 subagent;别把被看护项目的文件在这里改动(边界见 AGENTS.md)。
