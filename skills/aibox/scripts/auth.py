"""
AIBox Token 管理脚本

用于管理 X-AMS-TOKEN（用户增值部 token）和 TAI-TOKEN（太湖 token）。
Token 以 base64 编码的形式保存到 hooks 目录下的 aibox.secret 文件中，
格式为每行一条：`token类型##token值`，相同类型会覆盖。

存储位置（$AGENT 为检测到的 Agent 目录名）：
- macOS / Linux: $HOME/.$AGENT/hooks/aibox.secret（如 .codebuddy / .workbuddy / .claude / .cursor / .openclaw）
- Windows:       %USERPROFILE%\\.codebuddy\\hooks\\aibox.secret 等，规则同上

用法：
    # 设置 X-AMS-TOKEN
    python3 auth.py set --type X-AMS-TOKEN --token <your_token>

    # 设置 TAI-TOKEN
    python3 auth.py set --type TAI-TOKEN --token <your_token>

    # 交互式设置（未提供 --token 时从终端读取）
    python3 auth.py set --type X-AMS-TOKEN

    # 查看已存储的 token（默认不显示值，只显示类型）
    python3 auth.py list

    # 查看已存储 token 的完整值（明文输出）
    python3 auth.py list --show

    # 删除指定类型的 token
    python3 auth.py delete --type X-AMS-TOKEN

    # 清空所有 token
    python3 auth.py clear

    # 指定 agent 类型（codebuddy / workbuddy / claude / cursor / openclaw），默认自动判断
    python3 auth.py set --type TAI-TOKEN --token xxx --agent workbuddy
"""

from __future__ import annotations

import os
import sys
import io
import base64
import argparse
import getpass
from pathlib import Path
from typing import Optional, Dict, Tuple, List


# ==================== Windows 中文编码兼容 ====================

def _fix_encoding():
    """修复 Windows 下的中文/emoji 编码问题"""
    if sys.platform == "win32":
        os.environ.setdefault("PYTHONIOENCODING", "utf-8")
        try:
            os.system("chcp 65001 >nul 2>&1")
        except Exception:
            pass
        # [patch] 模块级 keepalive 防止旧 wrapper 被 GC 回收时关闭底层 buffer
        if hasattr(sys.stdout, "buffer"):
            _IO_KEEPALIVE.append(sys.stdout)
            sys.stdout = io.TextIOWrapper(
                sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True
            )
        if hasattr(sys.stderr, "buffer"):
            _IO_KEEPALIVE.append(sys.stderr)
            sys.stderr = io.TextIOWrapper(
                sys.stderr.buffer, encoding="utf-8", errors="replace", line_buffering=True
            )

_IO_KEEPALIVE: list = []  # [patch] 必须在 _fix_encoding 调用前定义
_fix_encoding()


# ==================== 常量 ====================

#: 合法的 token 类型白名单
AUTH_TOKEN_TYPE_AMS = "X-AMS-TOKEN"
AUTH_TOKEN_TYPE_TAI = "TAI-TOKEN"
ALLOWED_TOKEN_TYPES: Tuple[str, ...] = (AUTH_TOKEN_TYPE_AMS, AUTH_TOKEN_TYPE_TAI)

#: aibox.secret 文件名
SECRET_FILE_NAME = "aibox.secret"

#: 每行的分隔符（token类型##token值）
SECRET_LINE_SEP = "##"


# ==================== 路径相关 ====================

#: 各 Agent 类型对应的配置目录名（相对用户主目录，token 存放在其 hooks/ 子目录下）
AGENT_HOOKS_DIR_NAMES: Dict[str, str] = {
    "codebuddy": ".codebuddy",
    "workbuddy": ".workbuddy",
    "claude": ".claude",
    "cursor": ".cursor",
    "openclaw": ".openclaw",
}

#: Agent 类型检测时读取的项目目录环境变量（与 aibox_hooks.py 的检测保持一致）
AGENT_PROJECT_DIR_ENV: Dict[str, str] = {
    "workbuddy": "WORKBUDDY_PROJECT_DIR",
    "codebuddy": "CODEBUDDY_PROJECT_DIR",
    "claude": "CLAUDE_PROJECT_DIR",
}


def get_home_dir() -> Path:
    """
    获取用户主目录。
    - Windows 使用 %USERPROFILE%
    - macOS / Linux 使用 $HOME
    """
    if sys.platform == "win32":
        home = os.environ.get("USERPROFILE") or os.environ.get("HOME")
    else:
        home = os.environ.get("HOME") or os.environ.get("USERPROFILE")
    if not home:
        # 兜底使用 Path.home()，内部也会做跨平台判断
        return Path.home()
    return Path(home)


def _normalize_agent_type(val: str) -> Optional[str]:
    """规范化 Agent 类型字符串，兼容 claude-code 等历史写法"""
    v = val.strip().lower()
    if v == "claude-code":
        v = "claude"
    return v if v in AGENT_HOOKS_DIR_NAMES else None


def detect_agent_type(explicit: Optional[str] = None) -> str:
    """
    判断 Agent 类型（codebuddy / workbuddy / claude / cursor / openclaw）。

    优先级：
    1. 显式传入 explicit 参数
    2. 环境变量 AIBOX_AGENT_TYPE
    3. 各 Agent 的项目目录环境变量（WORKBUDDY_PROJECT_DIR / CODEBUDDY_PROJECT_DIR / CLAUDE_PROJECT_DIR）
    4. 本脚本所在路径包含 .{agent}/ 目录（skill 安装在 <项目根>/.{agent}/skills/ 下时最可靠）
    5. 当前工作目录路径包含 .{agent}
    6. 默认使用 codebuddy

    注：workbuddy 环境下 cwd 是项目根目录（不含 .workbuddy 标记），
    因此第 4 条的脚本路径检测是 workbuddy 下最可靠的判定依据。
    """
    if explicit:
        normalized = _normalize_agent_type(explicit)
        if normalized:
            return normalized

    env_val = _normalize_agent_type(os.environ.get("AIBOX_AGENT_TYPE", ""))
    if env_val:
        return env_val

    for agent, env_key in AGENT_PROJECT_DIR_ENV.items():
        if os.environ.get(env_key):
            return agent

    # 从脚本自身路径推断：skill 位于 <项目根>/.{agent}/skills/aibox/scripts/auth.py
    script_path = str(Path(__file__).resolve()).replace("\\", "/").lower()
    for agent, dir_name in AGENT_HOOKS_DIR_NAMES.items():
        if f"/{dir_name}/" in script_path:
            return agent

    cwd = str(Path.cwd()).replace("\\", "/").lower()
    for agent, dir_name in AGENT_HOOKS_DIR_NAMES.items():
        if f"/{dir_name}" in cwd or cwd.endswith(f"/{dir_name}"):
            return agent

    return "codebuddy"


def get_hooks_dir(agent_type: Optional[str] = None) -> Path:
    """
    获取 hooks 目录路径。

    - macOS / Linux: $HOME/.{agent}/hooks/
    - Windows:       %USERPROFILE%\\.{agent}\\hooks\\
    """
    agent = detect_agent_type(agent_type)
    dir_name = AGENT_HOOKS_DIR_NAMES.get(agent, ".codebuddy")
    return get_home_dir() / dir_name / "hooks"


def get_secret_file_path(agent_type: Optional[str] = None) -> Path:
    """获取 aibox.secret 文件绝对路径"""
    return get_hooks_dir(agent_type) / SECRET_FILE_NAME


# ==================== Secret 读写 ====================

def _b64_encode(text: str) -> str:
    """对字符串进行 base64 编码"""
    return base64.b64encode(text.encode("utf-8")).decode("ascii")


def _b64_decode(text: str) -> str:
    """对 base64 字符串进行解码，失败时返回空串"""
    try:
        return base64.b64decode(text.encode("ascii")).decode("utf-8")
    except Exception:
        return ""


def load_secrets(agent_type: Optional[str] = None) -> Dict[str, str]:
    """
    加载 aibox.secret 中的 token 映射。

    文件格式（每行一条）：
        <base64(token类型##token值)>

    Returns:
        Dict[str, str]: {token_type: token_value}
    """
    path = get_secret_file_path(agent_type)
    secrets: Dict[str, str] = {}
    if not path.is_file():
        return secrets

    try:
        content = path.read_text(encoding="utf-8")
    except Exception:
        return secrets

    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        decoded = _b64_decode(line)
        if not decoded or SECRET_LINE_SEP not in decoded:
            continue
        ttype, _, tvalue = decoded.partition(SECRET_LINE_SEP)
        ttype = ttype.strip()
        if ttype:
            secrets[ttype] = tvalue
    return secrets


def save_secrets(secrets: Dict[str, str], agent_type: Optional[str] = None) -> Path:
    """
    将 token 映射写回 aibox.secret 文件，每行一个 base64 编码条目。
    同 token 类型自然覆盖（dict 保证唯一）。
    """
    path = get_secret_file_path(agent_type)
    path.parent.mkdir(parents=True, exist_ok=True)

    lines: List[str] = []
    for ttype, tvalue in secrets.items():
        if not ttype:
            continue
        encoded = _b64_encode(f"{ttype}{SECRET_LINE_SEP}{tvalue or ''}")
        lines.append(encoded)

    path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")

    # 尝试把文件权限收紧到仅当前用户可读写（Unix），Windows 下会被忽略
    try:
        if sys.platform != "win32":
            os.chmod(path, 0o600)
    except Exception:
        pass

    return path


def get_token(token_type: str, agent_type: Optional[str] = None) -> str:
    """
    便捷函数：读取指定类型的 token，不存在则返回空串。
    此函数供 download_skill.py / search.py 等脚本调用。
    """
    if not token_type:
        return ""
    secrets = load_secrets(agent_type)
    return secrets.get(token_type, "") or ""


def build_auth_headers(agent_type: Optional[str] = None) -> Dict[str, str]:
    """
    便捷函数：构建请求头。
    所有已存储且非空的 token 会以「原 token 类型字符串」作为 header 名加入。

    Returns:
        Dict[str, str]: 形如 {"X-AMS-TOKEN": "xxx", "TAI-TOKEN": "yyy"}
    """
    headers: Dict[str, str] = {}
    secrets = load_secrets(agent_type)
    for ttype, tvalue in secrets.items():
        if ttype and tvalue:
            headers[ttype] = tvalue
    return headers


# ==================== 命令实现 ====================

def _validate_token_type(token_type: str) -> str:
    """校验并返回规范化的 token 类型（大写）"""
    if not token_type:
        raise SystemExit(
            f"❌ --type 不能为空，必须是 {' / '.join(ALLOWED_TOKEN_TYPES)}"
        )
    normalized = token_type.strip().upper()
    if normalized not in ALLOWED_TOKEN_TYPES:
        raise SystemExit(
            f"❌ --type 取值无效: {token_type}，必须是 {' / '.join(ALLOWED_TOKEN_TYPES)}"
        )
    return normalized


def cmd_set(args: argparse.Namespace) -> int:
    """set 命令：设置某个 token 类型"""
    ttype = _validate_token_type(args.type)

    token_value = args.token
    if token_value is None:
        # 交互式输入（隐藏回显）
        if not sys.stdin.isatty():
            print("❌ 非交互模式下请通过 --token 提供 token 值")
            return 1
        try:
            token_value = getpass.getpass(f"请输入 {ttype} 的值（输入不回显）: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n⏹️  已取消")
            return 1

    if not token_value:
        print("❌ token 值不能为空")
        return 1

    secrets = load_secrets(args.agent)
    old_value = secrets.get(ttype, "")
    secrets[ttype] = token_value
    path = save_secrets(secrets, args.agent)

    action = "更新" if old_value else "新增"
    print(f"✅ 已{action} {ttype}")
    print(f"   📁 文件位置: {path}")
    print(f"   🔐 加密方式: base64（格式：{ttype}{SECRET_LINE_SEP}<token>）")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    """list 命令：列出所有已保存的 token 类型"""
    path = get_secret_file_path(args.agent)
    secrets = load_secrets(args.agent)

    print(f"📁 Secret 文件: {path}")
    if not path.exists():
        print("⚠️  文件不存在，尚未保存任何 token")
        return 0

    if not secrets:
        print("⚠️  文件内没有有效的 token 条目")
        return 0

    print(f"🔐 已保存 {len(secrets)} 个 token：")
    print("-" * 60)
    for ttype in ALLOWED_TOKEN_TYPES + tuple(t for t in secrets if t not in ALLOWED_TOKEN_TYPES):
        if ttype not in secrets:
            continue
        value = secrets[ttype]
        if args.show:
            display = value
        else:
            # 脱敏显示：只展示前 4 + 末 4 字符
            if len(value) <= 8:
                display = "*" * len(value)
            else:
                display = f"{value[:4]}{'*' * (len(value) - 8)}{value[-4:]}"
        print(f"  • {ttype}: {display}")
    print("-" * 60)
    return 0


def cmd_delete(args: argparse.Namespace) -> int:
    """delete 命令：删除指定类型的 token"""
    ttype = _validate_token_type(args.type)
    secrets = load_secrets(args.agent)
    if ttype not in secrets:
        print(f"⚠️  未找到 {ttype}，无需删除")
        return 0
    del secrets[ttype]
    path = save_secrets(secrets, args.agent)
    print(f"🗑️  已删除 {ttype}")
    print(f"   📁 文件位置: {path}")
    return 0


def cmd_clear(args: argparse.Namespace) -> int:
    """clear 命令：清空所有 token"""
    path = get_secret_file_path(args.agent)
    if not path.exists():
        print("⚠️  文件不存在，无需清空")
        return 0
    save_secrets({}, args.agent)
    print(f"🗑️  已清空所有 token")
    print(f"   📁 文件位置: {path}")
    return 0


# ==================== 主入口 ====================

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="AIBox Token 管理工具（X-AMS-TOKEN / TAI-TOKEN）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
说明:
  支持两种 token 类型:
    - X-AMS-TOKEN  (用户增值部 Token)
    - TAI-TOKEN    (太湖 Token)

  存储位置 ($AGENT 为检测到的 Agent 目录名):
    macOS/Linux : $HOME/.$AGENT/hooks/aibox.secret
    Windows     : %USERPROFILE%\\.codebuddy\\hooks\\aibox.secret（其他 Agent 同理）
    （支持 codebuddy / workbuddy / claude / cursor / openclaw，自动判断）

  加密方式:
    每行一条 base64(<token类型>##<token值>)，同类型覆盖。

示例:
  python3 auth.py set --type X-AMS-TOKEN --token abc123
  python3 auth.py set --type TAI-TOKEN         # 交互式输入
  python3 auth.py list
  python3 auth.py list --show
  python3 auth.py delete --type X-AMS-TOKEN
  python3 auth.py clear
        """
    )

    sub = parser.add_subparsers(dest="command", required=True, metavar="COMMAND")

    _AGENT_CHOICES = list(AGENT_HOOKS_DIR_NAMES.keys()) + ["claude-code"]

    # set
    p_set = sub.add_parser("set", help="设置指定类型的 token")
    p_set.add_argument("--type", "-t", required=True,
                       choices=list(ALLOWED_TOKEN_TYPES),
                       help="Token 类型：X-AMS-TOKEN 或 TAI-TOKEN")
    p_set.add_argument("--token", default=None,
                       help="Token 值；未提供则进入交互式输入")
    p_set.add_argument("--agent", default=None, choices=_AGENT_CHOICES,
                       help="Agent 类型，默认自动判断")
    p_set.set_defaults(func=cmd_set)

    # list
    p_list = sub.add_parser("list", help="列出已保存的 token 类型")
    p_list.add_argument("--show", action="store_true",
                        help="显示完整 token 值（默认脱敏）")
    p_list.add_argument("--agent", default=None, choices=_AGENT_CHOICES,
                        help="Agent 类型，默认自动判断")
    p_list.set_defaults(func=cmd_list)

    # delete
    p_del = sub.add_parser("delete", help="删除指定类型的 token")
    p_del.add_argument("--type", "-t", required=True,
                       choices=list(ALLOWED_TOKEN_TYPES),
                       help="Token 类型：X-AMS-TOKEN 或 TAI-TOKEN")
    p_del.add_argument("--agent", default=None, choices=_AGENT_CHOICES,
                       help="Agent 类型，默认自动判断")
    p_del.set_defaults(func=cmd_delete)

    # clear
    p_clr = sub.add_parser("clear", help="清空所有 token")
    p_clr.add_argument("--agent", default=None, choices=_AGENT_CHOICES,
                       help="Agent 类型，默认自动判断")
    p_clr.set_defaults(func=cmd_clear)

    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (UnicodeEncodeError, UnicodeDecodeError) as e:
        sys.stderr.write(f"[encoding error] {e}\n")
        sys.stderr.write("Tip: try running with 'set PYTHONIOENCODING=utf-8' or 'chcp 65001' on Windows.\n")
        sys.exit(1)
    except BrokenPipeError:
        sys.exit(0)
    except KeyboardInterrupt:
        print("\n⏹️  已取消")
        sys.exit(0)
