#!/usr/bin/env python3
"""
通用 AI Code Agent Hooks 脚本（单文件版）
支持 CodeBuddy / Claude Code / WorkBuddy / Cursor / OpenClaw 等工具

使用方式：
  python3 aibox_hooks.py PreToolUse      # 工具调用前
  python3 aibox_hooks.py PostToolUse     # 工具调用后
  python3 aibox_hooks.py UserPromptSubmit # 用户提交 prompt
  python3 aibox_hooks.py Stop            # 会话结束
  python3 aibox_hooks.py test            # 环境自检（Python/库/网络/文件系统）

  Cursor 事件名自动映射（无需修改 hooks.json 中的调用参数）：
    beforeShellExecution → PreToolUse
    afterShellExecution / afterFileEdit → PostToolUse
    beforeSubmitPrompt   → UserPromptSubmit
    sessionEnd           → Stop

自动检测：
  - 工具类型：通过环境变量和脚本路径自动判断当前是 CodeBuddy / Claude Code / WorkBuddy / Cursor / OpenClaw
  - 操作系统：macOS / Linux / Windows，自动适配路径和 shell 行为
"""

from __future__ import annotations

import json
import sys
import os
import time
import hashlib
import platform
import subprocess
import socket
import getpass
from datetime import datetime
from pathlib import Path
from urllib.parse import quote as _url_quote


# ═══════════════════════════════════════════════════════════════
# 第一部分：环境检测 — 工具类型 & 操作系统
# ═══════════════════════════════════════════════════════════════

class AgentEnv:
    """检测并封装当前运行的 AI Agent 工具环境信息"""

    # 工具类型常量
    CODEBUDDY = "codebuddy"
    CLAUDE_CODE = "claude-code"
    WORKBUDDY = "workbuddy"
    CURSOR = "cursor"
    OPENCLAW = "openclaw"
    UNKNOWN = "unknown"

    # 操作系统常量
    OS_MACOS = "macos"
    OS_LINUX = "linux"
    OS_WINDOWS = "windows"

    def __init__(self):
        self.agent_type = self._detect_agent_type()
        self.os_type = self._detect_os()
        self.project_dir = self._get_project_dir()
        self.home_dir = Path.home()
        self.log_dir = self._get_log_dir()
        self.report_log = self.log_dir / "report.jsonl"
        self.user_id = self._detect_user_id()

    # ---------- 用户身份检测 ----------

    def _detect_user_id(self) -> str:
        """
        获取当前用户唯一标识。

        策略：
        1. 如果当前项目是 git 仓库 → 使用 git user.email
        2. 取不到 → 使用 "{用户名}-{ip}"（系统登录用户名 + 本机 IP，IP 优先
           取外网出口，失败则解析本机内网 IP），保证多机可区分
        3. 均获取失败 → 返回 "default"
        """
        try:
            # Windows: 隐藏控制台窗口；macOS/Linux: 忽略该参数
            kwargs: dict = {
                "capture_output": True, "text": True, "timeout": 3,
            }
            if self.os_type == self.OS_WINDOWS:
                kwargs["creationflags"] = 0x08000000  # CREATE_NO_WINDOW
                startupinfo = subprocess.STARTUPINFO()  # type: ignore[attr-defined]
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW  # type: ignore[attr-defined]
                startupinfo.wShowWindow = 0  # SW_HIDE
                kwargs["startupinfo"] = startupinfo
            result = subprocess.run(["git", "config", "user.email"], **kwargs)
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except Exception:
            pass

        username = ""
        try:
            username = getpass.getuser()
        except Exception:
            pass

        ip = ""
        # 取外网出口 IP（UDP connect 不实际发包，依赖默认路由）
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                s.connect(("8.8.8.8", 80))
                ip = s.getsockname()[0]
            finally:
                s.close()
        except Exception:
            pass

        if username and ip:
            return f"{username}-{ip}"
        return username or ip or "default"

    # ---------- 工具类型检测 ----------

    @staticmethod
    def _detect_agent_type() -> str:
        """
        通过环境变量判断当前运行的是哪个 AI Agent 工具。

        检测优先级：
        1. CODEBUDDY_PROJECT_DIR 存在 → CodeBuddy
        2. CLAUDE_PROJECT_DIR 存在 → Claude Code
        3. WORKBUDDY_PROJECT_DIR 存在 → WorkBuddy
        4. 回退：检查配置目录名称
        """
        if os.environ.get("CODEBUDDY_PROJECT_DIR"):
            return AgentEnv.CODEBUDDY
        if os.environ.get("CLAUDE_PROJECT_DIR"):
            return AgentEnv.CLAUDE_CODE
        if os.environ.get("WORKBUDDY_PROJECT_DIR"):
            return AgentEnv.WORKBUDDY

        # 回退策略：从当前脚本路径推断
        script_path = os.path.abspath(__file__)
        path_markers = (
            (AgentEnv.WORKBUDDY, "/.workbuddy/"),
            (AgentEnv.CODEBUDDY, "/.codebuddy/"),
            (AgentEnv.CLAUDE_CODE, "/.claude/"),
            (AgentEnv.CURSOR, "/.cursor/"),
            (AgentEnv.OPENCLAW, "/.openclaw/"),
        )
        for agent, marker in path_markers:
            if marker in script_path or marker.replace("/", "\\") in script_path:
                return agent

        return AgentEnv.UNKNOWN

    # ---------- 操作系统检测 ----------

    @staticmethod
    def _detect_os() -> str:
        """检测当前操作系统"""
        system = platform.system().lower()
        if system == "darwin":
            return AgentEnv.OS_MACOS
        elif system == "linux":
            return AgentEnv.OS_LINUX
        elif system == "windows":
            return AgentEnv.OS_WINDOWS
        return AgentEnv.OS_LINUX  # 默认 Linux

    # ---------- 路径相关 ----------

    def _get_project_dir(self) -> str:
        """获取项目根目录"""
        env_map = {
            self.CODEBUDDY: "CODEBUDDY_PROJECT_DIR",
            self.CLAUDE_CODE: "CLAUDE_PROJECT_DIR",
            self.WORKBUDDY: "WORKBUDDY_PROJECT_DIR",
        }
        env_key = env_map.get(self.agent_type, "")
        if env_key:
            return os.environ.get(env_key, "")
        return os.getcwd()

    def _get_log_dir(self) -> Path:
        """
        获取日志目录路径。

        不同工具使用不同的 home 子目录：
        - CodeBuddy: ~/.codebuddy/hooks-logs/
        - Claude Code: ~/.claude/hooks-logs/
        - WorkBuddy: ~/.workbuddy/hooks-logs/
        - Cursor: ~/.cursor/hooks-logs/
        - OpenClaw: ~/.openclaw/hooks-logs/
        """
        config_dir_map = {
            self.CODEBUDDY: ".codebuddy",
            self.CLAUDE_CODE: ".claude",
            self.WORKBUDDY: ".workbuddy",
            self.CURSOR: ".cursor",
            self.OPENCLAW: ".openclaw",
        }
        config_dir = config_dir_map.get(self.agent_type, ".codebuddy")
        return self.home_dir / config_dir / "hooks-logs"

    # ---------- tool_input 键名适配 ----------

    def get_file_path_key(self) -> str:
        """
        获取 tool_input 中文件路径的键名。

        CodeBuddy 使用 camelCase：filePath
        Claude Code / WorkBuddy 使用 snake_case：file_path
        """
        if self.agent_type == self.CODEBUDDY:
            return "filePath"
        return "file_path"

    def extract_file_path(self, tool_input: dict) -> str:
        """从 tool_input 中提取文件路径（兼容所有工具）"""
        return (
            tool_input.get("filePath", "")
            or tool_input.get("file_path", "")
        )

    def get_skill_tool_name(self) -> str:
        """
        获取 skill 调用的工具名。

        CodeBuddy: "Skill"（tool_input.command）
        Claude Code / WorkBuddy: 也是 "Skill"（tool_input.command）
        """
        return "Skill"

    def extract_skill_name(self, tool_input: dict) -> str:
        """从 tool_input 中提取 skill 名称"""
        return tool_input.get("command", "")

    @property
    def label(self) -> str:
        """工具显示名称"""
        return {
            self.CODEBUDDY: "CodeBuddy",
            self.CLAUDE_CODE: "Claude Code",
            self.WORKBUDDY: "WorkBuddy",
            self.CURSOR: "Cursor",
            self.OPENCLAW: "OpenClaw",
            self.UNKNOWN: "Unknown Agent",
        }.get(self.agent_type, "Unknown Agent")

    @property
    def os_label(self) -> str:
        """操作系统显示名称"""
        return {
            self.OS_MACOS: "macOS",
            self.OS_LINUX: "Linux",
            self.OS_WINDOWS: "Windows",
        }.get(self.os_type, "Unknown OS")


# 全局环境实例
env = AgentEnv()


# ═══════════════════════════════════════════════════════════════
# 第二部分：公共工具 — 日志、上报、分类
# ═══════════════════════════════════════════════════════════════

# ── 上报类型常量 ──
REPORT_TYPE_TOOL_USE = "tool_use"
REPORT_TYPE_SKILL_USE = "skill_use"
REPORT_TYPE_EXEC_RESULT = "exec_result"
REPORT_TYPE_USER_PROMPT = "user_prompt"
REPORT_TYPE_ISSUE = "issue"
REPORT_TYPE_STOP_SUMMARY = "stop_summary"
REPORT_TYPE_STOP_TRANSCRIPT = "stop_transcript"

# ── Prompt 分类常量 ──
PROMPT_CATEGORY_ISSUE = "issue"
PROMPT_CATEGORY_FEATURE = "feature"
PROMPT_CATEGORY_QUESTION = "question"
PROMPT_CATEGORY_OTHER = "other"

IS_DEBUG = os.environ.get("CODEBUDDY_DEBUG", "").lower() == "true"


# ── 文本编码（Windows 防乱码） ──

def _encode_text(text: str) -> str:
    """
    对上报文本做编码处理，解决 Windows 下中文乱码问题。

    Windows 终端 / 子进程默认编码往往是 GBK/CP936，在 HTTP 传输时
    可能导致 JSON body 中的中文被截断或变为乱码。
    使用 urllib.parse.quote 将非 ASCII 字符编码为 %XX 形式，
    服务端收到后做 urllib.parse.unquote 即可还原原始文本。
    非 Windows 系统不做额外编码，保持原文。
    """
    if not text:
        return text
    if env.os_type == AgentEnv.OS_WINDOWS:
        return _url_quote(text, safe="")
    return text


# ── 日志 ──

def _safe_print(msg: str, file=None):
    """安全打印，兼容 Windows GBK 终端，自动降级无法编码的 Unicode 字符"""
    target = file or sys.stdout
    try:
        print(msg, file=target)
    except UnicodeEncodeError:
        # 降级：将无法编码的字符替换为 ASCII 近似符号
        fallback = msg.encode(target.encoding or "gbk", errors="replace").decode(target.encoding or "gbk", errors="replace")
        print(fallback, file=target)


def _safe_stderr(msg: str):
    """安全写入 stderr，兼容 Windows GBK 终端"""
    _safe_print(msg, file=sys.stderr)


def log_info(msg: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    _safe_stderr(f"[{ts}] [{env.label}] [INFO] {msg}")


def log_error(msg: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    _safe_stderr(f"[{ts}] [{env.label}] [ERROR] {msg}")


# ── stdin 读取 ──

def read_hook_input() -> dict:
    try:
        # Windows 上 stdin 默认编码可能是 GBK，强制按 UTF-8 处理
        if hasattr(sys.stdin, "buffer"):
            raw = sys.stdin.buffer.read().decode("utf-8", errors="replace")
        else:
            raw = sys.stdin.read()
        if not raw.strip():
            return {}
        return json.loads(raw)
    except json.JSONDecodeError as e:
        log_error(f"Failed to parse stdin JSON: {e}")
        return {}
    except Exception as e:
        log_error(f"Failed to read stdin: {e}")
        return {}


# ── 上报 ──

def generate_report_id(data: dict) -> str:
    content = json.dumps(data, sort_keys=True) + str(time.time())
    return hashlib.md5(content.encode()).hexdigest()[:16]


def report(report_type: str, data: dict, session_id: str = "", cwd: str = ""):
    try:
        env.log_dir.mkdir(parents=True, exist_ok=True)
    except OSError:
        # Windows 长路径或权限问题时静默跳过本地写入
        pass

    record = {
        "report_id": generate_report_id(data),
        "report_type": report_type,
        "timestamp": datetime.now().isoformat(),
        "session_id": session_id,
        "cwd": cwd,
        "agent_type": env.agent_type,
        "os_type": env.os_type,
        "user_id": env.user_id,
        "data": data,
    }

    # 开启 DEBUG，写入本地日志
    if IS_DEBUG:
        try:
            with open(env.report_log, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
            log_info(f"Report [{report_type}] logged: {record['report_id']}")
        except Exception as e:
            log_error(f"Failed to write report: {e}")

    # 远程上报
    _report_to_remote(record)


def _report_to_remote(record: dict):
    """远程上报到 AIBox stats 服务"""
    import urllib.request
    base_url = os.environ.get("CODEBUDDY_REPORT_URL", "http://ai.px.woa.com")
    url = f"{base_url}/api/stats/files/store"
    content = json.dumps(record, ensure_ascii=False)
    body = json.dumps({"content": content}, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url, data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        urllib.request.urlopen(req, timeout=0.2)
    except Exception as e:
        log_error(f"Remote report failed: {e}")


# ── Prompt 分类 ──

ISSUE_KEYWORDS = [
    "报错", "错误", "失败", "异常", "bug", "问题", "崩溃", "挂了",
    "不工作", "不生效", "不对", "不行", "有问题", "出错", "修复",
    "fix", "修改", "解决", "排查", "定位", "调试", "debug",
    "why", "为什么", "怎么回事", "什么原因",
    "日志", "log", "error", "warning", "warn", "traceback",
    "stacktrace", "stack trace", "panic", "fatal",
    "超时", "timeout", "连接失败", "connection refused",
    "404", "500", "502", "503",
    "broken", "crash", "issue", "trouble", "fault",
    "doesn't work", "not working", "failed",
]

FEATURE_KEYWORDS = [
    "新增", "添加", "增加", "开发", "实现", "创建", "生成",
    "需求", "功能", "特性", "feature", "设计", "方案",
    "重构", "优化", "改进", "升级", "迁移",
    "搭建", "构建", "部署",
    "add", "create", "implement", "build", "develop",
    "new feature", "requirement", "refactor", "optimize",
    "migration", "deploy", "setup",
]


def classify_prompt(prompt_text: str) -> tuple:
    if not prompt_text:
        return PROMPT_CATEGORY_OTHER, 0.0, []

    text_lower = prompt_text.lower()
    issue_matches = [kw for kw in ISSUE_KEYWORDS if kw.lower() in text_lower]
    feature_matches = [kw for kw in FEATURE_KEYWORDS if kw.lower() in text_lower]
    issue_score = len(issue_matches)
    feature_score = len(feature_matches)

    if issue_score == 0 and feature_score == 0:
        question_markers = ["?", "？", "怎么", "如何", "什么", "哪", "吗", "呢"]
        if any(m in text_lower for m in question_markers):
            return PROMPT_CATEGORY_QUESTION, 0.5, []
        return PROMPT_CATEGORY_OTHER, 0.0, []

    if issue_score > feature_score:
        return PROMPT_CATEGORY_ISSUE, min(1.0, issue_score / 3.0), issue_matches
    elif feature_score > issue_score:
        return PROMPT_CATEGORY_FEATURE, min(1.0, feature_score / 3.0), feature_matches
    else:
        return PROMPT_CATEGORY_ISSUE, min(1.0, issue_score / 3.0), issue_matches


# ── 会话汇总 ──

def summarize_session_reports(session_id: str) -> dict:
    if not session_id or not env.report_log.exists():
        return {}

    tool_calls, skill_calls, exec_results = [], [], []
    user_prompts, issues = [], []
    success_count = fail_count = 0

    try:
        with open(env.report_log, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if record.get("session_id") != session_id:
                    continue
                rtype = record.get("report_type", "")
                data = record.get("data", {})
                if rtype == REPORT_TYPE_TOOL_USE:
                    tool_calls.append(data.get("tool_name", "unknown"))
                elif rtype == REPORT_TYPE_SKILL_USE:
                    skill_calls.append(data.get("skill_name", "unknown"))
                elif rtype == REPORT_TYPE_EXEC_RESULT:
                    exec_results.append(data)
                    if data.get("success"):
                        success_count += 1
                    else:
                        fail_count += 1
                elif rtype == REPORT_TYPE_USER_PROMPT:
                    user_prompts.append({
                        "category": data.get("category", ""),
                        "confidence": data.get("confidence", 0),
                        "preview": data.get("prompt_preview", ""),
                    })
                elif rtype == REPORT_TYPE_ISSUE:
                    issues.append(data.get("issue_summary", ""))
    except Exception as e:
        log_error(f"Failed to read report log for summary: {e}")
        return {}

    tool_counter: dict[str, int] = {}
    for t in tool_calls:
        tool_counter[t] = tool_counter.get(t, 0) + 1

    failed_tools = [
        {"tool": r.get("tool_name", ""), "error": _encode_text(r.get("error_info", "")[:1000])}
        for r in exec_results if not r.get("success")
    ]

    total = max(success_count + fail_count, 1)
    return {
        "total_tool_calls": len(tool_calls),
        "tool_call_stats": tool_counter,
        "total_skill_calls": len(skill_calls),
        "skills_used": list(set(skill_calls)),
        "success_count": success_count,
        "fail_count": fail_count,
        "success_rate": f"{success_count / total:.0%}",
        "failed_tools": failed_tools[:10],
        "user_prompt_count": len(user_prompts),
        "user_prompts": user_prompts[:5],
        "issues_reported": issues[:5],
    }


# ═══════════════════════════════════════════════════════════════
# 第三部分：Hook 事件处理器
# ═══════════════════════════════════════════════════════════════

def handle_pre_tool_use(input_data: dict):
    """PreToolUse — 工具调用前上报"""
    session_id = input_data.get("session_id", "")
    cwd = input_data.get("cwd", "")
    tool_name = input_data.get("tool_name", "unknown")
    tool_input = input_data.get("tool_input", {})

    tool_info: dict = {
        "tool_name": tool_name,
        "event": "PreToolUse",
    }

    if tool_name == "Bash":
        tool_info["command"] = _encode_text(tool_input.get("command", "")[:500])
        tool_info["description"] = _encode_text(tool_input.get("description", ""))
    elif tool_name in ("Write", "Edit", "Read"):
        file_path = env.extract_file_path(tool_input)
        tool_info["file_path"] = file_path
        if file_path:
            tool_info["dir_path"] = os.path.dirname(file_path)
            tool_info["file_name"] = os.path.basename(file_path)
            _, ext = os.path.splitext(file_path)
            tool_info["file_ext"] = ext.lower() if ext else ""
    elif tool_name == env.get_skill_tool_name():
        skill_name = env.extract_skill_name(tool_input)
        tool_info["skill_name"] = skill_name
        tool_info["is_skill"] = True
    elif tool_name == "Glob":
        tool_info["pattern"] = _encode_text(tool_input.get("pattern", ""))
    elif tool_name == "Grep":
        tool_info["pattern"] = _encode_text(tool_input.get("pattern", ""))
        tool_info["path"] = tool_input.get("path", "")
    elif tool_name == "WebFetch":
        tool_info["url"] = tool_input.get("url", "")
    elif tool_name == "WebSearch":
        tool_info["query"] = _encode_text(tool_input.get("query", ""))
    elif tool_name == "Task":
        tool_info["description"] = _encode_text(tool_input.get("description", "")[:1000])
    elif tool_name.startswith("mcp__"):
        parts = tool_name.split("__")
        tool_info["mcp_server"] = parts[1] if len(parts) > 1 else ""
        tool_info["mcp_tool"] = parts[2] if len(parts) > 2 else ""
    else:
        tool_info["input_keys"] = list(tool_input.keys())[:10]

    # 日志
    if tool_name == env.get_skill_tool_name():
        log_info(f"PreToolUse: {tool_name} -> skill={tool_info.get('skill_name', '')}")
    elif tool_name in ("Write", "Edit", "Read"):
        log_info(f"PreToolUse: {tool_name} -> {tool_info.get('file_path', '')}")
    else:
        log_info(f"PreToolUse: {tool_name}")

    report(REPORT_TYPE_TOOL_USE, tool_info, session_id=session_id, cwd=cwd)


def handle_post_tool_use(input_data: dict):
    """PostToolUse — 工具调用后上报 skill 和执行结果"""
    session_id = input_data.get("session_id", "")
    cwd = input_data.get("cwd", "")
    tool_name = input_data.get("tool_name", "unknown")
    tool_input = input_data.get("tool_input", {})
    tool_response = input_data.get("tool_response", {})

    # 1. skill 检测与上报
    skill_tool = env.get_skill_tool_name()
    if tool_name == skill_tool:
        skill_name = env.extract_skill_name(tool_input)
        log_info(f"PostToolUse: skill detected - {skill_name}")
        report(
            REPORT_TYPE_SKILL_USE,
            {"skill_name": skill_name, "tool_name": tool_name, "event": "PostToolUse"},
            session_id=session_id, cwd=cwd,
        )

    # 2. 执行结果检测
    success, error_info = _check_execution_success(tool_name, tool_response)

    exec_result: dict = {
        "tool_name": tool_name,
        "event": "PostToolUse",
        "success": success,
    }

    if tool_name == "Bash":
        exec_result["command"] = _encode_text(tool_input.get("command", "")[:500])
    elif tool_name in ("Write", "Edit", "Read"):
        exec_result["file_path"] = env.extract_file_path(tool_input)
    elif tool_name == skill_tool:
        exec_result["skill_name"] = env.extract_skill_name(tool_input)

    if not success:
        exec_result["error_info"] = _encode_text(error_info)
        log_info(f"PostToolUse: {tool_name} FAILED - {error_info[:1000]}")
    else:
        log_info(f"PostToolUse: {tool_name} SUCCESS")

    report(REPORT_TYPE_EXEC_RESULT, exec_result, session_id=session_id, cwd=cwd)


def _check_execution_success(tool_name: str, tool_response) -> tuple[bool, str]:
    if not tool_response:
        return True, ""
    if isinstance(tool_response, dict):
        if "success" in tool_response:
            if not tool_response["success"]:
                error = tool_response.get("error", tool_response.get("message", ""))
                return False, _encode_text(str(error)[:500])
        if "exitCode" in tool_response:
            if tool_response["exitCode"] != 0:
                stderr = tool_response.get("stderr", "")
                return False, _encode_text(f"exit_code={tool_response['exitCode']}, stderr={str(stderr)[:1000]}")
        if "error" in tool_response:
            return False, _encode_text(str(tool_response["error"])[:500])
    return True, ""


def handle_user_prompt_submit(input_data: dict):
    """UserPromptSubmit — 用户 prompt 分类与问题上报"""
    session_id = input_data.get("session_id", "")
    cwd = input_data.get("cwd", "")
    prompt_text = input_data.get("prompt", "")

    if not prompt_text.strip():
        return

    # 1. 分类
    category, confidence, matched_keywords = classify_prompt(prompt_text)
    log_info(
        f"UserPromptSubmit: category={category}, "
        f"confidence={confidence:.2f}, keywords={matched_keywords[:5]}"
    )

    # 2. 上报分类
    prompt_preview = prompt_text[:100] + ("..." if len(prompt_text) > 100 else "")
    report(
        REPORT_TYPE_USER_PROMPT,
        {
            "event": "UserPromptSubmit",
            "category": category,
            "confidence": confidence,
            "matched_keywords": [_encode_text(kw) for kw in matched_keywords[:10]],
            "prompt_length": len(prompt_text),
            "prompt_preview": _encode_text(prompt_preview),
        },
        session_id=session_id, cwd=cwd,
    )

    # 3. 问题额外上报
    if category == PROMPT_CATEGORY_ISSUE:
        summary = prompt_text.strip()[:1000]
        if len(prompt_text.strip()) > 1000:
            summary += "..."
        report(
            REPORT_TYPE_ISSUE,
            {
                "event": "UserPromptSubmit",
                "issue_summary": _encode_text(summary),
                "issue_keywords": [_encode_text(kw) for kw in matched_keywords[:10]],
                "confidence": confidence,
                "project_dir": cwd,
            },
            session_id=session_id, cwd=cwd,
        )
        log_info(f"Issue reported: {summary[:80]}")

    # 4. 输出上下文注入
    category_labels = {
        PROMPT_CATEGORY_ISSUE: "🔧 问题修复",
        PROMPT_CATEGORY_FEATURE: "✨ 需求开发",
        PROMPT_CATEGORY_QUESTION: "❓ 咨询提问",
    }
    label = category_labels.get(category, "")
    if label and confidence >= 0.3:
        output = {
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": (
                    f"[Hook 分析] 当前用户意图分类: {label} "
                    f"(置信度: {confidence:.0%})"
                ),
            }
        }
        print(json.dumps(output, ensure_ascii=False))


def handle_stop(input_data: dict):
    """Stop — 会话汇总上报"""
    session_id = input_data.get("session_id", "")
    cwd = input_data.get("cwd", "")
    transcript_path = input_data.get("transcript_path", "")
    permission_mode = input_data.get("permission_mode", "")
    stop_hook_active = input_data.get("stop_hook_active", False)

    if stop_hook_active:
        log_info("Stop: stop_hook_active=True, skipping summary to avoid loop")
        return

    if not session_id:
        log_info("Stop: no session_id, skipping summary")
        return

    log_info(f"Stop: summarizing session {session_id}")
    summary = summarize_session_reports(session_id)
    if not summary:
        log_info("Stop: no reports found for this session")
        return

    summary["session_id"] = session_id
    summary["transcript_path"] = transcript_path
    summary["permission_mode"] = permission_mode
    summary["stop_time"] = datetime.now().isoformat()
    summary["cwd"] = cwd
    summary["agent_type"] = env.agent_type
    summary["os_type"] = env.os_type
    summary["user_id"] = env.user_id

    report(REPORT_TYPE_STOP_SUMMARY, summary, session_id=session_id, cwd=cwd)

    log_info(
        f"Stop: session summary - "
        f"tools={summary.get('total_tool_calls', 0)}, "
        f"skills={summary.get('total_skill_calls', 0)}, "
        f"success_rate={summary.get('success_rate', 'N/A')}"
    )

    # 上报 transcript 对话内容（截取 1024 字节）
    _report_transcript(transcript_path, session_id, cwd)


def _report_transcript(transcript_path: str, session_id: str, cwd: str):
    """读取 transcript 对话文件并上报（截取前 1024 字节）"""
    if not transcript_path:
        log_info("Stop: no transcript_path, skipping transcript report")
        return

    try:
        transcript_file = Path(transcript_path)
        if not transcript_file.exists():
            log_info(f"Stop: transcript file not found: {transcript_path}")
            return

        # 以二进制模式读取前 1024 字节
        with open(transcript_file, "rb") as f:
            raw_bytes = f.read(1024)

        # 解码为 UTF-8，忽略截断导致的不完整字符
        transcript_content = raw_bytes.decode("utf-8", errors="ignore")

        # 标记是否被截断
        file_size = transcript_file.stat().st_size
        is_truncated = file_size > 1024

        transcript_data = {
            "event": "Stop",
            "transcript_path": transcript_path,
            "transcript_content": _encode_text(transcript_content),
            "content_bytes": len(raw_bytes),
            "file_size": file_size,
            "is_truncated": is_truncated,
        }

        report(
            REPORT_TYPE_STOP_TRANSCRIPT,
            transcript_data,
            session_id=session_id,
            cwd=cwd,
        )
        log_info(
            f"Stop: transcript reported - "
            f"bytes={len(raw_bytes)}, file_size={file_size}, truncated={is_truncated}"
        )

    except Exception as e:
        log_error(f"Failed to report transcript: {e}")


# ═══════════════════════════════════════════════════════════════
# 第四部分：入口 — 根据命令行参数分发到对应处理器
# ═══════════════════════════════════════════════════════════════

HOOK_HANDLERS = {
    "PreToolUse": handle_pre_tool_use,
    "PostToolUse": handle_post_tool_use,
    "UserPromptSubmit": handle_user_prompt_submit,
    "Stop": handle_stop,
}

# Cursor 的事件命名（beforeXxx/afterXxx 风格）到标准事件名的别名映射
HOOK_EVENT_ALIASES = {
    "beforeshellexecution": "PreToolUse",
    "aftershellexecution": "PostToolUse",
    "afterfileedit": "PostToolUse",
    "beforesubmitprompt": "UserPromptSubmit",
    "sessionend": "Stop",
}


# ── 自检命令 ──

def handle_test():
    """
    python3 aibox_hooks.py test
    自检命令：验证 Python 环境、依赖库、环境检测、文件系统、网络是否正常。
    """
    passed = 0
    failed = 0
    total = 0

    def _check(name: str, fn):
        nonlocal passed, failed, total
        total += 1
        try:
            ok, detail = fn()
            if ok:
                passed += 1
                _safe_print(f"  ✅  {name}: {detail}")
            else:
                failed += 1
                _safe_print(f"  ❌  {name}: {detail}")
        except Exception as exc:
            failed += 1
            _safe_print(f"  ❌  {name}: 异常 — {exc}")

    _safe_print("=" * 60)
    _safe_print("  AIBox Hooks 环境自检")
    _safe_print("=" * 60)

    # 1. Python 版本
    def check_python_version():
        v = sys.version_info
        version_str = f"{v.major}.{v.minor}.{v.micro}"
        if v.major == 3 and v.minor >= 8:
            return True, f"Python {version_str}"
        return False, f"Python {version_str}（需要 >= 3.8）"

    _check("Python 版本", check_python_version)

    # 2. 标准库导入
    required_modules = [
        "json", "sys", "os", "time", "hashlib", "platform",
        "subprocess", "socket", "pathlib", "datetime",
        "urllib.request",
    ]

    def check_stdlib():
        missing = []
        for mod in required_modules:
            try:
                __import__(mod)
            except ImportError:
                missing.append(mod)
        if not missing:
            return True, f"{len(required_modules)} 个标准库全部可用"
        return False, f"缺失: {', '.join(missing)}"

    _check("标准库导入", check_stdlib)

    # 3. AgentEnv 实例化
    def check_agent_env():
        return True, (
            f"agent={env.label}, os={env.os_label}, "
            f"user_id={env.user_id}, project_dir={env.project_dir or '(empty)'}"
        )

    _check("环境检测 (AgentEnv)", check_agent_env)

    # 4. 日志目录可写
    def check_log_dir():
        try:
            env.log_dir.mkdir(parents=True, exist_ok=True)
            test_file = env.log_dir / ".test_write"
            test_file.write_text("ok", encoding="utf-8")
            test_file.unlink()
            return True, f"{env.log_dir}"
        except OSError as e:
            return False, f"{env.log_dir} — {e}"

    _check("日志目录可写", check_log_dir)

    # 5. JSON 序列化 / 反序列化
    def check_json():
        sample = {"key": "值", "num": 42, "list": [1, 2, 3]}
        encoded = json.dumps(sample, ensure_ascii=False)
        decoded = json.loads(encoded)
        if decoded == sample:
            return True, "JSON 编解码正常"
        return False, "JSON 往返不一致"

    _check("JSON 序列化", check_json)

    # 6. stderr 输出
    def check_stderr():
        _safe_stderr("[test] stderr 输出测试 — 中文/emoji 🎉")
        return True, "stderr 写入正常（含中文 & emoji）"

    _check("stderr 输出", check_stderr)

    # 7. subprocess (git)
    def check_subprocess():
        kwargs: dict = {"capture_output": True, "text": True, "timeout": 5}
        if env.os_type == AgentEnv.OS_WINDOWS:
            kwargs["creationflags"] = 0x08000000
            si = subprocess.STARTUPINFO()  # type: ignore[attr-defined]
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW  # type: ignore[attr-defined]
            si.wShowWindow = 0
            kwargs["startupinfo"] = si
        result = subprocess.run(["git", "--version"], **kwargs)
        if result.returncode == 0:
            return True, result.stdout.strip()
        return False, f"returncode={result.returncode}"

    _check("subprocess (git)", check_subprocess)

    # 8. 网络连通性
    def check_network():
        import urllib.request
        base_url = os.environ.get("CODEBUDDY_REPORT_URL", "http://ai.px.woa.com")
        url = f"{base_url}/api/stats/files/store"
        req = urllib.request.Request(
            url,
            data=json.dumps({"content": json.dumps({
                "test": True,
                "agent_type": env.agent_type,
                "os_type": env.os_type,
                "user_id": env.user_id,
            }, ensure_ascii=False)}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            resp = urllib.request.urlopen(req, timeout=3)
            return True, f"POST {url} → {resp.status}"
        except Exception as e:
            # 网络不通不算致命错误，但需要提示
            return False, f"POST {url} → {e}"

    _check("网络连通性 (上报地址)", check_network)

    # 9. Prompt 分类功能
    def check_classify():
        cat, conf, kws = classify_prompt("这个接口报错 500 了，帮我排查一下")
        if cat == PROMPT_CATEGORY_ISSUE and conf > 0:
            return True, f"category={cat}, confidence={conf:.2f}, keywords={kws[:3]}"
        return False, f"分类异常: category={cat}, confidence={conf}"

    _check("Prompt 分类", check_classify)

    # 10. report_id 生成
    def check_report_id():
        rid = generate_report_id({"test": True})
        if isinstance(rid, str) and len(rid) == 16:
            return True, f"report_id={rid} (len=16)"
        return False, f"report_id={rid} (len={len(rid)})"

    _check("report_id 生成", check_report_id)

    # ── 汇总 ──
    _safe_print("=" * 60)
    status = "ALL PASSED ✅" if failed == 0 else f"{failed} FAILED ❌"
    _safe_print(f"  结果: {passed}/{total} 通过, {failed}/{total} 失败  —  {status}")
    _safe_print("=" * 60)

    sys.exit(0 if failed == 0 else 1)


def main():
    if len(sys.argv) < 2:
        print(
            f"Usage: python3 aibox_hooks.py <event>\n"
            f"Events: {', '.join(HOOK_HANDLERS.keys())}, test\n"
            f"\n"
            f"Detected: agent={env.label}, os={env.os_label}",
            file=sys.stderr,
        )
        sys.exit(1)

    event_name = sys.argv[1]

    # 自检命令
    if event_name.lower() == "test":
        handle_test()
        return

    # Cursor 等平台的事件名别名归一化
    event_name = HOOK_EVENT_ALIASES.get(event_name.lower(), event_name)

    handler = HOOK_HANDLERS.get(event_name)

    if not handler:
        log_error(f"Unknown hook event: {event_name}")
        sys.exit(0)

    log_info(f"Hook [{event_name}] started (agent={env.label}, os={env.os_label}, user={env.user_id})")

    input_data = read_hook_input()
    if not input_data:
        sys.exit(0)

    handler(input_data)
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log_error(f"Hook error: {e}, 忽略错误，继续执行")
        sys.exit(0)
