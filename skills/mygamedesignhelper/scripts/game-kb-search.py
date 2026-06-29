# -*- coding: utf-8 -*-
"""
game-kb-search.py — 游戏设计知识库检索工具

用法:
  python game-kb-search.py search "关键词1 关键词2"
  python game-kb-search.py search --tags "标签1,标签2"
  python game-kb-search.py search "关键词" --category "系统设计"
  python game-kb-search.py get "C01-system-design/001-游戏乐趣的本质-认知成长双循环"

知识库路径解析优先级:
  1. --kb-path 命令行参数
  2. ~/.workbuddy/skills/mygamedesignhelper/.game-kb-config.json
  3. 环境变量 GAME_DESIGN_KB_PATH
  4. 默认路径 G:/project_output/game-design-kb
"""

from __future__ import annotations
import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Optional

# Windows UTF-8 兼容
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')


# ─────────────────────────────────────
# 路径解析
# ─────────────────────────────────────

def _resolve_kb_path(cli_path: Optional[str] = None) -> Optional[str]:
    """按优先级解析游戏设计知识库路径"""
    # 1. 命令行参数
    if cli_path:
        p = os.path.expanduser(cli_path)
        if os.path.isdir(p):
            return p
        return None

    # 2. .game-kb-config.json
    config_path = os.path.expanduser("~/.workbuddy/skills/mygamedesignhelper/.game-kb-config.json")
    if os.path.isfile(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
            repo = cfg.get("game_design_kb_path", "")
            if repo:
                p = os.path.expanduser(repo)
                if os.path.isdir(p):
                    return p
        except (json.JSONDecodeError, OSError):
            pass

    # 3. 环境变量
    env_path = os.environ.get("GAME_DESIGN_KB_PATH", "")
    if env_path:
        p = os.path.expanduser(env_path)
        if os.path.isdir(p):
            return p

    # 4. 默认路径
    default_path = "G:/project_output/game-design-kb"
    if os.path.isdir(default_path):
        return default_path

    return None


# ─────────────────────────────────────
# 知识卡片解析
# ─────────────────────────────────────

def _parse_card_metadata(content: str, file_path: str) -> dict:
    """从 Markdown 知识卡片中提取元数据"""
    metadata = {
        "file": file_path,
        "title": "",
        "ability": "",
        "tags": [],
        "source": "",
        "author": "",
        "date": "",
        "rating": "",
        "summary": ""
    }

    lines = content.split('\n')

    # 提取标题（第一个 # 标题）
    for line in lines:
        if line.startswith('# ') and not line.startswith('## '):
            metadata["title"] = line[2:].strip()
            break

    # 提取引用块中的元数据
    in_blockquote = False
    for line in lines:
        line_stripped = line.strip()

        if line_stripped.startswith('> **'):
            in_blockquote = True
            # 解析格式: > **能力**: xxx
            match = re.match(r'^>\s*\*\*(.+?)\*\*:\s*(.+)$', line_stripped)
            if match:
                key, value = match.group(1).strip(), match.group(2).strip()
                if key == '能力':
                    metadata["ability"] = value
                elif key == '标签':
                    # 提取反引号中的标签
                    tags = re.findall(r'`([^`]+)`', value)
                    metadata["tags"] = tags
                elif key == '来源':
                    # 提取链接文本
                    link_match = re.search(r'\[(.+?)\]', value)
                    metadata["source"] = link_match.group(1) if link_match else value
                elif key == '作者':
                    metadata["author"] = value
                elif key == '学习日期':
                    metadata["date"] = value
                elif key == '质量评级':
                    metadata["rating"] = value
        elif in_blockquote and not line_stripped.startswith('>'):
            in_blockquote = False

    # 提取核心观点作为摘要
    in_core_points = False
    core_points = []
    for line in lines:
        if '## 核心观点' in line:
            in_core_points = True
            continue
        if in_core_points:
            if line.startswith('## '):
                break
            # 提取编号列表项
            match = re.match(r'^\d+\.\s*\*\*(.+?)\*\*\s*[—–-]\s*(.+)$', line.strip())
            if match:
                core_points.append(f"{match.group(1)}: {match.group(2)}")

    if core_points:
        metadata["summary"] = "; ".join(core_points[:3])  # 最多3条

    return metadata


def _scan_kb(kb_path: str) -> list[dict]:
    """扫描知识库，构建卡片索引"""
    cards = []
    kb_path_obj = Path(kb_path)

    # 扫描所有 .md 文件
    for md_file in kb_path_obj.rglob("*.md"):
        # 跳过非知识卡片文件（如 README）
        if md_file.name.startswith('_') or md_file.name.startswith('.'):
            continue

        try:
            content = md_file.read_text(encoding='utf-8')
            # 计算相对路径作为文件标识
            rel_path = str(md_file.relative_to(kb_path_obj)).replace('\\', '/')
            metadata = _parse_card_metadata(content, rel_path)
            cards.append(metadata)
        except (OSError, UnicodeDecodeError):
            continue

    return cards


# ─────────────────────────────────────
# 相关度计算
# ─────────────────────────────────────

def _score_card(card: dict, keywords: list[str], tags_filter: list[str], category_filter: str) -> float:
    """计算知识卡片与查询的相关度得分 (0~1)"""
    score = 0.0
    title = (card.get("title") or "").lower()
    ability = (card.get("ability") or "").lower()
    card_tags = [t.lower() for t in (card.get("tags") or [])]
    summary = (card.get("summary") or "").lower()

    # 关键词匹配
    for kw in keywords:
        kw_lower = kw.lower()
        if kw_lower in title:
            score += 0.4
        if kw_lower in summary:
            score += 0.2
        if kw_lower in ability:
            score += 0.15
        if any(kw_lower in t for t in card_tags):
            score += 0.25

    # 标签过滤
    if tags_filter:
        matched_tags = sum(1 for t in tags_filter if t.lower() in card_tags)
        if matched_tags == 0:
            return 0.0  # 标签不匹配直接排除
        score += 0.3 * (matched_tags / len(tags_filter))

    # 分类过滤（匹配能力字段）
    if category_filter:
        if category_filter.lower() not in ability:
            return 0.0  # 分类不匹配直接排除
        score += 0.2

    # 质量评级加分
    rating = card.get("rating", "")
    if "⭐⭐⭐⭐⭐" in rating:
        score += 0.1
    elif "⭐⭐⭐⭐" in rating:
        score += 0.05

    return min(score, 1.0)


# ─────────────────────────────────────
# search 命令
# ─────────────────────────────────────

def cmd_search(kb_path: str, query: str, tags: str, category: str, top: int, output_json: bool):
    """执行搜索并输出结果"""
    cards = _scan_kb(kb_path)

    if not cards:
        print("## 查询结果\n")
        print(f"查询：{_format_query(query, tags, category)}")
        print("游戏设计知识库为空或不存在。")
        return

    keywords = query.split() if query else []
    tags_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []

    # 计算得分
    scored = []
    for card in cards:
        s = _score_card(card, keywords, tags_list, category)
        if s > 0:
            scored.append((s, card))

    scored.sort(key=lambda x: x[0], reverse=True)
    results = scored[:top]

    if output_json:
        # JSON 输出模式（供统一检索脚本调用）
        output = []
        for score, card in results:
            output.append({
                "source": "game-design-kb",
                "score": round(score, 3),
                "title": card.get("title", ""),
                "ability": card.get("ability", ""),
                "tags": card.get("tags", []),
                "summary": card.get("summary", ""),
                "file": card.get("file", ""),
                "rating": card.get("rating", "")
            })
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return

    # Markdown 输出模式
    print("## 游戏设计知识库查询结果\n")
    print(f"查询：{_format_query(query, tags, category)}")
    print(f"找到 {len(results)} 个匹配知识点{'：' if results else '。'}\n")

    for i, (score, card) in enumerate(results, 1):
        title = card.get("title", "(无标题)")
        ability = card.get("ability", "")
        card_tags = ", ".join(card.get("tags", []))
        summary = card.get("summary", "")
        file_path = card.get("file", "")
        rating = card.get("rating", "")

        print(f"### {i}. {title} [相关度: {score:.2f}]")
        if ability:
            print(f"- **能力**: {ability}")
        if card_tags:
            print(f"- **标签**: {card_tags}")
        if rating:
            print(f"- **评级**: {rating}")
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

def cmd_get(kb_path: str, file_id: str, full: bool):
    """获取单条知识点"""
    # 构建完整文件路径
    if not file_id.endswith('.md'):
        file_id = file_id + '.md'

    abs_path = os.path.join(kb_path, file_id)
    if not os.path.isfile(abs_path):
        print(f"❌ 未找到知识点: {file_id}")
        return

    try:
        content = abs_path.read_text(encoding='utf-8') if hasattr(abs_path, 'read_text') else open(abs_path, 'r', encoding='utf-8').read()
        metadata = _parse_card_metadata(content, file_id)

        print(f"## {metadata.get('title', file_id)}\n")
        if metadata.get('ability'):
            print(f"- **能力**: {metadata['ability']}")
        if metadata.get('tags'):
            print(f"- **标签**: {', '.join(metadata['tags'])}")
        if metadata.get('rating'):
            print(f"- **评级**: {metadata['rating']}")
        if metadata.get('summary'):
            print(f"- **摘要**: {metadata['summary']}")
        print()

        if full:
            print("---\n")
            print(content)
    except (OSError, UnicodeDecodeError) as e:
        print(f"⚠️ 读取知识点文件失败: {e}")


# ─────────────────────────────────────
# CLI 入口
# ─────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="游戏设计知识库检索工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--kb-path", help="知识库路径（覆盖配置文件）")
    parser.add_argument("--json", action="store_true", help="JSON 输出模式（供程序调用）")

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # search
    sp_search = subparsers.add_parser("search", help="搜索知识点")
    sp_search.add_argument("query", nargs="?", default="", help="搜索关键词")
    sp_search.add_argument("--tags", default="", help="标签过滤（逗号分隔）")
    sp_search.add_argument("--category", default="", help="能力分类过滤（如 '系统设计'）")
    sp_search.add_argument("--top", type=int, default=5, help="返回结果数量（默认5）")

    # get
    sp_get = subparsers.add_parser("get", help="获取单条知识点")
    sp_get.add_argument("file_id", help="知识点文件路径（如 C01-system-design/001-游戏乐趣的本质）")
    sp_get.add_argument("--full", action="store_true", help="输出完整内容")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # 解析知识库路径
    kb_path = _resolve_kb_path(args.kb_path)
    if not kb_path:
        print("⚠️ [游戏设计知识库] 知识库路径未配置或不可用。")
        print()
        print("请通过以下方式之一配置：")
        print("  1. --kb-path 命令行参数")
        print("  2. ~/.workbuddy/skills/mygamedesignhelper/.game-kb-config.json")
        print("  3. 环境变量 GAME_DESIGN_KB_PATH")
        print("  4. 默认路径 G:/project_output/game-design-kb")
        sys.exit(1)

    if args.command == "search":
        cmd_search(kb_path, args.query, args.tags, args.category, args.top, args.json)
    elif args.command == "get":
        cmd_get(kb_path, args.file_id, args.full)


if __name__ == "__main__":
    main()
