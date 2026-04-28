#!/usr/bin/env python3
"""
episode_store.py — 情景记忆存储
管理 episodes 的写入、查询、归档。
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# 默认存储路径
EPISODES_DIR = os.path.join(os.path.dirname(__file__), "..", "learning", "episodes")


def ensure_dir(path: str):
    """确保目录存在"""
    os.makedirs(path, exist_ok=True)


def store_episode(experience: dict, base_dir: str = None) -> str:
    """
    将经验存储为 episode 文件。
    
    Args:
        experience: extractor.py 的输出
        base_dir: episodes 根目录
    
    Returns:
        存储的文件路径
    """
    base = base_dir or EPISODES_DIR
    now = datetime.now()
    year_dir = os.path.join(base, now.strftime("%Y"), now.strftime("%m"))
    ensure_dir(year_dir)
    
    episode_id = experience.get("episode_id", f"ep-{now.strftime('%Y-%m-%d-%H%M%S')}")
    filename = f"{episode_id}.json"
    filepath = os.path.join(year_dir, filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(experience, f, ensure_ascii=False, indent=2)
    
    return filepath


def list_episodes(base_dir: str = None, year: str = None, month: str = None, limit: int = 20) -> list:
    """列出 episodes"""
    base = base_dir or EPISODES_DIR
    episodes = []
    
    for root, dirs, files in os.walk(base):
        for fname in sorted(files, reverse=True):
            if fname.endswith(".json") and fname.startswith("ep-"):
                filepath = os.path.join(root, fname)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        ep = json.load(f)
                    episodes.append({
                        "episode_id": ep.get("episode_id", fname),
                        "task_summary": ep.get("task_summary", ""),
                        "task_type": ep.get("task_type", ""),
                        "quality_score": ep.get("quality_score", 0),
                        "timestamp": ep.get("timestamp", ""),
                        "filepath": filepath
                    })
                except (json.JSONDecodeError, IOError):
                    continue
            if len(episodes) >= limit:
                break
        if len(episodes) >= limit:
            break
    
    return episodes


def search_episodes(keyword: str, base_dir: str = None, limit: int = 10) -> list:
    """按关键词搜索 episodes"""
    base = base_dir or EPISODES_DIR
    results = []
    
    for root, dirs, files in os.walk(base):
        for fname in sorted(files, reverse=True):
            if not (fname.endswith(".json") and fname.startswith("ep-")):
                continue
            filepath = os.path.join(root, fname)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                if keyword.lower() in content.lower():
                    ep = json.loads(content)
                    results.append({
                        "episode_id": ep.get("episode_id", fname),
                        "task_summary": ep.get("task_summary", ""),
                        "quality_score": ep.get("quality_score", 0),
                        "key_insight": ep.get("experience", {}).get("key_insight", ""),
                        "filepath": filepath
                    })
            except (json.JSONDecodeError, IOError):
                continue
            if len(results) >= limit:
                break
        if len(results) >= limit:
            break
    
    return results


def get_episode_count(base_dir: str = None) -> int:
    """获取 episode 总数"""
    base = base_dir or EPISODES_DIR
    count = 0
    for root, dirs, files in os.walk(base):
        count += sum(1 for f in files if f.endswith(".json") and f.startswith("ep-"))
    return count


if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "list":
            eps = list_episodes(limit=int(sys.argv[2]) if len(sys.argv) > 2 else 20)
            print(json.dumps(eps, ensure_ascii=False, indent=2))
        elif cmd == "search" and len(sys.argv) > 2:
            results = search_episodes(sys.argv[2])
            print(json.dumps(results, ensure_ascii=False, indent=2))
        elif cmd == "count":
            print(f"Total episodes: {get_episode_count()}")
        elif cmd == "store" and len(sys.argv) > 2:
            experience = json.loads(sys.argv[2])
            path = store_episode(experience)
            print(f"Stored: {path}")
    else:
        print("Usage: python episode_store.py [list|search|count|store] [args]")
