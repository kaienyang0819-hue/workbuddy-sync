# 🏠 家里电脑部署指南

> 在家里电脑上一次性完成 WorkBuddy 经验资产同步配置，之后自动保持两台电脑同步。

## 前置条件

- [x] 家里电脑已安装 WorkBuddy
- [x] 家里电脑已安装 Git（如未安装：`winget install Git.Git`，安装后**重启终端**）
- [x] 公司电脑已完成首次 push（已完成 ✅）

## 第一步：Clone 仓库

打开 PowerShell，选择一个你喜欢的位置存放同步仓库：

```powershell
# 比如放在 D:\workbuddy-sync（根据你的实际情况调整盘符）
cd D:\
git clone https://github.com/kaienyang0819-hue/workbuddy-sync.git
cd workbuddy-sync
```

> 如果提示认证，用浏览器登录 GitHub 授权即可。

## 第二步：修改路径映射

用编辑器打开 `sync.ps1`，找到 `$SyncMap` 部分。

### 必须检查的路径

**A/B/C 层（身份 + 记忆 + 技能）**：使用 `$WB` 变量，自动适配 `~/.workbuddy/`，**不需要改**。

**D 层（项目级知识）**：需要根据家里的项目目录修改：

```powershell
# 公司电脑原始配置：
"projects\workclaw\memory"        = "G:\workclaw\.workbuddy\memory"
"projects\workclaw\learning"      = "G:\workclaw\.workbuddy\learning"
"projects\workclaw\scripts"       = "G:\workclaw\.workbuddy\scripts"
"projects\stock_output\memory"    = "G:\stock_output\.workbuddy\memory"
"projects\gpt_output\memory"      = "G:\gpt_test\.workbuddy\memory"

# ↓ 改成家里电脑的路径，比如：
"projects\workclaw\memory"        = "D:\workclaw\.workbuddy\memory"
"projects\workclaw\learning"      = "D:\workclaw\.workbuddy\learning"
"projects\workclaw\scripts"       = "D:\workclaw\.workbuddy\scripts"
"projects\stock_output\memory"    = "D:\stock_output\.workbuddy\memory"
"projects\gpt_output\memory"      = "D:\gpt_test\.workbuddy\memory"
```

**E 层（知识库）**：同样需要改路径：

```powershell
# 公司：
"knowledge\game-design-kb"        = "G:\project_output\game-design-kb"

# ↓ 改成家里的：
"knowledge\game-design-kb"        = "D:\project_output\game-design-kb"
```

### 不存在的项目怎么办？

如果家里电脑没有某个项目（比如 `workclaw`），有两种处理方式：

- **方式一**：保留映射，pull 时会自动创建目录并填充内容
- **方式二**：注释掉对应行（行首加 `#`），这些项目就不会同步

## 第三步：首次拉取

```powershell
# 在 workbuddy-sync 目录下执行
powershell -ExecutionPolicy Bypass -File ".\sync.ps1" pull
```

这会把公司电脑推送的所有经验资产下载并分发到家里电脑的对应位置。

### 验证是否成功

```powershell
# 检查身份文件
cat "$env:USERPROFILE\.workbuddy\IDENTITY.md"

# 检查 Skills 数量
ls "$env:USERPROFILE\.workbuddy\skills\" | Measure-Object
```

如果能看到你的身份信息和 Skills 列表，说明同步成功！

## 第四步：设置自动同步

在 WorkBuddy 中对 Kai 说：

```
帮我创建一个自动化任务：
- 名称：WorkBuddy Sync
- 每2周（周五18:00）执行一次
- 工作目录：D:\workbuddy-sync（改成你的实际路径）
- 执行命令：powershell -ExecutionPolicy Bypass -File "D:\workbuddy-sync\sync.ps1" sync
```

或者手动在 WorkBuddy 的 Automations 面板中创建。

## 完成！🎉

配置完成后，两台电脑的同步流程是：

```
公司电脑改了 Skill / 记忆 / 知识卡片
  ↓ (每2周周五18:00自动 push)
GitHub 私有仓库
  ↓ (家里电脑每2周自动 pull)
家里电脑获得最新资产
  ↓ 反过来也一样
```

## 常用命令速查

```powershell
# 手动立即同步（不等自动任务）
.\sync.ps1 sync

# 只上传本机更改
.\sync.ps1 push

# 只拉取远程更新
.\sync.ps1 pull

# 查看同步状态
cd D:\workbuddy-sync
git log --oneline -5
```

## 遇到冲突怎么办？

因为使用 `git pull --rebase`，绝大多数情况不会冲突。万一冲突了：

```powershell
# 查看冲突文件
git status

# 选择保留某一端的版本
git checkout --theirs <文件路径>   # 保留远程（公司）版本
git checkout --ours <文件路径>     # 保留本地（家里）版本

# 解决后
git add -A
git rebase --continue
```

## 注意事项

1. **不要在两台电脑同时编辑同一个文件**——这是冲突的唯一来源
2. **离开工位前手动 push 一下**比等自动任务更靠谱：`.\sync.ps1 push`
3. **新增 Skill 后**记得两边都会自动同步，不需要手动安装
4. **sync.ps1 的修改不会同步**——因为两台电脑的路径不同，各自维护自己的版本
