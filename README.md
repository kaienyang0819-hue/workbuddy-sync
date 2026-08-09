# WorkBuddy Sync

私有仓库，用于在公司/家里两台电脑之间同步 WorkBuddy 的经验资产。

## 同步内容

| 层级 | 内容 | 说明 |
|------|------|------|
| A 身份 | SOUL/IDENTITY/USER.md | AI人格与用户画像 |
| B 记忆 | memery/ + memory/ | 系统级用户画像与记忆 |
| C 技能 | 10个自定义Skills | 策划工作流/PPT/文档模板等 |
| D 项目 | workclaw/stock_output/gpt_test 的 memory+learning | 项目级工作记忆+学习闭环 |
| E 知识库 | game-design-kb (~250张卡片) | 13维度Lv.7游戏设计知识库 |

## 使用方式

```powershell
# 完整双向同步（自动化任务用这个）
powershell -File "G:\workbuddy-sync\sync.ps1" sync

# 只上传（本机→GitHub）
powershell -File "G:\workbuddy-sync\sync.ps1" push

# 只下载（GitHub→本机）
powershell -File "G:\workbuddy-sync\sync.ps1" pull

# 通过 Pull Request 同步（推送到 sync/ 分支并创建/更新 PR，需要 gh CLI）
powershell -File "G:\workbuddy-sync\sync.ps1" pr
```

## 家里电脑部署

1. `git clone https://github.com/kaienyang0819-hue/workbuddy-sync.git`
2. 修改 `sync.ps1` 中的 `$SyncMap` 路径映射（适配家里的目录结构）
3. 运行 `.\sync.ps1 pull` 首次拉取
4. 设置 WorkBuddy automation 定时同步

> 如果希望同步经过 PR 审查而不是直接 push 到 main，把自动化任务的执行命令换成 `sync.ps1 pr`，
> 并确保已安装 GitHub CLI（`winget install GitHub.cli`）且完成 `gh auth login`。

## 不同步的内容

- MCP配置、插件配置、IMA笔记凭证
- 对话历史、会话状态、任务artifact
- 技能市场/插件市场缓存（自动拉取）
- 日志、备份、运行时文件
