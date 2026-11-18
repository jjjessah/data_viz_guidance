// Browser checks for run_checks.py: axe-core rules, sideways overflow, and optional screenshots.
// Called by run_checks.py with one argument: the path to a JSON settings file.
// Needs playwright-core and axe-core (see README.md for the install folder) and a Chrome or Chromium browser.
const fs = require('fs');
const path = require('path');
const cfg = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const nm = cfg.nodeModules;
const { chromium } = require(path.join(nm, 'playwright-core'));
const axeSrc = fs.readFileSync(path.join(nm, 'axe-core', 'axe.min.js'), 'utf8');

const VIEWPORTS = { desktop: { width: 1280, height: 900 }, phone: { width: 390, height: 844 } };

async function openAllDetails(page) {
  await page.evaluate(() => document.querySelectorAll('details').forEach(d => { d.open = true; }));
}

async function checkPage(page, url) {
  const resp = await page.goto(url, { waitUntil: 'load', timeout: 60000 });
  if (!resp || resp.status() >= 400) return { error: `HTTP ${resp ? resp.status() : 'no response'}` };
  await openAllDetails(page);
  await page.addScriptTag({ content: axeSrc });
  return page.evaluate(async (tags) => {
    const r = await axe.run(document, { runOnly: { type: 'tag', values: tags }, resultTypes: ['violations'] });
    const violations = r.violations.map(v => ({
      id: v.id, impact: v.impact, help: v.help, description: v.description, helpUrl: v.helpUrl,
      nodes: v.nodes.map(n => ({ target: n.target.join(' '), html: n.html.slice(0, 160),
                                 failureSummary: n.failureSummary || '' })),
    }));
    const overflow = Math.max(0, document.documentElement.scrollWidth - window.innerWidth);
    const brokenImages = [...document.querySelectorAll('main img')]
      .filter(i => i.complete && i.naturalWidth === 0)
      .map(i => i.getAttribute('src'));
    return { violations, overflowPx: overflow, brokenImages };
  }, cfg.axeTags);
}

async function scrollToSelector(page, sel, offset) {
  await page.evaluate(([sel, offset]) => {
    const el = document.querySelector(sel);
    if (el) window.scrollTo(0, el.getBoundingClientRect().top + window.scrollY - offset);
  }, [sel, offset]);
  await page.waitForTimeout(200);
}

(async () => {
  const browser = await chromium.launch({ executablePath: cfg.chrome, args: ['--no-sandbox'] });
  const out = { pages: {}, screenshots: [] };
  for (const [vpName, vp] of Object.entries(VIEWPORTS)) {
    const ctx = await browser.newContext({ viewport: vp });
    const page = await ctx.newPage();
    for (const p of cfg.pages) {
      out.pages[`${vpName} ${p}`] = await checkPage(page, cfg.baseUrl + p);
    }
    for (const s of cfg.screenshots || []) {
      await page.goto(cfg.baseUrl + s.page, { waitUntil: 'networkidle', timeout: 60000 });
      if (s.open) await page.evaluate((sel) => document.querySelectorAll(sel).forEach(d => { d.open = true; }), s.open);
      const offset = vpName === 'phone' ? 130 : 70;
      if (s.scrollTo) await scrollToSelector(page, s.scrollTo, offset);
      const file = path.join(cfg.shotDir, `${cfg.label}_${vpName}_${s.name}.png`);
      const found = s.scrollTo ? await page.evaluate((sel) => !!document.querySelector(sel), s.scrollTo) : true;
      await page.screenshot({ path: file });
      out.screenshots.push({ file, view: s.name, viewport: vpName, targetFound: found });
    }
    await ctx.close();
  }
  await browser.close();
  fs.writeFileSync(cfg.resultFile, JSON.stringify(out, null, 1));
})().catch(e => { console.error(e); process.exit(1); });
