# -*- coding: utf-8 -*-
"""
unified-kb-search.py — 统一知识库检索工具

同时检索 Team-KB 和游戏设计知识库，合并结果输出。

用法:
  python unified-kb-search.py search "关键词1 关键词2"
  python unified-kb-search.py search --tags "标签1,标签2"
  python unified-kb-search.py search "关键词" --category "系统设计"

输出格式:
  默认: Markdown 格式
  --json: JSON 格式（供程序调用）
"""

from __future__ import annotations
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

# Windows UTF-8 兼容
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')


# ─────────────────────────────────────
# 脚本路径解析
# ─────────────────────────────────────

def _get_script_dir() -> str:
    """获取当前脚本所在目录"""
    return os.path.dirname(os.path.abspath(__file__))


def _get_team_kb_script() -> str:
    """获取 Team-KB 检索脚本路径"""
    # 优先使用 mygamedesignhelper 内的副本
    local_script = os.path.join(_get_script_dir(), "kb-search.py")
    if os.path.isfile(local_script):
        return local_script

    # 回退到 team-kb 技能目录
    team_kb_script = os.path.expanduser("~/.workbuddy/skills/team-kb/scripts/kb-search.py")
    if os.path.isfile(team_kb_script):
        return team_kb_script

    return None


def _get_game_kb_script() -> str:
    """获取游戏设计知识库检索脚本路径"""
    return os.path.join(_get_script_dir(), "game-kb-search.py")


# ─────────────────────────────────────
# 执行子脚本
# ─────────────────────────────────────

def _run_search_script(script_path: str, args: list[str], timeout: int = 30) -> list[dict]:
    """执行检索脚本并解析 JSON 输出"""
    if not script_path or not os.path.isfile(script_path):
        return []

    cmd = [sys.executable, script_path, "--json"] + args

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=timeout
        )

        if result.returncode != 0:
            return []

        # 解析 JSON 输出
        try:
            data = json.loads(result.stdout)
            return data if isinstance(data, list) else []
        except json.JSONDecodeError:
            return []

    except (subprocess.TimeoutExpired, OSError):
        return []


# ─────────────────────────────────────
# 结果合并与排序
# ─────────────────────────────────────

def _merge_results(team_kb_results: list[dict], game_kb_results: list[dict], top: int) -> list[dict]:
    """合并两个知识库的搜索结果并排序"""
    all_results = []

    # Team-KB 结果
    for r in team_kb_results:
        r["source"] = "team-kb"
        all_results.append(r)

    # 游戏设计知识库结果
    for r in game_kb_results:
        r["source"] = "game-design-kb"
        all_results.append(r)

    # 按得分排序
    all_results.sort(key=lambda x: x.get("score", 0), reverse=True)

    return all_results[:top]


# ─────────────────────────────────────
# 输出格式化
# ─────────────────────────────────────

def _format_markdown_output(results: list[dict], query: str, tags: str, category: str):
    """Markdown 格式输出"""
    print("## 统一知识库查询结果\n")

    # 查询信息
    parts = []
    if query:
        parts.append(f"关键词: {query}")
    if tags:
        parts.append(f"标签: {tags}")
    if category:
        parts.append(f"分类: {category}")
    query_str = " | ".join(parts) if parts else "(空查询)"
    print(f"查询：{query_str}")
    print(f"找到 {len(results)} 个匹配知识点{'：' if results else '。'}\n")

    if not results:
        print("未找到相关知识点。")
        return

    # 按来源分组统计
    team_kb_count = sum(1 for r in results if r.get("source") == "team-kb")
    game_kb_count = sum(1 for r in results if r.get("source") == "game-design-kb")

    if team_kb_count > 0 and game_kb_count > 0:
        print(f"📊 来源分布：Team-KB ({team_kb_count}) + 游戏设计知识库 ({game_kb_count})\n")

    # 输出结果
    for i, result in enumerate(results, 1):
        source = result.get("source", "unknown")
        source_icon = "📚" if source == "team-kb" else "🎮"
        source_name = "Team-KB" if source == "team-kb" else "游戏设计知识库"
        title = result.get("title", "(无标题)")
        score = result.get("score", 0)
        summary = result.get("summary", "")
        tags_list = result.get("tags", [])
        file_path = result.get("file", "")

        print(f"### {i}. {source_icon} {title} [相关度: {score:.2f}]")
        print(f"- **来源**: {source_name}")

        if tags_list:
            print(f"- **标签**: {', '.join(tags_list)}")

        # Team-KB 特有字段
        if source == "team-kb":
            category_val = result.get("category", "")
            if category_val:
                print(f"- **分类**: {category_val}")
            status = result.get("status", "")
            if status:
                status_icon = "✅" if status in ("confirmed", "approved") else "📝"
                print(f"- **状态**: {status_icon} {status}")

        # 游戏设计知识库特有字段
        if source == "game-design-kb":
            ability = result.get("ability", "")
            if ability:
                print(f"- **能力**: {ability}")
            rating = result.get("rating", "")
            if rating:
                print(f"- **评级**: {rating}")

        if summary:
            print(f"- **摘要**: {summary}")
        if file_path:
            print(f"- **文件**: `{file_path}`")
        print()


def _format_json_output(results: list[dict]):
    """JSON 格式输出"""
    print(json.dumps(results, ensure_ascii=False, indent=2))


# ─────────────────────────────────────
# search 命令
# ─────────────────────────────────────

def cmd_search(args):
    """执行统一搜索"""
    # 构建传递给子脚本的参数
    search_args = []
    if args.query:
        search_args.append(args.query)
    if args.tags:
        search_args.extend(["--tags", args.tags])
    if args.category:
        search_args.extend(["--category", args.category])
    search_args.extend(["--top", str(args.top)])

    # 并行执行两个知识库的检索
    team_kb_script = _get_team_kb_script()
    game_kb_script = _get_game_kb_script()

    team_kb_results = _run_search_script(team_kb_script, ["search"] + search_args) if team_kb_script else []
    game_kb_results = _run_search_script(game_kb_script, ["search"] + search_args) if game_kb_script else []

    # 合并结果
    merged = _merge_results(team_kb_results, game_kb_results, args.top)

    # 输出
    if args.json:
        _format_json_output(merged)
    else:
        _format_markdown_output(merged, args.query, args.tags, args.category)


# ─────────────────────────────────────
# CLI 入口
# ─────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="统一知识库检索工具（同时检索 Team-KB 和游戏设计知识库）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--json", action="store_true", help="JSON 输出模式")

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # search
    sp_search = subparsers.add_parser("search", help="搜索知识点")
    sp_search.add_argument("query", nargs="?", default="", help="搜索关键词")
    sp_search.add_argument("--tags", default="", help="标签过滤（逗号分隔）")
    sp_search.add_argument("--category", default="", help="分类过滤")
    sp_search.add_argument("--top", type=int, default=10, help="返回结果数量（默认10）")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "search":
        cmd_search(args)


if __name__ == "__main__":
    main()
