#!/usr/bin/env node
/**
 * preview-all.mjs — 汇总预览生成器
 *
 * 用法: node preview-all.mjs <project_dir>
 *
 * 读取 presentation.json，将所有 slide HTML 合并为一个纵向排列的预览页面。
 * 输出到 <project_dir>/preview.html，浏览器打开即可快速浏览全部幻灯片。
 */

import { readFileSync, writeFileSync, existsSync } from 'fs';
import { join } from 'path';

const projectDir = process.argv[2];
if (!projectDir) {
  console.error('用法: node preview-all.mjs <project_dir>');
  process.exit(1);
}

const jsonPath = join(projectDir, 'presentation.json');
if (!existsSync(jsonPath)) {
  console.error(`[FAIL] presentation.json 不存在: ${jsonPath}`);
  process.exit(1);
}

const presentation = JSON.parse(readFileSync(jsonPath, 'utf-8'));
const slides = presentation.slides || [];

if (slides.length === 0) {
  console.error('[FAIL] presentation.json 中没有幻灯片');
  process.exit(1);
}

console.log(`\n📋 生成 ${slides.length} 页预览...\n`);

const slideFrames = slides.map((slide, i) => {
  const filePath = join(projectDir, 'slides', slide.file);
  if (!existsSync(filePath)) {
    console.warn(`  ⚠️ 文件不存在: ${slide.file}`);
    return '';
  }
  const num = String(i + 1).padStart(2, '0');
  return `
    <div class="slide-wrapper">
      <div class="slide-header">
        <span class="slide-num">${num}</span>
        <span class="slide-title">${slide.title || slide.file}</span>
        <span class="slide-type">${slide.type || ''}</span>
      </div>
      <div class="slide-frame">
        <iframe src="slides/${slide.file}" width="1280" height="720" frameborder="0"></iframe>
      </div>
    </div>`;
}).join('\n');

const html = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PPT 预览 — ${presentation.title || 'Untitled'}</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: -apple-system, 'Microsoft YaHei', 'Noto Sans SC', sans-serif;
    background: #0f0f13;
    color: #e2e8f0;
    padding: 40px 20px;
  }
  h1 {
    text-align: center;
    font-size: 24px;
    font-weight: 700;
    margin-bottom: 8px;
    color: #6ee7b7;
  }
  .subtitle {
    text-align: center;
    font-size: 14px;
    color: #64748b;
    margin-bottom: 40px;
  }
  .slide-wrapper {
    max-width: 1320px;
    margin: 0 auto 40px;
  }
  .slide-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 8px;
    padding: 0 4px;
  }
  .slide-num {
    background: rgba(110,231,183,0.15);
    color: #6ee7b7;
    font-size: 13px;
    font-weight: 700;
    padding: 2px 10px;
    border-radius: 6px;
  }
  .slide-title {
    font-size: 15px;
    font-weight: 600;
  }
  .slide-type {
    font-size: 12px;
    color: #64748b;
    background: rgba(255,255,255,0.06);
    padding: 2px 8px;
    border-radius: 4px;
  }
  .slide-frame {
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    overflow: hidden;
    background: #fff;
    aspect-ratio: 1280/720;
    position: relative;
  }
  .slide-frame iframe {
    width: 1280px;
    height: 720px;
    transform-origin: top left;
    transform: scale(var(--scale, 1));
    position: absolute;
    top: 0;
    left: 0;
  }
  .nav-bar {
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    background: rgba(15,15,19,0.9);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 20px;
    padding: 8px 20px;
    font-size: 13px;
    color: #94a3b8;
    z-index: 100;
  }
  .nav-bar span { color: #6ee7b7; font-weight: 700; }
</style>
</head>
<body>
  <h1>${presentation.title || 'PPT 预览'}</h1>
  <p class="subtitle">${slides.length} 页 · 浏览确认后导出</p>
  ${slideFrames}
  <div class="nav-bar">共 <span>${slides.length}</span> 页 · 滚动浏览全部幻灯片</div>
  <script>
    // 根据容器宽度自动缩放 iframe
    function scaleFrames() {
      document.querySelectorAll('.slide-frame').forEach(frame => {
        const containerWidth = frame.clientWidth;
        const scale = containerWidth / 1280;
        frame.style.setProperty('--scale', scale);
        frame.style.height = (720 * scale) + 'px';
      });
    }
    scaleFrames();
    window.addEventListener('resize', scaleFrames);
  </script>
</body>
</html>`;

const outputPath = join(projectDir, 'preview.html');
writeFileSync(outputPath, html, 'utf-8');
console.log(`✅ 预览页面已生成: ${outputPath}`);
console.log('   在浏览器中打开即可查看全部幻灯片。\n');
