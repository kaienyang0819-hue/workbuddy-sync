#!/usr/bin/env node
/**
 * Token 看板使用记录分析 CLI（跨平台：Windows / macOS / Linux）。
 *
 * 输入：从页面抓取的记录 JSON 文件（browser-extract.js 的返回结构，或已规整的对象数组）。
 * 输出：HTML 报告文件 + 控制台文本摘要。
 *
 * 用法：
 *   node analyze.js --input records.json --out report.html
 *   node analyze.js --input records.json --out report.html --user bigbinhe --short-len 20 --min-fee 3 --top 10
 *   node analyze.js --input records.json --quota-used 1294.89 --quota-total 10000
 *
 * 输入 JSON 支持两种结构：
 *   1) { headers: [...], rows: [[time, product, model, question, tokens, fee, observe], ...] }
 *   2) [[time, product, model, question, tokens, fee, observe], ...]
 *   3) [{ time, product, model, question, tokens, fee }, ...]  // 已规整对象
 */

import { readFileSync, writeFileSync } from 'node:fs';
import { resolve, isAbsolute } from 'node:path';
import { normalizeRows, analyze } from './lib/parser.js';
import { generateHtml, generateTextSummary } from './lib/report.js';

function parseArgs(argv) {
  const args = {};
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith('--')) {
      const key = a.slice(2);
      const next = argv[i + 1];
      if (next === undefined || next.startsWith('--')) {
        args[key] = true;
      } else {
        args[key] = next;
        i++;
      }
    }
  }
  return args;
}

function abs(p) {
  return isAbsolute(p) ? p : resolve(process.cwd(), p);
}

function main() {
  const args = parseArgs(process.argv);
  if (!args.input) {
    console.error('错误：必须通过 --input 指定记录 JSON 文件。');
    console.error('示例：node analyze.js --input records.json --out report.html');
    process.exit(1);
  }

  const raw = JSON.parse(readFileSync(abs(args.input), 'utf-8'));

  // 统一成对象数组
  let records;
  if (Array.isArray(raw) && raw.length && Array.isArray(raw[0])) {
    records = normalizeRows(raw, []);
  } else if (raw && Array.isArray(raw.rows)) {
    records = normalizeRows(raw.rows, raw.headers || []);
  } else if (Array.isArray(raw) && raw.length && typeof raw[0] === 'object') {
    // 已经是对象数组，补齐派生字段
    records = raw.map((r) => ({
      time: r.time || '',
      product: r.product || '',
      model: r.model || '',
      question: r.question || '',
      questionLen: String(r.question || '').trim().length,
      tokens: Number(r.tokens) || 0,
      fee: Number(r.fee) || 0
    }));
  } else {
    console.error('错误：无法识别的输入结构。');
    process.exit(1);
  }

  if (!records.length) {
    console.warn('[warn] 未解析到任何记录（0 条）。');
    console.warn('       请确认：1) 已登录并进入「Token 看板」；2) 「详细使用记录」已加载；');
    console.warn('       3) 抓取到的 JSON 结构正确。空数据不会产出有意义的榜单。');
  }


  const result = analyze(records, {
    shortPromptMaxLen: args['short-len'] ? Number(args['short-len']) : undefined,
    minTokens: args['min-tokens'] ? Number(args['min-tokens']) : undefined,
    minFee: args['min-fee'] ? Number(args['min-fee']) : undefined,
    topN: args.top ? Number(args.top) : undefined
  });

  const meta = {
    user: args.user || '-',
    source: args.source || 'Token 看板',
    generatedAt: new Date().toLocaleString(),
    quota:
      args['quota-used'] && args['quota-total']
        ? { used: Number(args['quota-used']), total: Number(args['quota-total']) }
        : null
  };

  // 控制台文本摘要
  console.log(generateTextSummary(result));

  // 写 HTML
  if (args.out) {
    const html = generateHtml(result, meta);
    writeFileSync(abs(args.out), html, 'utf-8');
    console.log('\nHTML 报告已生成：' + abs(args.out));
  }
}

main();
