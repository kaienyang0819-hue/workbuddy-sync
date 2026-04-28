#!/usr/bin/env python3
"""
nudge.py — 周期性自省
整理记忆系统：pattern 去重/剪枝 + episode 归档 + 技能健康检查 + 生成自省周报。
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pattern_store import load_patterns, save_patterns, load_config, get_stats as pattern_stats
from episode_store import list_episodes, get_episode_count, EPISODES_DIR
from skill_stats import load_stats as load_skill_stats, get_skill_report
from skill_evolver import list_skills

# 报告输出路径
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "..", "learning", "reports")


def prune_patterns(dry_run: bool = True) -> list:
    """
    剪枝低置信度 + 长期未用的 patterns。
    增强版：同时考虑 use_count 和 success_rate。
    对 candidate 状态应用更严格的过期规则。
    
    Returns:
        被剪枝/标记 deprecated 的 pattern 列表
    """
    config = load_config()
    pcfg = config.get("patterns", {})
    threshold = pcfg.get("deprecation_threshold", 0.3)
    months_unused = pcfg.get("deprecation_months_unused", 6)
    decay_rate = pcfg.get("decay_per_month_unused", 0.02)
    
    data = load_patterns()
    pruned = []
    now = datetime.now()
    
    for pid, pattern in data.get("patterns", {}).items():
        if pattern.get("status") == "deprecated":
            continue
        
        status = pattern.get("status", "active")
        
        # 计算未使用月数
        last_used_str = pattern.get("last_used", pattern.get("created", "2026-01-01"))
        try:
            last_used = datetime.strptime(last_used_str, "%Y-%m-%d")
        except ValueError:
            last_used = now
        
        months_since_use = (now - last_used).days / 30.0
        
        # 应用时间衰减
        if months_since_use > 1:
            decay = decay_rate * months_since_use
            new_confidence = max(0.0, pattern["confidence"] - decay)
            
            if not dry_run:
                pattern["confidence"] = round(new_confidence, 3)
        
        # 计算 success_rate
        success_count = pattern.get("success_count", 0)
        failure_count = pattern.get("failure_count", 0)
        total_hits = success_count + failure_count
        success_rate = success_count / total_hits if total_hits > 0 else None
        
        use_count = pattern.get("use_count", 0)
        should_deprecate = False
        reason = ""
        
        # 规则 1: 低置信度 + 长期未用（原有规则）
        if pattern["confidence"] < threshold and months_since_use > months_unused:
            should_deprecate = True
            reason = f"低置信度({pattern['confidence']:.2f}) + 长期未用({months_since_use:.0f}月)"
        
        # 规则 2: candidate 超过 3 个月未晋升 → 降级
        if status == "candidate" and months_since_use > 3 and use_count == 0:
            should_deprecate = True
            reason = f"candidate 超3月未验证(创建后 {months_since_use:.0f}月, 0次使用)"
        
        # 规则 3: 高使用量但高失败率 → 标记问题
        if total_hits >= 3 and success_rate is not None and success_rate < 0.3:
            should_deprecate = True
            reason = f"高失败率({success_rate:.0%}, {total_hits}次命中)"
        
        if should_deprecate:
            pruned.append({
                "id": pid,
                "name": pattern.get("name", ""),
                "status": status,
                "confidence": pattern["confidence"],
                "months_unused": round(months_since_use, 1),
                "use_count": use_count,
                "success_rate": f"{success_rate:.0%}" if success_rate is not None else "N/A",
                "reason": reason,
                "action": "deprecated" if not dry_run else "would_deprecate"
            })
            
            if not dry_run:
                pattern["status"] = "deprecated"
                pattern["deprecated_reason"] = reason
                pattern["deprecated_date"] = now.strftime("%Y-%m-%d")
    
    if not dry_run:
        save_patterns(data)
    
    return pruned


def archive_old_episodes(days: int = 30, dry_run: bool = True) -> dict:
    """
    归档旧 episodes（生成月度摘要）。
    
    Returns:
        {"archived_count": int, "summary_generated": bool}
    """
    now = datetime.now()
    cutoff = now - timedelta(days=days)
    
    old_episodes = []
    for root, dirs, files in os.walk(EPISODES_DIR):
        for fname in files:
            if not (fname.endswith(".json") and fname.startswith("ep-")):
                continue
            filepath = os.path.join(root, fname)
            mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
            if mtime < cutoff:
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        ep = json.load(f)
                    old_episodes.append(ep)
                except (json.JSONDecodeError, IOError):
                    continue
    
    return {
        "old_episode_count": len(old_episodes),
        "cutoff_date": cutoff.strftime("%Y-%m-%d"),
        "action": "would_archive" if dry_run else "archived",
        "note": "当前数据量较少，暂不执行归档"
    }


def generate_weekly_report() -> str:
    """生成自省周报"""
    now = datetime.now()
    week_num = now.isocalendar()[1]
    year = now.year
    
    # 收集数据
    p_stats = pattern_stats()
    ep_count = get_episode_count()
    skill_list = list_skills()
    skill_stats = load_skill_stats()
    
    # 本周 episodes
    week_start = now - timedelta(days=now.weekday())
    recent_episodes = list_episodes(limit=50)
    this_week = [e for e in recent_episodes if e.get("timestamp", "") >= week_start.strftime("%Y-%m-%d")]
    
    # 剪枝预检
    prune_preview = prune_patterns(dry_run=True)
    
    # 构建报告
    report = f"""# 📊 自进化周报 — {year} 第 {week_num} 周

> 生成时间: {now.strftime('%Y-%m-%d %H:%M')}

## 一、系统概览

| 指标 | 值 |
|------|-----|
| 活跃 Patterns | {p_stats['active']} |
| 候选 Patterns | {p_stats.get('candidate', 0)} |
| 已弃用 Patterns | {p_stats['deprecated']} |
| 平均置信度 | {p_stats['avg_confidence']} |
| 总 Episodes | {ep_count} |
| 本周 Episodes | {len(this_week)} |
| 已安装 Skills | {len(skill_list)} |
| 有使用记录的 Skills | {len(skill_stats.get('skills', {}))} |

## 二、Pattern 分布

| 分类 | 数量 |
|------|------|
"""
    for cat, count in sorted(p_stats.get("categories", {}).items(), key=lambda x: x[1], reverse=True):
        report += f"| {cat} | {count} |\n"
    
    report += f"""
## 三、本周经验 ({len(this_week)} 条)

"""
    if this_week:
        for ep in this_week:
            score = ep.get("quality_score", "?")
            report += f"- [{score}分] {ep.get('task_summary', '未知任务')}\n"
    else:
        report += "本周暂无新经验记录。\n"
    
    report += f"""
## 四、技能使用排行

{get_skill_report() if skill_stats.get('skills') else '暂无技能使用记录。'}

## 五、剪枝预检

"""
    if prune_preview:
        report += "以下 patterns 可能需要清理:\n\n"
        for p in prune_preview:
            report += f"- **{p['name']}** [{p.get('status','?')}] (置信度: {p['confidence']}, 使用: {p.get('use_count', 0)}次, 成功率: {p.get('success_rate', 'N/A')}) — {p.get('reason', '未知')}\n"
    else:
        report += "所有 patterns 状态良好，无需清理。\n"
    
    report += f"""
## 六、健康度评估

- **记忆膨胀风险**: {'⚠️ 关注' if ep_count > 100 else '🟢 安全'} ({ep_count}/200)
- **Pattern 质量**: {'🟢 优秀' if p_stats['avg_confidence'] > 0.7 else '🟡 一般' if p_stats['avg_confidence'] > 0.5 else '🔴 需改进'}
- **系统活跃度**: {'🟢 活跃' if len(this_week) > 0 else '🟡 本周较安静'}

---

*报告由学习闭环自省系统自动生成*
"""
    
    return report


def run_nudge(dry_run: bool = True, save_report: bool = True) -> dict:
    """
    执行完整的自省流程。
    
    Args:
        dry_run: True=只预检不执行，False=执行实际操作
        save_report: 是否保存周报到文件
    """
    results = {}
    
    # 1. Pattern 剪枝
    results["prune"] = prune_patterns(dry_run=dry_run)
    
    # 2. Episode 归档检查
    results["archive"] = archive_old_episodes(dry_run=dry_run)
    
    # 3. 生成周报
    report = generate_weekly_report()
    results["report_preview"] = report[:500] + "..." if len(report) > 500 else report
    
    if save_report:
        os.makedirs(REPORTS_DIR, exist_ok=True)
        now = datetime.now()
        week_num = now.isocalendar()[1]
        report_path = os.path.join(REPORTS_DIR, f"weekly-{now.year}-W{week_num:02d}.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)
        results["report_path"] = report_path
    
    results["summary"] = f"自省完成 | 剪枝候选: {len(results['prune'])} | 归档候选: {results['archive']['old_episode_count']} | 周报: {'已保存' if save_report else '未保存'}"
    
    return results


if __name__ == "__main__":
    dry_run = "--execute" not in sys.argv
    result = run_nudge(dry_run=dry_run, save_report=True)
    
    if dry_run:
        print("🔍 自省预检模式 (添加 --execute 执行实际操作)\n")
    else:
        print("⚡ 自省执行模式\n")
    
    print(result["summary"])
    
    if result.get("report_path"):
        print(f"\n📄 周报已保存: {result['report_path']}")
