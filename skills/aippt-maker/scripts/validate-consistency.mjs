#!/usr/bin/env node
/**
 * validate-consistency.mjs — 跨页风格一致性校验
 *
 * 用法: node validate-consistency.mjs <project_dir>
 *
 * 扫描所有 slide HTML 文件，检查以下维度是否跨页统一：
 * - tailwind.config 配色变量
 * - 字体声明
 * - 圆角值 (rounded-*)
 * - 图标尺寸 (w-* h-* on lucide icons)
 * - 文字大小分布
 *
 * 输出差异报告。无差异时输出 [OK]。
 */

import { readFileSync, readdirSync, existsSync } from 'fs';
import { join, basename } from 'path';

const projectDir = process.argv[2];
if (!projectDir) {
  console.error('用法: node validate-consistency.mjs <project_dir>');
  process.exit(1);
}

const slidesDir = join(projectDir, 'slides');
if (!existsSync(slidesDir)) {
  console.error(`[FAIL] slides 目录不存在: ${slidesDir}`);
  process.exit(1);
}

const files = readdirSync(slidesDir)
  .filter(f => f.endsWith('.html'))
  .sort()
  .map(f => ({
    name: f,
    content: readFileSync(join(slidesDir, f), 'utf-8')
  }));

if (files.length === 0) {
  console.error('[FAIL] slides 目录中没有 HTML 文件');
  process.exit(1);
}

console.log(`\n🔍 校验 ${files.length} 个幻灯片的风格一致性...\n`);

let issues = 0;

// ── 1. tailwind.config 配色一致性 ──
function extractTailwindConfig(html) {
  const match = html.match(/tailwind\.config\s*=\s*(\{[\s\S]*?\n\s*\})\s*<\/script>/);
  if (!match) return null;
  return match[1].replace(/\s+/g, ' ').trim();
}

const configs = files.map(f => ({ name: f.name, config: extractTailwindConfig(f.content) }));
const uniqueConfigs = [...new Set(configs.map(c => c.config).filter(Boolean))];

if (uniqueConfigs.length > 1) {
  console.log('⚠️  tailwind.config 配置不一致：');
  const groups = {};
  configs.forEach(c => {
    if (!c.config) return;
    const key = c.config;
    if (!groups[key]) groups[key] = [];
    groups[key].push(c.name);
  });
  Object.entries(groups).forEach(([config, slideNames], i) => {
    console.log(`   变体 ${i + 1} (${slideNames.length} 页): ${slideNames.join(', ')}`);
  });
  issues++;
} else if (uniqueConfigs.length === 1) {
  console.log('✅ tailwind.config 配色：所有页面一致');
} else {
  console.log('⚠️  未检测到 tailwind.config（可能使用内联样式）');
}

// ── 2. 圆角值统计 ──
function extractRoundedClasses(html) {
  const matches = html.match(/rounded-(?:sm|md|lg|xl|2xl|3xl|full|none)/g) || [];
  return [...new Set(matches)].sort();
}

const roundedBySlide = files.map(f => ({ name: f.name, rounded: extractRoundedClasses(f.content) }));
const allRounded = [...new Set(roundedBySlide.flatMap(s => s.rounded))].sort();

if (allRounded.length > 3) {
  console.log(`⚠️  圆角值种类过多 (${allRounded.length} 种): ${allRounded.join(', ')}`);
  console.log('   建议统一为 2-3 种（如 rounded-lg + rounded-xl + rounded-full）');
  issues++;
} else {
  console.log(`✅ 圆角值：共 ${allRounded.length} 种 (${allRounded.join(', ') || '无'})`);
}

// ── 3. 字号分布 ──
function extractTextSizes(html) {
  const matches = html.match(/text-(?:xs|sm|base|lg|xl|2xl|3xl|4xl|5xl|6xl|7xl|8xl|9xl)/g) || [];
  const counts = {};
  matches.forEach(m => { counts[m] = (counts[m] || 0) + 1; });
  return counts;
}

const sizesBySlide = files.map(f => ({ name: f.name, sizes: extractTextSizes(f.content) }));
const tooSmall = sizesBySlide.filter(s => s.sizes['text-xs'] || s.sizes['text-sm']);
if (tooSmall.length > 0) {
  console.log(`⚠️  以下页面使用了过小字号 (text-xs/text-sm)，可能导出后看不清：`);
  tooSmall.forEach(s => console.log(`   ${s.name}`));
  issues++;
} else {
  console.log('✅ 字号：所有页面均 >= text-base (16px)');
}

// ── 4. Google Fonts 引用一致性 ──
function extractGoogleFonts(html) {
  const matches = html.match(/fonts\.googleapis\.com\/css2\?[^"']*/g) || [];
  return matches.sort();
}

const fontsBySlide = files.map(f => ({ name: f.name, fonts: extractGoogleFonts(f.content) }));
const uniqueFontLinks = [...new Set(fontsBySlide.flatMap(s => s.fonts))];

if (uniqueFontLinks.length > 1) {
  console.log(`⚠️  Google Fonts 引用不一致 (${uniqueFontLinks.length} 种)：`);
  uniqueFontLinks.forEach((link, i) => {
    const slides = fontsBySlide.filter(s => s.fonts.includes(link)).map(s => s.name);
    console.log(`   引用 ${i + 1}: ${slides.join(', ')}`);
  });
  issues++;
} else {
  console.log(`✅ Google Fonts：${uniqueFontLinks.length === 0 ? '未使用' : '所有页面一致'}`);
}

// ── 5. Lucide 图标尺寸 ──
function extractIconSizes(html) {
  // 查找 data-lucide 附近的 w-* h-* 类
  const iconBlocks = html.match(/<[^>]*data-lucide[^>]*>/g) || [];
  const sizes = new Set();
  iconBlocks.forEach(block => {
    const wh = block.match(/(?:w-|h-)\d+/g) || [];
    if (wh.length >= 2) sizes.add(wh.sort().join(' '));
  });
  return [...sizes];
}

const iconSizesBySlide = files.map(f => ({ name: f.name, sizes: extractIconSizes(f.content) }));
const allIconSizes = [...new Set(iconSizesBySlide.flatMap(s => s.sizes))];

if (allIconSizes.length > 3) {
  console.log(`⚠️  图标尺寸种类过多 (${allIconSizes.length} 种): ${allIconSizes.join(' | ')}`);
  console.log('   建议统一为 2-3 种规格');
  issues++;
} else {
  console.log(`✅ 图标尺寸：共 ${allIconSizes.length} 种 (${allIconSizes.join(' | ') || '无图标'})`);
}

// ── 总结 ──
console.log('');
if (issues === 0) {
  console.log('🎉 所有页面风格一致，可以导出。');
} else {
  console.log(`⚠️  发现 ${issues} 项一致性问题，建议修复后再导出。`);
}
console.log('');
process.exit(issues > 0 ? 1 : 0);
