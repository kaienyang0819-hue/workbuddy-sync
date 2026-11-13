"""Local, auditable corpus candidate retrieval. No model calls or embeddings."""
import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIBRARY = ROOT / "references" / "playmate_library.json"
SOURCE_ROOT = Path("G:/project_output/ai_teammate_陪玩语料调研")
FIELDS = ("intent", "emotion", "phase", "interaction", "topic", "style")
WEIGHTS = {"intent": 5, "emotion": 2, "phase": 4, "interaction": 4, "topic": 3, "style": 1}
ALIASES = (
    ("担心", "不确定", "没玩过", "不会玩", "玩不明白", "陌生地图", "新地图"),
    ("紧张", "好怕", "惊慌", "急迫", "救我", "求助", "压力"),
    ("失误", "我的", "道歉", "掉装备", "事后受挫", "失望", "受挫"),
    ("共玩", "参与", "参战", "一起打", "一起玩", "共同目标"),
    ("结束", "不玩", "去忙", "退出", "告别", "尊重退出"),
    ("闲聊", "自我表达", "生活", "兴趣", "话题", "旅行"),
    ("甜", "专属", "亲近", "调侃", "香水", "羁绊"),
    ("物资", "给药", "让资源", "补给", "让渡成就"),
    ("夸赞", "手气", "高光", "具体反馈", "惊喜", "操作"),
)


def normalize(value):
    return re.sub(r"[^\w\u3400-\u9fff]", "", str(value).lower())


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def load_library():
    return json.loads(LIBRARY.read_text(encoding="utf-8"))


def resolve_source(item, source_root=None):
    if source_root:
        return Path(source_root) / item["source_file"]
    return Path(item["source_path"])


def verify_item(item, source_root=None):
    actual = [row["raw"] for row in item["excerpt"]]
    snapshot_hash = digest("\n".join(actual).encode("utf-8"))
    if snapshot_hash != item["excerpt_sha256"]:
        return "snapshot_integrity_error"
    expected_numbers = list(range(item["start_line"], item["end_line"] + 1))
    if [row["line"] for row in item["excerpt"]] != expected_numbers:
        return "snapshot_integrity_error"
    timestamp = re.compile(r"^\[([^,]+),([^,]+),(\d+)\]\s*(.*)$")
    for row in item["excerpt"]:
        match = timestamp.match(row["raw"])
        text = match.group(4) if match else row["raw"]
        if row["text"] != text:
            return "snapshot_integrity_error"
        if match and (row.get("start_time"), row.get("end_time"), row.get("speaker_id")) != match.group(1, 2, 3):
            return "snapshot_integrity_error"
    path = resolve_source(item, source_root)
    if not path.is_file():
        return "snapshot_only_source_missing"
    raw = path.read_bytes()
    if digest(raw) != item["source_sha256"]:
        return "source_changed_rebuild_required"
    lines = raw.decode("utf-8-sig").splitlines()
    expected = lines[item["start_line"] - 1:item["end_line"]]
    return "verified_current_source" if expected == actual else "excerpt_mismatch"


def tokenize_query(query):
    terms = {normalize(x) for x in re.split(r"[\s，。；、！？,:;!?]+", query) if normalize(x)}
    whole = normalize(query)
    for group in ALIASES:
        if any(normalize(word) in whole for word in group):
            terms.update(normalize(word) for word in group)
    return terms


def compatible(a, b):
    a, b = normalize(a), normalize(b)
    if not a or not b or a in {"未明", "未核实"} or b in {"未明", "未核实"}:
        return False
    return a == b or (min(len(a), len(b)) >= 2 and (a in b or b in a))


def score_item(item, query, features):
    score, reasons, anchors = 0.0, [], 0
    terms = tokenize_query(query)
    for field in FIELDS:
        tags = item.get(field, [])
        supplied = features.get(field, [])
        matches = [tag for tag in tags if any(compatible(tag, val) for val in supplied)]
        query_matches = [tag for tag in tags if any(compatible(tag, term) for term in terms)]
        if matches:
            score += WEIGHTS[field] + min(len(matches) - 1, 2)
            reasons.append(field + ": " + "、".join(matches))
            if field in {"intent", "phase", "interaction", "topic"}:
                anchors += 1
        elif query_matches:
            score += WEIGHTS[field] * 0.65
            reasons.append(field + "（词义候选）: " + "、".join(query_matches[:3]))
            if field in {"intent", "interaction", "topic"}:
                anchors += 1
    phase = features.get("phase", [])
    known = [p for p in item.get("phase", []) if p != "未明"]
    if phase and known and not any(compatible(p, val) for p in known for val in phase):
        score -= 4
        reasons.append("phase_mismatch: 仅可考虑交互类比，不可当同阶段实录")
    if features.get("pressure") and item["pressure"] not in {features["pressure"], "未明"}:
        score -= 2
        reasons.append("pressure_mismatch: 不照搬发话长度与战术节奏")
    if features.get("game") and item["game"] == features["game"]:
        score += 1
        reasons.append("game: 同游戏标注，仍需核实机制")
    text = normalize(item["title"] + item["transfer"] + "".join(r["text"] for r in item["excerpt"]))
    lexical = [term for term in terms if len(term) >= 2 and term in text]
    if lexical:
        score += min(len(lexical), 4) * 0.4
        reasons.append("text_terms: " + "、".join(sorted(lexical)[:6]))
    original_terms = {normalize(t) for t in re.split(r"[\s，。；、！？,:;!?]+", query) if normalize(t)}
    raw_text = normalize("".join(row["text"] for row in item["excerpt"]))
    literal_hits = [t for t in original_terms if len(t) >= 3 and t not in {"怎么办", "能不能", "我们一起", "说什么"} and t in raw_text]
    if literal_hits:
        score += 5
        anchors += 1
        reasons.append("literal_source: " + "、".join(sorted(literal_hits)[:4]))
    if not anchors:
        return None
    if item["evidence_kind"] == "summary":
        score -= 2
        reasons.append("evidence: 摘要补充，不是连续问答")
    elif item["polarity"] == "mixed":
        score -= 0.5
        reasons.append("evidence: 混合片段，只迁移明示的正向部分")
    if score < 3:
        return None
    return round(score, 2), reasons


def retrieve(lib, query, features, top=5, include_summary=False, polarity="usable", source_root=None):
    candidates, excluded = [], Counter()
    for item in lib["clips"]:
        if item["is_duplicate_cut"]:
            excluded["duplicate_cut"] += 1
            continue
        if item["evidence_kind"] == "narration":
            excluded["narration_not_dialogue"] += 1
            continue
        if item["evidence_kind"] == "summary" and not include_summary:
            excluded["summary_disabled"] += 1
            continue
        if polarity == "usable" and item["polarity"] == "negative":
            excluded["negative_not_positive_reference"] += 1
            continue
        if polarity == "negative" and item["polarity"] != "negative":
            continue
        status = verify_item(item, source_root)
        if status in {"source_changed_rebuild_required", "excerpt_mismatch", "snapshot_integrity_error"}:
            excluded[status] += 1
            continue
        ranked = score_item(item, query, features)
        if ranked is None:
            continue
        score, reasons = ranked
        candidate = dict(item)
        candidate.update(retrieval_score=score, match_reasons=reasons, source_status=status)
        candidates.append(candidate)
    candidates.sort(key=lambda c: (-c["retrieval_score"], c["evidence_kind"] == "summary", c["clip_id"]))
    selected, seen = [], set()
    for c in candidates:
        if c["excerpt_sha256"] in seen:
            continue
        seen.add(c["excerpt_sha256"])
        selected.append(c)
        if len(selected) == top:
            break
    unavailable = any(excluded[k] for k in ("source_changed_rebuild_required", "excerpt_mismatch", "snapshot_integrity_error"))
    status = "candidates_require_semantic_review" if selected else ("source_evidence_unavailable" if unavailable else "no_supported_match")
    return {
        "query": query, "features": features,
        "status": status,
        "method": "本地标签与词义候选召回；非向量检索，分数不是语义置信度或效果概率",
        "instruction": "读完整excerpt与limits，挑1–2段作类比。无匹配不编来源；快照缺原文件须标明。",
        "excluded": dict(excluded), "total_candidate_count": len(candidates), "results": selected,
    }


def build(annotations, source_root, output):
    manifests, raw_clips = {}, []
    for filename in annotations:
        doc = json.loads(Path(filename).read_text(encoding="utf-8"))
        for meta in doc["sources"]:
            name = Path(meta["file"]).name
            if name in manifests:
                raise ValueError("Repeated source manifest: " + name)
            if meta["read_complete"] is not True:
                raise ValueError("Incomplete semantic source review: " + name)
            path = Path(source_root) / name
            raw = path.read_bytes()
            lines = raw.decode("utf-8-sig").splitlines()
            manifests[name] = dict(meta, file=name, path=str(path), sha256=digest(raw), line_count=len(lines))
        raw_clips.extend(doc["clips"])
    actual = {p.name for p in Path(source_root).glob("*_转写.txt")}
    if actual != set(manifests):
        raise ValueError("Source coverage mismatch: " + str(actual ^ set(manifests)))
    clips, seen = [], set()
    timestamp = re.compile(r"^\[([^,]+),([^,]+),(\d+)\]\s*(.*)$")
    for entry in raw_clips:
        name = Path(entry["file"]).name
        meta = manifests[name]
        lines = Path(meta["path"]).read_text(encoding="utf-8-sig").splitlines()
        start, end = entry["start_line"], entry["end_line"]
        if type(start) is not int or type(end) is not int or not 1 <= start <= end <= len(lines):
            raise ValueError("Invalid span: " + name)
        key = (name, start, end)
        if key in seen:
            raise ValueError("Repeated annotated span: " + repr(key))
        seen.add(key)
        excerpt = []
        for number in range(start, end + 1):
            raw = lines[number - 1]
            match = timestamp.match(raw)
            row = {"line": number, "raw": raw, "text": match.group(4) if match else raw}
            if match:
                row.update(start_time=match.group(1), end_time=match.group(2), speaker_id=match.group(3))
            excerpt.append(row)
        kind = "narration" if "BV1yGF6ziERU" in name else meta["source_type"]
        turns = sum("speaker_id" in row for row in excerpt)
        if kind == "timestamped" and turns < 3:
            raise ValueError("Continuous dialogue needs >=3 ASR segments: " + repr(key))
        item = dict(entry)
        item.pop("file")
        item.update(
            clip_id=name.split("_")[0] + ":" + str(start) + "-" + str(end),
            source_file=name, source_path=meta["path"], source_sha256=meta["sha256"],
            source_notes=meta["notes"], evidence_kind=kind, asr_segments=turns,
            is_duplicate_cut="BV1yNaBzLEWz" in name,
            excerpt_sha256=digest("\n".join(r["raw"] for r in excerpt).encode("utf-8")), excerpt=excerpt,
            speaker_mapping_note="编号取自ASR；身份需结合文件头及上下文，混轮不修造成精确角色对话",
        )
        for field in FIELDS:
            if not isinstance(item.get(field), list):
                raise ValueError("Tags must be lists: " + field)
        if item["polarity"] not in {"positive", "mixed", "negative"}:
            raise ValueError("Unknown polarity")
        clips.append(item)
    lib = {
        "version": "3.0", "source_root": str(source_root),
        "evidence_note": "连续行不保证未剪辑或ASR无误。完整来源已阅读，但片段库是精选而非所有发言全索引；没有模型训练或留存验证。",
        "sources": sorted(manifests.values(), key=lambda m: m["file"]), "clips": clips,
    }
    out = Path(output)
    if not out.parent.is_dir() or out.exists():
        raise ValueError("Output parent must exist and output must be new: " + str(out))
    out.write_text(json.dumps(lib, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return stats(lib)


def stats(lib):
    return {
        "source_count": len(lib["sources"]),
        "source_types": dict(Counter(s["source_type"] for s in lib["sources"])),
        "clips": len(lib["clips"]), "evidence_kinds": dict(Counter(c["evidence_kind"] for c in lib["clips"])),
        "polarities": dict(Counter(c["polarity"] for c in lib["clips"])),
        "duplicate_cut_clips": sum(c["is_duplicate_cut"] for c in lib["clips"]),
        "primary_eligible_clips": sum(c["evidence_kind"] == "timestamped" and not c["is_duplicate_cut"] and c["polarity"] != "negative" for c in lib["clips"]),
        "verified_clips": dict(Counter(verify_item(c) for c in lib["clips"])),
    }


def self_test(lib):
    assert len({c["clip_id"] for c in lib["clips"]}) == len(lib["clips"])
    assert all(verify_item(c) == "verified_current_source" for c in lib["clips"])
    fear = retrieve(lib, "没玩过地图怎么办 我担心玩不明白", {"intent": ["担心", "陌生地图"], "phase": ["事前担心"]})
    assert any("BV1rqa8zHE5k:36-45" == c["clip_id"] for c in fear["results"])
    talk = retrieve(lib, "旅行 闲聊 分享经历", {"interaction": ["自我表达"], "topic": ["旅行"]})
    assert talk["results"] and talk["results"][0]["clip_id"] == "BV14UBSB7E3k:316-323"
    assert all(c["evidence_kind"] == "timestamped" and not c["is_duplicate_cut"] and c["polarity"] != "negative" for c in fear["results"] + talk["results"])
    empty = retrieve(lib, "量子纠缠量子计算", {})
    assert empty["status"] == "no_supported_match" and not empty["results"]
    current = lib["clips"][0]
    modified = dict(current, source_sha256="invalid")
    assert verify_item(modified) == "source_changed_rebuild_required"
    snapshot = dict(current, source_path=str(ROOT / "missing_source_for_test.txt"))
    assert verify_item(snapshot) == "snapshot_only_source_missing"
    literal = retrieve(lib, "甘孜川西", {})
    assert any(c["clip_id"] == "BV14UBSB7E3k:316-323" for c in literal["results"])
    tampered = json.loads(json.dumps(current))
    tampered["excerpt"][0]["text"] = "并不存在的原话"
    assert verify_item(tampered) == "snapshot_integrity_error"
    tampered["source_path"] = snapshot["source_path"]
    assert verify_item(tampered) == "snapshot_integrity_error"
    unavailable_lib = dict(lib, clips=[modified])
    unavailable = retrieve(unavailable_lib, "游戏", {"intent": current["intent"]})
    assert unavailable["status"] == "source_evidence_unavailable"
    return {"tests": ["all_excerpts_match", "ids_unique", "fear_retrieval", "travel_retrieval", "summary_negative_duplicate_gates", "no_match", "changed_source_block", "missing_source_label", "literal_source_retrieval", "tampered_text_block", "tampered_missing_source_block", "unavailable_not_no_match"], "result": "pass", "note": "检索和来源测试，不是生成效果测试"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    build_p = sub.add_parser("build")
    build_p.add_argument("--annotations", nargs="+", required=True)
    build_p.add_argument("--source-root", default=str(SOURCE_ROOT))
    build_p.add_argument("--output", default=str(LIBRARY))
    search = sub.add_parser("search")
    search.add_argument("--query", required=True)
    search.add_argument("--top", type=int, default=5, choices=range(1, 11))
    for field in FIELDS:
        search.add_argument("--" + field, action="append", default=[])
    search.add_argument("--pressure", choices=["高", "低", "未明"])
    search.add_argument("--game")
    search.add_argument("--source-root")
    search.add_argument("--include-summary", action="store_true")
    search.add_argument("--polarity", choices=["usable", "negative", "all"], default="usable")
    show = sub.add_parser("show")
    show.add_argument("--id", required=True)
    show.add_argument("--source-root")
    sub.add_parser("stats")
    sub.add_parser("self-test")
    args = parser.parse_args()
    if args.command == "build":
        result = build(args.annotations, args.source_root, args.output)
    else:
        lib = load_library()
        if args.command == "search":
            features = {field: getattr(args, field) for field in FIELDS if getattr(args, field)}
            for field in ("pressure", "game"):
                if getattr(args, field):
                    features[field] = getattr(args, field)
            result = retrieve(lib, args.query, features, args.top, args.include_summary, args.polarity, args.source_root)
        elif args.command == "show":
            matches = [c for c in lib["clips"] if c["clip_id"] == args.id]
            if not matches:
                raise ValueError("Unknown clip id: " + args.id)
            item = dict(matches[0])
            item["source_status"] = verify_item(item, args.source_root)
            if item["source_status"] in {"source_changed_rebuild_required", "excerpt_mismatch", "snapshot_integrity_error"}:
                raise ValueError(item["source_status"])
            result = item
        elif args.command == "stats":
            result = stats(lib)
        else:
            result = self_test(lib)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, AssertionError) as error:
        print(json.dumps({"error": str(error) or "assertion_failed"}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
