"""AI 降噪扫描器：定位候选噪声（只报告，不修改文件）。

用法:
  python denoise_scan.py <file>                 扫描候选噪声
  python denoise_scan.py --compare <old> <new>  对比降噪前后字数与结构
支持 .html/.htm/.md/.txt 及其他纯文本。命中仅为候选，需按 SKILL.md 第 1 节逐条判断。
"""
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

# 类别 -> 正则列表。新增高频噪声词时追加到这里。
RULES = {
    "A1 套话/汇报体": [
        r"总之", r"总而言之", r"总的来说", r"值得注意的是", r"需要指出的是", r"需要注意的是",
        r"不难发现", r"不难看出", r"众所周知", r"由此可见", r"可以看出", r"显而易见",
        r"毋庸置疑", r"综上所述", r"综上", r"开门见山", r"汇报概要", r"一言以蔽之",
        r"换句话说", r"简单来说", r"事实上",
    ],
    "A2 空泛价值": [
        r"提升(玩家|用户)?体验", r"优化(了)?体验", r"增强(了)?沉浸感", r"更有价值", r"赋能",
        r"闭环", r"全方位", r"多维度", r"深度融合", r"极致体验", r"带来更好的", r"更加智能",
        r"无缝", r"一站式", r"打造", r"助力",
    ],
    "A3 演绎/氛围": [r"仿佛", r"宛如", r"就像一(位|个)", r"充满温度", r"娓娓道来", r"默默守护"],
    "A5 无信息修饰": [
        r"非常", r"极其", r"十分", r"极大(地)?", r"切实", r"真正(地)?", r"充分(地)?",
        r"[！!]{1}\s*$",
    ],
    "A6 对话残留": [
        r"^\s*(关键|注意|说明|补充|PS)[:：]", r"体验更顺", r"[（(][^）)]{1,12}[）)]",
    ],
    "A7/A8 过程说明/元信息": [
        r"本页(将|会|用于|导航)", r"本文(将|会)", r"下面(我们|将)", r"如下所示",
        r"来源与(解释)?边界", r"实施顺序", r"验收口径", r"提问原则", r"对应观察",
    ],
    "A12 数据解读形容": [r"高达", r"仅有", r"多达", r"显著(提升|增长|下降)?", r"大幅(提升|增长|下降)?", r"惊人"],
    "H 装饰元素": [
        r"[\U0001F300-\U0001FAFF\u2600-\u27BF]",
    ],
}

# 命中这些模式的行多半是口径说明，降低优先级提示
CALIBER = re.compile(r"(N\s*=|分母|多选|限选|置信|来源|出处|样本|项次)")


class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.skip = 0
        self.items = []  # (line, text)
        self.tags = {"h1": 0, "h2": 0, "h3": 0, "section": 0, "li": 0, "p": 0, "details": 0}

    def handle_starttag(self, tag, attrs):
        if tag in ("style", "script"):
            self.skip += 1
        if tag in self.tags:
            self.tags[tag] += 1

    def handle_endtag(self, tag):
        if tag in ("style", "script") and self.skip:
            self.skip -= 1

    def handle_data(self, data):
        if self.skip:
            return
        t = data.strip()
        if t:
            self.items.append((self.getpos()[0], t))


def load(path):
    p = Path(path)
    raw = p.read_text(encoding="utf-8", errors="ignore")
    if p.suffix.lower() in (".html", ".htm"):
        ex = TextExtractor()
        ex.feed(raw)
        return ex.items, ex.tags
    items = [(i + 1, l.strip()) for i, l in enumerate(raw.splitlines()) if l.strip()]
    tags = {
        "heading": sum(1 for _, l in items if l.startswith("#")),
        "list": sum(1 for _, l in items if re.match(r"^([-*]|\d+\.)\s", l)),
    }
    return items, tags


def scan(path):
    items, _ = load(path)
    hits = []
    for line, text in items:
        for cat, pats in RULES.items():
            for pat in pats:
                for m in re.finditer(pat, text, flags=re.M):
                    # 括号内含数字/字母/等号的多为口径或编号（N=853、P0、48/162），跳过
                    if cat.startswith("A6") and m.group(0)[0] in "（(" and re.search(r"[\dA-Za-z=/%]", m.group(0)):
                        continue
                    s = max(0, m.start() - 14)
                    snippet = text[s:m.end() + 14].replace("|", "｜")
                    flag = "口径?" if CALIBER.search(text) else ""
                    hits.append((line, cat, m.group(0), snippet, flag))
    if not hits:
        print("未发现候选噪声。")
        return
    print(f"# 候选噪声 {len(hits)} 处：{path}\n")
    print("| 行 | 类别 | 命中 | 上下文 | 提示 |\n|---|---|---|---|---|")
    for h in hits:
        print(f"| {h[0]} | {h[1]} | {h[2]} | …{h[3]}… | {h[4]} |")
    print("\n提示列为“口径?”的命中所在句含口径说明，删除前务必确认。")


def stats(path):
    items, tags = load(path)
    chars = sum(len(re.sub(r"\s", "", t)) for _, t in items)
    return chars, tags


def compare(old, new):
    c1, t1 = stats(old)
    c2, t2 = stats(new)
    pct = (c1 - c2) / c1 * 100 if c1 else 0
    print("| 指标 | 降噪前 | 降噪后 | 变化 |\n|---|---|---|---|")
    print(f"| 可见字数 | {c1} | {c2} | -{c1 - c2}（-{pct:.1f}%） |")
    for k in t1:
        print(f"| {k} 数 | {t1[k]} | {t2.get(k, 0)} | {t2.get(k, 0) - t1[k]:+d} |")
    if pct > 30:
        print("\n⚠ 删减量 > 30%，交付前需用户确认。")


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) == 3 and a[0] == "--compare":
        compare(a[1], a[2])
    elif len(a) == 1:
        scan(a[0])
    else:
        print(__doc__)
