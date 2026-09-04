#!/usr/bin/env node
/**
 * 前置检查：确保 chrome-devtools MCP 已安装并启用。
 *
 * 跨平台（Windows / macOS / Linux）：CodeBuddy 的 MCP 配置统一位于
 *   <用户主目录>/.codebuddy/mcp.json
 *
 * 行为：
 *   - 读取 mcp.json（不存在则按需创建基础结构）；
 *   - 缺少 chrome-devtools：写入配置（安装）；
 *   - chrome-devtools 已存在且启用：不改动；
 *   - chrome-devtools 被用户显式禁用（disabled=true）：默认**不静默启用**，仅提示，
 *     需用户加 --force-enable 显式确认后才会启用，避免覆盖用户意图。
 *
 * 用法：
 *   node ensure-chrome-mcp.js                 # 检测；缺失则安装；被禁用则仅提示
 *   node ensure-chrome-mcp.js --check         # 仅检测，不写入（exit 0=就绪, 3=缺失, 4=被禁用）
 *   node ensure-chrome-mcp.js --force-enable  # 连同被用户禁用的项一起启用
 *
 * 注意：写入配置后，需要在 CodeBuddy 中重新加载 / 重启 MCP 才会生效。
 */

import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'node:fs';
import { homedir } from 'node:os';
import { join, dirname } from 'node:path';

const MCP_KEY = 'chrome-devtools';

// 锁定具体版本，避免 @latest 带来的供应链不可控风险。
// 需要升级时手动修改此版本号（查询：npm view chrome-devtools-mcp version）。
const CHROME_MCP_VERSION = '1.1.1';

const CHROME_MCP_CONFIG = {
  command: 'npx',
  args: ['-y', `chrome-devtools-mcp@${CHROME_MCP_VERSION}`],
  type: 'stdio',
  disabled: false
};

/** 返回 mcp.json 的绝对路径（跨平台）。 */
export function getMcpConfigPath() {
  return join(homedir(), '.codebuddy', 'mcp.json');
}

/** 读取配置；文件不存在或解析失败时返回空骨架。 */
function loadConfig(path) {
  if (!existsSync(path)) return { mcpServers: {} };
  try {
    const json = JSON.parse(readFileSync(path, 'utf-8'));
    if (!json.mcpServers || typeof json.mcpServers !== 'object') {
      json.mcpServers = {};
    }
    return json;
  } catch (e) {
    throw new Error(`mcp.json 解析失败，请检查格式：${path}\n${e.message}`);
  }
}

/** 判断 chrome MCP 是否已安装且启用。 */
export function isChromeMcpReady(config) {
  const entry = config.mcpServers && config.mcpServers[MCP_KEY];
  return Boolean(entry) && entry.disabled !== true;
}

/**
 * 确保 chrome MCP 配置存在并启用，返回 { changed, path, reason }。
 * @param {object} opts
 * @param {boolean} opts.checkOnly    仅检测，不写入
 * @param {boolean} opts.forceEnable  允许启用被用户显式禁用（disabled=true）的项
 */
export function ensureChromeMcp({ checkOnly = false, forceEnable = false } = {}) {
  const path = getMcpConfigPath();
  const config = loadConfig(path);
  const entry = config.mcpServers[MCP_KEY];

  // 已存在且启用：无需改动
  if (entry && entry.disabled !== true) {
    return { changed: false, path, reason: 'already-ready' };
  }

  // 被用户显式禁用：默认不动，尊重用户意图
  if (entry && entry.disabled === true) {
    if (checkOnly) {
      return { changed: false, path, reason: 'disabled' };
    }
    if (!forceEnable) {
      // 不静默启用，交给调用方提示用户手动确认
      return { changed: false, path, reason: 'disabled-skip' };
    }
    // 用户显式确认：仅翻转 disabled，保留其原有 command/args/version，不强行覆盖
    entry.disabled = false;
    writeConfig(path, config);
    return { changed: true, path, reason: 'enabled' };
  }

  // 完全缺失
  if (checkOnly) {
    return { changed: false, path, reason: 'missing' };
  }
  config.mcpServers[MCP_KEY] = { ...CHROME_MCP_CONFIG };
  writeConfig(path, config);
  return { changed: true, path, reason: 'installed' };
}

/** 写入配置文件，必要时创建目录。 */
function writeConfig(path, config) {
  if (!existsSync(dirname(path))) {
    mkdirSync(dirname(path), { recursive: true });
  }
  writeFileSync(path, JSON.stringify(config, null, 2) + '\n', 'utf-8');
}

function main() {
  const checkOnly = process.argv.includes('--check');
  const forceEnable = process.argv.includes('--force-enable');
  try {
    const path = getMcpConfigPath();

    if (checkOnly) {
      const res = ensureChromeMcp({ checkOnly: true });
      if (res.reason === 'already-ready') {
        console.log(`[ok] chrome-devtools MCP 已安装并启用：${path}`);
        process.exit(0);
      } else if (res.reason === 'disabled') {
        console.log(`[disabled] chrome-devtools MCP 存在但被用户禁用（disabled=true）：${path}`);
        console.log('如确需启用，请手动改为 disabled:false，或运行：node ensure-chrome-mcp.js --force-enable');
        process.exit(4);
      } else {
        console.log(`[missing] chrome-devtools MCP 未安装：${path}`);
        process.exit(3);
      }
    }

    const res = ensureChromeMcp({ forceEnable });
    if (res.reason === 'already-ready') {
      console.log(`[ok] chrome-devtools MCP 已就绪，无需改动：${res.path}`);
      process.exit(0);
    } else if (res.reason === 'installed') {
      console.log(`[installed] 已写入 chrome-devtools MCP 配置：${res.path}`);
      console.log('请在 CodeBuddy 中重新加载 / 重启 MCP 后再继续。');
      process.exit(0);
    } else if (res.reason === 'enabled') {
      console.log(`[enabled] 已按 --force-enable 启用 chrome-devtools MCP：${res.path}`);
      console.log('请在 CodeBuddy 中重新加载 / 重启 MCP 后再继续。');
      process.exit(0);
    } else if (res.reason === 'disabled-skip') {
      console.warn(`[skip] chrome-devtools MCP 被用户显式禁用（disabled=true），已尊重该设置未改动：${res.path}`);
      console.warn('未自动启用，避免覆盖你的意图。如确需启用，请二选一：');
      console.warn('  1) 手动把该项 disabled 改为 false；');
      console.warn('  2) 运行：node ensure-chrome-mcp.js --force-enable');
      process.exit(4);
    }
    process.exit(0);
  } catch (e) {
    console.error('[error] ' + e.message);
    process.exit(1);
  }
}

// 仅在作为脚本直接运行时执行 main（被 import 时不执行）
if (import.meta.url === `file://${process.argv[1]}` || process.argv[1]?.endsWith('ensure-chrome-mcp.js')) {
  main();
}
