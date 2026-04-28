#!/usr/bin/env python3
"""
pattern_store.py — 语义模式库管理
管理 patterns 的写入、查询、置信度更新、剪枝。
"""

import json
import os
import sys
from datetime import datetime

# 默认存储路径
PATTERNS_PATH = os.path.join(os.path.dirname(__file__), "..", "learning", "semantic-patterns.json")
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "learning", "config.json")


def load_patterns(path: str = None) -> dict:
    """加载模式库"""
    p = path or PATTERNS_PATH
    if os.path.exists(p):
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"version": "2.0.0", "total_patterns": 0, "patterns": {}}


def save_patterns(data: dict, path: str = None):
    """保存模式库"""
    p = path or PATTERNS_PATH
    data["last_updated"] = datetime.now().strftime("%Y-%m-%d")
    data["total_patterns"] = len(data.get("patterns", {}))
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_config(path: str = None) -> dict:
    """加载配置"""
    p = path or CONFIG_PATH
    if os.path.exists(p):
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def add_pattern(
    pattern_id: str,
    name: str,
    category: str,
    problem: str,
    solution: str,
    pitfalls: str = "",
    target_skills: list = None,
    source_episode: str = "",
    patterns_path: str = None
) -> dict:
    """
    添加新模式。新模式以 candidate 状态创建，需多次验证后升级为 active。
    
    Returns:
        添加后的 pattern 对象
    """
    config = load_config()
    candidate_confidence = config.get("patterns", {}).get("candidate_initial_confidence", 0.50)
    
    data = load_patterns(patterns_path)
    now = datetime.now().strftime("%Y-%m-%d")
    
    pattern = {
        "id": pattern_id,
        "name": name,
        "category": category,
        "confidence": candidate_confidence,
        "use_count": 0,
        "success_count": 0,
        "failure_count": 0,
        "last_used": now,
        "created": now,
        "problem": problem,
        "solution": solution,
        "pitfalls": pitfalls,
        "target_skills": target_skills or [],
        "source_episodes": [source_episode] if source_episode else [],
        "status": "candidate"
    }
    
    data["patterns"][pattern_id] = pattern
    save_patterns(data, patterns_path)
    
    return pattern


def update_confidence(pattern_id: str, event: str, patterns_path: str = None) -> dict:
    """
    更新模式置信度，并追踪成功/失败次数。
    candidate 模式满足晋升条件后自动升级为 active。
    
    Args:
        pattern_id: 模式ID
        event: success / failure / positive_feedback / negative_feedback
    
    Returns:
        更新后的 pattern（含 promoted 标记表示本次是否晋升）
    """
    config = load_config()
    pcfg = config.get("patterns", {})
    
    data = load_patterns(patterns_path)
    pattern = data["patterns"].get(pattern_id)
    if not pattern:
        return None
    
    confidence = pattern["confidence"]
    
    # 更新成功/失败计数
    if event == "success":
        confidence += pcfg.get("boost_on_success", 0.05)
        pattern["success_count"] = pattern.get("success_count", 0) + 1
    elif event == "failure":
        confidence += pcfg.get("penalty_on_failure", -0.10)
        pattern["failure_count"] = pattern.get("failure_count", 0) + 1
    elif event == "positive_feedback":
        confidence += pcfg.get("boost_on_positive_feedback", 0.10)
        pattern["success_count"] = pattern.get("success_count", 0) + 1
    elif event == "negative_feedback":
        confidence += pcfg.get("penalty_on_negative_feedback", -0.15)
        pattern["failure_count"] = pattern.get("failure_count", 0) + 1
    
    # 应用边界
    cap = pcfg.get("confidence_cap", 0.99)
    floor = pcfg.get("confidence_floor", 0.0)
    confidence = max(floor, min(cap, confidence))
    
    pattern["confidence"] = round(confidence, 3)
    pattern["use_count"] = pattern.get("use_count", 0) + 1
    pattern["last_used"] = datetime.now().strftime("%Y-%m-%d")
    
    # 晋升检查: candidate → active
    promoted = False
    if pattern.get("status") == "candidate":
        promotion_cfg = pcfg.get("promotion", {})
        min_hits = promotion_cfg.get("min_hits", 2)
        min_success_rate = promotion_cfg.get("min_success_rate", 0.75)
        min_confidence = promotion_cfg.get("min_confidence", 0.65)
        
        total = pattern.get("success_count", 0) + pattern.get("failure_count", 0)
        success_rate = pattern.get("success_count", 0) / total if total > 0 else 0
        
        if (total >= min_hits 
            and success_rate >= min_success_rate 
            and pattern["confidence"] >= min_confidence):
            pattern["status"] = "active"
            pattern["promoted_date"] = datetime.now().strftime("%Y-%m-%d")
            promoted = True
    
    save_patterns(data, patterns_path)
    
    result = dict(pattern)
    result["_promoted"] = promoted
    return result


def search_patterns(keyword: str = None, category: str = None, min_confidence: float = 0.0, include_candidates: bool = False, patterns_path: str = None) -> list:
    """搜索模式。默认只返回 active 模式，设 include_candidates=True 可包含候选模式。"""
    data = load_patterns(patterns_path)
    results = []
    
    for pid, pattern in data.get("patterns", {}).items():
        status = pattern.get("status", "active")
        if status == "deprecated":
            continue
        if status == "candidate" and not include_candidates:
            continue
        if pattern.get("confidence", 0) < min_confidence:
            continue
        if category and pattern.get("category") != category:
            continue
        if keyword:
            searchable = json.dumps(pattern, ensure_ascii=False).lower()
            if keyword.lower() not in searchable:
                continue
        results.append(pattern)
    
    # 按置信度降序
    results.sort(key=lambda x: x.get("confidence", 0), reverse=True)
    return results


def get_relevant_patterns(task_description: str, task_type: str = None, top_k: int = 5, include_candidates: bool = False, patterns_path: str = None) -> list:
    """
    获取与任务最相关的 patterns。
    Phase 1 使用关键词匹配，Phase 4 升级为向量检索。
    默认只返回 active 模式用于任务注入。
    """
    data = load_patterns(patterns_path)
    scored = []
    
    words = task_description.lower().split()
    
    for pid, pattern in data.get("patterns", {}).items():
        status = pattern.get("status", "active")
        if status == "deprecated":
            continue
        if status == "candidate" and not include_candidates:
            continue
        
        # 简单关键词匹配打分
        searchable = json.dumps(pattern, ensure_ascii=False).lower()
        match_count = sum(1 for w in words if w in searchable)
        
        # 类别匹配加分
        category_bonus = 0.2 if task_type and pattern.get("category") == task_type else 0
        
        # 置信度权重
        confidence = pattern.get("confidence", 0.5)
        
        relevance = match_count * 0.3 + confidence * 0.5 + category_bonus
        
        if match_count > 0 or category_bonus > 0:
            scored.append((relevance, pattern))
    
    scored.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in scored[:top_k]]


def get_stats(patterns_path: str = None) -> dict:
    """获取模式库统计"""
    data = load_patterns(patterns_path)
    patterns = data.get("patterns", {})
    
    active = [p for p in patterns.values() if p.get("status") == "active"]
    candidate = [p for p in patterns.values() if p.get("status") == "candidate"]
    deprecated = [p for p in patterns.values() if p.get("status") == "deprecated"]
    
    categories = {}
    for p in active + candidate:
        cat = p.get("category", "unknown")
        categories[cat] = categories.get(cat, 0) + 1
    
    all_live = active + candidate
    avg_confidence = sum(p.get("confidence", 0) for p in all_live) / len(all_live) if all_live else 0
    
    return {
        "total": len(patterns),
        "active": len(active),
        "candidate": len(candidate),
        "deprecated": len(deprecated),
        "avg_confidence": round(avg_confidence, 3),
        "categories": categories
    }


if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "stats":
            print(json.dumps(get_stats(), ensure_ascii=False, indent=2))
        elif cmd == "search" and len(sys.argv) > 2:
            results = search_patterns(keyword=sys.argv[2])
            print(json.dumps(results, ensure_ascii=False, indent=2))
        elif cmd == "list":
            results = search_patterns(min_confidence=0.0)
            print(json.dumps(results, ensure_ascii=False, indent=2))
        elif cmd == "relevant" and len(sys.argv) > 2:
            results = get_relevant_patterns(sys.argv[2])
            print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print("Usage: python pattern_store.py [stats|search|list|relevant] [args]")
