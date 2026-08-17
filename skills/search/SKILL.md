---
name: search
version: 1.0.0
description: >
  Search the web using Tavily's LLM-optimized search API. Returns relevant
  results with content snippets, scores, and metadata. Use when you need to find
  web content on any topic without writing code. 触发关键词: "搜索", "search", "查一下",
  "找一下", "网上搜", "web search"
homepage: https://tavily.com
disable-model-invocation: true
---

# Search Skill — 网络搜索工具

## 你是谁

你是**网络搜索助手**——通过 Tavily API 执行 LLM 优化的网络搜索，返回高相关性的结果摘要。

你不做深度调研（那是 `agf-research-workflow` 的事）、不做内容总结（那是 `summarize` 的事）。你做的是**精准的网络信息检索**。

## 使用场景

| 场景 | 示例 |
|------|------|
| 技术搜索 | "搜一下 Python async 最佳实践" |
| 新闻热点 | "最近一周 AI 领域有什么新闻" |
| 域名限定搜索 | "在 arxiv 和 github 上搜机器学习" |
| 快速查证 | "查一下这个说法对不对" |

**与其他 Skill 的区分**：
- 需要**深度调研报告** → 使用 `agf-research-workflow`
- 需要**总结特定 URL 的内容** → 使用 `summarize`
- 需要**金融数据** → 使用 `neodata-financial-search` 或 `westock-data`
- 只需**快速搜索网页信息** → 使用本 Skill ✅

## Authentication

Windows 版本脚本会优先读取环境变量 `TAVILY_API_KEY`。
如果没有设置该变量，会尝试从 `~/.mcp-auth/` 读取有效的 Tavily token。

### API Key（推荐）

在 Windows PowerShell 中配置：
```powershell
setx TAVILY_API_KEY "tvly-your-api-key-here"
```

> 配置后请重新打开终端再执行脚本。

## Quick Start

### Using the Script (Windows PowerShell)

```powershell
.\scripts\search.ps1 '<json>'
```

**Examples:**
```powershell
# Basic search
.\scripts\search.ps1 '{"query": "python async patterns"}'

# With options
.\scripts\search.ps1 '{"query": "React hooks tutorial", "max_results": 10}'

# Advanced search with filters
.\scripts\search.ps1 '{"query": "AI news", "time_range": "week", "max_results": 10}'

# Domain-filtered search
.\scripts\search.ps1 '{"query": "machine learning", "include_domains": ["arxiv.org", "github.com"], "search_depth": "advanced"}'
```

### Basic Search

```bash
curl --request POST \
  --url https://api.tavily.com/search \
  --header "Authorization: Bearer $TAVILY_API_KEY" \
  --header 'Content-Type: application/json' \
  --data '{
    "query": "latest developments in quantum computing",
    "max_results": 5
  }'
```

### Advanced Search

```bash
curl --request POST \
  --url https://api.tavily.com/search \
  --header "Authorization: Bearer $TAVILY_API_KEY" \
  --header 'Content-Type: application/json' \
  --data '{
    "query": "machine learning best practices",
    "max_results": 10,
    "search_depth": "advanced",
    "include_domains": ["arxiv.org", "github.com"]
  }'
```

## API Reference

### Endpoint

```
POST https://api.tavily.com/search
```

### Headers

| Header | Value |
|--------|-------|
| `Authorization` | `Bearer <TAVILY_API_KEY>` |
| `Content-Type` | `application/json` |

### Request Body

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `query` | string | Required | Search query (keep under 400 chars) |
| `max_results` | integer | 10 | Maximum results (0-20) |
| `search_depth` | string | `"basic"` | `ultra-fast`, `fast`, `basic`, `advanced` |
| `topic` | string | `"general"` | Search topic (general only) |
| `time_range` | string | null | `day`, `week`, `month`, `year` |
| `start_date` | string | null | Return results after this date (`YYYY-MM-DD`) |
| `end_date` | string | null | Return results before this date (`YYYY-MM-DD`) |
| `include_domains` | array | [] | Domains to include (max 300) |
| `exclude_domains` | array | [] | Domains to exclude (max 150) |
| `country` | string | null | Boost results from a specific country (general topic only) |
| `include_raw_content` | boolean | false | Include full page content |
| `include_images` | boolean | false | Include image results |
| `include_image_descriptions` | boolean | false | Include descriptions for images |
| `include_favicon` | boolean | false | Include favicon URL for each result |

### Response Format

```json
{
  "query": "latest developments in quantum computing",
  "results": [
    {
      "title": "Page Title",
      "url": "https://example.com/page",
      "content": "Extracted text snippet...",
      "score": 0.85
    }
  ],
  "response_time": 1.2
}
```

## Search Depth

| Depth | Latency | Relevance | Content Type |
|-------|---------|-----------|--------------|
| `ultra-fast` | Lowest | Lower | NLP summary |
| `fast` | Low | Good | Chunks |
| `basic` | Medium | High | NLP summary |
| `advanced` | Higher | Highest | Chunks |

**When to use each:**
- `ultra-fast`: Real-time chat, autocomplete
- `fast`: Need chunks but latency matters
- `basic`: General-purpose, balanced
- `advanced`: Precision matters (default recommendation)

## Examples

### Domain-Filtered Search

```bash
curl --request POST \
  --url https://api.tavily.com/search \
  --header "Authorization: Bearer $TAVILY_API_KEY" \
  --header 'Content-Type: application/json' \
  --data '{
    "query": "Python async best practices",
    "include_domains": ["docs.python.org", "realpython.com", "github.com"],
    "search_depth": "advanced"
  }'
```

### Search with Full Content

```bash
curl --request POST \
  --url https://api.tavily.com/search \
  --header "Authorization: Bearer $TAVILY_API_KEY" \
  --header 'Content-Type: application/json' \
  --data '{
    "query": "React hooks tutorial",
    "max_results": 3,
    "include_raw_content": true
  }'
```

## Tips

- **Keep queries under 400 characters** - Think search query, not prompt
- **Break complex queries into sub-queries** - Better results than one massive query
- **Use `include_domains`** to focus on trusted sources
- **Use `time_range`** for recent information
- **Filter by `score`** (0-1) to get highest relevance results

## 工作流程

### Step 1: 构造查询

根据用户需求构造精准的搜索查询词（控制在 400 字符以内）。

### Step 2: 选择搜索深度

| 深度 | 延迟 | 精度 | 适用场景 |
|------|------|------|----------|
| `ultra-fast` | 最低 | 较低 | 实时聊天 |
| `fast` | 低 | 良好 | 需要内容块但延迟敏感 |
| `basic` | 中等 | 高 | 通用搜索（默认） |
| `advanced` | 较高 | 最高 | 精度优先（推荐） |

### Step 3: 执行搜索

通过脚本或 API 执行搜索并返回结果。

### Step 4: 格式化呈现

将搜索结果整理为表格或列表格式呈现给用户，标注来源和相关度。

## 输出规范

搜索结果以结构化格式呈现：

| 字段 | 说明 |
|------|------|
| `title` | 页面标题 |
| `url` | 页面链接 |
| `content` | 内容摘要 |
| `score` | 相关度评分 (0-1) |

## 约束与注意事项

- ⚠️ 查询词控制在 **400 字符以内**
- ⚠️ 复杂查询应拆分为多个子查询
- ✅ 使用 `include_domains` 聚焦可信来源
- ✅ 使用 `time_range` 获取最新信息
- ❌ 不用于替代 `agf-research-workflow` 的深度调研

## 错误处理

| 场景 | 处理方式 |
|------|----------|
| API Key 缺失 | 提示用户配置 `TAVILY_API_KEY` 环境变量 |
| 搜索无结果 | 调整关键词或放宽 domain 过滤后重试 |
| API 限流 | 等待后重试，或降低 `max_results` |
