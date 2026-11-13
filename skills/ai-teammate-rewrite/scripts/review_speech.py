"""Review speech candidates for audit flags; never certify naturalness."""
import argparse
import json
import re
from pathlib import Path

NUMBER = r"[0-9零〇一二两三四五六七八九十百千万点.]+(?:来|多|左右)?"
MEASUREMENT = re.compile(NUMBER + r"\s*(?:米|秒|分钟|血|点血|血量)")
BOOKISH = ("惦记", "对峙", "先别凑", "互耗", "收益", "成本", "可协同", "隐蔽监视", "风险可控")
ENEMY_MODELS = ("AS50", "AKM", "猎弓")
MARKER = ("标好了", "我标的", "看我的标", "已经标")


def scan(items):
    flags, total = [], 0
    rows = []
    for item in items:
        row = item["row"]
        rows.append(row)
        speech = item.get("rewrites", [])
        if len(speech) != 6 or len(set(speech)) != len(speech):
            flags.append({"row": row, "type": "six_unique_variants_required"})
        tactical = item.get("kind") == "tactical" or not str(item.get("action", "")).startswith("取")
        for index, text in enumerate(speech, 1):
            total += 1
            problems = []
            if not isinstance(text, str) or not text.strip():
                problems.append("empty_speech")
                text = str(text)
            if MEASUREMENT.search(text) or re.search(r"信号(?:值)?.{0,5}(?:剩|才|只有)?\s*[0-9]+", text):
                problems.append("measurement_speech")
            if any(word.lower() in text.lower() for word in ENEMY_MODELS):
                problems.append("weapon_requires_visibility_review")
            if "满血" in text:
                problems.append("true_enemy_health_requires_review")
            if any(word in text for word in BOOKISH):
                problems.append("bookish_or_report_expression")
            if tactical and any(word in text for word in ("咱", "我们")):
                problems.append("redundant_tactical_pronoun")
            if any(word in text for word in MARKER):
                problems.append("marker_requires_actual_state")
            if "有狙" in text:
                problems.append("weapon_category_visibility_required")
            if len(text) > 45:
                problems.append("long_candidate_review")
            if problems:
                flags.append({"row": row, "variant": index, "text": text, "types": problems})
    if len(set(rows)) != len(rows):
        flags.append({"type": "duplicate_rows"})
    return {"rows": len(items), "sentences": total, "flags": flags,
            "status": "candidate_flags" if flags else "machine_checks_pass_no_semantic_claim",
            "note": "机器检查不证明口语、逻辑或玩家体验；需逐条独立语义审阅。"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path)
    args = parser.parse_args()
    doc = json.loads(args.file.read_text(encoding="utf-8"))
    print(json.dumps(scan(doc["items"]), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
