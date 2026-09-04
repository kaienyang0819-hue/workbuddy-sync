"""
Skill 下载脚本
从远端服务器搜索、查看和下载 skill 的 zip 包，解压到本地 .codebuddy/skills 目录。
支持列表查询、搜索和交互式安装。

用法：
    # 列出远端所有可用 skills
    python3 download_skill.py --list

    # 搜索 skill（模糊匹配名称或描述）
    python3 download_skill.py --search "workflow"

    # 下载并安装指定 skill
    python3 download_skill.py --install <skill_name>

    # 强制覆盖已存在的 skill
    python3 download_skill.py --install <skill_name> --force

    # 指定本地 skills 目录
    python3 download_skill.py --install <skill_name> --skills-dir /path/to/.codebuddy/skills
"""

import os
import sys
import io
import shutil
import zipfile
import argparse
import getpass
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional, List, Dict

# ==================== Windows 中文编码兼容 ====================
# Windows 默认控制台编码通常为 GBK(cp936)，无法输出 emoji 和部分中文
# 强制将 stdout/stderr 切换为 UTF-8，并设置环境变量确保子进程也使用 UTF-8

def _fix_encoding():
    """修复 Windows 下的中文/emoji 编码问题"""
    if sys.platform == "win32":
        # 设置环境变量，影响子进程
        os.environ.setdefault("PYTHONIOENCODING", "utf-8")
        # 尝试启用 Windows 控制台的 UTF-8 模式 (Windows 10 1903+)
        try:
            os.system("chcp 65001 >nul 2>&1")
        except Exception:
            pass
        # 重新包装 stdout/stderr 为 UTF-8，遇到无法编码的字符用 replace 策略
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

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import re
import requests

# ==================== Token 读取（来自 auth.py） ====================
# 将 scripts 目录加入 sys.path，以便复用 auth.py 中的 token 读取逻辑
_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

try:
    from auth import build_auth_headers as _build_auth_headers  # type: ignore
    from auth import detect_agent_type  # type: ignore
except Exception:
    def _build_auth_headers():
        return {}

    def detect_agent_type(explicit=None) -> str:  # type: ignore
        return "codebuddy"


def _auth_headers() -> dict:
    """读取本地存储的 X-AMS-TOKEN / TAI-TOKEN，token 不存在或为空则不返回该项"""
    try:
        return _build_auth_headers() or {}
    except Exception:
        return {}


# ==================== 配置 ====================

PROXY_USER = os.getenv("PROXY_USER", "") or getpass.getuser()
WORKFLOW_BASE_URL = os.getenv("WORKFLOW_BASE_URL", "http://ai.px.woa.com")

# API 端点
SKILLS_LIST_URL = f"{WORKFLOW_BASE_URL}/api/skills/summary"
SKILL_DOWNLOAD_URL = f"{WORKFLOW_BASE_URL}/api/skills/{{skill_name}}/download"
SKILL_DETAIL_URL = f"{WORKFLOW_BASE_URL}/api/skills/{{skill_name}}"

# 请求超时（秒）
REQUEST_TIMEOUT = 120

# 默认本地 skills 目录（相对于项目根目录）
DEFAULT_SKILLS_DIR = ".codebuddy/skills"

# 各 Agent 类型对应的默认 skills 目录（相对于项目根目录）
SKILLS_DIR_BY_AGENT = {
    "codebuddy": ".codebuddy/skills",
    "workbuddy": ".workbuddy/skills",
    "claude": ".claude/skills",
    "cursor": ".cursor/skills",
    "openclaw": ".openclaw/skills",
}

# 项目根定位时识别的 Agent 配置目录（顺序即优先级）
AGENT_CONFIG_DIRS = (".workbuddy", ".codebuddy", ".claude", ".cursor")


def _override_base_url(base_url: str):
    """运行时覆盖 API 基础地址"""
    global WORKFLOW_BASE_URL, SKILLS_LIST_URL, SKILL_DOWNLOAD_URL, SKILL_DETAIL_URL
    WORKFLOW_BASE_URL = base_url
    SKILLS_LIST_URL = f"{WORKFLOW_BASE_URL}/api/skills/summary"
    SKILL_DOWNLOAD_URL = f"{WORKFLOW_BASE_URL}/api/skills/{{skill_name}}/download"
    SKILL_DETAIL_URL = f"{WORKFLOW_BASE_URL}/api/skills/{{skill_name}}"


def _request_headers() -> dict:
    """构建请求头：X-Proxy-User + 本地保存的 X-AMS-TOKEN / TAI-TOKEN"""
    headers: dict = {}
    if PROXY_USER:
        headers["X-Proxy-User"] = PROXY_USER
    headers.update(_auth_headers())
    return headers


# ==================== 工具函数 ====================

def find_project_root() -> Path:
    """
    向上查找项目根目录（包含 .codebuddy / .workbuddy / .claude / .cursor
    任一 Agent 配置目录的最近父目录）

    Returns:
        Path: 项目根目录路径
    """
    current = Path.cwd()
    while current != current.parent:
        for config_dir in AGENT_CONFIG_DIRS:
            if (current / config_dir).is_dir():
                return current
        current = current.parent
    # 如果没找到，使用当前目录
    return Path.cwd()


def _detect_default_skills_dir(project_root: Path) -> str:
    """
    根据环境变量、项目根下的配置目录推断默认 skills 目录。

    优先级：
    1. 复用 auth.detect_agent_type（显式/环境变量/脚本路径检测）
    2. 项目根下实际存在的 Agent 配置目录
    3. 兜底 DEFAULT_SKILLS_DIR
    """
    try:
        agent = detect_agent_type()
    except Exception:
        agent = None
    if agent in SKILLS_DIR_BY_AGENT:
        return SKILLS_DIR_BY_AGENT[agent]

    for config_dir in AGENT_CONFIG_DIRS:
        if (project_root / config_dir).is_dir():
            return f"{config_dir}/skills"

    return DEFAULT_SKILLS_DIR


def get_skills_dir(skills_dir: Optional[str] = None) -> Path:
    """
    获取本地 skills 目录路径

    Args:
        skills_dir: 用户指定的 skills 目录路径，为 None 时自动查找

    Returns:
        Path: skills 目录的绝对路径
    """
    if skills_dir:
        return Path(skills_dir).resolve()
    project_root = find_project_root()
    return project_root / _detect_default_skills_dir(project_root)


def get_local_skills(skills_dir: Path) -> Dict[str, Path]:
    """
    扫描本地已安装的 skills

    Args:
        skills_dir: 本地 skills 目录

    Returns:
        Dict[str, Path]: skill 名称 -> 目录路径 的映射
    """
    local_skills = {}
    if skills_dir.is_dir():
        for item in skills_dir.iterdir():
            if item.is_dir() and (item / "SKILL.md").exists():
                local_skills[item.name] = item
    return local_skills


# ==================== API 调用 ====================

def fetch_skill_list() -> List[Dict]:
    """
    从远端获取可用的 skill 列表（XML 格式）

    接口返回示例：
        <skills>
          <skill available="true">
            <name>skill-name</name>
            <description>skill description</description>
            <location>/path/to/SKILL.md</location>
          </skill>
          ...
        </skills>

    Returns:
        List[Dict]: skill 信息列表，每项包含 name, description, available 等字段
    """
    try:
        print(f"🌐 正在从 {WORKFLOW_BASE_URL} 获取 skill 列表...")
        response = requests.post(
            SKILLS_LIST_URL,
            timeout=REQUEST_TIMEOUT,
            headers=_request_headers()
        )
        response.raise_for_status()

        # 解析 XML 响应；服务端个别 skill 路径含未转义的 &（如 forT&D），
        # 单条脏数据不应导致整个列表不可用，解析失败时尝试修复后重试
        try:
            root = ET.fromstring(response.text)
        except ET.ParseError:
            fixed = re.sub(r"&(?!amp;|lt;|gt;|quot;|apos;|#)", "&amp;", response.text)
            root = ET.fromstring(fixed)

        skills = []
        for skill_el in root.findall("skill"):
            skill = {
                "name": (skill_el.findtext("name") or "").strip(),
                "description": (skill_el.findtext("description") or "").strip(),
                "location": (skill_el.findtext("location") or "").strip(),
                "available": skill_el.get("available", "true").lower() == "true",
            }
            # 可选字段
            requires = skill_el.findtext("requires")
            if requires:
                skill["requires"] = requires.strip()
            skills.append(skill)

        return skills

    except requests.exceptions.ConnectionError:
        print(f"❌ 连接失败，请检查服务是否可用: {WORKFLOW_BASE_URL}")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print("❌ 请求超时，请稍后重试")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP 错误: {e}")
        if e.response is not None:
            print(f"   服务端响应: {e.response.text.strip()}")
        sys.exit(1)
    except ET.ParseError:
        print("❌ 服务端返回了无效的 XML 数据")
        sys.exit(1)


def fetch_skill_detail(skill_name: str) -> Optional[Dict]:
    """
    获取指定 skill 的详细信息

    Args:
        skill_name: skill 名称

    Returns:
        Optional[Dict]: skill 详细信息，获取失败返回 None
    """
    url = SKILL_DETAIL_URL.format(skill_name=skill_name)
    try:
        response = requests.get(
            url,
            timeout=REQUEST_TIMEOUT,
            headers=_request_headers()
        )
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response is not None and e.response.status_code != 404:
            print(f"❌ HTTP 错误: {e}")
            print(f"   服务端响应: {e.response.text.strip()}")
        return None
    except Exception:
        return None


def download_skill_zip(skill_name: str, dest_path: Path) -> bool:
    """
    下载指定 skill 的 zip 包到本地

    Args:
        skill_name: skill 名称
        dest_path: zip 文件保存路径

    Returns:
        bool: 下载是否成功
    """
    url = SKILL_DOWNLOAD_URL.format(skill_name=skill_name)
    try:
        print(f"📥 正在下载 skill: {skill_name} ...")
        response = requests.get(
            url,
            timeout=REQUEST_TIMEOUT,
            stream=True,
            headers=_request_headers()
        )

        if response.status_code == 404:
            print(f"❌ 远端未找到 skill: {skill_name}")
            return False

        response.raise_for_status()

        # 获取文件大小（如果有）
        total_size = int(response.headers.get("content-length", 0))
        downloaded = 0

        with open(dest_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        bar_len = 30
                        filled = int(bar_len * downloaded // total_size)
                        bar = "#" * filled + "-" * (bar_len - filled)
                        try:
                            print(f"\r   [{bar}] {percent:.1f}% ({downloaded}/{total_size} bytes)", end="", flush=True)
                        except (UnicodeEncodeError, OSError):
                            # Windows 低版本控制台可能无法处理 \r
                            pass

        if total_size > 0:
            print()  # 换行
        print(f"   ✅ 下载完成: {dest_path} ({downloaded} bytes)")
        return True

    except requests.exceptions.ConnectionError:
        print(f"\n❌ 连接失败: {url}")
        return False
    except requests.exceptions.Timeout:
        print("\n❌ 下载超时")
        return False
    except requests.exceptions.HTTPError as e:
        print(f"\n❌ HTTP 错误: {e}")
        if e.response is not None:
            print(f"   服务端响应: {e.response.text.strip()}")
        return False
    except Exception as e:
        print(f"\n❌ 下载失败: {e}")
        return False


# ==================== 核心操作 ====================

def list_skills(skills_dir: Path) -> None:
    """
    列出远端可用的 skills，并标注本地安装状态

    Args:
        skills_dir: 本地 skills 目录
    """
    remote_skills = fetch_skill_list()
    if not remote_skills:
        print("⚠️  远端暂无可用的 skill")
        return

    local_skills = get_local_skills(skills_dir)

    print(f"\n📦 远端可用 Skills（共 {len(remote_skills)} 个）：")
    print(f"   本地 skills 目录: {skills_dir}")
    print("-" * 70)

    for i, skill in enumerate(remote_skills, 1):
        name = skill.get("name", "unknown")
        description = skill.get("description", "无描述")
        available = skill.get("available", True)

        # 标注本地安装状态
        if name in local_skills:
            status = "✅ 已安装"
        elif not available:
            status = "🚫 不可用"
        else:
            status = "⬜ 未安装"

        print(f"  {i:>3}. {status}  {name}")
        print(f"       {description[:60]}{'...' if len(description) > 60 else ''}")
        # 展示缺失依赖
        if not available and skill.get("requires"):
            print(f"       ⚠️  缺失依赖: {skill['requires']}")

    print("-" * 70)
    print(f"💡 使用 --install <skill_name> 安装 skill")
    print(f"💡 使用 --search <关键词> 搜索 skill")


def search_skills(keyword: str, skills_dir: Path) -> List[Dict]:
    """
    搜索远端 skills（模糊匹配名称和描述）

    Args:
        keyword: 搜索关键词
        skills_dir: 本地 skills 目录

    Returns:
        List[Dict]: 匹配的 skill 列表
    """
    remote_skills = fetch_skill_list()
    if not remote_skills:
        print("⚠️  远端暂无可用的 skill")
        return []

    local_skills = get_local_skills(skills_dir)
    keyword_lower = keyword.lower()

    matched = []
    for skill in remote_skills:
        name = skill.get("name", "").lower()
        description = skill.get("description", "").lower()
        if keyword_lower in name or keyword_lower in description:
            matched.append(skill)

    if not matched:
        print(f"🔍 未找到匹配 \"{keyword}\" 的 skill")
        return []

    print(f"\n🔍 搜索 \"{keyword}\" 的结果（共 {len(matched)} 个匹配）：")
    print("-" * 70)

    for i, skill in enumerate(matched, 1):
        name = skill.get("name", "unknown")
        description = skill.get("description", "无描述")
        available = skill.get("available", True)

        if name in local_skills:
            status = "✅ 已安装"
        elif not available:
            status = "🚫 不可用"
        else:
            status = "⬜ 未安装"

        print(f"  {i:>3}. {status}  {name}")
        print(f"       {description[:60]}{'...' if len(description) > 60 else ''}")
        if not available and skill.get("requires"):
            print(f"       ⚠️  缺失依赖: {skill['requires']}")

    print("-" * 70)
    return matched


def install_skill(skill_name: str, skills_dir: Path, force: bool = False) -> bool:
    """
    下载并安装指定的 skill

    Args:
        skill_name: skill 名称
        skills_dir: 本地 skills 目录
        force: 是否强制覆盖已存在的 skill

    Returns:
        bool: 安装是否成功
    """
    target_dir = skills_dir / skill_name

    # 检查本地是否已存在
    if target_dir.is_dir() and (target_dir / "SKILL.md").exists():
        if not force:
            print(f"⚠️  skill \"{skill_name}\" 已存在于: {target_dir}")
            print(f"   如需覆盖，请使用 --force 参数")

            # 交互式确认（非管道模式下）
            if sys.stdin.isatty():
                try:
                    answer = input("   是否覆盖？(y/N): ").strip().lower()
                    if answer not in ("y", "yes"):
                        print("   ⏭️  已跳过安装")
                        return False
                except (EOFError, KeyboardInterrupt):
                    print("\n   ⏭️  已跳过安装")
                    return False
            else:
                print("   ⏭️  非交互模式，跳过安装（请使用 --force 强制覆盖）")
                return False

        print(f"🔄 将覆盖已存在的 skill: {skill_name}")

    # 创建临时目录用于下载和解压
    with tempfile.TemporaryDirectory(prefix="skill_download_") as tmp_dir:
        tmp_path = Path(tmp_dir)
        zip_path = tmp_path / f"{skill_name}.zip"

        # 下载 zip 包
        if not download_skill_zip(skill_name, zip_path):
            return False

        # 验证 zip 文件
        if not zipfile.is_zipfile(zip_path):
            print(f"❌ 下载的文件不是有效的 zip 格式")
            return False

        # 解压到临时目录
        extract_dir = tmp_path / "extracted"
        try:
            print(f"📦 正在解压...")
            with zipfile.ZipFile(zip_path, 'r') as zf:
                # 安全检查：防止 zip slip 攻击
                for member in zf.namelist():
                    member_path = (extract_dir / member).resolve()
                    if not str(member_path).startswith(str(extract_dir.resolve())):
                        print(f"❌ 检测到不安全的 zip 路径: {member}")
                        return False

                # Windows 中文文件名兼容：zip 内文件名可能是 GBK/CP437 编码
                # 逐个解压并修正文件名编码
                for info in zf.infolist():
                    # 尝试修正中文文件名（ZIP 规范中非 UTF-8 标记的文件名默认 CP437）
                    if info.flag_bits & 0x800:
                        # bit 11 已设置，文件名已经是 UTF-8
                        fixed_name = info.filename
                    else:
                        # 尝试用 GBK 解码（Windows 中文系统常见）
                        try:
                            fixed_name = info.filename.encode('cp437').decode('gbk')
                        except (UnicodeDecodeError, UnicodeEncodeError):
                            try:
                                fixed_name = info.filename.encode('cp437').decode('utf-8')
                            except (UnicodeDecodeError, UnicodeEncodeError):
                                fixed_name = info.filename  # 保持原样

                    # 构建目标路径
                    target_path = extract_dir / fixed_name
                    target_path.parent.mkdir(parents=True, exist_ok=True)

                    if info.is_dir():
                        target_path.mkdir(parents=True, exist_ok=True)
                    else:
                        with zf.open(info) as src, open(target_path, 'wb') as dst:
                            shutil.copyfileobj(src, dst)
        except zipfile.BadZipFile:
            print("❌ zip 文件损坏")
            return False
        except Exception as e:
            print(f"❌ 解压失败: {e}")
            return False

        # 定位 skill 根目录（解压后可能有一层包装目录）
        skill_root = find_skill_root(extract_dir)
        if skill_root is None:
            print(f"❌ 解压后未找到有效的 skill（需要包含 SKILL.md）")
            # 列出解压内容帮助排查
            print(f"   解压内容:")
            for item in extract_dir.rglob("*"):
                rel = item.relative_to(extract_dir)
                print(f"   - {rel}")
            return False

        # 确保目标父目录存在
        skills_dir.mkdir(parents=True, exist_ok=True)

        # 如果目标已存在，先备份再删除
        if target_dir.exists():
            backup_dir = target_dir.with_suffix(".bak")
            if backup_dir.exists():
                shutil.rmtree(backup_dir)
            try:
                shutil.move(str(target_dir), str(backup_dir))
            except Exception as e:
                print(f"⚠️  备份已有 skill 失败: {e}")
                # 直接删除
                shutil.rmtree(target_dir, ignore_errors=True)

        # 移动到目标位置
        try:
            shutil.copytree(str(skill_root), str(target_dir))
        except Exception as e:
            print(f"❌ 安装失败: {e}")
            # 尝试恢复备份
            backup_dir = target_dir.with_suffix(".bak")
            if backup_dir.exists():
                shutil.move(str(backup_dir), str(target_dir))
                print("   已恢复原有 skill")
            return False

        # 清理备份
        backup_dir = target_dir.with_suffix(".bak")
        if backup_dir.exists():
            shutil.rmtree(backup_dir, ignore_errors=True)

    # 打印安装结果
    print(f"\n✅ skill \"{skill_name}\" 安装成功!")
    print(f"   📁 安装目录: {target_dir}")

    # 显示 skill 信息
    skill_md = target_dir / "SKILL.md"
    if skill_md.exists():
        content = skill_md.read_text(encoding="utf-8")
        # 提取前几行作为摘要
        lines = content.strip().split("\n")
        summary_lines = []
        for line in lines[:10]:
            if line.strip().startswith("---"):
                continue
            if line.strip():
                summary_lines.append(line.strip())
        if summary_lines:
            print(f"   📝 描述: {summary_lines[0][:80]}")

    # 列出安装的文件
    file_count = sum(1 for _ in target_dir.rglob("*") if _.is_file())
    dir_count = sum(1 for _ in target_dir.rglob("*") if _.is_dir())
    print(f"   📊 包含 {file_count} 个文件，{dir_count} 个目录")

    return True


def find_skill_root(extract_dir: Path) -> Optional[Path]:
    """
    在解压目录中查找 skill 根目录（包含 SKILL.md 的目录）

    zip 包可能有以下结构：
    1. 直接包含 SKILL.md（无包装目录）
    2. 有一层包装目录，如 skill_name/SKILL.md
    3. 有多层嵌套

    Args:
        extract_dir: 解压后的目录

    Returns:
        Optional[Path]: skill 根目录路径，未找到返回 None
    """
    # 情况 1：直接在解压目录下
    if (extract_dir / "SKILL.md").exists():
        return extract_dir

    # 情况 2：在子目录下（只查找前两层）
    for skill_md in extract_dir.rglob("SKILL.md"):
        # 取 SKILL.md 的父目录作为 skill 根目录
        depth = len(skill_md.relative_to(extract_dir).parts) - 1
        if depth <= 2:  # 最多两层嵌套
            return skill_md.parent

    return None


# ==================== 主流程 ====================

def main():
    parser = argparse.ArgumentParser(
        description="从远端搜索和下载 skill 到本地 .codebuddy/skills 目录",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 列出所有可用 skill
  python3 download_skill.py --list

  # 搜索 skill
  python3 download_skill.py --search "faas"

  # 安装 skill
  python3 download_skill.py --install my-skill

  # 强制覆盖安装
  python3 download_skill.py --install my-skill --force

  # 指定 API 地址
  python3 download_skill.py --list --base-url http://ai.px.woa.com

环境变量:
  WORKFLOW_BASE_URL    API 基础地址（默认: http://ai.px.woa.com）
  PROXY_USER           用户标识（默认: 当前系统用户）
        """
    )

    # 操作模式（互斥）
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--list", "-l", action="store_true",
                       help="列出远端所有可用的 skill")
    group.add_argument("--search", "-s", type=str, metavar="KEYWORD",
                       help="按关键词搜索 skill（模糊匹配名称和描述）")
    group.add_argument("--install", "-i", type=str, metavar="SKILL_NAME",
                       help="下载并安装指定的 skill")

    # 公共参数
    parser.add_argument("--skills-dir", type=str, default=None,
                        help=f"本地 skills 目录路径（默认: <项目根>/{DEFAULT_SKILLS_DIR}）")
    parser.add_argument("--base-url", type=str, default=None,
                        help=f"API 基础地址（覆盖环境变量，默认: {WORKFLOW_BASE_URL}）")
    parser.add_argument("--force", "-f", action="store_true",
                        help="强制覆盖已存在的 skill（无需确认）")

    args = parser.parse_args()

    # 覆盖 base URL
    if args.base_url:
        _override_base_url(args.base_url)

    # 获取本地 skills 目录
    skills_dir = get_skills_dir(args.skills_dir)

    # 执行操作
    if args.list:
        list_skills(skills_dir)

    elif args.search:
        search_skills(args.search, skills_dir)

    elif args.install:
        success = install_skill(args.install, skills_dir, force=args.force)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    try:
        main()
    except (UnicodeEncodeError, UnicodeDecodeError) as e:
        # 最后兜底：如果仍然出现编码错误，给出友好提示
        sys.stderr.write(f"[encoding error] {e}\n")
        sys.stderr.write("Tip: try running with 'set PYTHONIOENCODING=utf-8' or 'chcp 65001' on Windows.\n")
        sys.exit(1)
    except BrokenPipeError:
        # 管道中断（如 head/less 提前关闭），静默退出
        sys.exit(0)
