# -*- coding: utf-8 -*-
"""
kb-search.py — 团队知识库 CLI 检索工具

用法:
  python kb-search.py search "关键词1 关键词2"
  python kb-search.py search --tags "标签1,标签2"
  python kb-search.py search "关键词" --category "分类名"
  python kb-search.py search "关键词" --top 10
  python kb-search.py get KB-001
  python kb-search.py get KB-001 --full

知识库路径解析优先级:
  1. --kb-path 命令行参数
  2. ~/.workbuddy/skills/team-kb/.kb-config.json 的 repo_path
  3. 环境变量 TEAM_KB_PATH
"""

from __future__ import annotations
import argparse
import json
import os
import re
import sys

# Windows UTF-8 兼容
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')


# ─────────────────────────────────────
# 路径解析
# ─────────────────────────────────────

def _resolve_kb_path(cli_path: str | None = None) -> str | None:
    """按优先级解析知识库仓库路径"""
    # 1. 命令行参数
    if cli_path:
        p = os.path.expanduser(cli_path)
        if os.path.isdir(p):
            return p
        return None

    # 2. .kb-config.json
    config_path = os.path.expanduser("~/.workbuddy/skills/team-kb/.kb-config.json")
    if os.path.isfile(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
            repo = cfg.get("repo_path", "")
            if repo:
                p = os.path.expanduser(repo)
                if os.path.isdir(p):
                    return p
        except (json.JSONDecodeError, OSError):
            pass

    # 3. 环境变量
    env_path = os.environ.get("TEAM_KB_PATH", "")
    if env_path:
        p = os.path.expanduser(env_path)
        if os.path.isdir(p):
            return p

    return None


def _load_index(kb_path: str) -> list[dict]:
    """加载全量索引"""
    index_file = os.path.join(kb_path, "_index", "all-knowledge.json")
    if not os.path.isfile(index_file):
        return []
    try:
        with open(index_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


# ─────────────────────────────────────
# 相关度计算
# ─────────────────────────────────────

def _score_entry(entry: dict, keywords: list[str], tags_filter: list[str], category_filter: str) -> float:
    """计算知识点与查询的相关度得分 (0~1)"""
    score = 0.0
    title = (entry.get("title") or "").lower()
    summary = (entry.get("summary") or "").lower()
    entry_tags = [t.lower() for t in (entry.get("tags") or [])]
    entry_cat = (entry.get("category") or "").lower()

    # 关键词匹配
    for kw in keywords:
        kw_lower = kw.lower()
        if kw_lower in title:
            score += 0.4
        if kw_lower in summary:
            score += 0.2
        if kw_lower in entry_tags:
            score += 0.3

    # 标签过滤
    if tags_filter:
        matched_tags = sum(1 for t in tags_filter if t.lower() in entry_tags)
        if matched_tags == 0:
            return 0.0  # 标签不匹配直接排除
        score += 0.3 * (matched_tags / len(tags_filter))

    # 分类过滤
    if category_filter:
        if category_filter.lower() not in entry_cat:
            return 0.0  # 分类不匹配直接排除
        score += 0.2

    # 状态加分
    if entry.get("status") == "confirmed" or entry.get("status") == "approved":
        score += 0.05

    return min(score, 1.0)


# ─────────────────────────────────────
# search 命令
# ─────────────────────────────────────

def cmd_search(kb_path: str, query: str, tags: str, category: str, top: int):
    """执行搜索并输出结果"""
    index = _load_index(kb_path)
    if not index:
        print("## 查询结果\n")
        print(f"查询：{_format_query(query, tags, category)}")
        print("知识库索引为空或不存在。")
        return

    keywords = query.split() if query else []
    tags_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []

    # 计算得分
    scored = []
    for entry in index:
        s = _score_entry(entry, keywords, tags_list, category)
        if s > 0:
            scored.append((s, entry))

    scored.sort(key=lambda x: x[0], reverse=True)
    results = scored[:top]

    # 输出
    print("## 查询结果\n")
    print(f"查询：{_format_query(query, tags, category)}")
    print(f"找到 {len(results)} 个匹配知识点{'：' if results else '。'}\n")

    for i, (score, entry) in enumerate(results, 1):
        kb_id = entry.get("id", "?")
        title = entry.get("title", "(无标题)")
        cat = entry.get("category", "")
        entry_tags = ", ".join(entry.get("tags", []))
        status_raw = entry.get("status", "")
        status_icon = "✅" if status_raw in ("confirmed", "approved") else "📝"
        summary = entry.get("summary", "")
        file_path = entry.get("file", "")

        print(f"### {i}. {kb_id} {title} [相关度: {score:.2f}]")
        if cat:
            print(f"- **分类**: {cat}")
        if entry_tags:
            print(f"- **标签**: {entry_tags}")
        print(f"- **状态**: {status_icon} {status_raw}")
        if summary:
            print(f"- **摘要**: {summary}")
        if file_path:
            print(f"- **文件**: `{file_path}`")
        print()


def _format_query(query, tags, category):
    parts = []
    if query:
        parts.append(f"关键词: {query}")
    if tags:
        parts.append(f"标签: {tags}")
    if category:
        parts.append(f"分类: {category}")
    return " | ".join(parts) if parts else "(空查询)"


# ─────────────────────────────────────
# get 命令
# ─────────────────────────────────────

def cmd_get(kb_path: str, kb_id: str, full: bool):
    """获取单条知识点"""
    index = _load_index(kb_path)

    # 查找匹配的知识点
    entry = None
    for item in index:
        if item.get("id", "").upper() == kb_id.upper():
            entry = item
            break

    if not entry:
        print(f"❌ 未找到知识点: {kb_id}")
        return

    kb_id_found = entry.get("id", "?")
    title = entry.get("title", "(无标题)")
    cat = entry.get("category", "")
    tags = ", ".join(entry.get("tags", []))
    status = entry.get("status", "")
    summary = entry.get("summary", "")
    file_path = entry.get("file", "")

    print(f"## {kb_id_found} — {title}\n")
    if cat:
        print(f"- **分类**: {cat}")
    if tags:
        print(f"- **标签**: {tags}")
    if status:
        print(f"- **状态**: {status}")
    if summary:
        print(f"- **摘要**: {summary}")
    print()

    if full and file_path:
        # 读取完整知识点文件
        abs_path = os.path.join(kb_path, file_path)
        if os.path.isfile(abs_path):
            try:
                with open(abs_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                print("---\n")
                print(content)
            except OSError as e:
                print(f"⚠️ 读取知识点文件失败: {e}")
        else:
            print(f"⚠️ 知识点文件不存在: {file_path}")
    elif full and not file_path:
        print("⚠️ 索引中未记录文件路径，无法读取全文。")


# ─────────────────────────────────────
# CLI 入口
# ─────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="团队知识库 CLI 检索工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--kb-path", help="知识库仓库路径（覆盖配置文件）")

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # search
    sp_search = subparsers.add_parser("search", help="搜索知识点")
    sp_search.add_argument("query", nargs="?", default="", help="搜索关键词")
    sp_search.add_argument("--tags", default="", help="标签过滤（逗号分隔）")
    sp_search.add_argument("--category", default="", help="分类过滤")
    sp_search.add_argument("--top", type=int, default=5, help="返回结果数量（默认5）")

    # get
    sp_get = subparsers.add_parser("get", help="获取单条知识点")
    sp_get.add_argument("kb_id", help="知识点 ID（如 KB-001）")
    sp_get.add_argument("--full", action="store_true", help="输出完整内容")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # 解析知识库路径
    kb_path = _resolve_kb_path(args.kb_path)
    if not kb_path:
        print("⚠️ [知识库查找] 知识库路径未配置或不可用。")
        print()
        print("请通过以下方式之一配置：")
        print("  1. --kb-path 命令行参数")
        print("  2. ~/.workbuddy/skills/team-kb/.kb-config.json 的 repo_path 字段")
        print("  3. 环境变量 TEAM_KB_PATH")
        sys.exit(1)

    if args.command == "search":
        cmd_search(kb_path, args.query, args.tags, args.category, args.top)
    elif args.command == "get":
        cmd_get(kb_path, args.kb_id, args.full)


if __name__ == "__main__":
    main()
