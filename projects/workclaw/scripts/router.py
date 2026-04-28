#!/usr/bin/env python3
"""
router.py — 分流决策器
根据评估结果和经验，决定后续操作路径。
"""

import json
import sys
import os

# 默认配置路径
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "learning", "config.json")


def load_config(config_path: str = None) -> dict:
    """加载闭环配置"""
    path = config_path or CONFIG_PATH
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def route_decision(evaluation: dict, experience: dict, config: dict = None) -> dict:
    """
    根据评估+经验做分流决策。
    
    Args:
        evaluation: evaluator.py 的输出
        experience: extractor.py 的输出
        config: 闭环配置（None则自动加载）
    
    Returns:
        {
            "decisions": ["store_episode", "extract_pattern", ...],
            "details": { ... }
        }
    """
    if config is None:
        config = load_config()
    
    router_config = config.get("router", {})
    skill_create_cfg = router_config.get("skill_creation_threshold", {})
    skill_improve_cfg = router_config.get("skill_improvement_threshold", {})
    
    eval_data = evaluation.get("evaluation", {})
    exp_data = experience.get("experience", {})
    
    score = eval_data.get("overall_score", 0)
    steps = eval_data.get("complexity", {}).get("steps", 0)
    used_skill = eval_data.get("skill_reuse", {}).get("used_existing", False)
    skill_name = eval_data.get("skill_reuse", {}).get("skill_name")
    has_pattern = exp_data.get("reusable_pattern", False)
    has_issues = len(exp_data.get("what_went_wrong", [])) > 0 or len(exp_data.get("pitfalls", [])) > 0
    
    decisions = []
    details = {}
    
    # 路径 A: 创建新技能
    min_score = skill_create_cfg.get("min_score", 7.0)
    min_steps = skill_create_cfg.get("min_steps", 3)
    require_no_skill = skill_create_cfg.get("require_no_existing_skill", True)
    
    if score >= min_score and steps >= min_steps and (not used_skill if require_no_skill else True):
        decisions.append("create_skill")
        details["create_skill"] = {
            "reason": f"高分({score}) + 复杂({steps}步) + {'未复用已有skill' if not used_skill else '可扩展'}",
            "task_summary": evaluation.get("task_summary", ""),
            "procedure": exp_data.get("procedure", []),
            "requires_confirmation": True
        }
    
    # 路径 B: 改进已有技能
    if used_skill and has_issues:
        decisions.append("improve_skill")
        details["improve_skill"] = {
            "skill_name": skill_name,
            "issues": exp_data.get("what_went_wrong", []),
            "pitfalls": exp_data.get("pitfalls", []),
            "action": "append_gotchas"
        }
    
    # 路径 C: 提取通用模式
    if has_pattern:
        decisions.append("extract_pattern")
        details["extract_pattern"] = {
            "pattern_candidates": experience.get("pattern_candidates", []),
            "key_insight": exp_data.get("key_insight", ""),
            "source_episode": experience.get("episode_id", "")
        }
    
    # 路径 D: 总是存储情景（兜底）
    decisions.append("store_episode")
    details["store_episode"] = {
        "episode_id": experience.get("episode_id", ""),
        "task_type": experience.get("task_type", "general")
    }
    
    # 路径 E: 更新技能统计
    if used_skill:
        decisions.append("update_skill_stats")
        details["update_skill_stats"] = {
            "skill_name": skill_name,
            "score": score,
            "effectiveness": eval_data.get("skill_reuse", {}).get("skill_effectiveness")
        }
    
    return {
        "decisions": decisions,
        "details": details,
        "summary": f"[score={score}, steps={steps}, skill={'✅'+skill_name if used_skill else '❌'}] → {', '.join(decisions)}"
    }


if __name__ == "__main__":
    if len(sys.argv) > 2:
        evaluation = json.loads(sys.argv[1])
        experience = json.loads(sys.argv[2])
        result = route_decision(evaluation, experience)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("Usage: python router.py '<evaluation_json>' '<experience_json>'")
