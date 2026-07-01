#!/usr/bin/env bash
# init.sh — 从干净 clone 一键重建环境并运行 (macOS / Linux)
# One-command rebuild + run from a clean clone.
# 配套 Windows 版本见 init.ps1。请按项目实际情况替换 TODO。
set -euo pipefail
cd "$(dirname "$0")"

echo "==> handoff-pack init (bash) :: $(pwd)"

# --- 依赖检查 / prerequisite check (TODO: 改成你的 runtime) -------------------
# command -v python3 >/dev/null || { echo "需要 python3 / python3 required"; exit 1; }

# --- 重建环境 / rebuild environment ------------------------------------------
# venv 不可移植,不要提交,在此重建 / venv is NOT portable; rebuild here.
#
# Python 示例 / Python example:
#   python3 -m venv .venv
#   source .venv/bin/activate
#   pip install -r requirements.txt        # 或 / or: uv sync
#
# Node 示例 / Node example:
#   npm ci                                  # 用锁文件,可复现 / uses lockfile
echo "TODO: 在此重建依赖 / rebuild dependencies here"

# --- 运行 / run --------------------------------------------------------------
# echo "==> starting dev server"
# python app.py
echo "TODO: 在此启动开发服务器 / start dev server here"

echo "==> init done."
