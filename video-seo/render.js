// Renders index.html frame by frame with headless Chromium and pipes the frames into ffmpeg.
//   node render.js                       -> build/video_silent.mp4 (30 fps), needs build/timeline.json (voice.py)
//   node render.js --fps=60 --out=x.mp4
//   node render.js --stills=0.5,2.8,...  -> build/still_<t>.png (for checking the layout)
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const args = Object.fromEntries(process.argv.slice(2).map(a => {
  const [k, v] = a.replace(/^--/, '').split('=');
  return [k, v ?? true];
}));
const BUILD = path.join(__dirname, 'build');
fs.mkdirSync(BUILD, { recursive: true });

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  page.on('console', m => console.log('[page]', m.text()));
  page.on('pageerror', e => { console.error('[pageerror]', e.message); process.exit(1); });
  const timeline = JSON.parse(fs.readFileSync(path.join(BUILD, 'timeline.json'), 'utf8'));
  await page.addInitScript(tl => { window.TIMELINE = tl; }, timeline);
  await page.goto('file://' + path.join(__dirname, 'index.html'));
  await page.waitForFunction(() => window.READY === true, null, { timeout: 30000 });
  const { duration, cues, marks } = await page.evaluate(() => ({ duration: window.DURATION, cues: window.CUES, marks: window.MARKS }));
  fs.writeFileSync(path.join(BUILD, 'cues.json'), JSON.stringify({ duration, cues, marks }, null, 1));

  if (args.stills) {
    for (const t of String(args.stills).split(',').map(Number)) {
      await page.evaluate(t => window.render(t), t);
      await page.screenshot({ path: path.join(BUILD, `still_${t.toFixed(2)}.png`) });
    }
  } else {
    const fps = Number(args.fps || 30);
    const out = args.out || path.join(BUILD, 'video_silent.mp4');
    const total = Math.round(duration * fps);
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-',
      '-c:v', 'libx264', '-preset', 'slow', '-crf', '15', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out],
      { stdio: ['pipe', 'inherit', 'inherit'] });
    const t0 = Date.now();
    for (let i = 0; i < total; i++) {
      await page.evaluate(t => window.render(t), i / fps);
      const buf = await page.screenshot({ type: 'jpeg', quality: 96 });
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      if (i % 120 === 0) console.log(`frame ${i}/${total}  ${((Date.now() - t0) / 1000).toFixed(0)}s`);
    }
    ff.stdin.end();
    await new Promise(r => ff.on('close', r));
    console.log('wrote', out);
  }
  await browser.close();
})();
