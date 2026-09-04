/**
 * 报告本地预览（跨平台，Node.js，无第三方依赖，无需启动 web 服务）。
 *
 * 用途：直接用操作系统默认程序打开本地 HTML 报告文件进行预览，
 * 不启动任何 HTTP 服务，使用本地文件路径即可。
 *
 * 用法：
 *   node preview-report.js --dir <报告目录> --file report.html
 *   node preview-report.js --path <报告文件完整路径>
 *
 * 参数：
 *   --path  报告文件完整路径（优先级最高）
 *   --dir   报告所在目录（默认：当前工作目录）
 *   --file  报告文件名（默认：report.html）
 *
 * 平台打开方式：Windows: start / macOS: open / Linux: xdg-open。
 */
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

function parseArgs(argv) {
  const out = {};
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith('--')) out[a.slice(2)] = argv[++i];
  }
  return out;
}

const args = parseArgs(process.argv);
const filePath = args.path
  ? path.resolve(args.path)
  : path.resolve(args.dir || process.cwd(), args.file || 'report.html');

if (!fs.existsSync(filePath)) {
  console.error('[error] 报告文件不存在：' + filePath);
  process.exit(1);
}

function openLocal(fp) {
  if (process.platform === 'win32') {
    // start 的第一个引号参数是窗口标题，需占位
    return spawn('cmd', ['/c', 'start', '', fp], { detached: true, stdio: 'ignore' });
  }
  if (process.platform === 'darwin') {
    return spawn('open', [fp], { detached: true, stdio: 'ignore' });
  }
  return spawn('xdg-open', [fp], { detached: true, stdio: 'ignore' });
}

try {
  const child = openLocal(filePath);
  child.unref();
  console.log('[preview] 已用系统默认程序打开本地报告：' + filePath);
} catch (e) {
  console.error('[error] 打开失败：' + e.message);
  console.error('可手动打开本地文件：' + filePath);
  process.exit(1);
}
