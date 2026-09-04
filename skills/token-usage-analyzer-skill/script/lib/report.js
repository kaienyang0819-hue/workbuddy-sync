/**
 * HTML 报告生成模块。
 * 根据 analyze() 的结果产出一份深色主题、响应式的 HTML 报告字符串。
 */

/** HTML 转义，防止提问文本里的尖括号破坏结构。 */
function esc(s) {
  return String(s == null ? '' : s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function fmtTokens(n) {
  return Number(n || 0).toLocaleString('en-US');
}

function fmtFee(n) {
  return '¥' + Number(n || 0).toFixed(2);
}

/** 截断过长提问，便于表格展示。 */
function clip(text, max = 60) {
  const s = String(text || '').trim();
  return s.length > max ? s.slice(0, max) + '…' : s;
}

function rowTag(model) {
  const m = String(model || '');
  const cls = /1m/i.test(m) ? 'tag m1' : 'tag';
  return `<span class="${cls}">${esc(m)}</span>`;
}

function renderRows(list, withModel = true) {
  return list
    .map(
      (r) => `        <tr>
          <td>${esc(r.time)}</td>
          <td class="q">${esc(clip(r.question))}</td>
          <td class="num tk">${fmtTokens(r.tokens)}</td>
          <td class="num fee">${fmtFee(r.fee)}</td>${
        withModel ? `\n          <td>${rowTag(r.model)}</td>` : ''
      }
        </tr>`
    )
    .join('\n');
}

function renderGroup(list) {
  return list
    .map(
      (g) => `        <tr>
          <td>${esc(g.key)}</td>
          <td class="num">${g.count}</td>
          <td class="num tk">${fmtTokens(g.tokens)}</td>
          <td class="num fee">${fmtFee(g.fee)}</td>
        </tr>`
    )
    .join('\n');
}

/** 渲染逐条诊断卡片：每条记录的成因标签 + 针对性建议。 */
function renderPerRecord(list) {
  if (!list || !list.length) {
    return '    <p style="color:var(--sub)">暂无可逐条分析的高消耗记录。</p>';
  }
  return list
    .map((r, i) => {
      const a = r.analysis || { severity: 'low', reasons: [], suggestions: [] };
      const tags = a.reasons
        .map((x) => `<span class="rtag">${esc(x.label)}</span>`)
        .join('');
      const tips = a.suggestions.length
        ? `<ul class="rtips">${a.suggestions.map((s) => `<li>${esc(s)}</li>`).join('')}</ul>`
        : '<div class="rtips none">未识别到明显可优化点，重点关注会话长度。</div>';
      return `      <div class="rec sev-${a.severity}">
        <div class="rec-head">
          <span class="rec-idx">${i + 1}</span>
          <span class="rec-q">${esc(clip(r.question, 80))}</span>
        </div>
        <div class="rec-meta">
          <span>${esc(r.time)}</span>
          <span>${rowTag(r.model)}</span>
          <span class="tk">${fmtTokens(r.tokens)} tokens</span>
          <span class="fee">${fmtFee(r.fee)}</span>
        </div>
        <div class="rec-body">
          <div class="rec-col"><div class="rec-label">可能原因</div>${tags || '<span class="rtag">长会话累积</span>'}</div>
          <div class="rec-col"><div class="rec-label">节约建议</div>${tips}</div>
        </div>
      </div>`;
    })
    .join('\n');
}

/**
 * 生成完整 HTML 报告。
 * @param {object} result analyze() 的返回值
 * @param {object} meta   { user, source, generatedAt, quota }
 */
export function generateHtml(result, meta = {}) {
  const {
    user = '-',
    source = 'Token 看板',
    generatedAt = new Date().toLocaleString(),
    quota = null
  } = meta;
  const { summary, shortHigh, topByFee, notable, byProduct, byModel, options } = result;

  const quotaCards = quota
    ? `      <div class="stat"><div class="label">本月费用</div><div class="val warn">${fmtFee(quota.used)}</div></div>
      <div class="stat"><div class="label">额度</div><div class="val">${fmtFee(quota.total)}</div></div>
      <div class="stat"><div class="label">已用占比</div><div class="val hi">${quota.total ? ((quota.used / quota.total) * 100).toFixed(1) : '0'}%</div></div>`
    : '';

  return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Token 使用分析报告</title>
<style>
  :root{--bg:#0f1220;--card:#181c2e;--card2:#1f2438;--txt:#e8eaf2;--sub:#9aa3c0;--acc:#6c8cff;--warn:#ff6b6b;--hi:#ffb454;--ok:#3ddc97;--line:#2a3050;}
  *{box-sizing:border-box;margin:0;padding:0}
  body{font-family:-apple-system,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;background:linear-gradient(160deg,#0f1220,#141832);color:var(--txt);line-height:1.6;padding:32px 18px}
  .wrap{max-width:1080px;margin:0 auto}
  header{margin-bottom:28px}
  h1{font-size:30px;font-weight:700;letter-spacing:.5px}
  h1 .em{background:linear-gradient(90deg,#6c8cff,#a77bff);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}
  .meta{color:var(--sub);font-size:14px;margin-top:8px}
  section{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:22px 24px;margin-bottom:22px;box-shadow:0 8px 30px rgba(0,0,0,.25)}
  h2{font-size:20px;margin-bottom:14px;display:flex;align-items:center;gap:10px}
  h2::before{content:"";width:6px;height:20px;border-radius:3px;background:linear-gradient(180deg,#6c8cff,#a77bff)}
  .cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:14px}
  .stat{background:var(--card2);border:1px solid var(--line);border-radius:12px;padding:16px}
  .stat .label{color:var(--sub);font-size:13px}
  .stat .val{font-size:24px;font-weight:700;margin-top:6px}
  .stat .val.warn{color:var(--warn)}.stat .val.hi{color:var(--hi)}.stat .val.ok{color:var(--ok)}
  table{width:100%;border-collapse:collapse;font-size:14px;margin-top:6px}
  th,td{padding:10px 12px;text-align:left;border-bottom:1px solid var(--line);vertical-align:top}
  th{color:var(--sub);font-weight:600;font-size:13px;letter-spacing:.4px}
  tbody tr:hover{background:rgba(108,140,255,.06)}
  td.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
  .tk{color:var(--hi);font-weight:600}
  .fee{color:var(--warn);font-weight:700}
  .q{max-width:380px}
  .tag{display:inline-block;font-size:11px;padding:2px 8px;border-radius:999px;background:rgba(108,140,255,.15);color:#9fb4ff;border:1px solid rgba(108,140,255,.3)}
  .tag.m1{background:rgba(255,107,107,.13);color:#ff9b9b;border-color:rgba(255,107,107,.3)}
  .reason{counter-reset:r;list-style:none;display:grid;gap:14px}
  .reason li{background:var(--card2);border:1px solid var(--line);border-left:3px solid var(--acc);border-radius:10px;padding:14px 16px 14px 50px;position:relative}
  .reason li::before{counter-increment:r;content:counter(r);position:absolute;left:14px;top:14px;width:24px;height:24px;border-radius:50%;background:linear-gradient(135deg,#6c8cff,#a77bff);color:#fff;font-size:13px;font-weight:700;display:flex;align-items:center;justify-content:center}
  .reason b,.tip b{color:#fff}
  .tips{display:grid;gap:12px}
  .tip-cat{margin:14px 0 2px;font-size:14px;font-weight:700;color:#9fb4ff;letter-spacing:.3px}
  .tip-cat:first-child{margin-top:0}
  .tip{background:var(--card2);border:1px solid var(--line);border-radius:10px;padding:14px 16px;display:flex;gap:12px;align-items:flex-start}
  .tip .ic{flex:none;width:30px;height:30px;border-radius:8px;background:rgba(61,220,151,.15);color:var(--ok);display:flex;align-items:center;justify-content:center;font-weight:700}
  .note{color:var(--sub);font-size:13px;margin-top:10px;padding:10px 14px;border-radius:8px;background:rgba(255,180,84,.08);border:1px solid rgba(255,180,84,.25)}
  .conclusion{background:linear-gradient(135deg,rgba(108,140,255,.14),rgba(167,123,255,.14));border:1px solid rgba(108,140,255,.3)}
  .rec{background:var(--card2);border:1px solid var(--line);border-radius:12px;padding:14px 16px;margin-bottom:12px;border-left:4px solid var(--acc)}
  .rec.sev-high{border-left-color:var(--warn)}.rec.sev-medium{border-left-color:var(--hi)}.rec.sev-low{border-left-color:var(--ok)}
  .rec-head{display:flex;align-items:flex-start;gap:10px}
  .rec-idx{flex:none;width:22px;height:22px;border-radius:50%;background:rgba(108,140,255,.2);color:#9fb4ff;font-size:12px;font-weight:700;display:flex;align-items:center;justify-content:center;margin-top:2px}
  .rec-q{font-weight:600;color:#fff;word-break:break-all}
  .rec-meta{display:flex;flex-wrap:wrap;gap:14px;color:var(--sub);font-size:13px;margin:8px 0 10px 32px}
  .rec-body{display:grid;grid-template-columns:1fr 1.4fr;gap:14px;margin-left:32px}
  .rec-col{background:rgba(0,0,0,.15);border:1px solid var(--line);border-radius:8px;padding:10px 12px}
  .rec-label{color:var(--sub);font-size:12px;margin-bottom:8px}
  .rtag{display:inline-block;font-size:12px;padding:3px 9px;margin:0 6px 6px 0;border-radius:6px;background:rgba(255,180,84,.13);color:#ffce8a;border:1px solid rgba(255,180,84,.3)}
  .rtips{margin:0;padding-left:18px}.rtips li{margin-bottom:5px;font-size:13px}
  .rtips.none{padding-left:0;color:var(--sub);font-size:13px}
  footer{text-align:center;color:var(--sub);font-size:12px;margin-top:10px}
  @media (max-width:640px){.q{max-width:160px}h1{font-size:24px}.rec-body{grid-template-columns:1fr}}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>Token 使用<span class="em">分析报告</span></h1>
    <div class="meta">用户：${esc(user)}&nbsp;·&nbsp;数据来源：${esc(source)}（共 ${summary.count} 条记录）&nbsp;·&nbsp;生成时间：${esc(generatedAt)}</div>
  </header>

  <section>
    <h2>概览</h2>
    <div class="cards">
${quotaCards}
      <div class="stat"><div class="label">记录数</div><div class="val">${summary.count}</div></div>
      <div class="stat"><div class="label">总 Tokens</div><div class="val">${fmtTokens(summary.totalTokens)}</div></div>
      <div class="stat"><div class="label">总费用</div><div class="val warn">${fmtFee(summary.totalFee)}</div></div>
      <div class="stat"><div class="label">单条均价</div><div class="val hi">${fmtFee(summary.avgFee)}</div></div>
    </div>
  </section>

  <section>
    <h2>一、提问很短，但 Token / 费用很高（≤ ${options.shortPromptMaxLen} 字，按费用排序）</h2>
    <table>
      <thead><tr><th>时间</th><th class="q">提问</th><th class="num">总 Tokens</th><th class="num">费用</th><th>模型</th></tr></thead>
      <tbody>
${renderRows(shortHigh, true)}
      </tbody>
    </table>
    <div class="note">说明：「提问」列只显示最后输入的一句话，并不代表本次请求实际发送给模型的内容量。</div>
  </section>

  <section>
    <h2>二、绝对费用最高的记录</h2>
    <table>
      <thead><tr><th>时间</th><th class="q">提问（节选）</th><th class="num">总 Tokens</th><th class="num">费用</th><th>模型</th></tr></thead>
      <tbody>
${renderRows(topByFee, true)}
      </tbody>
    </table>
  </section>

  <section>
    <h2>三、逐条诊断与针对性节约建议</h2>
    <p style="color:var(--sub);margin-bottom:14px">对高消耗记录逐条推断成因并给出对应建议（启发式，仅供定位方向）。左边框颜色表示费用严重度：<span style="color:var(--warn)">红=高</span> / <span style="color:var(--hi)">黄=中</span> / <span style="color:var(--ok)">绿=低</span>。</p>
${renderPerRecord(notable)}
  </section>

  <section>
    <h2>四、按产品 / 模型聚合</h2>
    <table>
      <thead><tr><th>产品</th><th class="num">次数</th><th class="num">Tokens</th><th class="num">费用</th></tr></thead>
      <tbody>
${renderGroup(byProduct)}
      </tbody>
    </table>
    <table style="margin-top:16px">
      <thead><tr><th>模型</th><th class="num">次数</th><th class="num">Tokens</th><th class="num">费用</th></tr></thead>
      <tbody>
${renderGroup(byModel)}
      </tbody>
    </table>
  </section>

  <section>
    <h2>五、为什么"短提问"会这么贵</h2>
    <p style="color:var(--sub);margin-bottom:14px">核心结论：<b style="color:#fff">计费按"整次请求发给模型的全部上下文"算，不是按你打的那几个字算。</b></p>
    <ol class="reason">
      <li><b>历史对话累积（最主要）</b>：每轮请求都会把之前所有对话重新发一遍。短指令往往出现在长会话后期，此时历史最长，单次最贵。</li>
      <li><b>大文件 / 大数据读取</b>：读取大 JSON、整份代码文件、设计稿数据等，会瞬间灌入几十万~几百万 token。</li>
      <li><b>MCP 工具返回体积巨大</b>：figma 数据、chrome 页面快照、网页内容动辄几十万 token。</li>
      <li><b>Agent 多轮工具循环</b>：一句简短指令会触发"读文件→改文件→再读→验证"多步，每步工具结果都累计到同一条记录。</li>
      <li><b>模型与计费差异</b>：1m 上下文版单价更高；费用还区分输入/输出、cache 写入(贵)/读取(便宜)。</li>
    </ol>
  </section>

  <section>
    <h2>六、节省 Token 的办法（按收益排序，通用）</h2>
    <div class="tips">
      <div class="tip-cat">A. 会话与上下文管理（收益最大）</div>
      <div class="tip"><div class="ic">1</div><div><b>任务切换就开新会话</b><br>每轮请求都会重发全部历史，换需求/模块时开新会话，能把单次基础体积大幅降下来。</div></div>
      <div class="tip"><div class="ic">2</div><div><b>长会话定期重开</b><br>同一会话越聊越贵；阶段性任务完成后，用一句话总结结论带入新会话，而不是拖着长历史继续。</div></div>
      <div class="tip"><div class="ic">3</div><div><b>不在一个会话里塞多个无关任务</b><br>无关任务混在一起会让彼此的上下文互相计费，拆分到不同会话更省。</div></div>
      <div class="tip-cat">B. 文件与数据读取</div>
      <div class="tip"><div class="ic">4</div><div><b>避免整文件读取</b><br>用搜索/grep 先定位，再按需读取相关行范围（offset/limit），不要一次性读整份大文件。</div></div>
      <div class="tip"><div class="ic">5</div><div><b>大 JSON / 数据先用脚本预处理</b><br>只提取需要的字段或前几条样例喂给模型，不要把几 MB 的原始数据整份贴进来。</div></div>
      <div class="tip"><div class="ic">6</div><div><b>日志 / 命令输出先过滤</b><br>长日志、构建输出先 grep / head 截取关键部分，再交给模型分析。</div></div>
      <div class="tip"><div class="ic">7</div><div><b>避免重复粘贴同一段内容</b><br>同一文件/数据多次贴入会反复计费；让模型记住一次即可。</div></div>
      <div class="tip-cat">C. 指令表达</div>
      <div class="tip"><div class="ic">8</div><div><b>指令一次讲清对象与范围</b><br>"改哪个文件、哪一段、改成什么"，避免模型反复翻历史猜测。</div></div>
      <div class="tip"><div class="ic">9</div><div><b>少用"继续/删除/需要/ok"等模糊词</b><br>模糊指令会触发模型重读大量上下文并增加来回轮次。</div></div>
      <div class="tip"><div class="ic">10</div><div><b>批量需求一次说清</b><br>把相关的多个小要求合并成一条清晰指令，减少多轮交互累积。</div></div>
      <div class="tip"><div class="ic">11</div><div><b>给精确路径 / 行号</b><br>直接 @文件 或给出行号，省去模型全局搜索定位的开销。</div></div>
      <div class="tip-cat">D. 工具与 MCP</div>
      <div class="tip"><div class="ic">12</div><div><b>控制 MCP 返回量</b><br>调用时设置 maxOutputLength；优先用精确查询而非拉全量。</div></div>
      <div class="tip"><div class="ic">13</div><div><b>Figma 只取目标节点</b><br>用具体 node-id 提取，避免拉取整页/整文件的庞大图层数据。</div></div>
      <div class="tip"><div class="ic">14</div><div><b>浏览器快照 / 网页只取关键区域</b><br>a11y 快照、网页正文很大，只抓需要的部分或用选择器定位。</div></div>
      <div class="tip"><div class="ic">15</div><div><b>减少不必要的探索轮次</b><br>明确告诉模型改哪、不要全局乱搜，能显著减少工具调用与结果累积。</div></div>
      <div class="tip-cat">E. 模型与多媒体</div>
      <div class="tip"><div class="ic">16</div><div><b>按需选模型</b><br>日常小问答 / 简单改动用便宜模型，复杂重构才用高价模型。</div></div>
      <div class="tip"><div class="ic">17</div><div><b>谨慎使用 1m 上下文版</b><br>单价更高，小操作用它很不划算；仅在确需超长上下文时用。</div></div>
      <div class="tip"><div class="ic">18</div><div><b>图片 / 截图按需传</b><br>图片 token 开销大，能用文字 / 坐标 / 报错文本描述就别截图。</div></div>
      <div class="tip-cat">F. 工程化沉淀</div>
      <div class="tip"><div class="ic">19</div><div><b>重复说明沉淀成规则 / Skill</b><br>把每次都要重复输入的背景、规范固化为项目规则或 skill，避免反复贴。</div></div>
      <div class="tip"><div class="ic">20</div><div><b>保持稳定前缀以命中缓存</b><br>系统提示 / 固定上下文尽量稳定，cache 读取远比重新写入便宜。</div></div>
    </div>
  </section>

  <section class="conclusion">
    <h2>结论</h2>
    <p>费用高的根因不是"问得多"，而是 <b>长会话 + 大文件/MCP 数据 + Agent 多轮工具调用</b> 三者叠加。最立竿见影的两招：<b style="color:var(--ok)">勤开新会话</b> 与 <b style="color:var(--ok)">少读整文件/整数据</b>。</p>
  </section>

  <footer>本报告由 token-usage-analyzer-skill 自动生成 · 仅供内部成本优化参考</footer>
</div>
</body>
</html>`;
}

/** 生成可直接粘贴到对话里的纯文本摘要。 */
export function generateTextSummary(result) {
  const { summary, shortHigh, topByFee, notable, options } = result;
  const lines = [];
  lines.push(`Token 使用分析（共 ${summary.count} 条，总费用 ${fmtFee(summary.totalFee)}，单条均价 ${fmtFee(summary.avgFee)}）`);
  lines.push('');
  lines.push(`一、提问 ≤ ${options.shortPromptMaxLen} 字但消耗高（按费用）：`);
  shortHigh.forEach((r, i) => {
    lines.push(`  ${i + 1}. [${r.time}] "${clip(r.question, 24)}" — ${fmtTokens(r.tokens)} tokens / ${fmtFee(r.fee)} (${r.model})`);
  });
  lines.push('');
  lines.push('二、绝对费用最高：');
  topByFee.forEach((r, i) => {
    lines.push(`  ${i + 1}. [${r.time}] "${clip(r.question, 24)}" — ${fmtTokens(r.tokens)} tokens / ${fmtFee(r.fee)}`);
  });

  if (notable && notable.length) {
    lines.push('');
    lines.push('三、逐条诊断与针对性节约建议：');
    notable.forEach((r, i) => {
      const a = r.analysis || { reasons: [], suggestions: [] };
      const sev = a.severity === 'high' ? '高' : a.severity === 'medium' ? '中' : '低';
      lines.push('');
      lines.push(`  ${i + 1}. [${r.time}] "${clip(r.question, 30)}"`);
      lines.push(`     ${fmtTokens(r.tokens)} tokens / ${fmtFee(r.fee)} (${r.model}) · 严重度:${sev}`);
      lines.push(`     原因：${a.reasons.length ? a.reasons.map((x) => x.label).join('；') : '长会话累积'}`);
      if (a.suggestions.length) {
        a.suggestions.forEach((s) => lines.push(`     建议：${s}`));
      } else {
        lines.push('     建议：未识别明显可优化点，重点关注会话长度。');
      }
    });
  }
  return lines.join('\n');
}
