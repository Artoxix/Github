// node shot.js page.html out.png [width]
const { chromium } = require('playwright'); const path = require('path');
(async () => {
  const [, , page_, out, w] = process.argv;
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: +(w || 1800), height: 1000 } });
  p.on('pageerror', e => { console.error(e.message); process.exit(1); });
  await p.goto('file://' + path.resolve(page_)); await p.waitForFunction(() => window.READY);
  await p.screenshot({ path: out, fullPage: true }); await b.close();
})();
