/**
 * 浏览器上下文提取脚本。
 *
 * 该文件导出一个「在页面里执行」的函数字符串，供 Chrome MCP 的 evaluate_script 调用，
 * 用于从 Token 看板「详细使用记录」表格里抓取所有行数据。
 *
 * 用法（在 CodeBuddy 里通过 Chrome MCP 调用）：
 *   1. navigate_page 打开 https://token.woa.com/
 *   2. 若跳转登录页，handleLogin（见 SKILL.md），完成后回到看板
 *   3. fill 把「每页显示」下拉调到 100
 *   4. evaluate_script，function 传入 EXTRACT_RECORDS_FN
 *
 * 返回结构：{ rowCount, headers, rows: [[time, product, model, question, totalTokens, fee, observe], ...] }
 */

/**
 * 真正在页面里运行的提取函数（保持纯浏览器 API，禁止依赖外部变量）。
 * 这里同时导出为可读函数与字符串，方便排查与直接传给 MCP。
 */
export function extractRecordsInPage() {
  // 找到包含「详细使用记录」表头特征的表格
  const tables = Array.from(document.querySelectorAll('table'));
  let target = null;
  for (const t of tables) {
    const head = (t.innerText || '');
    if (head.includes('总TOKENS') || head.includes('总Tokens') || head.includes('提问')) {
      target = t;
      break;
    }
  }
  // 兜底：取行数最多的表
  if (!target && tables.length) {
    target = tables
      .slice()
      .sort((a, b) => b.querySelectorAll('tr').length - a.querySelectorAll('tr').length)[0];
  }
  if (!target) {
    return { rowCount: 0, headers: [], rows: [], error: 'no table found' };
  }

  const headers = Array.from(target.querySelectorAll('thead th'))
    .map((th) => (th.innerText || '').trim());

  const rows = Array.from(target.querySelectorAll('tbody tr')).map((tr) =>
    Array.from(tr.querySelectorAll('td')).map((td) => (td.innerText || '').trim())
  );

  return { rowCount: rows.length, headers, rows };
}

/**
 * 提供给 MCP evaluate_script 的函数字符串。
 * MCP 要求传入一个「函数声明字符串」，因此这里把上面的函数体序列化出来。
 */
export const EXTRACT_RECORDS_FN = `() => {${extractRecordsInPage
  .toString()
  // 去掉外层 "function extractRecordsInPage() {" 与结尾的 "}"，只保留函数体
  .replace(/^function[^{]*\{/, '')
  .replace(/\}\s*$/, '')}}`;
