#!/usr/bin/env python3
"""
skill_evolver.py — 技能进化器
自动改进已有技能（追加 Gotchas）+ 生成新技能草稿。
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# 默认路径
SKILLS_DIR = os.path.expanduser("~/.workbuddy/skills")


def append_gotcha(skill_name: str, pitfalls: list, source_episode: str = "", skills_dir: str = None) -> dict:
    """
    向已有 skill 的候选 Gotchas 文件写入新条目。
    不直接修改 SKILL.md，而是写入 gotchas-candidates.jsonl。
    同一类坑出现次数 ≥ config 阈值后，可通过 promote_gotchas() 合并到正式文件。
    
    Args:
        skill_name: 技能名称（目录名）
        pitfalls: 要追加的陷阱列表
        source_episode: 来源 episode ID
        skills_dir: skills 根目录
    
    Returns:
        {"success": bool, "message": str, "added_count": int}
    """
    base = skills_dir or SKILLS_DIR
    skill_dir = os.path.join(base, skill_name)
    
    if not os.path.exists(skill_dir):
        return {"success": False, "message": f"Skill 目录不存在: {skill_dir}", "added_count": 0}
    
    candidates_path = os.path.join(skill_dir, "gotchas-candidates.jsonl")
    now = datetime.now().strftime("%Y-%m-%d")
    
    added = 0
    with open(candidates_path, "a", encoding="utf-8") as f:
        for pitfall in pitfalls:
            entry = {
                "pitfall": pitfall,
                "source_episode": source_episode,
                "date": now,
                "occurrences": 1
            }
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            added += 1
    
    return {
        "success": True,
        "message": f"已向 {skill_name}/gotchas-candidates.jsonl 写入 {added} 条候选 Gotchas",
        "added_count": added,
        "candidates_path": candidates_path
    }


def promote_gotchas(skill_name: str, min_occurrences: int = 2, skills_dir: str = None) -> dict:
    """
    将满足出现次数阈值的候选 Gotchas 合并到正式 SKILL.md。
    合并后从候选文件中移除已晋升条目。
    
    Args:
        skill_name: 技能名称
        min_occurrences: 最少出现次数才晋升（默认2）
        skills_dir: skills 根目录
    
    Returns:
        {"promoted": list, "remaining": int}
    """
    base = skills_dir or SKILLS_DIR
    skill_dir = os.path.join(base, skill_name)
    candidates_path = os.path.join(skill_dir, "gotchas-candidates.jsonl")
    skill_path = os.path.join(skill_dir, "SKILL.md")
    
    if not os.path.exists(candidates_path):
        return {"promoted": [], "remaining": 0, "message": "无候选文件"}
    
    # 读取所有候选条目
    entries = []
    with open(candidates_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    
    if not entries:
        return {"promoted": [], "remaining": 0, "message": "候选文件为空"}
    
    # 按 pitfall 内容合并计数（简单去重：完全相同算同一条）
    from collections import Counter
    pitfall_counts = Counter()
    pitfall_sources = {}
    for e in entries:
        p = e["pitfall"]
        pitfall_counts[p] += e.get("occurrences", 1)
        if p not in pitfall_sources:
            pitfall_sources[p] = e.get("source_episode", "")
    
    # 分离：满足阈值的晋升，不满足的保留
    to_promote = [(p, pitfall_sources[p]) for p, c in pitfall_counts.items() if c >= min_occurrences]
    remaining = [(p, c) for p, c in pitfall_counts.items() if c < min_occurrences]
    
    if not to_promote:
        return {"promoted": [], "remaining": len(remaining), "message": f"无候选满足阈值（需 ≥{min_occurrences} 次）"}
    
    # 写入正式 SKILL.md
    if os.path.exists(skill_path):
        with open(skill_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        gotchas_marker = "## ⚠️ Gotchas"
        if gotchas_marker not in content and "## Gotchas" not in content:
            content += f"\n\n{gotchas_marker}（已知陷阱）\n\n"
            content += "| # | 陷阱描述 | 来源 | 日期 |\n"
            content += "|---|---------|------|------|\n"
        
        # 找到现有最大编号
        lines = content.split("\n")
        last_g_num = 0
        in_gotchas = False
        insert_idx = None
        
        for i, line in enumerate(lines):
            if gotchas_marker in line or "## Gotchas" in line:
                in_gotchas = True
            elif in_gotchas and line.startswith("## "):
                insert_idx = i
                break
            elif in_gotchas and line.startswith("| G"):
                try:
                    num = int(line.split("|")[1].strip().replace("G", ""))
                    last_g_num = max(last_g_num, num)
                except (ValueError, IndexError):
                    pass
                insert_idx = i + 1
        
        if insert_idx is None:
            insert_idx = len(lines)
        
        now = datetime.now().strftime("%Y-%m-%d")
        new_lines = []
        for i, (pitfall, source) in enumerate(to_promote, last_g_num + 1):
            new_lines.append(f"| G{i} | {pitfall} | {source} | {now} |")
        
        lines = lines[:insert_idx] + new_lines + lines[insert_idx:]
        content = "\n".join(lines)
        
        with open(skill_path, "w", encoding="utf-8") as f:
            f.write(content)
    
    # 重写候选文件（只保留未晋升的）
    with open(candidates_path, "w", encoding="utf-8") as f:
        for pitfall, count in remaining:
            entry = {
                "pitfall": pitfall,
                "source_episode": pitfall_sources.get(pitfall, ""),
                "date": datetime.now().strftime("%Y-%m-%d"),
                "occurrences": count
            }
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    
    return {
        "promoted": [p for p, _ in to_promote],
        "remaining": len(remaining),
        "message": f"已将 {len(to_promote)} 条 Gotchas 晋升到 {skill_name}/SKILL.md，{len(remaining)} 条仍在候选"
    }


def generate_skill_draft(
    task_summary: str,
    procedure: list,
    pitfalls: list = None,
    key_insight: str = "",
    source_episode: str = "",
    task_type: str = "general",
    initial_score: float = 7.0
) -> str:
    """
    生成新技能的 SKILL.md 草稿。
    
    Returns:
        SKILL.md 内容字符串（需用户确认后才写入）
    """
    now = datetime.now().strftime("%Y-%m-%d")
    
    # 从 task_summary 生成 skill 名称
    skill_name = task_summary[:50].lower()
    for ch in " /\\:*?\"<>|.,;()[]{}":
        skill_name = skill_name.replace(ch, "-")
    skill_name = "-".join(filter(None, skill_name.split("-")))
    
    # 生成步骤文本
    procedure_text = "\n".join(f"{i}. {step}" for i, step in enumerate(procedure, 1))
    
    # 生成陷阱文本
    pitfalls_text = ""
    if pitfalls:
        pitfalls_text = "\n".join(f"- {p}" for p in pitfalls)
    else:
        pitfalls_text = "- (暂无)"
    
    draft = f"""---
name: {skill_name}
description: {task_summary}
version: 1.0.0
created: {now}
source: auto-extracted from {source_episode}
confidence: 0.7
use_count: 0
avg_score: {initial_score}
---

# {task_summary}

> 自动从闭环学习中提取的技能草稿。

## 适用场景

当需要执行类似「{task_summary}」的任务时使用。
任务类型: {task_type}

## 执行步骤 (Procedure)

{procedure_text}

## 关键洞察

{key_insight or '(暂无)'}

## 已知陷阱 (Pitfalls)

{pitfalls_text}

## 验证标准 (Verification)

- [ ] 任务完整完成
- [ ] 输出质量满足预期
- [ ] 无遗漏步骤

## 进化日志

| 日期 | 版本 | 变更 | 来源 |
|------|-----|------|------|
| {now} | 1.0.0 | 初始创建（自动提取） | {source_episode} |
"""
    
    return draft


def list_skills(skills_dir: str = None) -> list:
    """列出所有已安装的 skills"""
    base = skills_dir or SKILLS_DIR
    skills = []
    if os.path.exists(base):
        for name in sorted(os.listdir(base)):
            skill_md = os.path.join(base, name, "SKILL.md")
            if os.path.exists(skill_md):
                size = os.path.getsize(skill_md)
                mtime = datetime.fromtimestamp(os.path.getmtime(skill_md)).strftime("%Y-%m-%d")
                skills.append({"name": name, "skill_md_size": size, "last_modified": mtime})
    return skills


if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "list":
            skills = list_skills()
            for s in skills:
                print(f"  {s['name']:30s} | {s['skill_md_size']:>8d} B | {s['last_modified']}")
        elif cmd == "draft" and len(sys.argv) > 2:
            data = json.loads(sys.argv[2])
            draft = generate_skill_draft(**data)
            print(draft)
        elif cmd == "gotcha" and len(sys.argv) > 3:
            skill_name = sys.argv[2]
            pitfalls = json.loads(sys.argv[3])
            result = append_gotcha(skill_name, pitfalls)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif cmd == "promote" and len(sys.argv) > 2:
            skill_name = sys.argv[2]
            min_occ = int(sys.argv[3]) if len(sys.argv) > 3 else 2
            result = promote_gotchas(skill_name, min_occurrences=min_occ)
            print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("Usage:")
        print("  python skill_evolver.py list")
        print("  python skill_evolver.py draft '<json_data>'")
        print("  python skill_evolver.py gotcha <skill_name> '[\"pitfall1\", \"pitfall2\"]'")
        print("  python skill_evolver.py promote <skill_name> [min_occurrences]")
