#!/usr/bin/env python3
"""
loop_runner.py — 学习闭环主入口
一键串联: evaluator → extractor → router → stores
供对话内或 CLI 调用。
"""

import json
import os
import sys
from datetime import datetime

# 将 scripts 目录加入 path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from evaluator import evaluate_task
from extractor import extract_experience
from router import route_decision
from episode_store import store_episode
from pattern_store import add_pattern, update_confidence, get_stats as pattern_stats
from skill_stats import record_usage, record_gotcha


def run_learning_loop(
    # 评估参数
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
    novelty: str = "low",
    
    # 经验参数
    situation: str = "",
    procedure: list = None,
    what_went_well: list = None,
    what_went_wrong: list = None,
    pitfalls: list = None,
    key_insight: str = "",
    reusable_pattern: bool = False,
    pattern_candidates: list = None,
    
    # 模式详情 (当 reusable_pattern=True 时)
    pattern_details: list = None
) -> dict:
    """
    执行完整的学习闭环。
    
    Args:
        (评估参数) — 同 evaluator.evaluate_task
        (经验参数) — 同 extractor.extract_experience
        pattern_details: 模式详情列表，每个元素是 dict:
            {
                "id": "pattern_id",
                "name": "模式名称",
                "category": "game_design",
                "problem": "问题描述",
                "solution": "解决方案",
                "pitfalls": "注意事项",
                "target_skills": ["skill1", "skill2"]
            }
    
    Returns:
        {
            "evaluation": { ... },
            "experience": { ... },
            "routing": { ... },
            "actions_taken": [ ... ],
            "summary": "..."
        }
    """
    actions_taken = []
    errors = []
    
    # Step 1: 评估（关键步骤，失败则中止）
    try:
        evaluation = evaluate_task(
            task_summary=task_summary,
            task_type=task_type,
            steps=steps,
            tool_calls=tool_calls,
            files_touched=files_touched,
            duration_minutes=duration_minutes,
            skill_used=skill_used,
            skill_effectiveness=skill_effectiveness,
            user_feedback_score=user_feedback_score,
            quality_estimate=quality_estimate,
            completion_estimate=completion_estimate,
            novelty=novelty
        )
        actions_taken.append(f"✅ 评估完成: 综合得分 {evaluation['evaluation']['overall_score']}")
    except Exception as e:
        return {"error": f"评估阶段失败: {e}", "actions_taken": [], "summary": "闭环中止: 评估失败"}
    
    # Step 2: 提取经验（关键步骤，失败则中止）
    try:
        experience = extract_experience(
            evaluation=evaluation,
            situation=situation,
            procedure=procedure,
            what_went_well=what_went_well,
            what_went_wrong=what_went_wrong,
            pitfalls=pitfalls,
            key_insight=key_insight,
            reusable_pattern=reusable_pattern,
            pattern_candidates=pattern_candidates
        )
        actions_taken.append(f"✅ 经验提取完成: {experience['episode_id']}")
    except Exception as e:
        return {"error": f"提取阶段失败: {e}", "evaluation": evaluation, "actions_taken": actions_taken, "summary": "闭环中止: 提取失败"}
    
    # Step 3: 分流决策（关键步骤，失败则中止）
    try:
        routing = route_decision(evaluation, experience)
        actions_taken.append(f"✅ 分流决策: {routing['summary']}")
    except Exception as e:
        return {"error": f"分流阶段失败: {e}", "evaluation": evaluation, "experience": experience, "actions_taken": actions_taken, "summary": "闭环中止: 分流失败"}
    
    # Step 4: 执行决策（各步骤独立容错，一个失败不影响其他）
    decisions = routing["decisions"]
    details = routing["details"]
    
    # 4a: 存储 episode（总是执行）
    if "store_episode" in decisions:
        try:
            ep_path = store_episode(experience)
            actions_taken.append(f"📝 情景已存储: {ep_path}")
        except Exception as e:
            errors.append(f"episode存储失败: {e}")
            actions_taken.append(f"❌ 情景存储失败: {e}")
    
    # 4b: 提取模式
    if "extract_pattern" in decisions and pattern_details:
        for pd in pattern_details:
            try:
                pattern = add_pattern(
                    pattern_id=pd.get("id", f"pat-{datetime.now().strftime('%Y-%m-%d-%H%M%S')}"),
                    name=pd.get("name", ""),
                    category=pd.get("category", "general"),
                    problem=pd.get("problem", ""),
                    solution=pd.get("solution", ""),
                    pitfalls=pd.get("pitfalls", ""),
                    target_skills=pd.get("target_skills", []),
                    source_episode=experience.get("episode_id", "")
                )
                actions_taken.append(f"🧩 模式已创建: {pattern['name']} (置信度: {pattern['confidence']})")
            except Exception as e:
                errors.append(f"模式创建失败({pd.get('name', '?')}): {e}")
                actions_taken.append(f"❌ 模式创建失败({pd.get('name', '?')}): {e}")
    
    # 4c: 更新技能统计
    if "update_skill_stats" in decisions:
        try:
            stat_detail = details["update_skill_stats"]
            record_usage(
                skill_name=stat_detail["skill_name"],
                score=stat_detail["score"],
                effectiveness=stat_detail.get("effectiveness")
            )
            actions_taken.append(f"📊 技能统计已更新: {stat_detail['skill_name']}")
        except Exception as e:
            errors.append(f"技能统计更新失败: {e}")
            actions_taken.append(f"❌ 技能统计更新失败: {e}")
    
    # 4d: 创建新技能（标记需要确认，不自动执行）
    skill_draft = None
    if "create_skill" in decisions:
        skill_draft = details["create_skill"]
        actions_taken.append(f"🆕 建议创建新技能（需用户确认）: {task_summary[:50]}")
    
    # 4e: 改进已有技能（标记建议）
    skill_improvement = None
    if "improve_skill" in decisions:
        skill_improvement = details["improve_skill"]
        actions_taken.append(f"🔧 建议改进技能 [{skill_improvement['skill_name']}]: {', '.join(skill_improvement.get('pitfalls', [])[:3])}")
    
    # 构建结果
    status = "完成" if not errors else f"部分完成({len(errors)}个错误)"
    result = {
        "evaluation": evaluation,
        "experience": experience,
        "routing": routing,
        "actions_taken": actions_taken,
        "errors": errors,
        "skill_draft": skill_draft,
        "skill_improvement": skill_improvement,
        "summary": f"闭环{status} | 得分: {evaluation['evaluation']['overall_score']} | 决策: {', '.join(decisions)} | 执行: {len(actions_taken)}个动作"
    }
    
    return result


def run_from_dict(data: dict) -> dict:
    """从单个字典运行闭环"""
    return run_learning_loop(**data)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            input_data = json.loads(sys.argv[1])
        except json.JSONDecodeError as e:
            print(json.dumps({"error": f"JSON 解析失败: {e}"}, ensure_ascii=False))
            sys.exit(1)
        result = run_from_dict(input_data)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # 端到端测试示例
        result = run_learning_loop(
            task_summary="研究 Hermes Agent 架构并设计 WorkBuddy 学习闭环系统",
            task_type="research",
            steps=8,
            tool_calls=12,
            files_touched=3,
            duration_minutes=30,
            quality_estimate=8.5,
            novelty="high",
            
            situation="用户要求研究 Hermes Agent 自进化架构，设计适配 WorkBuddy 的学习闭环",
            procedure=[
                "调研 Hermes Agent 官方文档和深度分析",
                "盘点现有基础设施（SOUL/MEMORY/skills/AGF）",
                "发现 self-improving-agent 空壳并删除",
                "设计五层记忆架构 + 闭环引擎",
                "生成设计方案文档 + 路线图",
                "风险评估：确认纯加法无破坏性变更",
                "获得用户确认开始实施",
                "编写 Phase 0 + Phase 1 全部代码"
            ],
            what_went_well=["架构对比清晰", "发现空壳skill并及时清理", "设计方案获得用户一次通过"],
            what_went_wrong=[],
            pitfalls=["看似完整的skill可能是空壳——必须验证实际数据而非只看文档"],
            key_insight="学习闭环应是系统底层能力而非独立skill，放在SOUL.md里驱动",
            reusable_pattern=True,
            pattern_candidates=["verify_before_trust", "system_capability_over_skill"],
            pattern_details=[
                {
                    "id": "pat-verify-before-trust",
                    "name": "验证先于信任",
                    "category": "architecture",
                    "problem": "安装的组件/skill看似文档完整、架构精美，但可能完全没有实际实现",
                    "solution": "对任何声称有功能的组件，检查实际数据文件（是否有非空数据）、执行记录、运行环境兼容性",
                    "pitfalls": "不要只看文档描述和架构图，必须验证实际产出",
                    "target_skills": ["skill-vetter", "agf-quality-gate"]
                },
                {
                    "id": "pat-system-capability-over-skill",
                    "name": "系统能力优于独立技能",
                    "category": "architecture",
                    "problem": "将核心基础能力（如学习、评估）封装为独立skill会导致需要手动加载才生效",
                    "solution": "核心能力嵌入SOUL.md或系统配置中，让它始终在线自动运行",
                    "pitfalls": "并非所有能力都适合全局化——领域专用能力仍应是独立skill",
                    "target_skills": []
                }
            ]
        )
        
        print("=" * 60)
        print("🔄 学习闭环端到端测试结果")
        print("=" * 60)
        print(f"\n📊 综合得分: {result['evaluation']['evaluation']['overall_score']}")
        print(f"🆔 Episode: {result['experience']['episode_id']}")
        print(f"🛤️ 决策路径: {', '.join(result['routing']['decisions'])}")
        print(f"\n📋 执行的动作:")
        for action in result["actions_taken"]:
            print(f"   {action}")
        print(f"\n📝 总结: {result['summary']}")
