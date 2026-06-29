# WorkBuddy Sync Automation Memory

## 2026-06-05 18:00 — Bi-weekly Sync Run
- **Action:** sync (pull → scatter → gather → push)
- **Local sync:** ✅ 成功。Scatter 分发 26 skills（新增 cell-cc-design、elite-frontend-design、ima笔记）+ 6 projects；Gather 收集 26 skills + 8 project dirs。
- **Git sync:** ❌ 失败。PowerShell session 中 `git` 不在 PATH 中，导致 pull 和 push 均跳过。
- **Action needed:** 修复 sync.ps1 中 git 路径问题（可在脚本顶部硬编码 Git 路径或确保系统 PATH 包含 Git）。

## 2026-06-08 10:15 — 手动触发修复
- **问题诊断:** PowerShell 独立进程中 `git` 不在 PATH → 两个月来远程同步从未成功。
- **修复内容:**
  1. sync.ps1 顶部添加 `C:\Program Files\Git\cmd` 到 PATH
  2. Invoke-GitPull 加入 auto-stash 逻辑，避免本地未提交文件阻塞 rebase
- **本次结果:** gather/scatter ✅；push ✅（commit `7c97c87` 成功推送）；脚本自身的修复 commit `96c2674` 已本地提交，待下次桌面环境 sync 推送（自动化 session 无法弹出 credential 窗口）。
- **GitHub 状态:** 远程已从 4月29日 更新到 6月8日。
