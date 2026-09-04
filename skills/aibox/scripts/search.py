"""
AIBox 资源查询脚本
支持查询 MCP Server、知识库、Workflow、CLI 工具、A2A Agent 等平台资源的列表和详情。

用法：
    # 查询 MCP Server 列表
    python3 search.py mcp

    # 按关键词搜索 MCP Server
    python3 search.py mcp --keyword "git"

    # 查询知识库列表
    python3 search.py knowledge

    # 搜索知识库内容（需指定知识库 project_id 和查询内容）
    python3 search.py knowledge --id a45f0b16 --query "如何部署"

    # 查询 Workflow 列表（即项目列表中 type=workflow 的项目）
    python3 search.py workflow

    # 按关键词搜索 Workflow
    python3 search.py workflow --keyword "翻译"

    # 获取指定 Workflow 详情（SKILL.md 内容）
    python3 search.py workflow --id fiw5c4xm

    # 查询 CLI 工具列表
    python3 search.py cli

    # 按关键词搜索 CLI 工具
    python3 search.py cli --keyword "idip"

    # 查看 CLI 工具详情（含下载地址）
    python3 search.py cli --id my-tool

    # 查询 A2A Agent 列表
    python3 search.py agent

    # 按关键词搜索 Agent
    python3 search.py agent --keyword "translate"

    # 查看 Agent 详情（含探测连通性）
    python3 search.py agent --id my-agent

    # 指定 API 地址
    python3 search.py mcp --base-url http://ai.px.woa.com
"""

import os
import sys
import io
import json
import argparse
import getpass
from typing import Optional, List, Dict, Any

# ==================== Windows 中文编码兼容 ====================

def _fix_encoding():
    """修复 Windows 下的中文/emoji 编码问题"""
    if sys.platform == "win32":
        os.environ.setdefault("PYTHONIOENCODING", "utf-8")
        try:
            os.system("chcp 65001 >nul 2>&1")
        except Exception:
            pass
        if hasattr(sys.stdout, "buffer"):
            sys.stdout = io.TextIOWrapper(
                sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True
            )
        if hasattr(sys.stderr, "buffer"):
            sys.stderr = io.TextIOWrapper(
                sys.stderr.buffer, encoding="utf-8", errors="replace", line_buffering=True
            )

_fix_encoding()

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import requests

# ==================== Token 读取（来自 auth.py） ====================
# 将 scripts 目录加入 sys.path，以便复用 auth.py 中的 token 读取逻辑
from pathlib import Path as _Path
_SCRIPTS_DIR = _Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

try:
    from auth import build_auth_headers as _build_auth_headers  # type: ignore
except Exception:
    def _build_auth_headers():
        return {}


def _auth_headers() -> dict:
    """读取本地存储的 X-AMS-TOKEN / TAI-TOKEN，不存在或为空则不返回该项"""
    try:
        return _build_auth_headers() or {}
    except Exception:
        return {}


# ==================== 配置 ====================

PROXY_USER = os.getenv("PROXY_USER", "") or getpass.getuser()
WORKFLOW_BASE_URL = os.getenv("WORKFLOW_BASE_URL", "http://ai.px.woa.com")

# 请求超时（秒）
REQUEST_TIMEOUT = 120


def _override_base_url(base_url: str):
    """运行时覆盖 API 基础地址"""
    global WORKFLOW_BASE_URL
    WORKFLOW_BASE_URL = base_url


def _headers() -> dict:
    """构建公共请求头（含 Content-Type、X-Proxy-User、本地保存的 token）"""
    h = {"Content-Type": "application/json"}
    if PROXY_USER:
        h["X-Proxy-User"] = PROXY_USER
    h.update(_auth_headers())
    return h


def _api_url(path: str) -> str:
    """拼接完整 API URL，自动附加 from=aibox 参数"""
    sep = "&" if "?" in path else "?"
    return f"{WORKFLOW_BASE_URL}{path}{sep}from=aibox"


# ==================== API 调用 ====================

def fetch_mcp_servers() -> List[Dict]:
    """
    获取 MCP Server 列表（自动翻页拉全）

    GET /api/mcp/servers?page=N&page_size=M
    响应: {"success": true, "servers": [...], "total": N}
    服务端默认单页只返回 30 条，需按 total 循环翻页取全。
    """
    url = _api_url("/api/mcp/servers")
    all_servers: List[Dict] = []
    page = 1
    page_size = 100
    try:
        while True:
            resp = requests.get(
                url, timeout=REQUEST_TIMEOUT, headers=_headers(),
                params={"page": page, "page_size": page_size},
            )
            resp.raise_for_status()
            data = resp.json()
            if not data.get("success"):
                print(f"❌ 接口返回失败: {data}")
                return all_servers
            servers = data.get("servers", [])
            all_servers.extend(servers)
            total = data.get("total", len(all_servers))
            if not servers or len(all_servers) >= total:
                break
            page += 1
        return all_servers
    except requests.exceptions.ConnectionError:
        print(f"❌ 连接失败，请检查服务是否可用: {WORKFLOW_BASE_URL}")
        return []
    except requests.exceptions.Timeout:
        print("❌ 请求超时，请稍后重试")
        return []
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP 错误: {e}")
        if e.response is not None:
            print(f"   服务端响应: {e.response.text.strip()}")
        return []
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return []


def fetch_knowledge_bases() -> List[Dict]:
    """
    获取知识库列表

    GET /api/knowledge
    响应: {"success": true, "knowledge_bases": [{name, description, owner_id, is_public, status, rag_collection, ...}]}
    """
    url = _api_url("/api/knowledge")
    try:
        resp = requests.get(url, timeout=REQUEST_TIMEOUT, headers=_headers())
        resp.raise_for_status()
        data = resp.json()
        if not data.get("success"):
            print(f"❌ 接口返回失败: {data}")
            return []
        return data.get("knowledge_bases", [])
    except requests.exceptions.ConnectionError:
        print(f"❌ 连接失败，请检查服务是否可用: {WORKFLOW_BASE_URL}")
        return []
    except requests.exceptions.Timeout:
        print("❌ 请求超时，请稍后重试")
        return []
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP 错误: {e}")
        if e.response is not None:
            print(f"   服务端响应: {e.response.text.strip()}")
        return []
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return []


def search_knowledge_base(project_id: str, query: str, limit: int = 5) -> List[Dict]:
    """
    检索知识库内容

    POST /api/knowledge/{project_id}/search
    请求体: {"query": "...", "limit": 5}
    响应: {"success": true, "results": [{text, score, source, chunk_index}]}
    """
    url = _api_url(f"/api/knowledge/{project_id}/search")
    payload = {"query": query, "limit": limit}
    try:
        resp = requests.post(url, json=payload, timeout=REQUEST_TIMEOUT, headers=_headers())
        resp.raise_for_status()
        data = resp.json()
        if not data.get("success"):
            print(f"❌ 接口返回失败: {data}")
            return []
        return data.get("results", [])
    except requests.exceptions.HTTPError as e:
        if resp.status_code == 404:
            print(f"❌ 知识库不存在: {project_id}")
        elif resp.status_code == 400:
            print(f"❌ 知识库尚未配置 RAG 集合: {project_id}")
        else:
            print(f"❌ HTTP 错误: {e}")
            if e.response is not None:
                print(f"   服务端响应: {e.response.text.strip()}")
        return []
    except requests.exceptions.ConnectionError:
        print(f"❌ 连接失败，请检查服务是否可用: {WORKFLOW_BASE_URL}")
        return []
    except requests.exceptions.Timeout:
        print("❌ 请求超时，请稍后重试")
        return []
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return []


def fetch_workflow_list(keyword: Optional[str] = None) -> List[Dict]:
    """
    获取 Workflow 列表（通过项目列表接口，过滤 type=workflow，自动翻页拉全）

    POST /api/myclaw/list
    请求体: {"type": ["workflow"], "keyword": "...", "page": N, "page_size": M}
    响应: {"success": true, "projects": [{id, name, description, type, ...}], "total": N}
    """
    url = _api_url("/api/myclaw/list")
    all_projects: List[Dict] = []
    page = 1
    page_size = 100
    try:
        while True:
            payload: Dict[str, Any] = {"type": ["workflow"], "page": page, "page_size": page_size}
            if keyword:
                payload["keyword"] = keyword
            resp = requests.post(url, json=payload, timeout=REQUEST_TIMEOUT, headers=_headers())
            resp.raise_for_status()
            data = resp.json()
            if not data.get("success"):
                print(f"❌ 接口返回失败: {data}")
                return all_projects
            projects = data.get("projects", [])
            all_projects.extend(projects)
            total = data.get("total", len(all_projects))
            if not projects or len(all_projects) >= total:
                break
            page += 1
        return all_projects
    except requests.exceptions.ConnectionError:
        print(f"❌ 连接失败，请检查服务是否可用: {WORKFLOW_BASE_URL}")
        return []
    except requests.exceptions.Timeout:
        print("❌ 请求超时，请稍后重试")
        return []
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP 错误: {e}")
        if e.response is not None:
            print(f"   服务端响应: {e.response.text.strip()}")
        return []
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return []


def fetch_workflow_detail(project_id: str) -> Optional[Dict]:
    """
    获取指定 Workflow 的详情（包含 SKILL.md 内容）

    GET /api/workflow/{project_id}
    响应: {"success": true, "workflow": {...}, "workflow_skillmd": "...", "project": {id, name, description}}
    """
    url = _api_url(f"/api/workflow/{project_id}")
    try:
        resp = requests.get(url, timeout=REQUEST_TIMEOUT, headers=_headers())
        resp.raise_for_status()
        data = resp.json()
        if not data.get("success"):
            print(f"❌ 接口返回失败: {data}")
            return None
        return data
    except requests.exceptions.HTTPError as e:
        if resp.status_code == 404:
            print(f"❌ 项目未找到: {project_id}")
        else:
            print(f"❌ HTTP 错误: {e}")
            if e.response is not None:
                print(f"   服务端响应: {e.response.text.strip()}")
        return None
    except requests.exceptions.ConnectionError:
        print(f"❌ 连接失败，请检查服务是否可用: {WORKFLOW_BASE_URL}")
        return None
    except requests.exceptions.Timeout:
        print("❌ 请求超时，请稍后重试")
        return None
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None


def fetch_cli_tools(keyword: Optional[str] = None) -> List[Dict]:
    """
    获取 CLI 工具列表

    GET /api/cli/list?search=...
    响应: {"success": true, "tools": [{name, description, version, platforms, file_count, ...}], "total": N}
    """
    params = ""
    if keyword:
        params = f"?search={keyword}"
    url = _api_url(f"/api/cli/list{params}")
    try:
        resp = requests.get(url, timeout=REQUEST_TIMEOUT, headers=_headers())
        resp.raise_for_status()
        data = resp.json()
        if not data.get("success"):
            print(f"❌ 接口返回失败: {data}")
            return []
        return data.get("tools", [])
    except requests.exceptions.ConnectionError:
        print(f"❌ 连接失败，请检查服务是否可用: {WORKFLOW_BASE_URL}")
        return []
    except requests.exceptions.Timeout:
        print("❌ 请求超时，请稍后重试")
        return []
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP 错误: {e}")
        if e.response is not None:
            print(f"   服务端响应: {e.response.text.strip()}")
        return []
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return []


def fetch_cli_tool_detail(tool_name: str) -> Optional[Dict]:
    """
    获取 CLI 工具详情

    GET /api/cli/detail/{tool_name}
    响应: {"success": true, "tool": {name, description, version, author, platforms, files, downloads, ...}}
    """
    url = _api_url(f"/api/cli/detail/{tool_name}")
    try:
        resp = requests.get(url, timeout=REQUEST_TIMEOUT, headers=_headers())
        resp.raise_for_status()
        data = resp.json()
        if not data.get("success"):
            print(f"❌ 接口返回失败: {data}")
            return None
        return data.get("tool")
    except requests.exceptions.HTTPError as e:
        if resp.status_code == 404:
            print(f"❌ CLI 工具不存在: {tool_name}")
        else:
            print(f"❌ HTTP 错误: {e}")
            if e.response is not None:
                print(f"   服务端响应: {e.response.text.strip()}")
        return None
    except requests.exceptions.ConnectionError:
        print(f"❌ 连接失败，请检查服务是否可用: {WORKFLOW_BASE_URL}")
        return None
    except requests.exceptions.Timeout:
        print("❌ 请求超时，请稍后重试")
        return None
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None


def fetch_a2a_agents() -> List[Dict]:
    """
    获取 A2A Agent 列表

    GET /api/a2a/agents
    响应: {"success": true, "agents": [{name, description, base_url, protocol, status, skills, ...}]}
    """
    url = _api_url("/api/a2a/agents")
    try:
        resp = requests.get(url, timeout=REQUEST_TIMEOUT, headers=_headers())
        resp.raise_for_status()
        data = resp.json()
        if not data.get("success"):
            print(f"❌ 接口返回失败: {data}")
            return []
        return data.get("agents", [])
    except requests.exceptions.ConnectionError:
        print(f"❌ 连接失败，请检查服务是否可用: {WORKFLOW_BASE_URL}")
        return []
    except requests.exceptions.Timeout:
        print("❌ 请求超时，请稍后重试")
        return []
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP 错误: {e}")
        if e.response is not None:
            print(f"   服务端响应: {e.response.text.strip()}")
        return []
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return []


def fetch_a2a_agent_detail(name: str) -> Optional[Dict]:
    """
    探测 A2A Agent 详情（通过 probe 接口获取 Agent Card）

    POST /api/a2a/agents/{name}/probe
    响应: {"success": true, "agent_name": "...", "description": "...", "version": "...", "skills_count": N, "capabilities": {...}}
    """
    # 先从列表中找到 agent 的基本信息
    agents = fetch_a2a_agents()
    agent = None
    for a in agents:
        if a.get("name") == name:
            agent = a
            break

    if not agent:
        print(f"❌ Agent '{name}' 不存在")
        return None

    # 尝试 probe 获取实时状态
    url = _api_url(f"/api/a2a/agents/{name}/probe")
    probe_result = None
    try:
        resp = requests.post(url, json={}, timeout=REQUEST_TIMEOUT, headers=_headers())
        if resp.status_code == 200:
            data = resp.json()
            if data.get("success"):
                probe_result = data
    except Exception:
        pass  # probe 失败不阻塞，仍返回基本信息

    return {"agent": agent, "probe": probe_result}


# ==================== 展示函数 ====================

def _truncate(text: str, max_len: int = 60) -> str:
    """截断文本并添加省略号"""
    text = (text or "").replace("\n", " ").strip()
    return text[:max_len] + "..." if len(text) > max_len else text


def display_mcp_servers(servers: List[Dict], keyword: Optional[str] = None):
    """展示 MCP Server 列表"""
    if keyword:
        kw = keyword.lower()
        servers = [s for s in servers
                   if kw in s.get("name", "").lower()
                   or kw in s.get("description", "").lower()]

    if not servers:
        print("⚠️  未找到匹配的 MCP Server")
        return

    print(f"\n🔌 MCP Server 列表（共 {len(servers)} 个）：")
    print("-" * 80)
    for i, s in enumerate(servers, 1):
        name = s.get("name", "unknown")
        desc = _truncate(s.get("description", ""))
        status = s.get("status", "")
        stype = s.get("type", "")
        tools = s.get("tools", [])
        tool_count = len(tools) if isinstance(tools, list) else 0

        status_icon = "✅" if status == "available" else "⚠️"
        print(f"  {i:>3}. {status_icon} {name}")
        if desc:
            print(f"       📝 {desc}")
        info_parts = []
        if stype:
            info_parts.append(f"类型: {stype}")
        if tool_count:
            info_parts.append(f"工具数: {tool_count}")
        if s.get("created_by"):
            info_parts.append(f"创建者: {s['created_by']}")
        if info_parts:
            print(f"       {' | '.join(info_parts)}")
    print("-" * 80)


def display_knowledge_bases(kbs: List[Dict], keyword: Optional[str] = None):
    """展示知识库列表"""
    if keyword:
        kw = keyword.lower()
        kbs = [kb for kb in kbs
               if kw in kb.get("name", "").lower()
               or kw in kb.get("description", "").lower()]

    if not kbs:
        print("⚠️  未找到匹配的知识库")
        return

    print(f"\n📚 知识库列表（共 {len(kbs)} 个）：")
    print("-" * 80)
    for i, kb in enumerate(kbs, 1):
        name = kb.get("name", "unknown")
        desc = _truncate(kb.get("description", ""))
        owner = kb.get("owner_id", "")
        is_public = "🌍 公开" if kb.get("is_public") else "🔒 私有"
        status = kb.get("status", "")
        project_id = kb.get("project_id", "")

        print(f"  {i:>3}. {name}  [{is_public}]")
        if desc:
            print(f"       📝 {desc}")
        info_parts = []
        if project_id:
            info_parts.append(f"ID: {project_id}")
        if owner:
            info_parts.append(f"创建者: {owner}")
        if status:
            info_parts.append(f"状态: {status}")
        if info_parts:
            print(f"       {' | '.join(info_parts)}")
    print("-" * 80)
    print("💡 使用 --id <project_id> --query <关键词> 搜索知识库内容")


def display_knowledge_search_results(results: List[Dict], project_id: str, query: str):
    """展示知识库搜索结果"""
    if not results:
        print(f"⚠️  未找到与 \"{query}\" 相关的结果")
        return

    print(f"\n🔍 知识库 [{project_id}] 搜索 \"{query}\" 的结果（共 {len(results)} 条）：")
    print("=" * 80)
    for i, r in enumerate(results, 1):
        text = (r.get("text", "") or "").strip()
        score = r.get("score")
        source = r.get("source", "")

        score_str = f"  (相关度: {score:.4f})" if score is not None else ""
        print(f"\n--- 结果 {i}{score_str} ---")
        if source:
            print(f"📄 来源: {source}")
        print(text)
    print("\n" + "=" * 80)


def display_workflow_list(workflows: List[Dict]):
    """展示 Workflow 列表"""
    if not workflows:
        print("⚠️  未找到 Workflow")
        return

    print(f"\n⚙️  Workflow 列表（共 {len(workflows)} 个）：")
    print("-" * 80)
    for i, w in enumerate(workflows, 1):
        project_id = w.get("id", "")
        name = w.get("name", "unknown")
        desc = _truncate(w.get("description", ""))
        owner = w.get("owner_id", "")
        updated = w.get("updated_at", "")

        print(f"  {i:>3}. {name}")
        if desc:
            print(f"       📝 {desc}")
        info_parts = []
        if project_id:
            info_parts.append(f"ID: {project_id}")
        if owner:
            info_parts.append(f"创建者: {owner}")
        if updated:
            info_parts.append(f"更新: {updated}")
        if info_parts:
            print(f"       {' | '.join(info_parts)}")
    print("-" * 80)
    print("💡 使用 --id <project_id> 查看 Workflow 详情")


def display_workflow_detail(data: Dict):
    """展示 Workflow 详情"""
    project = data.get("project", {})
    skillmd = data.get("workflow_skillmd", "")

    print(f"\n⚙️  Workflow 详情")
    print("=" * 80)
    print(f"  📛 名称: {project.get('name', 'unknown')}")
    print(f"  🆔 ID:   {project.get('id', '')}")
    if project.get("description"):
        print(f"  📝 描述: {project['description']}")
    print("-" * 80)

    if skillmd:
        print("\n📄 SKILL.md 内容:\n")
        print(skillmd)
    else:
        print("\n⚠️  该 Workflow 暂无 SKILL.md 内容")

    print("\n" + "=" * 80)


def display_cli_tools(tools: List[Dict], keyword: Optional[str] = None):
    """展示 CLI 工具列表"""
    if keyword:
        kw = keyword.lower()
        tools = [t for t in tools
                 if kw in t.get("name", "").lower()
                 or kw in t.get("description", "").lower()]

    if not tools:
        print("⚠️  未找到匹配的 CLI 工具")
        return

    print(f"\n🔧 CLI 工具列表（共 {len(tools)} 个）：")
    print("-" * 80)
    for i, t in enumerate(tools, 1):
        name = t.get("name", "unknown")
        desc = _truncate(t.get("description", ""))
        version = t.get("version", "")
        platforms = t.get("platforms", [])
        file_count = t.get("file_count", 0)

        print(f"  {i:>3}. 🔧 {name}")
        if desc:
            print(f"       📝 {desc}")
        info_parts = []
        if version:
            info_parts.append(f"版本: {version}")
        if platforms:
            info_parts.append(f"平台: {', '.join(platforms)}")
        if file_count:
            info_parts.append(f"文件数: {file_count}")
        if t.get("created_by"):
            info_parts.append(f"创建者: {t['created_by']}")
        if info_parts:
            print(f"       {' | '.join(info_parts)}")
    print("-" * 80)
    print("💡 使用 --id <tool_name> 查看 CLI 工具详情")


def display_cli_tool_detail(tool: Dict):
    """展示 CLI 工具详情"""
    print(f"\n🔧 CLI 工具详情")
    print("=" * 80)
    print(f"  📛 名称:   {tool.get('name', 'unknown')}")
    if tool.get("version"):
        print(f"  🏷️  版本:   {tool['version']}")
    if tool.get("author"):
        print(f"  👤 作者:   {tool['author']}")
    if tool.get("description"):
        print(f"  📝 描述:   {tool['description']}")
    if tool.get("platforms"):
        print(f"  💻 平台:   {', '.join(tool['platforms'])}")
    if tool.get("command"):
        print(f"  ⚡ 命令:   {tool['command']}")

    # 下载地址
    downloads = tool.get("downloads", {})
    if downloads:
        print("\n  📥 下载地址:")
        platform_downloads = downloads.get("platforms", {})
        for plat, info in platform_downloads.items():
            url = info.get("url", "")
            fc = info.get("file_count", 0)
            print(f"     • {plat}: {WORKFLOW_BASE_URL}{url}  ({fc} 个文件)")
        generic = downloads.get("generic")
        if generic:
            url = generic.get("url", "")
            fc = generic.get("file_count", 0)
            print(f"     • 通用: {WORKFLOW_BASE_URL}{url}  ({fc} 个文件)")

    # 文件列表
    files = tool.get("files", [])
    if files:
        print(f"\n  📂 文件列表（共 {tool.get('file_count', len(files))} 个）:")
        for f in files[:20]:
            if isinstance(f, dict):
                path = f.get("path", "")
                size = f.get("size", 0)
                size_str = f"  ({_format_size(size)})" if size else ""
                print(f"     • {path}{size_str}")
            else:
                print(f"     • {f}")
        if len(files) > 20:
            print(f"     ... 等共 {tool.get('file_count', len(files))} 个文件")

    # README
    readme = tool.get("readme", "")
    if readme:
        print("\n" + "-" * 80)
        print("📄 README.md:\n")
        print(readme)

    print("\n" + "=" * 80)


def display_a2a_agents(agents: List[Dict], keyword: Optional[str] = None):
    """展示 A2A Agent 列表"""
    if keyword:
        kw = keyword.lower()
        agents = [a for a in agents
                  if kw in a.get("name", "").lower()
                  or kw in a.get("description", "").lower()]

    if not agents:
        print("⚠️  未找到匹配的 A2A Agent")
        return

    print(f"\n🤖 A2A Agent 列表（共 {len(agents)} 个）：")
    print("-" * 80)
    for i, a in enumerate(agents, 1):
        name = a.get("name", "unknown")
        desc = _truncate(a.get("description", ""))
        protocol = a.get("protocol", "A2A")
        status = a.get("status", "")
        base_url = a.get("base_url", "")
        skills = a.get("skills", [])

        status_icon = "✅" if status == "online" else "⚠️"
        print(f"  {i:>3}. {status_icon} {name}")
        if desc:
            print(f"       📝 {desc}")
        info_parts = []
        if protocol:
            info_parts.append(f"协议: {protocol}")
        if base_url:
            info_parts.append(f"地址: {_truncate(base_url, 40)}")
        if skills:
            info_parts.append(f"技能数: {len(skills)}")
        if a.get("created_by"):
            info_parts.append(f"创建者: {a['created_by']}")
        if info_parts:
            print(f"       {' | '.join(info_parts)}")
    print("-" * 80)
    print("💡 使用 --id <agent_name> 查看 Agent 详情（探测连通性）")


def display_a2a_agent_detail(data: Dict):
    """展示 A2A Agent 详情"""
    agent = data.get("agent", {})
    probe = data.get("probe")

    print(f"\n🤖 A2A Agent 详情")
    print("=" * 80)
    print(f"  📛 名称:     {agent.get('name', 'unknown')}")
    if agent.get("description"):
        print(f"  📝 描述:     {agent['description']}")
    if agent.get("protocol"):
        print(f"  🔗 协议:     {agent['protocol']}")
    if agent.get("base_url"):
        print(f"  🌐 地址:     {agent['base_url']}")
    if agent.get("status"):
        status = agent['status']
        icon = "✅" if status == "online" else "⚠️"
        print(f"  📊 状态:     {icon} {status}")
    if agent.get("skills"):
        print(f"  🎯 技能:     {', '.join(agent['skills'])}")
    if agent.get("created_by"):
        print(f"  👤 创建者:   {agent['created_by']}")

    # Probe 结果
    if probe:
        print("\n  🔍 实时探测结果:")
        print(f"     ✅ {probe.get('message', '连接成功')}")
        if probe.get("version"):
            print(f"     版本: {probe['version']}")
        if probe.get("skills_count"):
            print(f"     技能数: {probe['skills_count']}")
        caps = probe.get("capabilities", {})
        if caps:
            print(f"     能力: {json.dumps(caps, ensure_ascii=False)}")
    else:
        print("\n  ⚠️  实时探测未成功（Agent 可能离线或不可达）")

    print("\n" + "=" * 80)


def _format_size(size_bytes: int) -> str:
    """格式化文件大小"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"

def main():
    parser = argparse.ArgumentParser(
        description="查询 AIBox 平台资源（MCP Server、知识库、Workflow、CLI 工具、A2A Agent）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 查询 MCP Server 列表
  python3 search.py mcp

  # 按关键词搜索 MCP Server
  python3 search.py mcp --keyword "git"

  # 查询知识库列表
  python3 search.py knowledge

  # 搜索知识库内容
  python3 search.py knowledge --id a45f0b16 --query "如何部署"

  # 查询 Workflow 列表
  python3 search.py workflow

  # 查看 Workflow 详情
  python3 search.py workflow --id fiw5c4xm

  # 查询 CLI 工具列表
  python3 search.py cli

  # 按关键词搜索 CLI 工具
  python3 search.py cli --keyword "idip"

  # 查看 CLI 工具详情
  python3 search.py cli --id my-tool

  # 查询 A2A Agent 列表
  python3 search.py agent

  # 按关键词搜索 Agent
  python3 search.py agent --keyword "translate"

  # 查看 Agent 详情（含探测）
  python3 search.py agent --id my-agent

环境变量:
  WORKFLOW_BASE_URL    API 基础地址（默认: http://ai.px.woa.com）
  PROXY_USER           用户标识（默认: 当前系统用户）
        """
    )

    parser.add_argument("resource", choices=["mcp", "knowledge", "workflow", "cli", "agent"],
                        help="要查询的资源类型: mcp / knowledge / workflow / cli / agent")
    parser.add_argument("--id", type=str, default=None,
                        help="资源 ID（知识库 project_id / Workflow project_id / CLI 工具名 / Agent 名称）")
    parser.add_argument("--query", "-q", type=str, default=None,
                        help="搜索知识库时的查询内容")
    parser.add_argument("--keyword", "-k", type=str, default=None,
                        help="按关键词过滤列表结果（名称或描述模糊匹配）")
    parser.add_argument("--limit", type=int, default=5,
                        help="知识库搜索返回的最大结果数（默认: 5）")
    parser.add_argument("--base-url", type=str, default=None,
                        help=f"API 基础地址（覆盖环境变量，默认: {WORKFLOW_BASE_URL}）")
    parser.add_argument("--json", action="store_true",
                        help="以 JSON 格式输出原始数据")

    args = parser.parse_args()

    # 覆盖 base URL
    if args.base_url:
        _override_base_url(args.base_url)

    # ── MCP Server ──
    if args.resource == "mcp":
        print(f"🌐 正在从 {WORKFLOW_BASE_URL} 查询 MCP Server ...", file=sys.stderr)
        servers = fetch_mcp_servers()
        if args.json:
            print(json.dumps(servers, ensure_ascii=False, indent=2))
        else:
            display_mcp_servers(servers, keyword=args.keyword)

    # ── 知识库 ──
    elif args.resource == "knowledge":
        if args.id and args.query:
            # 搜索知识库内容
            print(f"🌐 正在从 {WORKFLOW_BASE_URL} 搜索知识库 [{args.id}] ...", file=sys.stderr)
            results = search_knowledge_base(args.id, args.query, limit=args.limit)
            if args.json:
                print(json.dumps(results, ensure_ascii=False, indent=2))
            else:
                display_knowledge_search_results(results, args.id, args.query)
        elif args.id and not args.query:
            print("❌ 搜索知识库需要同时指定 --id 和 --query 参数")
            print("   示例: python3 search.py knowledge --id a45f0b16 --query \"如何部署\"")
            sys.exit(1)
        else:
            # 列出知识库
            print(f"🌐 正在从 {WORKFLOW_BASE_URL} 查询知识库列表 ...", file=sys.stderr)
            kbs = fetch_knowledge_bases()
            if args.json:
                print(json.dumps(kbs, ensure_ascii=False, indent=2))
            else:
                display_knowledge_bases(kbs, keyword=args.keyword)

    # ── Workflow ──
    elif args.resource == "workflow":
        if args.id:
            # 获取 Workflow 详情
            print(f"🌐 正在从 {WORKFLOW_BASE_URL} 获取 Workflow [{args.id}] 详情 ...", file=sys.stderr)
            detail = fetch_workflow_detail(args.id)
            if detail:
                if args.json:
                    print(json.dumps(detail, ensure_ascii=False, indent=2))
                else:
                    display_workflow_detail(detail)
        else:
            # 列出 Workflow
            print(f"🌐 正在从 {WORKFLOW_BASE_URL} 查询 Workflow 列表 ...", file=sys.stderr)
            workflows = fetch_workflow_list(keyword=args.keyword)
            if args.json:
                print(json.dumps(workflows, ensure_ascii=False, indent=2))
            else:
                display_workflow_list(workflows)

    # ── CLI 工具 ──
    elif args.resource == "cli":
        if args.id:
            # 获取 CLI 工具详情
            print(f"🌐 正在从 {WORKFLOW_BASE_URL} 获取 CLI 工具 [{args.id}] 详情 ...", file=sys.stderr)
            tool = fetch_cli_tool_detail(args.id)
            if tool:
                if args.json:
                    print(json.dumps(tool, ensure_ascii=False, indent=2))
                else:
                    display_cli_tool_detail(tool)
        else:
            # 列出 CLI 工具
            print(f"🌐 正在从 {WORKFLOW_BASE_URL} 查询 CLI 工具列表 ...", file=sys.stderr)
            tools = fetch_cli_tools(keyword=args.keyword)
            if args.json:
                print(json.dumps(tools, ensure_ascii=False, indent=2))
            else:
                display_cli_tools(tools, keyword=args.keyword)

    # ── A2A Agent ──
    elif args.resource == "agent":
        if args.id:
            # 获取 Agent 详情（含探测）
            print(f"🌐 正在从 {WORKFLOW_BASE_URL} 获取 Agent [{args.id}] 详情 ...", file=sys.stderr)
            detail = fetch_a2a_agent_detail(args.id)
            if detail:
                if args.json:
                    print(json.dumps(detail, ensure_ascii=False, indent=2))
                else:
                    display_a2a_agent_detail(detail)
        else:
            # 列出 Agent
            print(f"🌐 正在从 {WORKFLOW_BASE_URL} 查询 A2A Agent 列表 ...", file=sys.stderr)
            agents = fetch_a2a_agents()
            if args.json:
                print(json.dumps(agents, ensure_ascii=False, indent=2))
            else:
                display_a2a_agents(agents, keyword=args.keyword)


if __name__ == "__main__":
    try:
        main()
    except (UnicodeEncodeError, UnicodeDecodeError) as e:
        sys.stderr.write(f"[encoding error] {e}\n")
        sys.stderr.write("Tip: try running with 'set PYTHONIOENCODING=utf-8' or 'chcp 65001' on Windows.\n")
        sys.exit(1)
    except BrokenPipeError:
        sys.exit(0)
    except KeyboardInterrupt:
        print("\n⏹️  已取消")
        sys.exit(0)
