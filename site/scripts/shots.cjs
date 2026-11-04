// Local only: share image (public/og.png, 1200x630) and README screenshot (../docs/img/site.png) from the built site.
// Run `npx vite preview` first. Needs `playwright` (not a site dependency); CHROME may point at a headless Chromium.
// The images show the masthead, whose numbers are bound to the export, so re-run after any model change.
const { chromium } = require('playwright');
const path = require('path');
const url = process.argv[2] || 'http://localhost:4173/';
const exe = process.env.CHROME || path.join(process.env.LOCALAPPDATA || '', 'ms-playwright', 'chromium_headless_shell-1228', 'chrome-headless-shell-win64', 'chrome-headless-shell.exe');
(async () => {
  const b = await chromium.launch({ executablePath: exe });
  const shots = [
    { w: 1200, h: 630, scale: 1, out: path.join(__dirname, '..', 'public', 'og.png') },
    { w: 1440, h: 900, scale: 1, out: path.join(__dirname, '..', '..', 'docs', 'img', 'site.png') },
  ];
  for (const s of shots) {
    const p = await b.newPage({ viewport: { width: s.w, height: s.h }, deviceScaleFactor: s.scale, colorScheme: 'light' });
    await p.goto(url, { waitUntil: 'networkidle' });
    await p.waitForTimeout(800);
    await p.screenshot({ path: s.out });
    console.log('wrote', s.out);
    await p.close();
  }
  await b.close();
})();
