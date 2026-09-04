/**
 * 逐条记录诊断模块。
 *
 * 由于看板只暴露有限字段（时间/产品/模型/提问/总Tokens/费用），
 * 这里基于「提问文本特征 + token/费用量级 + 模型」做启发式推断，
 * 为每一条记录输出：消耗高的可能原因（reasons）+ 针对性节约建议（suggestions）。
 *
 * 结论是启发式的，仅供定位方向，不代表绝对成因。
 */

/** 各类特征的正则 / 判断。 */
const PATTERNS = {
  url: /https?:\/\/[^\s]+/i,
  figma: /figma\.com/i,
  image: /@image|image\.[0-9a-z]+\.(png|jpe?g|gif|webp)|\.(png|jpe?g|gif|webp)\b/i,
  injected: /<user_info>|<question_answer>|User's input is:|<questions>|<title>/i,
  mcp: /\bmcp\b|浏览器|chrome|快照|headless/i,
  bigJson: /json|数据结构|字段|list\b|数组|对象示例/i,
  cron: /\[cron/i,
  // 模糊 / 续作类短指令
  vague: /^(继续|ok|好的?|嗯|是的?|对|行|可以|需要|删除|删掉|确认|同意|好吧|没问题|改一下|改下|继续做.*|接着.*)[\s。.,，!！?？]*$/i
};

/** 把 "继续做面板对接子模块" 这种也视为模糊续作（动词+宾语但无明确范围/文件）。 */
function isVagueContinuation(q) {
  const s = q.trim();
  if (PATTERNS.vague.test(s)) return true;
  // 极短且不含具体定位信息（无 URL、无 @、无文件名、无引号代码）
  if (s.length <= 12 && !/[@/.]|https?:|`|"/.test(s) && /继续|做|改|加|删|处理|对接|看看|试一下/.test(s)) {
    return true;
  }
  return false;
}

/**
 * 诊断单条记录。
 * @param {object} rec normalizeRows 产出的记录
 * @param {object} options { shortPromptMaxLen }
 * @returns {{ severity, tokenLevel, reasons: Array, suggestions: string[] }}
 */
export function analyzeRecord(rec, options = {}) {
  const { shortPromptMaxLen = 20 } = options;
  const q = String(rec.question || '');
  const reasons = [];
  const suggestions = [];

  const add = (code, label, suggestion) => {
    reasons.push({ code, label });
    if (suggestion) suggestions.push(suggestion);
  };

  // 1. 图片输入
  if (PATTERNS.image.test(q)) {
    add('IMAGE_INPUT', '包含图片输入', '图片 token 开销很大；非必要不传图，能用文字/坐标描述就别截图。');
  }

  // 2. Figma 设计稿
  if (PATTERNS.figma.test(q)) {
    add('URL_FIGMA', '读取 Figma 设计稿数据', '只取目标 node-id 的节点，避免拉取整页/整文件；必要时先缩小选区。');
  } else if (PATTERNS.url.test(q)) {
    // 3. 其它 URL（网页/JSON/仓库等）
    add('URL_WEB', '抓取外部 URL（网页/JSON/仓库）', '只取需要的关键片段或字段，设置 maxOutputLength；大 JSON 先用脚本预处理。');
  }

  // 4. 大 JSON / 数据结构探查
  if (PATTERNS.bigJson.test(q) && !PATTERNS.figma.test(q)) {
    add('BIG_DATA', '读取/分析大数据结构', '别整份丢给模型，用脚本只提取需要的字段或前几条样例。');
  }

  // 5. 注入上下文 / 工具结果
  if (PATTERNS.injected.test(q)) {
    add('INJECTED_CTX', '携带大量注入上下文/工具结果', '这是系统/工具注入内容；重点检查会话是否过长，必要时开新会话。');
  }

  // 6. MCP 重返回
  if (PATTERNS.mcp.test(q)) {
    add('MCP_HEAVY', '触发 MCP 大体积返回（浏览器/快照等）', '限制 MCP 返回量：页面快照/网页内容只取关键区域，设置 maxOutputLength。');
  }

  // 7. cron 定时任务
  if (PATTERNS.cron.test(q)) {
    add('CRON_TASK', '定时任务自动消耗', '评估触发频率与每次拉取的数据量；只查必要数据，精简输出格式。');
  }

  // 8. 模糊 / 续作短指令 —— 主要靠历史上下文
  if (isVagueContinuation(q)) {
    add('VAGUE_CONTEXT', '模糊/续作指令，主要消耗在历史上下文', '一次讲清对象与范围（哪个文件、哪段、改什么），减少模型翻历史和来回轮次。');
  }

  // 9. 短提问但 token 高 —— 历史累积（与 8 互补，覆盖非续作的短问）
  if (rec.questionLen <= shortPromptMaxLen && rec.tokens >= 300000 && !isVagueContinuation(q)) {
    add('CONTEXT_ACCUM', '提问很短但上下文累积大', '任务切换时开新会话，避免历史无限叠加（收益最大）。');
  }

  // 10. 1m 模型单价高
  if (/1m/i.test(rec.model)) {
    add('MODEL_1M', '使用 1m 上下文版（单价更高）', '日常/小操作切换到普通或更便宜的模型，仅超长上下文才用 1m 版。');
  }

  // 兜底：没有命中任何特征但费用/ token 很高
  if (reasons.length === 0 && (rec.tokens >= 1000000 || rec.fee >= 10)) {
    add('LONG_SESSION', '疑似长会话/多轮工具循环累积', '检查是否在长对话后期；适时开新会话，减少整文件读取与多轮探索。');
  }

  // 严重度按费用分级
  let severity = 'low';
  if (rec.fee >= 20) severity = 'high';
  else if (rec.fee >= 5) severity = 'medium';

  return { severity, reasons, suggestions };
}

/** 为一组记录批量附加诊断结果，返回新数组（不改原对象）。 */
export function attachAnalysis(records, options = {}) {
  return records.map((r) => ({ ...r, analysis: analyzeRecord(r, options) }));
}
