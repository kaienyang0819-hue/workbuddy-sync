# full-cycle-workflow —— 通用产出质量闭环

把「人工验收返工」还给 AI 自己的通用工作流 skill。源自腾讯内部 `@tencent/fcd-ai`（Full-Cycle Developer）方法论的通用化改造，适配策划 / 文档 / 问卷 / PPT / Excel / HTML / 图片等各类产出。

## 能力

接到任何形式的需求（一句话 / 文档 / 链接 / 截图 / 图片），自动走五段闭环：

> 需求评审 → Plan 实现清单 → 逐点产出 → 自验收（文档质量门禁 + 像素级比稿）→ 经验沉淀

核心机制：Plan 实现清单作为全流程唯一基准 + 零空格铁律（每字段四选一 ✅/❌/⛔/[~]）+ 完成口径（逐条核对，禁「全部完成」空话）。

## 文件结构

| 文件 | 作用 |
|---|---|
| `SKILL.md` | 五段闭环主流程 |
| `quality-gates.md` | 验收门禁：文档质量门禁 / 像素级比稿 / 图片产出 |
| `experience.md` | 经验沉淀库（长记性，踩坑往里追加） |

## 安装

本 `.skill` 文件本质是 zip，解压后把 `full-cycle-workflow` 目录复制到：

- 用户级（所有项目可用）：`~/.workbuddy/skills/`
- 项目级（仅当前项目）：`<项目>/.workbuddy/skills/`

复制后新建会话即可生效。

## 可选依赖（像素级比稿）

`quality-gates.md` 里的像素级比稿复用了 fcd CLI 的 `fcd diff`（pixelmatch + SSIM），需要先安装：

```bash
npm i -g @tencent/fcd-ai --registry=https://mirrors.tencent.com/npm/
```

不装 fcd 也能用「文档质量门禁」和「图片产出」两类验收，只是 HTML 界面 / UI 还原类产出无法做像素级量化比稿。

## 触发

提需求即自动触发，无需手动调用。触发词：做方案、出文档、写策划案、做 PPT、做问卷、画图、做 HTML、产出一份……
