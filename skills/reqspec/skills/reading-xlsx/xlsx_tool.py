# -*- coding: utf-8 -*-
"""
xlsx_tool.py — 通用 xlsx 读取与图片提取工具

功能：
  1. list    — 列出 xlsx 中所有 sheet 名称
  2. read    — 读取指定 sheet 的文本内容（支持多sheet、模糊匹配）
  3. images  — 提取指定 sheet 关联的内嵌图片
  4. media   — 列出 xlsx 中所有媒体文件
  5. dump    — 一次性导出所有 sheet 文本 + 所有图片

零外部依赖：仅使用 Python 标准库（zipfile + xml.etree）。
适用于不想安装 pandas / openpyxl 的环境。

用法：
  python xlsx_tool.py <xlsx文件> <命令> [选项]

示例：
  python xlsx_tool.py data.xlsx list
  python xlsx_tool.py data.xlsx read "装备保险"
  python xlsx_tool.py data.xlsx read "装备保险" "大厅"
  python xlsx_tool.py data.xlsx read --all
  python xlsx_tool.py data.xlsx images "装备保险" --output ./imgs
  python xlsx_tool.py data.xlsx media
  python xlsx_tool.py data.xlsx dump --output ./export
"""

import zipfile
import xml.etree.ElementTree as ET
import os
import sys
import argparse
import re

# ============================================================
# XML 命名空间常量
# ============================================================
NS = {
    'ss':  'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
    'r':   'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'pkg': 'http://schemas.openxmlformats.org/package/2006/relationships',
    'xdr': 'http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing',
    'a':   'http://schemas.openxmlformats.org/drawingml/2006/main',
}


# ============================================================
# 工具函数
# ============================================================
def col_letter_to_num(col_str: str) -> int:
    """将列字母转换为数字索引（A=0, B=1, ..., AA=26, ...）"""
    result = 0
    for c in col_str:
        result = result * 26 + (ord(c.upper()) - ord('A') + 1)
    return result - 1


def parse_cell_ref(ref: str):
    """解析单元格引用（如 'B3'）为 (col_index, row_index)"""
    col_str = ''
    row_str = ''
    for c in ref:
        if c.isalpha():
            col_str += c
        else:
            row_str += c
    return col_letter_to_num(col_str), int(row_str) - 1


def num_to_col_letter(n: int) -> str:
    """将数字索引转换为列字母（0=A, 1=B, ..., 26=AA, ...）"""
    result = ''
    n += 1
    while n > 0:
        n, rem = divmod(n - 1, 26)
        result = chr(65 + rem) + result
    return result


# ============================================================
# 核心类
# ============================================================
class XlsxReader:
    """零依赖 xlsx 读取器，基于 zipfile + xml.etree 解析 OOXML 结构"""

    def __init__(self, xlsx_path: str):
        self.xlsx_path = xlsx_path
        if not os.path.isfile(xlsx_path):
            raise FileNotFoundError(f"文件不存在: {xlsx_path}")
        self._z = zipfile.ZipFile(xlsx_path, 'r')
        self._shared_strings = self._load_shared_strings()
        self._sheet_info, self._rels = self._load_workbook()

    def close(self):
        self._z.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    # ---------- 内部加载 ----------

    def _load_shared_strings(self) -> list:
        """加载共享字符串表"""
        strings = []
        if 'xl/sharedStrings.xml' in self._z.namelist():
            tree = ET.parse(self._z.open('xl/sharedStrings.xml'))
            for si in tree.findall('.//ss:si', NS):
                texts = si.findall('.//ss:t', NS)
                strings.append(''.join(t.text or '' for t in texts))
        return strings

    def _load_workbook(self):
        """加载 workbook 和关系映射"""
        wb_tree = ET.parse(self._z.open('xl/workbook.xml'))
        sheets = []
        for s in wb_tree.findall('.//ss:sheet', NS):
            name = s.get('name')
            rid = s.get(f'{{{NS["r"]}}}id')
            sheets.append((name, rid))

        rels = {}
        rels_tree = ET.parse(self._z.open('xl/_rels/workbook.xml.rels'))
        for rel in rels_tree.findall(f'{{{NS["pkg"]}}}Relationship'):
            rels[rel.get('Id')] = rel.get('Target')

        return sheets, rels

    # ---------- 公开 API ----------

    def list_sheets(self) -> list:
        """返回所有 sheet 名称列表"""
        return [name for name, _ in self._sheet_info]

    def find_sheets(self, keywords: list) -> list:
        """模糊匹配 sheet 名称（包含任一关键词即匹配）"""
        if not keywords:
            return self.list_sheets()
        matched = []
        for name in self.list_sheets():
            for kw in keywords:
                if kw.lower() in name.lower():
                    matched.append(name)
                    break
        return matched

    def read_sheet(self, sheet_name: str, max_cols: int = 50, max_cell_len: int = 500) -> dict:
        """
        读取指定 sheet 的文本内容。
        返回: {
            'name': str,
            'rows': int,
            'cols': int,
            'merged_cells': [str, ...],
            'data': {row_idx: {col_idx: str, ...}, ...}
        }
        """
        # 找到 sheet 文件路径
        rid = None
        for name, r in self._sheet_info:
            if name == sheet_name:
                rid = r
                break
        if rid is None:
            raise ValueError(f"Sheet '{sheet_name}' 不存在。可用: {self.list_sheets()}")

        target = self._rels.get(rid, '')
        sheet_file = 'xl/' + target if not target.startswith('/') else target[1:]
        if sheet_file not in self._z.namelist():
            raise FileNotFoundError(f"Sheet 文件不存在: {sheet_file}")

        tree = ET.parse(self._z.open(sheet_file))
        root = tree.getroot()

        # 读取单元格数据
        rows_data = {}
        max_col = 0
        max_row = 0
        for row in root.findall('.//ss:sheetData/ss:row', NS):
            for cell in row.findall('ss:c', NS):
                ref = cell.get('r', '')
                cell_type = cell.get('t', '')
                value = self._get_cell_value(cell, cell_type)

                if ref and value.strip():
                    col, row_idx = parse_cell_ref(ref)
                    if col >= max_cols:
                        continue
                    if row_idx not in rows_data:
                        rows_data[row_idx] = {}
                    rows_data[row_idx][col] = value[:max_cell_len]
                    max_col = max(max_col, col)
                    max_row = max(max_row, row_idx)

        # 读取合并单元格
        merged = []
        for mc in root.findall('.//ss:mergeCells/ss:mergeCell', NS):
            merged.append(mc.get('ref', ''))

        return {
            'name': sheet_name,
            'rows': max_row + 1,
            'cols': max_col + 1,
            'merged_cells': merged,
            'data': rows_data,
            '_sheet_file': sheet_file,
        }

    def _get_cell_value(self, cell, cell_type: str) -> str:
        """提取单元格值（支持共享字符串、内联字符串、直接值）"""
        value_elem = cell.find('ss:v', NS)
        if value_elem is not None and value_elem.text is not None:
            if cell_type == 's':
                idx = int(value_elem.text)
                return self._shared_strings[idx] if idx < len(self._shared_strings) else f'[idx:{idx}]'
            return value_elem.text

        # 内联字符串 <is><t>...</t></is>
        is_elem = cell.find('ss:is', NS)
        if is_elem is not None:
            texts = is_elem.findall('.//ss:t', NS)
            return ''.join(t.text or '' for t in texts)

        return ''

    def get_sheet_images(self, sheet_name: str) -> list:
        """
        获取指定 sheet 关联的图片信息。
        返回: [{'embed_id': str, 'image_path': str, 'from_cell': str, 'to_cell': str, 'size': int}, ...]
        """
        result = self.read_sheet(sheet_name)
        sheet_file = result['_sheet_file']
        sheet_basename = os.path.basename(sheet_file)
        sheet_dir = os.path.dirname(sheet_file)
        sheet_rels_path = f"{sheet_dir}/_rels/{sheet_basename}.rels"

        if sheet_rels_path not in self._z.namelist():
            return []

        # 找 drawing 文件
        sheet_rels = ET.parse(self._z.open(sheet_rels_path))
        drawing_file = None
        for rel in sheet_rels.findall(f'{{{NS["pkg"]}}}Relationship'):
            if 'drawing' in rel.get('Type', ''):
                target = rel.get('Target')
                drawing_file = self._resolve_path(sheet_dir, target)
                break

        if not drawing_file or drawing_file not in self._z.namelist():
            return []

        # 解析 drawing XML 获取锚点信息
        draw_tree = ET.parse(self._z.open(drawing_file))
        anchors = []
        for anchor in draw_tree.iter():
            tag = anchor.tag.split('}')[-1] if '}' in anchor.tag else anchor.tag
            if tag in ('twoCellAnchor', 'oneCellAnchor', 'absoluteAnchor'):
                from_cell = self._get_anchor_cell(anchor, 'from')
                to_cell = self._get_anchor_cell(anchor, 'to')
                embed_id = ''
                for blip in anchor.iter(f'{{{NS["a"]}}}blip'):
                    embed_id = blip.get(f'{{{NS["r"]}}}embed', '')
                    break
                if embed_id:
                    anchors.append({
                        'embed_id': embed_id,
                        'from_cell': from_cell,
                        'to_cell': to_cell,
                    })

        # 解析 drawing rels 获取 embed → 图片路径映射
        drawing_dir = os.path.dirname(drawing_file)
        drawing_basename = os.path.basename(drawing_file)
        drawing_rels_path = f"{drawing_dir}/_rels/{drawing_basename}.rels"
        embed_map = {}
        if drawing_rels_path in self._z.namelist():
            drels_tree = ET.parse(self._z.open(drawing_rels_path))
            for rel in drels_tree.findall(f'{{{NS["pkg"]}}}Relationship'):
                rid = rel.get('Id')
                target = rel.get('Target')
                resolved = self._resolve_path(drawing_dir, target)
                embed_map[rid] = resolved

        # 组装结果
        images = []
        for a in anchors:
            img_path = embed_map.get(a['embed_id'], '')
            size = 0
            if img_path and img_path in self._z.namelist():
                size = self._z.getinfo(img_path).file_size
            images.append({
                'embed_id': a['embed_id'],
                'image_path': img_path,
                'from_cell': a['from_cell'],
                'to_cell': a['to_cell'],
                'size': size,
            })
        return images

    def extract_images(self, sheet_name: str, output_dir: str) -> list:
        """提取指定 sheet 的图片到本地目录。返回提取的文件列表。"""
        os.makedirs(output_dir, exist_ok=True)
        images = self.get_sheet_images(sheet_name)
        extracted = []
        for img in images:
            if img['image_path'] and img['image_path'] in self._z.namelist():
                fname = os.path.basename(img['image_path'])
                out_path = os.path.join(output_dir, fname)
                with self._z.open(img['image_path']) as src, open(out_path, 'wb') as dst:
                    dst.write(src.read())
                extracted.append({'file': out_path, 'size': img['size'], 'from_cell': img['from_cell']})
        return extracted

    def list_all_media(self) -> list:
        """列出 xlsx 中所有媒体文件"""
        media = []
        for f in sorted(self._z.namelist()):
            if 'media' in f.lower() or 'image' in f.lower():
                if not f.endswith('/'):
                    info = self._z.getinfo(f)
                    media.append({'path': f, 'size': info.file_size})
        return media

    def extract_all_media(self, output_dir: str) -> list:
        """提取所有媒体文件到本地目录"""
        os.makedirs(output_dir, exist_ok=True)
        extracted = []
        for m in self.list_all_media():
            fname = os.path.basename(m['path'])
            # 避免同名冲突
            out_path = os.path.join(output_dir, fname)
            counter = 1
            base, ext = os.path.splitext(fname)
            while os.path.exists(out_path):
                out_path = os.path.join(output_dir, f"{base}_{counter}{ext}")
                counter += 1
            with self._z.open(m['path']) as src, open(out_path, 'wb') as dst:
                dst.write(src.read())
            extracted.append(out_path)
        return extracted

    # ---------- 内部辅助 ----------

    def _resolve_path(self, base_dir: str, target: str) -> str:
        """解析相对路径"""
        if target.startswith('/'):
            return target[1:]
        # 处理 ../
        parts = (base_dir + '/' + target).replace('\\', '/').split('/')
        resolved = []
        for p in parts:
            if p == '..':
                if resolved:
                    resolved.pop()
            elif p and p != '.':
                resolved.append(p)
        return '/'.join(resolved)

    def _get_anchor_cell(self, anchor, direction: str) -> str:
        """从 drawing anchor 提取 from/to 单元格位置"""
        el = anchor.find(f'{{{NS["xdr"]}}}{direction}')
        if el is None:
            return ''
        col_el = el.find(f'{{{NS["xdr"]}}}col')
        row_el = el.find(f'{{{NS["xdr"]}}}row')
        if col_el is not None and row_el is not None:
            col_letter = num_to_col_letter(int(col_el.text))
            return f"{col_letter}{int(row_el.text) + 1}"
        return ''


# ============================================================
# 格式化输出
# ============================================================
def format_sheet_text(sheet_data: dict, fmt: str = 'table') -> str:
    """
    将 sheet 数据格式化为可读文本。
    fmt: 'table' (默认，管道分隔) | 'csv' | 'markdown'
    """
    data = sheet_data['data']
    max_row = sheet_data['rows']
    max_col = sheet_data['cols']
    lines = []

    if fmt == 'csv':
        import csv
        import io
        buf = io.StringIO()
        writer = csv.writer(buf)
        for r in range(max_row):
            row_vals = [data.get(r, {}).get(c, '') for c in range(max_col)]
            if any(v.strip() for v in row_vals):
                writer.writerow(row_vals)
        return buf.getvalue()

    elif fmt == 'markdown':
        # 找出有内容的列
        active_cols = set()
        for r_data in data.values():
            active_cols.update(r_data.keys())
        if not active_cols:
            return '(空sheet)'
        cols = sorted(active_cols)

        # 表头（使用列字母）
        headers = [num_to_col_letter(c) for c in cols]
        lines.append('| ' + ' | '.join(headers) + ' |')
        lines.append('| ' + ' | '.join(['---'] * len(cols)) + ' |')
        for r in range(max_row):
            if r not in data:
                continue
            vals = [data.get(r, {}).get(c, '') for c in cols]
            if any(v.strip() for v in vals):
                # 转义 markdown 管道符
                vals = [v.replace('|', '\\|') for v in vals]
                lines.append('| ' + ' | '.join(vals) + ' |')
        return '\n'.join(lines)

    else:  # table (default)
        for r in range(max_row):
            if r not in data:
                continue
            row_vals = []
            has_content = False
            for c in range(min(max_col, 30)):
                val = data.get(r, {}).get(c, '')
                if val:
                    has_content = True
                row_vals.append(val)
            if has_content:
                lines.append(f"R{r}: {' | '.join(row_vals)}")
        return '\n'.join(lines)


# ============================================================
# CLI 入口
# ============================================================
def main():
    parser = argparse.ArgumentParser(
        description='xlsx_tool — 通用 xlsx 读取与图片提取工具（零外部依赖）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  python xlsx_tool.py data.xlsx list
  python xlsx_tool.py data.xlsx read "装备保险"
  python xlsx_tool.py data.xlsx read "装备保险" "大厅"
  python xlsx_tool.py data.xlsx read --all
  python xlsx_tool.py data.xlsx read --all --format markdown
  python xlsx_tool.py data.xlsx images "装备保险" --output ./imgs
  python xlsx_tool.py data.xlsx media
  python xlsx_tool.py data.xlsx dump --output ./export
        """)
    parser.add_argument('xlsx', help='xlsx 文件路径')
    parser.add_argument('command', choices=['list', 'read', 'images', 'media', 'dump'],
                        help='执行的命令')
    parser.add_argument('sheets', nargs='*', help='目标 sheet 名称（支持模糊匹配）')
    parser.add_argument('--all', action='store_true', help='处理所有 sheet')
    parser.add_argument('--output', '-o', default='.', help='图片输出目录（默认当前目录）')
    parser.add_argument('--format', '-f', choices=['table', 'csv', 'markdown'], default='table',
                        help='文本输出格式（默认 table）')
    parser.add_argument('--max-cols', type=int, default=50, help='最大列数（默认 50）')
    parser.add_argument('--max-cell-len', type=int, default=500, help='单元格最大字符数（默认 500）')

    args = parser.parse_args()

    try:
        with XlsxReader(args.xlsx) as reader:
            if args.command == 'list':
                cmd_list(reader)
            elif args.command == 'read':
                cmd_read(reader, args)
            elif args.command == 'images':
                cmd_images(reader, args)
            elif args.command == 'media':
                cmd_media(reader)
            elif args.command == 'dump':
                cmd_dump(reader, args)
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_list(reader: XlsxReader):
    sheets = reader.list_sheets()
    print(f"共 {len(sheets)} 个 sheet：\n")
    for i, name in enumerate(sheets, 1):
        print(f"  {i}. {name}")


def cmd_read(reader: XlsxReader, args):
    if args.all:
        target_sheets = reader.list_sheets()
    elif args.sheets:
        target_sheets = reader.find_sheets(args.sheets)
        if not target_sheets:
            print(f"未匹配到 sheet。可用: {reader.list_sheets()}", file=sys.stderr)
            sys.exit(1)
    else:
        print("请指定 sheet 名称或使用 --all", file=sys.stderr)
        sys.exit(1)

    for name in target_sheets:
        data = reader.read_sheet(name, max_cols=args.max_cols, max_cell_len=args.max_cell_len)
        print(f"\n{'='*100}")
        print(f"  Sheet: {data['name']} ({data['rows']} 行 × {data['cols']} 列)")
        if data['merged_cells']:
            print(f"  合并单元格: {', '.join(data['merged_cells'][:10])}"
                  + (f" ... 共 {len(data['merged_cells'])} 处" if len(data['merged_cells']) > 10 else ''))
        print(f"{'='*100}\n")
        print(format_sheet_text(data, args.format))


def cmd_images(reader: XlsxReader, args):
    if not args.sheets:
        print("请指定 sheet 名称", file=sys.stderr)
        sys.exit(1)

    target_sheets = reader.find_sheets(args.sheets)
    for name in target_sheets:
        print(f"\n--- Sheet: {name} ---")
        images = reader.get_sheet_images(name)
        if not images:
            print("  (无关联图片)")
            continue

        print(f"  找到 {len(images)} 张图片：")
        for img in images:
            print(f"    {img['embed_id']}: {img['image_path']} "
                  f"({img['size']:,} bytes) [{img['from_cell']} → {img['to_cell']}]")

        # 提取图片
        extracted = reader.extract_images(name, args.output)
        print(f"\n  已提取 {len(extracted)} 张到 {os.path.abspath(args.output)}：")
        for e in extracted:
            print(f"    ✓ {os.path.basename(e['file'])} ({e['size']:,} bytes)")


def cmd_media(reader: XlsxReader):
    media = reader.list_all_media()
    print(f"共 {len(media)} 个媒体文件：\n")
    total_size = 0
    for m in media:
        print(f"  {m['path']}  ({m['size']:,} bytes)")
        total_size += m['size']
    print(f"\n  总计: {total_size:,} bytes ({total_size/1024/1024:.1f} MB)")


def cmd_dump(reader: XlsxReader, args):
    output_dir = args.output
    os.makedirs(output_dir, exist_ok=True)
    text_dir = os.path.join(output_dir, 'sheets')
    img_dir = os.path.join(output_dir, 'images')
    os.makedirs(text_dir, exist_ok=True)

    # 导出所有 sheet 文本
    for name in reader.list_sheets():
        data = reader.read_sheet(name, max_cols=args.max_cols, max_cell_len=args.max_cell_len)
        safe_name = re.sub(r'[\\/:*?"<>|]', '_', name)
        text_path = os.path.join(text_dir, f"{safe_name}.txt")
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(f"Sheet: {name} ({data['rows']} 行 × {data['cols']} 列)\n")
            if data['merged_cells']:
                f.write(f"合并单元格: {', '.join(data['merged_cells'])}\n")
            f.write('\n')
            f.write(format_sheet_text(data, args.format))
        print(f"  ✓ Sheet '{name}' → {text_path}")

    # 导出所有媒体
    media = reader.extract_all_media(img_dir)
    print(f"\n  ✓ {len(media)} 张图片 → {os.path.abspath(img_dir)}")
    print(f"\n导出完成 → {os.path.abspath(output_dir)}")


if __name__ == '__main__':
    main()
