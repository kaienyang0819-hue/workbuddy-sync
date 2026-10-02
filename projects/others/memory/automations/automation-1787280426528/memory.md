# 自动化执行记忆

## 任务
通过企业微信向本人杨凯发送文本提醒：需要同步本周AI大事件到老板群

## 执行历史

### 2026-08-31
- 前置检查：wecom-cli 1.2.0，授权状态 authorized
- 通过 `identity whoami` 获取授权人杨凯身份，直接向其发送 markdown 文本消息
- 发送结果：success=true，消息内容「需要同步本周AI大事件到老板群」

### 2026-09-07
- 前置检查：wecom-cli 1.2.0，授权状态 authorized
- 通过 `identity whoami` 获取授权人杨凯身份，直接向其发送 markdown 文本消息
- 发送结果：success=true，消息内容「需要同步本周AI大事件到老板群」

### 2026-09-14
- 前置检查：wecom-cli 1.2.1，授权状态 authorized
- 通过 `identity whoami` 获取授权人杨凯身份，直接向其发送 markdown 文本消息
- 发送结果：success=true，消息内容「需要同步本周AI大事件到老板群」

### 2026-09-21
- 前置检查：wecom-cli 1.3.0，授权状态 authorized
- 通过 `identity whoami` 获取授权人杨凯身份，直接向其发送 markdown 文本消息（sessions_count=0，仍可向授权人发送）
- 发送结果：success=true，消息内容「需要同步本周AI大事件到老板群」

### 2026-09-28
- 前置检查：wecom-cli 1.3.0，授权状态 authorized；sessions_count=0，仍可向授权人发送
- 授权人杨凯 userid 仍为 whoami 返回的「授权真人用户身份 ID」
- ⚠️ 踩坑：用 `--json '{"chat_id":...}'` 传参会返回 40073「非法 chat_id」；改用显式参数 `--chat-id ... --msg-type markdown --markdown '{...}'` 后发送成功
- 另注：`message send`（纯 text）返回 853006「this tool is not available for your corporation」，本企业仅可用 `message aibot send`（markdown）通道
- 发送结果：success=true，消息内容「需要同步本周AI大事件到老板群」
