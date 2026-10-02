---
name: oa-pages-deploy
description: 将 HTML 文件部署到 OA Pages (pages.woa.com) 静态托管服务。当用户要求将 HTML
  报告、网页、或静态文件发布/部署到 pages.woa.com 时触发此 skill。触发词包括："发到 pages"、"部署到 pages"、"放到
  pages 上"、"pages 部署"、"OA Pages"。
description_zh: 部署 HTML 到 OA Pages
description_en: Deploy HTML to OA Pages
agent_created: true
---

# oa-pages-deploy

## When to use

当用户要求将 HTML 文件（分析报告、网站、静态页面等）部署到 OA Pages (pages.woa.com) 时使用。典型触发场景：
- "帮我发到 pages 上"
- "部署到 OA Pages"
- "放到 pages.woa.com"
- "生成一个 pages 站点"
- 用户提供了 API Key 并要求部署

## Prerequisites

- 用户需提供 OA Pages API Key（格式为 `oa-pages-key-...`）
- 待部署的 HTML 文件已生成
- 用户指定域名前缀（8位字母），或由 AI 随机生成

## Steps

1. **确认部署信息**：
   - HTML 文件路径
   - API Key（用户提供或已知）
   - 域名前缀（用户指定或随机生成 8 位纯小写字母）
   - 权限模式（whitelist 仅自己可见 / tof 需登录 / public 公开）

2. **生成随机域名**（如需要）：
   ```python
   python -c "import random, string; print(''.join(random.choices(string.ascii_lowercase, k=8)))"
   ```

3. **检查域名冲突**（用户指定前缀时）：
   部署前先探测目标域名是否已被占用：
   ```python
   import urllib.request, urllib.error

   prefix = '<prefix>'
   url = f'https://{prefix}.pages.woa.com'

   try:
       urllib.request.urlopen(url, timeout=10)
       print(f"域名已被占用：{url}")
   except urllib.error.HTTPError as e:
       if e.code == 404:
           print(f"域名可用：{url}")
       else:
           # 401/403 等状态码说明站点已存在，只是无权限访问
           print(f"域名已被占用：{url}（HTTP {e.code}）")
   except urllib.error.URLError:
       # DNS 解析失败 / 连接失败，通常说明尚未建站
       print(f"域名可用：{url}（未解析/连接失败）")
   ```
   判断规则：能访问到内容（200）或返回 401/403 等状态码，说明已有站点；返回 404 或连接失败，说明尚未建站。探测结果不稳定时，以部署时服务端返回为准。

4. **部署到 OA Pages**：
   ```python
   import json, urllib.request, urllib.error

   # 读取 HTML（原始内容，不要 base64 编码）
   with open('<html_file_path>', 'r', encoding='utf-8') as f:
       html_content = f.read()

   # 构建请求 — 关键：files 是字典格式，不是数组！值直接传原始文件内容
   payload = {
       'cname': '<prefix>.pages.woa.com',   # 完整域名，必须含后缀
       'files': {
           'index.html': html_content         # 字典格式: {文件名: 原始内容}
       }
   }

   data = json.dumps(payload).encode('utf-8')

   req = urllib.request.Request(
       'https://pages.woa.com/api/sites',
       data=data,
       headers={
           'Content-Type': 'application/json',
           'X-API-Key': '<api_key>'          # 认证使用 X-API-Key header
       },
       method='POST'
   )

   try:
       with urllib.request.urlopen(req, timeout=30) as resp:
           result = json.loads(resp.read().decode('utf-8'))
           print(f"部署成功: {result['url']}")
   except urllib.error.HTTPError as e:
       body = e.read().decode('utf-8', errors='ignore')
       if e.code in (400, 409) or 'exist' in body.lower() or 'conflict' in body.lower() or '已存在' in body or '占用' in body:
           print(f"部署失败：域名可能已被占用（HTTP {e.code}），请换一个前缀重试")
       else:
           print(f"部署失败：HTTP {e.code} - {body}")
   ```

5. **告知用户结果**：
   - 访问地址：`https://<prefix>.pages.woa.com`
   - 管理后台：`https://pages.woa.com/admin/<prefix>.pages.woa.com`
   - 权限说明：新建站点默认 `whitelist`（仅创建者可见）。调整权限/白名单请进入管理后台操作（API 无可靠的权限设置接口）。

## API 参考

| 字段 | 说明 |
|------|------|
| Endpoint（创建） | `POST https://pages.woa.com/api/sites` |
| Endpoint（更新文件） | `PUT https://pages.woa.com/api/sites/<cname>` |
| 认证 Header | `X-API-Key: <api_key>` |
| cname | 完整域名，必须含 `.pages.woa.com` 后缀 |
| files | **字典格式** `{"filename": "原始文件内容"}`（不要 base64） |
| 权限/白名单 | 创建默认 `whitelist`（仅创建者可见）；调整需进入管理后台，API 无可靠设置接口 |

## Pitfalls

- **认证方式**：必须使用 `X-API-Key` header，不是 `Authorization: Bearer`。后者会返回 401。
- **files 格式**：必须是字典 `{"index.html": 原始内容}`，不能用数组 `[{path, content}]`。数组格式会导致 500 错误（服务端收到 Object 而非 string）。
- **cname 格式**：必须是完整域名如 `abc.pages.woa.com`，不能只传前缀 `abc`。
- **编码**：files 的值传**原始文件内容**（HTML 原文），**不要 base64 编码**。服务端不会解码，若传 base64 字符串，页面会直接显示成一串 base64 字符。
- **多文件**：如需部署多个文件，在 files 字典中添加多个键值对即可，如 `{"index.html": html_content, "style.css": css_content}`。
- **域名冲突**：指定的前缀若已被占用，服务端会报错（常见 400/409，body 含 exist/conflict/已存在 等关键词）。部署前先用步骤 3 探测，失败时提示用户换一个前缀重试。
- **权限/白名单**：新建站点默认 `whitelist`（仅创建者可见）。创建接口（POST）传 `visibility`/`whitelist_users` 均被忽略；PUT 接口虽返回"更新成功"但不校验字段（传非法值也返回成功），`visibility`/`whitelist_users` 未被确认生效，且无专门的权限设置端点（`/whitelist`、`/permission`、`/visibility` 均返回 405）。调整权限/白名单请通过管理后台 `https://pages.woa.com/admin/<cname>` 操作。

## Verification

- API 返回 200 且 response 包含 `url` 字段即为成功
- 可通过返回的 URL 在浏览器中验证（需有对应权限）
- 管理后台 `https://pages.woa.com/admin/<domain>` 可查看和修改配置
