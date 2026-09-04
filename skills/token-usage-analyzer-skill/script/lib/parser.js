/**
 * 记录解析与分析模块。
 * 把从页面抓取的原始行（字符串数组）规整为结构化对象，并计算各类排行。
 */

import { attachAnalysis } from './advisor.js';

/** 把 "6,826,151" / "1.2M" 之类的字符串解析为数字。 */
export function parseTokens(value) {
  if (value == null) return 0;
  const s = String(value).trim().replace(/,/g, '');
  const m = s.match(/([\d.]+)\s*([MmKk])?/);
  if (!m) return 0;
  let n = parseFloat(m[1]);
  if (Number.isNaN(n)) return 0;
  if (m[2] === 'M' || m[2] === 'm') n *= 1e6;
  if (m[2] === 'K' || m[2] === 'k') n *= 1e3;
  return Math.round(n);
}

/** 把 "¥38.89" / "$5.20" 之类的字符串解析为数字（人民币元）。 */
export function parseFee(value) {
  if (value == null) return 0;
  const s = String(value).replace(/[^\d.]/g, '');
  const n = parseFloat(s);
  return Number.isNaN(n) ? 0 : n;
}

/** 计算提问文本的"长度"。中文按字符计，去掉首尾空白。 */
export function promptLength(text) {
  return String(text || '').trim().length;
}

/**
 * 把原始行数组规整成对象数组。
 * 默认列序：[时间, 产品, 模型, 提问, 总Tokens, 费用, 观测]
 * 若传入 headers，可按表头自动匹配列位置，增强健壮性。
 */
export function normalizeRows(rows, headers = []) {
  const idx = resolveColumnIndex(headers);
  return rows
    .map((cols) => {
      const get = (i) => (i >= 0 && i < cols.length ? cols[i] : '');
      const question = get(idx.question);
      const tokensRaw = get(idx.tokens);
      const feeRaw = get(idx.fee);
      return {
        time: get(idx.time),
        product: get(idx.product),
        model: get(idx.model),
        question,
        questionLen: promptLength(question),
        tokens: parseTokens(tokensRaw),
        tokensRaw: String(tokensRaw || '').trim(),
        fee: parseFee(feeRaw),
        feeRaw: String(feeRaw || '').trim()
      };
    })
    .filter((r) => r.tokens > 0 || r.fee > 0 || r.question);
}

/** 根据表头猜测各字段所在列，匹配不到时回退到默认列序。 */
function resolveColumnIndex(headers) {
  const def = { time: 0, product: 1, model: 2, question: 3, tokens: 4, fee: 5, observe: 6 };
  if (!Array.isArray(headers) || headers.length === 0) return def;
  const find = (keywords) => {
    for (let i = 0; i < headers.length; i++) {
      const h = String(headers[i] || '').toLowerCase();
      if (keywords.some((k) => h.includes(k))) return i;
    }
    return -1;
  };
  const time = find(['时间', 'time']);
  const product = find(['产品', 'product']);
  const model = find(['模型', 'model']);
  const question = find(['提问', '问题', 'prompt', 'question']);
  const tokens = find(['总token', 'tokens', 'token']);
  const fee = find(['费用', '金额', 'cost', 'fee']);
  return {
    time: time < 0 ? def.time : time,
    product: product < 0 ? def.product : product,
    model: model < 0 ? def.model : model,
    question: question < 0 ? def.question : question,
    tokens: tokens < 0 ? def.tokens : tokens,
    fee: fee < 0 ? def.fee : fee,
    observe: def.observe
  };
}

/**
 * 分析记录，产出各类榜单与汇总。
 * options:
 *   shortPromptMaxLen 短提问最大长度（默认 20）
 *   minTokens         进入"短提问高消耗"榜的最低 token（默认 300000）
 *   minFee            进入"短提问高消耗"榜的最低费用（默认 3）
 *   topN              各榜单取前 N（默认 10）
 */
export function analyze(records, options = {}) {
  const {
    shortPromptMaxLen = 20,
    minTokens = 300000,
    minFee = 3,
    topN = 10
  } = options;

  const totalTokens = records.reduce((s, r) => s + r.tokens, 0);
  const totalFee = records.reduce((s, r) => s + r.fee, 0);

  // 短提问 + 高消耗（token 或费用任一超阈值），按费用降序
  const shortHigh = records
    .filter((r) => r.questionLen <= shortPromptMaxLen && (r.tokens >= minTokens || r.fee >= minFee))
    .sort((a, b) => b.fee - a.fee)
    .slice(0, topN);

  // 绝对费用最高
  const topByFee = records.slice().sort((a, b) => b.fee - a.fee).slice(0, topN);

  // 绝对 token 最高
  const topByTokens = records.slice().sort((a, b) => b.tokens - a.tokens).slice(0, topN);

  // 按产品 / 模型聚合
  const byProduct = groupBy(records, (r) => r.product || '未知');
  const byModel = groupBy(records, (r) => r.model || '未知');

  // 逐条诊断：合并「短提问高消耗」与「费用最高」两榜并去重，作为需重点逐条分析的集合
  const notableMap = new Map();
  [...shortHigh, ...topByFee].forEach((r) => {
    const key = `${r.time}|${r.question}`;
    if (!notableMap.has(key)) notableMap.set(key, r);
  });
  const notable = attachAnalysis(
    Array.from(notableMap.values()).sort((a, b) => b.fee - a.fee),
    { shortPromptMaxLen }
  );

  return {
    summary: {
      count: records.length,
      totalTokens,
      totalFee: round2(totalFee),
      avgFee: records.length ? round2(totalFee / records.length) : 0
    },
    shortHigh,
    topByFee,
    topByTokens,
    notable,
    byProduct,
    byModel,
    options: { shortPromptMaxLen, minTokens, minFee, topN }
  };
}

function groupBy(records, keyFn) {
  const map = new Map();
  for (const r of records) {
    const k = keyFn(r);
    const cur = map.get(k) || { key: k, count: 0, tokens: 0, fee: 0 };
    cur.count += 1;
    cur.tokens += r.tokens;
    cur.fee += r.fee;
    map.set(k, cur);
  }
  return Array.from(map.values())
    .map((g) => ({ ...g, fee: round2(g.fee) }))
    .sort((a, b) => b.fee - a.fee);
}

function round2(n) {
  return Math.round(n * 100) / 100;
}
