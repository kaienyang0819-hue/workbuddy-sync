#!/usr/bin/env python3
"""
skill_stats.py — 技能使用统计
追踪每个 skill 的使用次数、平均评分、效果趋势。
"""

import json
import os
from datetime import datetime

STATS_PATH = os.path.join(os.path.dirname(__file__), "..", "learning", "skill-stats.json")


def load_stats(path: str = None) -> dict:
    p = path or STATS_PATH
    if os.path.exists(p):
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"version": "1.0.0", "last_updated": "", "skills": {}}


def save_stats(data: dict, path: str = None):
    p = path or STATS_PATH
    data["last_updated"] = datetime.now().strftime("%Y-%m-%d")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def record_usage(skill_name: str, score: float, effectiveness: float = None, path: str = None):
    """
    记录一次 skill 使用。
    
    Args:
        skill_name: 技能名称
        score: 任务综合得分
        effectiveness: 技能效果评分 (可选)
    """
    data = load_stats(path)
    
    if skill_name not in data["skills"]:
        data["skills"][skill_name] = {
            "use_count": 0,
            "total_score": 0,
            "avg_score": 0,
            "scores_history": [],
            "last_used": "",
            "first_used": datetime.now().strftime("%Y-%m-%d"),
            "gotchas_added": 0
        }
    
    skill = data["skills"][skill_name]
    skill["use_count"] += 1
    skill["total_score"] = round(skill["total_score"] + score, 2)
    skill["avg_score"] = round(skill["total_score"] / skill["use_count"], 2)
    skill["last_used"] = datetime.now().strftime("%Y-%m-%d")
    
    # 保留最近20次评分
    skill["scores_history"].append({
        "date": datetime.now().strftime("%Y-%m-%d"),
        "score": score,
        "effectiveness": effectiveness
    })
    skill["scores_history"] = skill["scores_history"][-20:]
    
    save_stats(data, path)


def record_gotcha(skill_name: str, path: str = None):
    """记录一次 Gotcha 追加"""
    data = load_stats(path)
    if skill_name in data["skills"]:
        data["skills"][skill_name]["gotchas_added"] = data["skills"][skill_name].get("gotchas_added", 0) + 1
        save_stats(data, path)


def get_skill_report(path: str = None) -> str:
    """生成技能使用报告"""
    data = load_stats(path)
    
    if not data["skills"]:
        return "尚无技能使用记录。"
    
    lines = ["# 技能使用统计\n"]
    lines.append(f"| 技能 | 使用次数 | 平均评分 | 最近使用 | Gotchas追加 |")
    lines.append(f"|------|---------|---------|---------|------------|")
    
    for name, skill in sorted(data["skills"].items(), key=lambda x: x[1]["use_count"], reverse=True):
        lines.append(
            f"| {name} | {skill['use_count']} | {skill['avg_score']} | {skill['last_used']} | {skill.get('gotchas_added', 0)} |"
        )
    
    return "\n".join(lines)
