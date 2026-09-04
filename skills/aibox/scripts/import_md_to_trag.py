"""
AIBox Skill — 本地文档批量导入 TRAG 向量知识库

流程：
  扫描目录 → 文件白名单过滤 → 文档转 Markdown → 分块 → 调用后端接口逐块导入

白名单文件类型：
  - Markdown : .md / .markdown        （原样读取）
  - Text     : .txt                   （原样读取）
  - PDF      : .pdf                   （markitdown 转 Markdown）
  - Word     : .doc / .docx           （markitdown 转 Markdown）
  - Excel    : .xls / .xlsx           （markitdown 转 Markdown）

不在白名单内的文件（图片、音视频、压缩包、二进制等）一律跳过并输出提醒。

用法：
    python3 {SKILL_DIR}/scripts/import_md_to_trag.py \\
        --dir /path/to/docs \\
        --collection col-xxxxxx

清空指定 collection 的全部内容：
    python3 {SKILL_DIR}/scripts/import_md_to_trag.py \\
        --clean \\
        --collection col-xxxxxx

可选参数：
    --base-url    AIBox 后端地址（默认 WORKFLOW_BASE_URL 或 http://ai.px.woa.com）
    --chunk-size  分块字符数（默认 1500）
    --chunk-overlap 分块重叠字符数（默认 200）
    --encoding    文本文件编码（默认 utf-8）
    --ext         限定扫描的白名单扩展名（不含点号，可多个），默认全部白名单
    --dry-run     只扫描/过滤/转换/分块，不调用后端
    --delay       chunk 间请求间隔秒数（默认 0.2）
    --clean       清空 --collection 指定集合的全部内容（不导入）
    --yes/-y      清空时跳过交互确认（危险）
"""

from __future__ import annotations

import argparse
import getpass
import os
import re
import sys
import time
from pathlib import Path
from typing import Optional

# ── Windows 中文编码兼容 ──────────────────────────────────────────────

if sys.platform == "win32":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    try:
        os.system("chcp 65001 >nul 2>&1")
    except Exception:
        pass
    import io
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True)
    if hasattr(sys.stderr, "buffer"):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace", line_buffering=True)

# ── 第三方依赖（宽松导入，缺失时仅降级） ──────────────────────────────

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    import requests as _requests
except ImportError:
    print("❌ 缺少 requests 库，请运行: pip install requests")
    sys.exit(1)

# auth.py 与本脚本同目录
_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

try:
    from auth import build_auth_headers as _build_auth_headers
except Exception:
    def _build_auth_headers():
        return {}

# ── 常量 ─────────────────────────────────────────────────────────────

TRAG_MAX_INPUT_LENGTH = 3000      # 与服务端 _TRAG_MAX_TEXT_LENGTH 一致
DEFAULT_CHUNK_SIZE = 1500
DEFAULT_CHUNK_OVERLAP = 200
DEFAULT_DELAY = 0.2

# 文件白名单：key=扩展名（小写无点），value=处理方式
_PLAINTEXT_EXTS = {"md", "markdown", "txt"}
_CONVERT_EXTS   = {"pdf", "doc", "docx", "xls", "xlsx"}
SUPPORTED_EXTS  = _PLAINTEXT_EXTS | _CONVERT_EXTS

# 单条最大重试次数
MAX_RETRIES = 3

# 后端 API 路径
IMPORT_PATH = "/api/knowledge/trag/import-text"
CLEAN_PATH = "/api/knowledge/trag/clean-collection"

PROXY_USER = os.getenv("PROXY_USER", "") or getpass.getuser()
WORKFLOW_BASE_URL = os.getenv("WORKFLOW_BASE_URL", "http://ai.px.woa.com")

# ── markitdown 可用性检测 ─────────────────────────────────────────────

def _check_markitdown() -> bool:
    try:
        from markitdown import MarkItDown  # noqa: F401
        return True
    except ImportError:
        return False

_MARKITDOWN_AVAILABLE = _check_markitdown()

# ── doc_id 生成（与 import_md_to_rag.py 逻辑一致） ───────────────────

_DOC_ID_SAFE = re.compile(r"[^a-zA-Z0-9_\-]")


def make_doc_id(rel_path: Path) -> str:
    stem = str(rel_path.with_suffix(""))
    doc_id = stem.replace("/", "_").replace("\\", "_")
    doc_id = _DOC_ID_SAFE.sub("-", doc_id)
    while "--" in doc_id:
        doc_id = doc_id.replace("--", "-")
    return doc_id.strip("-")


# ── 文本分块 ─────────────────────────────────────────────────────────

def split_text(
    content: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[str]:
    """按 Markdown 边界切分文本，确保每块不超过 TRAG_MAX_INPUT_LENGTH。"""
    if len(content) <= TRAG_MAX_INPUT_LENGTH:
        return [content]

    try:
        from langchain_text_splitters import RecursiveCharacterTextSplitter, Language
        splitter = RecursiveCharacterTextSplitter.from_language(
            language=Language.MARKDOWN,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            strip_whitespace=True,
        )
    except ImportError:
        # 降级：按行简单切分
        print("  [警告] langchain_text_splitters 未安装，使用简单切分；建议: pip install langchain-text-splitters")
        return _simple_split(content, chunk_size, chunk_overlap)

    chunks = splitter.split_text(content)
    result: list[str] = []
    for chunk in chunks:
        if len(chunk) > TRAG_MAX_INPUT_LENGTH:
            sub = RecursiveCharacterTextSplitter.from_language(
                language=Language.MARKDOWN,
                chunk_size=TRAG_MAX_INPUT_LENGTH - chunk_overlap,
                chunk_overlap=chunk_overlap,
                strip_whitespace=True,
            )
            result.extend(sub.split_text(chunk))
        else:
            result.append(chunk)
    return result


def _simple_split(content: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    """简单按字符数切分（langchain 不可用时的降级方案）。"""
    chunks: list[str] = []
    start = 0
    while start < len(content):
        end = min(start + chunk_size, len(content))
        chunks.append(content[start:end])
        start = end - chunk_overlap
        if start >= end:
            break
    return chunks


# ── 纯文本稳健读取 ────────────────────────────────────────────────────

def _read_text_file(filepath: Path, encoding: str = "utf-8") -> str:
    """
    稳健读取纯文本文件（md / markdown / txt），原样返回内容。
    优先使用指定编码，失败时按常见编码依次回退（处理繁体 Big5/CP950 等）。
    全部失败时以 utf-8 + errors='replace' 兜底，保证不抛异常。
    """
    candidates = [encoding, "utf-8", "utf-8-sig", "gb18030", "big5", "cp950", "latin-1"]
    seen: set[str] = set()
    for enc in candidates:
        if not enc or enc.lower() in seen:
            continue
        seen.add(enc.lower())
        try:
            return filepath.read_text(encoding=enc)
        except (UnicodeDecodeError, LookupError):
            continue
    # 兜底：替换无法解码的字节，避免整体失败
    return filepath.read_text(encoding="utf-8", errors="replace")


# ── 文件转 Markdown ───────────────────────────────────────────────────

def convert_to_markdown(filepath: Path, encoding: str = "utf-8") -> Optional[str]:
    """
    将文件转换为 Markdown 字符串。
    纯文本类直接读取；PDF/Word/Excel 用 markitdown 转换。
    转换失败返回 None。
    """
    ext = filepath.suffix.lstrip(".").lower()

    # 纯文本：稳健读取（处理繁体 Big5/CP950 等非 UTF-8 编码）
    if ext in _PLAINTEXT_EXTS:
        try:
            return _read_text_file(filepath, encoding)
        except Exception as e:
            print(f"  [错误] 无法读取 {filepath}: {e}")
            return None

    # 需要转换的格式：pdf / doc / docx / xls / xlsx
    if ext in _CONVERT_EXTS:
        if not _MARKITDOWN_AVAILABLE:
            print(
                f"  [跳过] markitdown 未安装，无法转换 {filepath.name}；"
                "请运行: pip install markitdown"
            )
            return None
        try:
            from markitdown import MarkItDown
            md = MarkItDown()
            result = md.convert(str(filepath))
            text = result.text_content or ""
            if not text.strip():
                print(f"  [警告] {filepath.name} 转换结果为空，跳过")
                return None
            # 加文件头注释，便于溯源
            header = f"# {filepath.name}\n\n<!-- source: {filepath} -->\n<!-- converted_by: aibox_skill -->\n\n"
            return header + text
        except Exception as e:
            print(f"  [错误] 转换失败 {filepath.name}: {e}")
            return None

    return None  # 不应到达此处


# ── 请求封装 ──────────────────────────────────────────────────────────

def _api_url(base_url: str, path: str) -> str:
    sep = "&" if "?" in path else "?"
    return f"{base_url}{path}{sep}from=aibox"


def _headers() -> dict:
    h = {"Content-Type": "application/json"}
    if PROXY_USER:
        h["X-Proxy-User"] = PROXY_USER
    try:
        h.update(_build_auth_headers())
    except Exception:
        pass
    return h


def import_chunk(
    base_url: str,
    collection: str,
    text: str,
    doc_id: str,
    metadata: dict,
) -> bool:
    """调用后端接口导入单个 chunk。成功返回 True，失败返回 False。"""
    url = _api_url(base_url, IMPORT_PATH)
    payload = {
        "collection": collection,
        "text": text,
        "doc_id": doc_id,
        "metadata": metadata,
    }
    for attempt in range(MAX_RETRIES):
        try:
            resp = _requests.post(url, json=payload, headers=_headers(), timeout=120)
            resp.raise_for_status()
            return True
        except _requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response is not None else "?"
            detail = ""
            try:
                detail = e.response.json().get("detail", "") if e.response else ""
            except Exception:
                pass
            if status in (400, 401, 403):
                # 客户端错误，不重试
                print(f"    ❌ HTTP {status}: {detail or e}")
                return False
            if attempt < MAX_RETRIES - 1:
                wait = (attempt + 1) * 5
                print(f"    ⚠️  HTTP {status} (第{attempt+1}次)，{wait}s 后重试...")
                time.sleep(wait)
            else:
                print(f"    ❌ HTTP {status}: {detail or e}")
                return False
        except _requests.exceptions.ConnectionError:
            if attempt < MAX_RETRIES - 1:
                print(f"    ⚠️  连接失败 (第{attempt+1}次)，5s 后重试...")
                time.sleep(5)
            else:
                print(f"    ❌ 连接失败: {base_url}")
                return False
        except _requests.exceptions.Timeout:
            if attempt < MAX_RETRIES - 1:
                print(f"    ⚠️  请求超时 (第{attempt+1}次)，5s 后重试...")
                time.sleep(5)
            else:
                print("    ❌ 请求超时")
                return False
        except Exception as e:
            print(f"    ❌ 请求异常: {e}")
            return False
    return False


def clean_collection(base_url: str, collection: str) -> bool:
    """调用后端接口清空指定 collection 的全部文档。成功返回 True。"""
    url = _api_url(base_url, CLEAN_PATH)
    payload = {"collection": collection, "confirm": True}
    for attempt in range(MAX_RETRIES):
        try:
            resp = _requests.post(url, json=payload, headers=_headers(), timeout=120)
            resp.raise_for_status()
            return True
        except _requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response is not None else "?"
            detail = ""
            try:
                detail = e.response.json().get("detail", "") if e.response else ""
            except Exception:
                pass
            if status in (400, 401, 403):
                print(f"  ❌ HTTP {status}: {detail or e}")
                return False
            if attempt < MAX_RETRIES - 1:
                wait = (attempt + 1) * 5
                print(f"  ⚠️  HTTP {status} (第{attempt+1}次)，{wait}s 后重试...")
                time.sleep(wait)
            else:
                print(f"  ❌ HTTP {status}: {detail or e}")
                return False
        except (_requests.exceptions.ConnectionError, _requests.exceptions.Timeout):
            if attempt < MAX_RETRIES - 1:
                print(f"  ⚠️  连接失败/超时 (第{attempt+1}次)，5s 后重试...")
                time.sleep(5)
            else:
                print(f"  ❌ 连接失败/超时: {base_url}")
                return False
        except Exception as e:
            print(f"  ❌ 请求异常: {e}")
            return False
    return False


def run_clean(base_url: str, collection: str, assume_yes: bool = False) -> bool:
    """清空指定 collection 全部内容（含交互确认）。"""
    print(f"\n{'=' * 60}")
    print("  清空 TRAG collection")
    print(f"  后端地址  : {base_url}")
    print(f"  目标集合  : {collection}")
    print(f"{'=' * 60}\n")
    print("⚠️  此操作将删除该 collection 的全部文档，且不可恢复！\n")

    if not assume_yes:
        try:
            answer = input(f"确认清空 {collection} ？输入集合编码以确认: ").strip()
        except EOFError:
            answer = ""
        if answer != collection:
            print("已取消（输入与集合编码不一致）。")
            return False

    print(f"\n[清空] 正在清空 {collection} ...")
    ok = clean_collection(base_url, collection)
    if ok:
        print(f"✅ collection {collection} 已清空")
    else:
        print(f"❌ collection {collection} 清空失败")
    return ok


# ── 核心逻辑 ──────────────────────────────────────────────────────────

def run_import(
    root_dir: str,
    collection: str,
    base_url: str = WORKFLOW_BASE_URL,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    encoding: str = "utf-8",
    ext_filter: Optional[set[str]] = None,
    dry_run: bool = False,
    delay: float = DEFAULT_DELAY,
) -> dict:
    """
    核心导入流程。返回统计字典。
    """
    root = Path(root_dir).resolve()
    if not root.is_dir():
        print(f"❌ 目录不存在: {root}")
        sys.exit(1)

    # 决定本次扫描的扩展名白名单
    active_exts = ext_filter if ext_filter else SUPPORTED_EXTS

    # ── 扫描所有文件 ──────────────────────────────────────────
    all_files = sorted(root.rglob("*"))
    all_files = [f for f in all_files if f.is_file()]

    print(f"\n{'=' * 60}")
    print(f"  扫描目录  : {root}")
    print(f"  目标集合  : {collection}")
    print(f"  后端地址  : {base_url}")
    print(f"  分块大小  : {chunk_size} 字符 (重叠 {chunk_overlap})")
    print(f"  模式      : {'预览 (dry-run)' if dry_run else '正式导入'}")
    print(f"  markitdown: {'可用' if _MARKITDOWN_AVAILABLE else '不可用（PDF/Word/Excel 将跳过）'}")
    print(f"{'=' * 60}\n")

    # ── 分类文件 ──────────────────────────────────────────────
    to_process: list[Path] = []
    skipped_unsupported: list[tuple[Path, str]] = []

    for f in all_files:
        ext = f.suffix.lstrip(".").lower()
        if not ext:
            skipped_unsupported.append((f, "无扩展名"))
            continue
        if ext not in SUPPORTED_EXTS:
            skipped_unsupported.append((f, f"不支持的文件类型 (.{ext})"))
            continue
        if ext not in active_exts:
            skipped_unsupported.append((f, f"已通过 --ext 排除 (.{ext})"))
            continue
        to_process.append(f)

    # 输出跳过提醒
    if skipped_unsupported:
        print("[跳过文件]")
        for fp, reason in skipped_unsupported:
            rel = fp.relative_to(root)
            print(f"  [跳过] {reason}: {rel}")
        print()

    if not to_process:
        print("[提示] 没有可处理的文件。")
        return {
            "scanned": len(all_files),
            "processed": 0,
            "skipped": len(skipped_unsupported),
            "failed_files": 0,
            "chunks_total": 0,
            "chunks_imported": 0,
            "chunks_failed": 0,
        }

    print(f"[文件列表] 共 {len(all_files)} 个扫描文件，{len(to_process)} 个待处理，{len(skipped_unsupported)} 个跳过\n")

    # ── 转换 & 分块 ───────────────────────────────────────────
    all_chunks: list[dict] = []      # {text, doc_id, metadata, rel_path}
    failed_files: list[Path] = []

    for filepath in to_process:
        rel = filepath.relative_to(root)
        ext = filepath.suffix.lstrip(".").lower()
        print(f"  处理: {rel}")

        content = convert_to_markdown(filepath, encoding)
        if content is None:
            failed_files.append(filepath)
            continue

        content = content.strip()
        if not content:
            print(f"    [跳过] 内容为空")
            skipped_unsupported.append((filepath, "内容为空"))
            continue

        chunks = split_text(content, chunk_size, chunk_overlap)
        doc_id_base = make_doc_id(rel)

        for i, chunk_text in enumerate(chunks):
            chunk_id = doc_id_base if len(chunks) == 1 else f"{doc_id_base}_chunk_{i}"
            meta = {
                "source": str(filepath),
                "rel_path": str(rel),
                "filename": filepath.name,
                "dir": str(rel.parent),
                "ext": ext,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "import_source": "aibox_skill",
            }
            all_chunks.append({"text": chunk_text, "doc_id": chunk_id, "metadata": meta})

        suffix_str = "" if len(chunks) == 1 else f"_chunk_0~{len(chunks)-1}"
        print(f"    → {len(chunks)} 块, id={doc_id_base}{suffix_str}")

    print(f"\n[汇总] {len(to_process)} 个文件 → {len(all_chunks)} 个文本块，{len(failed_files)} 个转换失败\n")

    if dry_run:
        print("[dry-run] 预览模式，未调用后端。")
        return {
            "scanned": len(all_files),
            "processed": len(to_process),
            "skipped": len(skipped_unsupported),
            "failed_files": len(failed_files),
            "chunks_total": len(all_chunks),
            "chunks_imported": 0,
            "chunks_failed": 0,
        }

    if not all_chunks:
        print("[提示] 没有可导入的文本块。")
        return {
            "scanned": len(all_files),
            "processed": len(to_process),
            "skipped": len(skipped_unsupported),
            "failed_files": len(failed_files),
            "chunks_total": 0,
            "chunks_imported": 0,
            "chunks_failed": 0,
        }

    # ── 逐块导入 ──────────────────────────────────────────────
    print(f"[导入] 开始向 {collection} 写入 {len(all_chunks)} 个文本块...\n")
    imported = 0
    failed_chunks = 0

    for idx, item in enumerate(all_chunks, 1):
        rel_path = item["metadata"]["rel_path"]
        chunk_idx = item["metadata"]["chunk_index"]
        total = item["metadata"]["total_chunks"]
        print(f"  [{idx}/{len(all_chunks)}] {rel_path} chunk {chunk_idx}/{total-1}  doc_id={item['doc_id']}")

        ok = import_chunk(
            base_url=base_url,
            collection=collection,
            text=item["text"],
            doc_id=item["doc_id"],
            metadata=item["metadata"],
        )
        if ok:
            imported += 1
        else:
            failed_chunks += 1

        if delay > 0 and idx < len(all_chunks):
            time.sleep(delay)

    # ── 最终汇总 ──────────────────────────────────────────────
    print(f"\n{'=' * 60}")
    print("  导入完成！")
    print(f"  扫描文件     : {len(all_files)}")
    print(f"  处理文件     : {len(to_process)}")
    print(f"  跳过文件     : {len(skipped_unsupported)}")
    print(f"  转换失败文件 : {len(failed_files)}")
    print(f"  文本块总数   : {len(all_chunks)}")
    print(f"  成功导入     : {imported}")
    print(f"  导入失败     : {failed_chunks}")
    print(f"{'=' * 60}")

    return {
        "scanned": len(all_files),
        "processed": len(to_process),
        "skipped": len(skipped_unsupported),
        "failed_files": len(failed_files),
        "chunks_total": len(all_chunks),
        "chunks_imported": imported,
        "chunks_failed": failed_chunks,
    }


# ── 命令行入口 ────────────────────────────────────────────────────────

def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="AIBox Skill — 本地文档批量导入 TRAG 向量知识库",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
支持的文件类型（白名单）:
  Markdown : .md / .markdown     （原样读取）
  Text     : .txt                （原样读取）
  PDF      : .pdf                （markitdown 转 Markdown）
  Word     : .doc / .docx        （markitdown 转 Markdown）
  Excel    : .xls / .xlsx        （markitdown 转 Markdown）

其他文件类型（图片、音视频、压缩包等）一律跳过并输出提醒。

示例:
  python3 import_md_to_trag.py --dir ./docs --collection col-xxxxxx
  python3 import_md_to_trag.py --dir ./docs --collection col-xxxxxx --dry-run
  python3 import_md_to_trag.py --dir ./docs --collection col-xxxxxx --ext md txt
  python3 import_md_to_trag.py --clean --collection col-xxxxxx
  python3 import_md_to_trag.py --clean --collection col-xxxxxx --yes
        """,
    )
    parser.add_argument("--dir", "-d", help="本地文档目录（递归扫描）；导入模式必填")
    parser.add_argument("--collection", "-c", required=True, help="TRAG collection code（如 col-xxxxxxxx）")
    parser.add_argument(
        "--base-url",
        default=WORKFLOW_BASE_URL,
        help=f"AIBox 后端地址（默认 {WORKFLOW_BASE_URL}）",
    )
    parser.add_argument("--chunk-size", type=int, default=DEFAULT_CHUNK_SIZE, help=f"分块大小，字符数（默认 {DEFAULT_CHUNK_SIZE}）")
    parser.add_argument("--chunk-overlap", type=int, default=DEFAULT_CHUNK_OVERLAP, help=f"分块重叠字符数（默认 {DEFAULT_CHUNK_OVERLAP}）")
    parser.add_argument("--encoding", default="utf-8", help="文本文件编码（默认 utf-8）")
    parser.add_argument(
        "--ext",
        nargs="+",
        default=None,
        metavar="EXT",
        help=f"限定白名单内的扩展名（不含点号），可多个；默认全部白名单：{' '.join(sorted(SUPPORTED_EXTS))}",
    )
    parser.add_argument("--dry-run", action="store_true", help="只扫描/过滤/转换/分块，不调用后端")
    parser.add_argument("--delay", type=float, default=DEFAULT_DELAY, help=f"chunk 间请求间隔秒数（默认 {DEFAULT_DELAY}）")
    parser.add_argument("--clean", action="store_true", help="清空 --collection 指定集合的全部内容（不导入）")
    parser.add_argument("--yes", "-y", action="store_true", help="清空时跳过交互确认（危险）")
    return parser.parse_args()


def main():
    args = _parse_args()

    # 清空模式：清空 collection 后直接退出，不走导入流程
    if args.clean:
        ok = run_clean(args.base_url, args.collection, assume_yes=args.yes)
        sys.exit(0 if ok else 1)

    # 导入模式必须指定目录
    if not args.dir:
        print("❌ 导入模式必须指定 --dir；如需清空集合请使用 --clean")
        sys.exit(1)

    # 处理 --ext 过滤
    ext_filter: Optional[set[str]] = None
    if args.ext:
        requested = {e.strip().lower().lstrip(".") for e in args.ext}
        invalid = requested - SUPPORTED_EXTS
        if invalid:
            print(f"❌ --ext 包含不支持的类型：{', '.join(sorted(invalid))}；仅支持：{', '.join(sorted(SUPPORTED_EXTS))}")
            sys.exit(1)
        ext_filter = requested

    result = run_import(
        root_dir=args.dir,
        collection=args.collection,
        base_url=args.base_url,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        encoding=args.encoding,
        ext_filter=ext_filter,
        dry_run=args.dry_run,
        delay=args.delay,
    )

    sys.exit(1 if result.get("chunks_failed", 0) > 0 or result.get("failed_files", 0) > 0 else 0)


if __name__ == "__main__":
    try:
        main()
    except (UnicodeEncodeError, UnicodeDecodeError) as e:
        sys.stderr.write(f"[encoding error] {e}\n")
        sys.exit(1)
    except BrokenPipeError:
        sys.exit(0)
    except KeyboardInterrupt:
        print("\n⏹️  已取消")
        sys.exit(0)
