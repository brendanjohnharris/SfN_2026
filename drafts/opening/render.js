// Render SVG drafts to PNG with the pre-installed Playwright Chromium.
// Usage: node render.js out_dir scale file1.svg [file2.svg ...]
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
(async () => {
  const [outDir, scaleArg, ...files] = process.argv.slice(2);
  const scale = parseFloat(scaleArg || '1');
  const browser = await chromium.launch();
  const page = await browser.newPage({ deviceScaleFactor: scale });
  for (const f of files) {
    const svg = fs.readFileSync(f, 'utf8');
    const m = svg.match(/viewBox="0 0 ([\d.]+) ([\d.]+)"/);
    const w = Math.ceil(parseFloat(m[1])), h = Math.ceil(parseFloat(m[2]));
    await page.setViewportSize({ width: w, height: h });
    await page.setContent(`<html><body style="margin:0;background:#fff">${svg.replace(/<\?xml[^>]*>/, '')}</body></html>`);
    await page.evaluate(() => document.fonts.ready);
    const out = path.join(outDir, path.basename(f).replace(/\.svg$/, '.png'));
    await page.screenshot({ path: out, clip: { x: 0, y: 0, width: w, height: h } });
    console.log('rendered', out);
  }
  await browser.close();
})();
