const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const OUT = '/tmp/claude-0/-home-claude-huroof-app-github-io/f8dc82be-fff1-5272-ba4d-3f9390430d9e/scratchpad/';
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const ctx = await b.newContext({ viewport: { width: 1920, height: 1080 } });
  await ctx.route('**/*', async route => {
    const u = route.request().url();
    if (u.includes('gstatic.com/firebasejs')) return route.fulfill({ contentType: 'application/javascript', body: fs.readFileSync(path.join(__dirname, 'fakefb.js'), 'utf8') });
    if (u.startsWith('https://fonts.')) return route.fulfill({ contentType: 'text/css', body: '' });
    if (u.startsWith('http://app.test/')) return route.fulfill({ contentType: 'text/html', body: fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8') });
    return route.abort();
  });
  const p = await ctx.newPage(); const errs=[]; p.on('pageerror', e => errs.push(String(e)));
  await p.goto('http://app.test/index.html');
  await p.evaluate(() => { window.__FB.users['a@b.c'] = { pw: 'x123456' }; window.__FB.set('users/u_abc', { email: 'a@b.c', expiresAt: Date.now() + 9e9 }); });
  await p.click('[data-role=solo]'); await p.fill('[name=email]', 'a@b.c'); await p.fill('[name=password]', 'x123456'); await p.click('#gateForm button[type=submit]');
  await p.waitForSelector('#v-solo:not([hidden])'); await p.click('[data-act=start]');
  // own a few cells
  const code = await p.evaluate(() => { return document.getElementById('mode-chip').textContent.replace(/\D/g,''); });
  await p.click('[data-cell]'); await p.waitForTimeout(300); await p.click('[data-act=team-g]'); await p.click('[data-act=right]'); await p.waitForTimeout(300);
  await p.click('[data-cell]'); await p.waitForTimeout(300); await p.click('[data-act=team-r]'); await p.waitForTimeout(300);
  // switch same page to screen role (same in-page fake db)
  await p.click('#chg'); await p.evaluate(() => { location.hash = '#screen'; }); await p.click('[data-role=screen]').catch(()=>{});
  await p.waitForSelector('#v-screen:not([hidden])'); await p.waitForTimeout(500);
  await p.screenshot({ path: OUT + 'proj-1080.png' });
  await p.setViewportSize({ width: 1024, height: 768 }); await p.waitForTimeout(300); await p.screenshot({ path: OUT + 'proj-1024.png' });
  console.log('code', code, errs); await b.close();
})().catch(e => { console.error(e); process.exit(1); });
