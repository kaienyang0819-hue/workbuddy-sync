---
name: wechat-article-spider
version: 1.0.0
description: >
  微信公众号文章爬虫——将微信公号文章转换为 Markdown + 本地图片。 当用户提供微信公众号文章链接，或要求抓取/保存/下载微信文章时触发。
  触发关键词: "微信文章", "公众号", "mp.weixin.qq.com", "抓取微信", "下载公号文章"
disable-model-invocation: true
---

# wechat-article-spider — 微信公众号文章爬虫

## 你是谁

你是**微信文章提取工具**——将微信公众号文章抓取为本地 Markdown 文件，同时下载所有图片到本地。

你不做微信消息监控、不做批量公众号爬取、不做微信登录。你做的是**单篇文章的内容提取和本地化保存**。

## 核心能力

| 能力 | 说明 |
|------|------|
| 文章抓取 | 输入微信公号文章 URL，抓取全文 |
| 图片下载 | 自动下载所有图片到 `images/` 文件夹 |
| Markdown 生成 | 生成 Markdown 文件，图片使用相对路径引用 |

## 使用场景

| 场景 | 示例 |
|------|------|
| 保存文章 | "帮我保存这篇微信文章" + URL |
| 提取内容 | "把这个公号文章转成 Markdown" |
| 离线阅读 | "下载这篇文章到本地" |

**与其他 Skill 的区分**：
- 需要**总结任意 URL** → 使用 `summarize`
- 需要**网络搜索** → 使用 `search`
- 需要**保存微信公号文章为本地 Markdown** → 使用本 Skill ✅

## 工作流程

### Step 1: 获取文章 URL

确认用户提供的微信文章链接（格式: `https://mp.weixin.qq.com/s/...`）。

### Step 2: 安装依赖（首次）

```bash
cd ~/.workbuddy/skills/wechat-article-spider/scripts
pip install -r requirements.txt
```

### Step 3: 执行抓取

```bash
python main.py <文章URL> [输出目录]
```

**示例**：
```bash
# 下载到默认目录
python main.py https://mp.weixin.qq.com/s/xxxxx

# 指定输出目录
python main.py https://mp.weixin.qq.com/s/xxxxx G:/project_output/wechat-articles
```

### Step 4: 验证输出

检查输出目录，确认 Markdown 文件和图片完整。

## 输出规范

| 输出项 | 格式 | 存放位置 |
|--------|------|----------|
| 文章正文 | `{文章标题}.md` | 输出目录根 |
| 文章图片 | `img_001_xxx.jpg` 等 | `{输出目录}/images/` |

**输出目录结构**：
```
output/
├── 文章标题.md
└── images/
    ├── img_001_xxx.jpg
    ├── img_002_xxx.png
    └── ...
```

## 依赖

| 包名 | 用途 |
|------|------|
| `requests` | HTTP 请求 |
| `beautifulsoup4` | HTML 解析 |
| `lxml` | XML/HTML 解析引擎 |

## 约束与注意事项

- ⚠️ 微信文章可能有**反爬机制**，如遇失败可稍后重试
- ⚠️ 部分**动态加载**的图片可能无法获取
- ✅ 图片文件名使用哈希值避免重复
- ❌ 不支持需要登录才能查看的文章
- ❌ 不支持批量公众号抓取（仅单篇文章）

## 错误处理

| 场景 | 处理方式 |
|------|----------|
| URL 格式不正确 | 提示用户提供 `mp.weixin.qq.com` 格式的链接 |
| 文章被删除/不可访问 | 告知用户文章可能已被删除或设置了访问权限 |
| 反爬被拦截 | 提示稍后重试，或尝试更换 User-Agent |
| 依赖未安装 | 自动执行 `pip install -r requirements.txt` |
| 图片下载失败 | 跳过失败的图片，在 Markdown 中保留原始 URL |
