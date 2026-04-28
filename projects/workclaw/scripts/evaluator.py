#!/usr/bin/env python3
"""
evaluator.py — 任务评估器
评估每次任务的质量、复杂度、技能复用情况。
"""

import json
import os
import sys
from datetime import datetime

# 配置路径
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "learning", "config.json")


def _load_weights() -> dict:
    """从 config.json 加载评估权重，失败时返回默认值"""
    defaults = {"completion": 0.30, "quality": 0.30, "efficiency": 0.20, "satisfaction": 0.20}
    try:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                config = json.load(f)
            return config.get("evaluator", {}).get("weights", defaults)
    except (json.JSONDecodeError, IOError):
        pass
    return defaults


def evaluate_task(
    task_summary: str,
    task_type: str = "general",
    steps: int = 1,
    tool_calls: int = 0,
    files_touched: int = 0,
    duration_minutes: float = 0,
    skill_used: str = None,
    skill_effectiveness: float = None,
    user_feedback_score: float = None,
    quality_estimate: float = 7.0,
    completion_estimate: float = 1.0,
    novelty: str = "low"
) -> dict:
    """
    评估一次任务，返回结构化评估结果。
    
    Args:
        task_summary: 任务简要描述
        task_type: 任务类型 (game_design_doc, research, coding, analysis, general)
        steps: 执行步骤数
        tool_calls: 工具调用次数
        files_touched: 涉及文件数
        duration_minutes: 大致耗时(分钟)
        skill_used: 复用的技能名称 (None=未复用)
        skill_effectiveness: 技能效果评分 (1-10)
        user_feedback_score: 用户反馈评分 (1-10, None=未反馈)
        quality_estimate: 输出质量自评 (1-10)
        completion_estimate: 完成度 (0-1)
        novelty: 方案新颖度 (low/medium/high)
    
    Returns:
        结构化评估结果字典
    """
    
    # 计算综合质量得分（权重从 config.json 读取）
    weights = _load_weights()
    completion_score = completion_estimate * 10
    quality_score = quality_estimate
    
    # 效率评分: 步骤数合理性 (不是越少越好，太少可能粗糙)
    if steps <= 1:
        efficiency_score = 5.0
    elif steps <= 5:
        efficiency_score = 8.0
    elif steps <= 15:
        efficiency_score = 7.0
    else:
        efficiency_score = 6.0  # 步骤过多可能效率低
    
    # 满意度: 优先用户反馈，否则用质量自评
    satisfaction_score = user_feedback_score if user_feedback_score is not None else quality_estimate
    
    overall_score = round(
        completion_score * weights.get("completion", 0.30) +
        quality_score * weights.get("quality", 0.30) +
        efficiency_score * weights.get("efficiency", 0.20) +
        satisfaction_score * weights.get("satisfaction", 0.20),
        2
    )
    
    # 生成任务 ID
    now = datetime.now()
    task_id = f"task-{now.strftime('%Y-%m-%d')}-{now.strftime('%H%M%S')}"
    
    evaluation = {
        "task_id": task_id,
        "timestamp": now.isoformat(),
        "task_summary": task_summary,
        "task_type": task_type,
        
        "evaluation": {
            "overall_score": overall_score,
            "breakdown": {
                "completion": round(completion_score, 2),
                "quality": round(quality_score, 2),
                "efficiency": round(efficiency_score, 2),
                "satisfaction": round(satisfaction_score, 2)
            },
            "complexity": {
                "steps": steps,
                "tool_calls": tool_calls,
                "files_touched": files_touched,
                "duration_minutes": duration_minutes
            },
            "skill_reuse": {
                "used_existing": skill_used is not None,
                "skill_name": skill_used,
                "skill_effectiveness": skill_effectiveness
            },
            "novelty": novelty,
            "user_feedback": user_feedback_score
        }
    }
    
    return evaluation


def evaluate_from_dict(data: dict) -> dict:
    """从字典输入创建评估"""
    return evaluate_task(**data)


if __name__ == "__main__":
    # CLI 用法: python evaluator.py '{"task_summary": "...", "steps": 5}'
    if len(sys.argv) > 1:
        try:
            input_data = json.loads(sys.argv[1])
        except json.JSONDecodeError as e:
            print(json.dumps({"error": f"JSON 解析失败: {e}"}, ensure_ascii=False))
            sys.exit(1)
        result = evaluate_from_dict(input_data)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # 示例运行
        result = evaluate_task(
            task_summary="为和平精英AI队友系统生成策划文档",
            task_type="game_design_doc",
            steps=12,
            tool_calls=8,
            files_touched=3,
            duration_minutes=15,
            skill_used="game-design-doc-template",
            skill_effectiveness=9,
            quality_estimate=8.5
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
