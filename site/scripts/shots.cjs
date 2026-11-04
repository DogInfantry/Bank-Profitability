// Local only: share image (public/og.png, 1200x630), README masthead (../docs/img/site.png),
// README exhibit crops (../docs/img/ex*.png, workbench.png) and a phone-width shot (../docs/img/mobile.png).
// Run `npx vite preview` first. Needs `playwright` (not a site dependency); CHROME may point at a headless Chromium.
// The images show numbers bound to the export, so re-run after any model change.
const { chromium } = require('playwright');
const path = require('path');
const url = process.argv[2] || 'http://localhost:4173/';
const exe = process.env.CHROME || path.join(process.env.LOCALAPPDATA || '', 'ms-playwright', 'chromium_headless_shell-1228', 'chrome-headless-shell-win64', 'chrome-headless-shell.exe');
const img = path.join(__dirname, '..', '..', 'docs', 'img');
const exhibits = [
  ['#exhibit-1', 'ex01_roa_path.png'],
  ['#exhibit-3', 'ex03_roa_walk.png'],
  ['#exhibit-6', 'ex06_comps.png'],
  ['#exhibit-8', 'ex08_precedents.png'],
  ['#exhibit-9', 'ex09_moves.png'],
  ['#exhibit-11', 'ex11_implied_roe.png'],
  ['#exhibit-13', 'ex13_tornado.png'],
  ['#exhibit-15', 'ex15_breakevens.png'],
  ['#exhibit-18', 'ex18_two_pct_test.png'],
  ['#workbench-a', 'workbench.png'],
];
(async () => {
  const b = await chromium.launch({ executablePath: exe });
  const shots = [
    { w: 1200, h: 630, scale: 1, out: path.join(__dirname, '..', 'public', 'og.png') },
    { w: 1440, h: 900, scale: 1, out: path.join(img, 'site.png') },
    { w: 390, h: 844, scale: 2, out: path.join(img, 'mobile.png') },
  ];
  for (const s of shots) {
    const p = await b.newPage({ viewport: { width: s.w, height: s.h }, deviceScaleFactor: s.scale, colorScheme: 'light' });
    await p.goto(url, { waitUntil: 'networkidle' });
    await p.waitForTimeout(800);
    await p.screenshot({ path: s.out });
    console.log('wrote', s.out);
    await p.close();
  }
  const p = await b.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1.5, colorScheme: 'light' });
  await p.goto(url, { waitUntil: 'networkidle' });
  // A little breathing room round each crop, in the page's own background colour.
  await p.addStyleTag({ content: '.exhibit, #workbench-a { padding: 18px 24px !important; background: var(--bg, #f7f5f0); }' });
  for (const [sel, file] of exhibits) {
    const el = p.locator(sel).first();
    if (sel === '#exhibit-9') {
      // The bridge builds one move per scroll step; park on the last step so every bar is drawn.
      await p.locator('#moves .st').last().evaluate((n) => n.scrollIntoView({ block: 'center' }));
      await p.waitForTimeout(1200);
    } else {
      await el.scrollIntoViewIfNeeded();
    }
    await p.waitForTimeout(900); // let scroll-triggered D3 transitions finish
    await el.screenshot({ path: path.join(img, file) });
    console.log('wrote', file);
  }
  await b.close();
})();
