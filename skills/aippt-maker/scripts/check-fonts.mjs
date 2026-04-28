#!/usr/bin/env node
/**
 * check-fonts.mjs — 跨平台中文字体检查工具
 *
 * 用法:
 *   node check-fonts.mjs          # 检查并给出安装指引
 *   node check-fonts.mjs --install # 检查，若缺失则自动安装（Linux 需 sudo）
 *
 * 背景:
 *   导出工具使用 Playwright (headless Chromium) 解析 HTML 布局。
 *   如果系统缺少中文字体，Chromium 会用英文 fallback 字体渲染中文字符，
 *   导致 getBoundingClientRect() 返回的宽度与预期不符，
 *   flex/grid 布局中的卡片宽度分配异常、文本溢出容器。
 */

import { execSync } from 'child_process';
import { existsSync } from 'fs';
import { platform } from 'os';

const AUTO_INSTALL = process.argv.includes('--install');
const OS = platform(); // 'win32' | 'darwin' | 'linux'

function log(prefix, msg) {
  const colors = { OK: '\x1b[32m', FAIL: '\x1b[31m', INFO: '\x1b[36m', WARN: '\x1b[33m' };
  const reset = '\x1b[0m';
  console.log(`${colors[prefix] || ''}[${prefix}]${reset} ${msg}`);
}

// ── Windows: 检查注册表中的中文字体 ──
function checkWindowsFonts() {
  try {
    const cmd = 'powershell -NoProfile -Command "Get-ItemProperty \'HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Fonts\' | Out-String"';
    const output = execSync(cmd, { encoding: 'utf-8', timeout: 15000 });
    const cjkPatterns = [
      /Microsoft YaHei/i, /SimSun/i, /SimHei/i, /NSimSun/i,
      /FangSong/i, /KaiTi/i, /DengXian/i, /PingFang/i,
      /Noto Sans CJK/i, /Source Han Sans/i, /WenQuanYi/i
    ];
    const found = cjkPatterns.filter(p => p.test(output));
    return found.length;
  } catch {
    return -1; // 无法检测
  }
}

// ── macOS: 自带中文字体 ──
function checkMacFonts() {
  try {
    const output = execSync('system_profiler SPFontsDataType 2>/dev/null | grep -i "PingFang\\|Heiti\\|Songti\\|STSong\\|Noto Sans CJK" | head -5', { encoding: 'utf-8', timeout: 15000 });
    return output.trim().split('\n').filter(Boolean).length;
  } catch {
    return -1;
  }
}

// ── Linux: fc-list ──
function checkLinuxFonts() {
  try {
    const output = execSync('fc-list :lang=zh 2>/dev/null', { encoding: 'utf-8', timeout: 15000 });
    return output.trim().split('\n').filter(Boolean).length;
  } catch {
    return -1;
  }
}

function checkFonts() {
  switch (OS) {
    case 'win32': return checkWindowsFonts();
    case 'darwin': return checkMacFonts();
    case 'linux': return checkLinuxFonts();
    default: return -1;
  }
}

function detectLinuxDistro() {
  try {
    const release = execSync('cat /etc/os-release 2>/dev/null', { encoding: 'utf-8' });
    if (/ubuntu|debian|mint|pop/i.test(release)) return 'debian';
    if (/centos|rhel|fedora|rocky|alma/i.test(release)) return 'rhel';
    if (/alpine/i.test(release)) return 'alpine';
    if (/arch|manjaro/i.test(release)) return 'arch';
  } catch {}
  return 'unknown';
}

function installFonts() {
  if (OS === 'win32') {
    log('INFO', 'Windows 通常自带微软雅黑等中文字体。');
    log('INFO', '如确实缺少，请手动安装 Noto Sans CJK：');
    log('INFO', '  https://github.com/googlefonts/noto-cjk/releases');
    log('INFO', '  下载 NotoSansCJKsc-Regular.otf，双击安装即可。');
    return false;
  }
  if (OS === 'darwin') {
    log('OK', 'macOS 自带 PingFang SC 中文字体，无需额外安装。');
    return true;
  }
  // Linux
  const distro = detectLinuxDistro();
  const cmds = {
    debian: 'sudo apt-get update -qq && sudo apt-get install -y --no-install-recommends fonts-noto-cjk && sudo fc-cache -fv',
    rhel: 'sudo yum install -y google-noto-sans-cjk-ttc-fonts && sudo fc-cache -fv',
    alpine: 'sudo apk add --no-cache font-noto-cjk && sudo fc-cache -fv',
    arch: 'sudo pacman -S --noconfirm noto-fonts-cjk && sudo fc-cache -fv',
  };
  const cmd = cmds[distro];
  if (!cmd) {
    log('FAIL', '未识别的 Linux 发行版，请手动安装 Noto Sans CJK：');
    log('INFO', '  https://github.com/googlefonts/noto-cjk');
    return false;
  }
  log('INFO', `正在安装中文字体 (${distro})...`);
  try {
    execSync(cmd, { stdio: 'inherit', timeout: 120000 });
    log('OK', '字体安装完成。');
    return true;
  } catch (e) {
    log('FAIL', `安装失败: ${e.message}`);
    return false;
  }
}

function printInstallGuide() {
  console.log('');
  log('INFO', '请根据你的系统手动安装中文字体：');
  console.log('');
  switch (OS) {
    case 'win32':
      console.log('  1. 下载 Noto Sans CJK: https://github.com/googlefonts/noto-cjk/releases');
      console.log('  2. 双击 .otf 文件安装');
      console.log('  3. 或在设置 → 个性化 → 字体 中拖入安装');
      break;
    case 'darwin':
      console.log('  macOS 自带中文字体，如仍有问题请检查 Playwright 是否正确安装。');
      break;
    case 'linux':
      console.log('  Debian/Ubuntu: sudo apt-get install -y fonts-noto-cjk && fc-cache -fv');
      console.log('  CentOS/RHEL:   sudo yum install -y google-noto-sans-cjk-ttc-fonts && fc-cache -fv');
      console.log('  Alpine:        sudo apk add --no-cache font-noto-cjk && fc-cache -fv');
      console.log('  Arch:          sudo pacman -S noto-fonts-cjk && fc-cache -fv');
      break;
  }
  console.log('');
  console.log('  或重新运行此脚本并加上 --install 参数：');
  console.log('  node check-fonts.mjs --install');
  console.log('');
}

// ── 主流程 ──
console.log(`\n🔍 检查中文字体 (${OS})...\n`);
const count = checkFonts();

if (count > 0) {
  log('OK', `已检测到 ${count} 个中文字体，可以正常导出 PPTX。`);
  process.exit(0);
}

if (count === -1) {
  log('WARN', '无法自动检测字体。Windows/macOS 通常自带中文字体，如导出布局异常请手动检查。');
  process.exit(0);
}

// count === 0, 未检测到中文字体
log('FAIL', '未检测到中文字体。');

if (AUTO_INSTALL) {
  console.log('');
  const ok = installFonts();
  if (ok) {
    console.log('\n验证安装结果：');
    const recheck = checkFonts();
    if (recheck > 0) {
      log('OK', `安装成功，检测到 ${recheck} 个中文字体。`);
    }
  }
} else {
  printInstallGuide();
  process.exit(1);
}
