#!/usr/bin/env python3
"""
extractor.py — 经验提取器
从任务评估结果中提取结构化经验。
"""

import json
import sys
from datetime import datetime


def extract_experience(
    evaluation: dict,
    situation: str = "",
    procedure: list = None,
    what_went_well: list = None,
    what_went_wrong: list = None,
    pitfalls: list = None,
    key_insight: str = "",
    reusable_pattern: bool = False,
    pattern_candidates: list = None
) -> dict:
    """
    从评估结果+补充信息中提取结构化经验。
    
    Args:
        evaluation: evaluator.py 的输出
        situation: 任务场景描述
        procedure: 执行步骤列表
        what_went_well: 做得好的方面
        what_went_wrong: 做得不好的方面
        pitfalls: 发现的陷阱
        key_insight: 关键洞察
        reusable_pattern: 是否包含可复用模式
        pattern_candidates: 候选模式名称列表
    
    Returns:
        结构化经验字典
    """
    now = datetime.now()
    episode_id = f"ep-{now.strftime('%Y-%m-%d')}-{now.strftime('%H%M%S')}"
    
    task_eval = evaluation.get("evaluation", {})
    score = task_eval.get("overall_score", 0)
    
    well = what_went_well or []
    wrong = what_went_wrong or []
    pits = pitfalls or []
    
    # 推断 experience_type
    if reusable_pattern and key_insight and not wrong:
        experience_type = "discovery"
    elif score >= 7.0 and len(wrong) == 0:
        experience_type = "success"
    elif score < 5.0 or len(wrong) > len(well):
        experience_type = "failure"
    elif well and wrong:
        experience_type = "mixed"
    elif score >= 7.0:
        experience_type = "success"
    else:
        experience_type = "mixed"
    
    experience = {
        "episode_id": episode_id,
        "timestamp": now.isoformat(),
        "task_id": evaluation.get("task_id", "unknown"),
        "task_type": evaluation.get("task_type", "general"),
        "task_summary": evaluation.get("task_summary", ""),
        "skill_used": task_eval.get("skill_reuse", {}).get("skill_name"),
        "experience_type": experience_type,
        
        "experience": {
            "situation": situation or evaluation.get("task_summary", ""),
            "procedure": procedure or [],
            "what_went_well": well,
            "what_went_wrong": wrong,
            "pitfalls": pits,
            "key_insight": key_insight,
            "reusable_pattern": reusable_pattern
        },
        
        "quality_score": score,
        "complexity": task_eval.get("complexity", {}),
        "pattern_candidates": pattern_candidates or []
    }
    
    return experience


def extract_from_dict(evaluation: dict, experience_data: dict) -> dict:
    """从两个字典输入创建经验"""
    return extract_experience(evaluation, **experience_data)


if __name__ == "__main__":
    if len(sys.argv) > 2:
        evaluation = json.loads(sys.argv[1])
        experience_data = json.loads(sys.argv[2])
        result = extract_from_dict(evaluation, experience_data)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # 示例
        from evaluator import evaluate_task
        eval_result = evaluate_task(
            task_summary="研究 Hermes Agent 架构并设计学习闭环",
            task_type="research",
            steps=8,
            tool_calls=6,
            files_touched=2,
            quality_estimate=8.0
        )
        result = extract_experience(
            evaluation=eval_result,
            situation="用户要求研究 Hermes Agent 并设计适配方案",
            procedure=["调研官方文档", "盘点现有基础设施", "设计五层记忆架构", "生成方案文档"],
            what_went_well=["架构对比清晰", "发现现有空壳skill"],
            what_went_wrong=[],
            pitfalls=["self-improving-agent 看似完整实则空壳，需验证不能只看文档"],
            key_insight="学习闭环应是系统底层能力而非独立skill",
            reusable_pattern=True,
            pattern_candidates=["verify_before_trust", "system_capability_over_skill"]
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
