# init.ps1 — 从干净 clone 一键重建环境并运行 (Windows / PowerShell)
# One-command rebuild + run from a clean clone.
# 配套 macOS/Linux 版本见 init.sh。请按项目实际情况替换 TODO。
$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

Write-Host "==> handoff-pack init (PowerShell) :: $(Get-Location)"

# --- 依赖检查 / prerequisite check (TODO: 改成你的 runtime) -------------------
# if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
#     Write-Error "需要 python / python required"; exit 1
# }

# --- 重建环境 / rebuild environment ------------------------------------------
# venv 不可移植,不要提交,在此重建 / venv is NOT portable; rebuild here.
#
# Python 示例 / Python example:
#   python -m venv .venv
#   .\.venv\Scripts\Activate.ps1
#   pip install -r requirements.txt        # 或 / or: uv sync
#
# Node 示例 / Node example:
#   npm ci                                  # 用锁文件,可复现 / uses lockfile
Write-Host "TODO: 在此重建依赖 / rebuild dependencies here"

# --- 运行 / run --------------------------------------------------------------
# Write-Host "==> starting dev server"
# python app.py
Write-Host "TODO: 在此启动开发服务器 / start dev server here"

Write-Host "==> init done."
